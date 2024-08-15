"""
Module for interacting with the Ollama language model.
"""

import logging
from langchain_community.llms import Ollama
from config import CONFIG

logger = logging.getLogger(__name__)

class OllamaError(Exception):
    """Custom exception for Ollama-related errors."""
    pass

def get_ollama():
    """Initialize and return an Ollama instance."""
    try:
        ollama = Ollama(base_url=CONFIG['OLLAMA_URL'], model=CONFIG['OLLAMA_MODEL'])
        # Test the connection
        ollama("Test")
        return ollama
    except Exception as e:
        logger.error(f"Error initializing Ollama: {str(e)}")
        raise OllamaError(f"Failed to initialize Ollama: {str(e)}")
