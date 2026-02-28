"""
Document management routes — upload, list, and delete documents.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from services.document_service import DocumentService
from utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["documents"])

_doc_service = DocumentService()


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class DocumentInfo(BaseModel):
    doc_id: str
    filename: str
    source: str
    chunk_count: Optional[int] = None


class UploadResponse(BaseModel):
    message: str
    doc_id: str
    filename: str
    chunks_created: int


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/documents/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    description: Optional[str] = Form(default=None),
):
    """
    Upload a PDF, TXT, or Markdown file for ingestion into the RAG pipeline.
    The file is processed, chunked, embedded, and stored in ChromaDB.
    """
    allowed_types = {
        "application/pdf",
        "text/plain",
        "text/markdown",
        "text/x-markdown",
    }
    allowed_extensions = {".pdf", ".txt", ".md", ".markdown"}

    filename = file.filename or "upload"
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {allowed_extensions}",
        )

    try:
        content = await file.read()
        result = _doc_service.ingest_bytes(
            content=content,
            filename=filename,
            description=description,
        )
        return UploadResponse(
            message="Document uploaded and indexed successfully",
            doc_id=result["doc_id"],
            filename=filename,
            chunks_created=result["chunks_created"],
        )
    except Exception as exc:
        logger.exception("Document upload failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/documents", response_model=List[DocumentInfo])
async def list_documents():
    """List all ingested documents."""
    try:
        docs = _doc_service.list_documents()
        return [
            DocumentInfo(
                doc_id=d.get("doc_id", ""),
                filename=d.get("filename", ""),
                source=d.get("source", ""),
            )
            for d in docs
        ]
    except Exception as exc:
        logger.exception("Document list failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete all chunks for a given document from the vector store."""
    try:
        _doc_service.delete_document(doc_id)
        return {"message": f"Document '{doc_id}' deleted successfully"}
    except Exception as exc:
        logger.exception("Document deletion failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/documents/{doc_id}/chunks")
async def get_document_chunks(doc_id: str, limit: int = 20):
    """Return the stored chunks for a document (useful for debugging)."""
    try:
        chunks = _doc_service.get_chunks(doc_id, limit=limit)
        return {"doc_id": doc_id, "chunks": chunks}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
