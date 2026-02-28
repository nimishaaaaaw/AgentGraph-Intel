"""
Chat routes — standard and streaming endpoints.
"""
import json
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from services.chat_service import ChatService
from utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["chat"])

_chat_service = ChatService()


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str = Field(default="default", max_length=64)
    history: Optional[List[ChatMessage]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    sources: List[dict] = Field(default_factory=list)
    steps_taken: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message and receive a complete answer from the agent pipeline.
    """
    try:
        result = _chat_service.chat(
            message=request.message,
            session_id=request.session_id,
            history=[m.model_dump() for m in (request.history or [])],
        )
        return ChatResponse(
            answer=result["answer"],
            session_id=request.session_id,
            sources=result.get("sources", []),
            steps_taken=result.get("steps_taken", []),
        )
    except Exception as exc:
        logger.exception("Chat endpoint error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint using Server-Sent Events.
    Each event is a JSON-encoded chunk or a ``[DONE]`` sentinel.
    """

    async def event_generator():
        try:
            result = _chat_service.chat(
                message=request.message,
                session_id=request.session_id,
                history=[m.model_dump() for m in (request.history or [])],
            )
            answer: str = result["answer"]

            # Stream in ~50-char chunks to simulate token streaming
            chunk_size = 50
            for i in range(0, len(answer), chunk_size):
                chunk = answer[i : i + chunk_size]
                payload = json.dumps({"chunk": chunk, "done": False})
                yield f"data: {payload}\n\n"

            # Send final metadata
            final = json.dumps(
                {
                    "chunk": "",
                    "done": True,
                    "sources": result.get("sources", []),
                    "steps_taken": result.get("steps_taken", []),
                }
            )
            yield f"data: {final}\n\n"

        except Exception as exc:
            logger.exception("Streaming chat error: %s", exc)
            error_payload = json.dumps({"error": str(exc), "done": True})
            yield f"data: {error_payload}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Retrieve message history for a given session."""
    try:
        history = _chat_service.get_history(session_id)
        return {"session_id": session_id, "history": history}
    except Exception as exc:
        logger.exception("History retrieval error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.delete("/chat/history/{session_id}")
async def clear_chat_history(session_id: str):
    """Clear message history for a given session."""
    _chat_service.clear_history(session_id)
    return {"message": f"History cleared for session '{session_id}'"}
