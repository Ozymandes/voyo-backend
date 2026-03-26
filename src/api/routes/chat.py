"""
Chat Routes for CLEO API
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from src.cleo.cleo_agent import CleoAgent
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
agent = CleoAgent()

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., description="User's message to CLEO")
    user_id: Optional[str] = Field(None, description="User ID for personalization")
    debug: bool = Field(False, description="Enable debug mode")

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str = Field(..., description="CLEO's response")
    user_id: Optional[str] = Field(None, description="User ID")
    timestamp: str = Field(..., description="Response timestamp")

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint

    Processes user messages and returns CLEO's responses.

    Example:
        ```json
        {
            "message": "What are the opening hours for the Pyramids?",
            "user_id": "user123",
            "debug": false
        }
        ```
    """
    try:
        response = agent.process_message(
            user_message=request.message,
            user_id=request.user_id,
            debug=request.debug
        )

        return ChatResponse(
            response=response,
            user_id=request.user_id,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversation/history/{user_id}")
async def get_conversation_history(user_id: str, limit: int = 20):
    """
    Get conversation history for user

    Args:
        user_id: User identifier
        limit: Maximum number of messages to return
    """
    try:
        history = agent.memory.get_history(user_id, last_n=limit)
        return {"user_id": user_id, "history": history}
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/conversation/history/{user_id}")
async def clear_conversation_history(user_id: str):
    """
    Clear conversation history for user
    """
    try:
        agent.memory.clear_user_history(user_id)
        return {"message": "Conversation history cleared"}
    except Exception as e:
        logger.error(f"Error clearing history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversation/stats/{user_id}")
async def get_conversation_stats(user_id: str):
    """
    Get conversation statistics for user
    """
    try:
        stats = agent.memory.get_conversation_stats(user_id)
        return {"user_id": user_id, "stats": stats}
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
