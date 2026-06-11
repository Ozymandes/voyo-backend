"""
CLEO FastAPI Application
REST API for CLEO chatbot
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import chat, profile, recommendations, routing, itinerary
import logging

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CLEO API",
    description="Cairo Local Expert & Operator - Egyptian Travel Guide",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(profile.router, prefix="/api/v1", tags=["profile"])
app.include_router(recommendations.router, tags=["recommendations"])
app.include_router(routing.router, tags=["routing"])
app.include_router(itinerary.router, tags=["itinerary"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "CLEO - Cairo Local Expert & Operator",
        "status": "operational",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    """Health check for monitoring"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
