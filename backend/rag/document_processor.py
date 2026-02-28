"""
Document processor — handles ingestion, chunking, and metadata extraction
for PDF, plain-text, and Markdown files.
"""
import hashlib
import re
from pathlib import Path
from typing import List, Dict, Any

from utils.logger import get_logger

logger = get_logger(__name__)

# Default chunking parameters
DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 150


def _compute_doc_id(content: str, source: str) -> str:
    """Deterministic document ID based on content hash."""
    return hashlib.sha256(f"{source}:{content[:200]}".encode()).hexdigest()[:16]


class DocumentChunk:
    """Represents a single processed chunk ready for embedding."""

    __slots__ = ("chunk_id", "doc_id", "content", "metadata")

    def __init__(
        self,
        chunk_id: str,
        doc_id: str,
        content: str,
        metadata: Dict[str, Any],
    ) -> None:
        self.chunk_id = chunk_id
        self.doc_id = doc_id
        self.content = content
        self.metadata = metadata

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "content": self.content,
            "metadata": self.metadata,
        }


class DocumentProcessor:
    """
    Reads documents from disk, extracts text, and splits them into
    overlapping chunks suitable for embedding.
    """

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process_file(self, file_path: str) -> List[DocumentChunk]:
        """Detect file type, extract text, and return chunks."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        suffix = path.suffix.lower()
        if suffix == ".pdf":
            text = self._extract_pdf(str(path))
        elif suffix in {".txt", ".md", ".markdown"}:
            text = path.read_text(encoding="utf-8", errors="replace")
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

        doc_id = _compute_doc_id(text, str(path))
        chunks = self._split_text(text)
        logger.info(
            "Processed '%s' → %d chunks (doc_id=%s)", path.name, len(chunks), doc_id
        )

        return [
            DocumentChunk(
                chunk_id=f"{doc_id}-{i}",
                doc_id=doc_id,
                content=chunk,
                metadata={
                    "source": str(path),
                    "filename": path.name,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "doc_id": doc_id,
                },
            )
            for i, chunk in enumerate(chunks)
        ]

    def process_text(
        self, text: str, source: str = "inline"
    ) -> List[DocumentChunk]:
        """Process raw text directly (e.g. from an API upload)."""
        doc_id = _compute_doc_id(text, source)
        chunks = self._split_text(text)
        return [
            DocumentChunk(
                chunk_id=f"{doc_id}-{i}",
                doc_id=doc_id,
                content=chunk,
                metadata={
                    "source": source,
                    "filename": source,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "doc_id": doc_id,
                },
            )
            for i, chunk in enumerate(chunks)
        ]

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _extract_pdf(self, path: str) -> str:
        """Extract plain text from a PDF file using PyPDF2."""
        try:
            import PyPDF2  # noqa: PLC0415

            with open(path, "rb") as fh:
                reader = PyPDF2.PdfReader(fh)
                pages = [
                    page.extract_text() or "" for page in reader.pages
                ]
            return "\n\n".join(pages)
        except Exception as exc:
            logger.error("PDF extraction failed for %s: %s", path, exc)
            raise

    def _split_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks.

        Strategy:
        1. Split on paragraph boundaries first.
        2. If a paragraph exceeds ``chunk_size``, split it on sentences.
        3. Accumulate chunks with overlap.
        """
        # Normalise whitespace
        text = re.sub(r"\n{3,}", "\n\n", text.strip())

        paragraphs = text.split("\n\n")
        raw_sentences: List[str] = []
        for para in paragraphs:
            # Rough sentence split on ". " / "! " / "? "
            sentences = re.split(r"(?<=[.!?])\s+", para.strip())
            raw_sentences.extend(s for s in sentences if s)

        chunks: List[str] = []
        current: List[str] = []
        current_len = 0

        for sentence in raw_sentences:
            sent_len = len(sentence)
            if current_len + sent_len > self.chunk_size and current:
                chunks.append(" ".join(current))
                # Keep overlap — drop sentences from the front
                while current and current_len > self.chunk_overlap:
                    removed = current.pop(0)
                    current_len -= len(removed) + 1
            current.append(sentence)
            current_len += sent_len + 1

        if current:
            chunks.append(" ".join(current))

        return [c for c in chunks if len(c.strip()) > 20]
