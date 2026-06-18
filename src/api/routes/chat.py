"""
Chat Routes for CLEO API — Async + Streaming
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import List, Optional

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
    message: str = Field("", description="User's message to CLEO")
    user_id: Optional[str] = Field(None, description="User ID for personalization")
    debug: bool = Field(False, description="Enable debug mode")
    poi_id: Optional[int] = Field(
        None, description="POI id for the 'poi_explain' intent (grounded deep-dive)"
    )
    intent: Optional[str] = Field(
        None, description="Request intent, e.g. 'poi_explain' to explain the given poi_id"
    )


class SourceItem(BaseModel):
    """A single provenance pill shown under CLEO's answer (Tier 2 #3)."""
    label: str = Field(..., description="Human label, e.g. 'Karnak Temple' or 'OpenWeather (Luxor)'")
    kind: str = Field(..., description="'database' | 'weather' | 'web' | 'image'")


class ChatResponse(BaseModel):
    """Response model for chat endpoint.

    Non-breaking extension (D2): ``response`` remains the primary text field
    so older clients keep working. ``sources`` and ``confidence`` are optional
    and omitted (null) when CLEO answered from general knowledge or a cached
    reply with no recorded provenance.
    """
    response: str = Field(..., description="CLEO's response")
    user_id: Optional[str] = Field(None, description="User ID")
    timestamp: str = Field(..., description="Response timestamp")
    sources: Optional[List[SourceItem]] = Field(
        None, description="Provenance pills (DB rows / weather / web) grounding the answer"
    )
    confidence: Optional[str] = Field(
        None, description="Coarse grounding confidence: 'high' | 'medium' | 'low'"
    )


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
    When ``intent == 'poi_explain'`` and ``poi_id`` is set, runs the
    grounded POI deep-dive instead of the free-form pipeline.
    """
    try:
        if request.intent == "poi_explain" and request.poi_id is not None:
            result = await agent.explain_poi(
                poi_id=request.poi_id,
                user_message=request.message,
                user_id=request.user_id,
                debug=request.debug,
            )
        else:
            result = await agent.process_message(
                user_message=request.message,
                user_id=request.user_id,
                debug=request.debug,
            )

        return ChatResponse(
            response=result.text,
            user_id=request.user_id,
            timestamp=datetime.now().isoformat(),
            sources=[
                SourceItem(label=s.label, kind=s.kind) for s in result.sources
            ] or None,
            confidence=result.confidence,
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
            # The underlying "stream" methods just chunk an already-complete
            # response, so we call the non-stream pipeline once (which also
            # gives us the source provenance) and emit the text in chunks + a
            # final ``sources`` event. Keeps provenance consistent with /chat.
            if request.intent == "poi_explain" and request.poi_id is not None:
                result = await agent.explain_poi(
                    poi_id=request.poi_id,
                    user_message=request.message,
                    user_id=request.user_id,
                    debug=request.debug,
                )
            else:
                result = await agent.process_message(
                    user_message=request.message,
                    user_id=request.user_id,
                    debug=request.debug,
                )

            text = result.text
            chunk_size = 5
            for i in range(0, len(text), chunk_size):
                payload = json.dumps({"chunk": text[i : i + chunk_size], "done": False})
                yield f"data: {payload}\n\n"

            # Provenance pills (Tier 2 #3) — emitted once, after the text, so
            # the client can render source pills when streaming completes.
            meta_payload = json.dumps({
                "chunk": "",
                "done": False,
                "sources": [{"label": s.label, "kind": s.kind} for s in result.sources],
                "confidence": result.confidence,
            })
            yield f"data: {meta_payload}\n\n"

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
