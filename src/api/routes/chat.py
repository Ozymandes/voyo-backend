"""
Chat Routes for CLEO API — Async + Streaming
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.cleo.cleo_agent import CleoAgent

logger = logging.getLogger(__name__)

router = APIRouter()

# Lazy-init: create the agent once at module level.  ``CleoAgent.__init__``
# is synchronous and only does lightweight setup (no LLM call).
agent = CleoAgent()


# ── Request / Response models ─────────────────────────────────────────

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="User's message to CLEO")
    user_id: Optional[str] = Field(None, description="User ID for personalization")
    debug: bool = Field(False, description="Enable debug mode")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="CLEO's response")
    user_id: Optional[str] = Field(None, description="User ID")
    timestamp: str = Field(..., description="Response timestamp")


class StreamEvent(BaseModel):
    """SSE event payload."""
    chunk: str
    done: bool = False


# ── Endpoints ──────────────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint (async).

    Processes user messages through CLEO and returns the full response.
    """
    try:
        response = await agent.process_message(
            user_message=request.message,
            user_id=request.user_id,
            debug=request.debug,
        )

        return ChatResponse(
            response=response,
            user_id=request.user_id,
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    SSE streaming chat endpoint.

    Yields ``data: {"chunk": "..."}\\n\\n`` events as the response is
    generated, followed by a ``data: {"chunk": "", "done": true}\\n\\n``
    sentinel.
    """
    async def event_generator():
        try:
            async for chunk in agent.process_message_stream(
                user_message=request.message,
                user_id=request.user_id,
                debug=request.debug,
            ):
                payload = json.dumps({"chunk": chunk, "done": False})
                yield f"data: {payload}\n\n"

            # Sentinel
            yield f"data: {json.dumps({'chunk': '', 'done': True})}\n\n"

        except Exception as e:
            logger.error(f"Stream error: {e}", exc_info=True)
            error_payload = json.dumps({"chunk": f"[Error: {e}]", "done": True})
            yield f"data: {error_payload}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ── Conversation history endpoints ─────────────────────────────────────

@router.get("/conversation/history/{user_id}")
async def get_conversation_history(user_id: str, limit: int = 20):
    """Get conversation history for a user (from Supabase)."""
    try:
        history = agent.memory.get_history(user_id, last_n=limit)
        return {"user_id": user_id, "history": history}
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversation/history/{user_id}")
async def clear_conversation_history(user_id: str):
    """Clear conversation history for a user."""
    try:
        agent.memory.clear_user_history(user_id)
        return {"message": "Conversation history cleared"}
    except Exception as e:
        logger.error(f"Error clearing history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversation/stats/{user_id}")
async def get_conversation_stats(user_id: str):
    """Get conversation statistics for a user."""
    try:
        stats = agent.memory.get_conversation_stats(user_id)
        return {"user_id": user_id, "stats": stats}
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
