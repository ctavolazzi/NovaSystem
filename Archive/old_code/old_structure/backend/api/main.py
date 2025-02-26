from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import logging
from typing import Dict, Any

# Import routers
from api.routers import agents, ollama, nova, github

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("nova-api")

# Initialize FastAPI app
app = FastAPI(
    title="NovaSystem API",
    description="API for the NovaSystem multi-agent framework",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check() -> Dict[str, Any]:
    """Check if the API is running."""
    return {
        "status": "healthy",
        "version": app.version,
    }

# Root endpoint
@app.get("/", tags=["System"])
async def root() -> Dict[str, Any]:
    """Root endpoint with API information."""
    return {
        "name": "NovaSystem API",
        "version": app.version,
        "docs_url": "/docs",
    }

# Include routers
app.include_router(agents.router)
app.include_router(ollama.router)
app.include_router(nova.router)
app.include_router(github.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)