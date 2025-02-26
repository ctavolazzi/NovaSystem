"""
API endpoints for Ollama integration.
"""
import logging
import os
from typing import Any, Dict, List

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Get Ollama host from environment
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Create router
router = APIRouter(prefix="/ollama", tags=["Ollama"])


# ----- Pydantic models for responses -----

class OllamaModel(BaseModel):
    """Ollama model information."""
    name: str
    modified_at: str
    size: int
    digest: str
    details: Dict[str, Any] = {}


# ----- API endpoints -----

@router.get("/models", response_model=List[OllamaModel])
async def list_models() -> List[Dict[str, Any]]:
    """
    List all available Ollama models.

    Returns:
        List of available models.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{OLLAMA_HOST}/api/tags")
            response.raise_for_status()
            data = response.json()

            # Parse and enhance model data
            models = []
            for model in data.get("models", []):
                # Add human-readable size
                size_bytes = model.get("size", 0)
                if size_bytes >= 1_000_000_000:
                    size_gb = size_bytes / 1_000_000_000
                    human_size = f"{size_gb:.1f}GB"
                else:
                    size_mb = size_bytes / 1_000_000
                    human_size = f"{size_mb:.1f}MB"

                # Extract parameter count from model name (if available)
                name = model.get("name", "")
                parameter_size = ""

                # Common model parameter patterns
                if ":7b" in name.lower():
                    parameter_size = "7B"
                elif ":13b" in name.lower():
                    parameter_size = "13B"
                elif ":34b" in name.lower():
                    parameter_size = "34B"
                elif ":70b" in name.lower():
                    parameter_size = "70B"

                # Add enhanced details
                model["details"] = {
                    "human_size": human_size,
                    "parameter_size": parameter_size
                }

                models.append(model)

            return models
    except httpx.RequestError as e:
        logger.error(f"Error connecting to Ollama: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not connect to Ollama server. Make sure it's running."
        )
    except Exception as e:
        logger.error(f"Error listing Ollama models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing models: {str(e)}"
        )


@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """
    Check if Ollama is running.

    Returns:
        Status information.
    """
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{OLLAMA_HOST}/api/tags")
            response.raise_for_status()

            # Count available models
            data = response.json()
            model_count = len(data.get("models", []))

            return {
                "status": "running",
                "url": OLLAMA_HOST,
                "model_count": model_count
            }
    except Exception as e:
        logger.error(f"Ollama status check failed: {e}")
        return {
            "status": "not_running",
            "error": str(e)
        }