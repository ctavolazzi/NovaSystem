"""
LLM Provider abstract base class.

This module defines the interface for LLM providers that can be used by agents.
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, AsyncGenerator

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize LLM provider."""
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    async def complete(self,
                       prompt: str,
                       max_tokens: int = 1000,
                       temperature: float = 0.7,
                       **kwargs) -> Dict[str, Any]:
        """
        Generate a completion for the given prompt.

        Args:
            prompt: The prompt to generate a completion for.
            max_tokens: The maximum number of tokens to generate.
            temperature: Controls randomness. Higher values like 0.8 will make the output more random,
                         while lower values like 0.2 will make it more focused and deterministic.
            **kwargs: Additional provider-specific parameters.

        Returns:
            A dictionary containing the response data.
        """
        pass

    @abstractmethod
    async def complete_stream(self,
                             prompt: str,
                             max_tokens: int = 1000,
                             temperature: float = 0.7,
                             **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate a streaming completion for the given prompt.

        Args:
            prompt: The prompt to generate a completion for.
            max_tokens: The maximum number of tokens to generate.
            temperature: Controls randomness. Higher values like 0.8 will make the output more random,
                         while lower values like 0.2 will make it more focused and deterministic.
            **kwargs: Additional provider-specific parameters.

        Yields:
            Dictionaries containing partial response data.
        """
        pass

    def __repr__(self) -> str:
        """String representation of the LLM provider."""
        return f"<{self.__class__.__name__}>"