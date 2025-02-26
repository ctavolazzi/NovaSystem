"""
OpenAI implementation of the LLM provider.
"""
import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional, AsyncGenerator

import httpx
from dotenv import load_dotenv

from agents.llm.provider import LLMProvider

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Default API key from environment
DEFAULT_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class OpenAIProvider(LLMProvider):
    """OpenAI implementation of the LLM provider."""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key. Defaults to environment variable.
            **kwargs: Additional configuration options.
        """
        super().__init__(api_key=api_key or DEFAULT_OPENAI_API_KEY, **kwargs)
        self.base_url = kwargs.get("base_url", "https://api.openai.com/v1")
        self.default_model = kwargs.get("default_model", "gpt-4")
        self.timeout = kwargs.get("timeout", 60)
        self.http_client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )

    async def complete(self,
                       prompt: str,
                       max_tokens: int = 1000,
                       temperature: float = 0.7,
                       **kwargs) -> Dict[str, Any]:
        """
        Generate a completion from OpenAI.

        Args:
            prompt: The prompt to complete.
            max_tokens: Maximum tokens to generate.
            temperature: Controls randomness (0.0 to 1.0).
            **kwargs: Additional parameters to pass to the API.

        Returns:
            The API response as a dictionary.

        Raises:
            Exception: If the API request fails.
        """
        model = kwargs.get("model", self.default_model)
        messages = kwargs.get("messages", [{"role": "user", "content": prompt}])

        # If only prompt is provided, convert to messages format
        if not kwargs.get("messages") and prompt:
            messages = [{"role": "user", "content": prompt}]

        # Prepare the request payload
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        # Add optional parameters if provided
        for param in ["top_p", "n", "stop", "presence_penalty", "frequency_penalty"]:
            if param in kwargs:
                payload[param] = kwargs[param]

        try:
            # Make the API request
            response = await self.http_client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    async def complete_stream(self,
                             prompt: str,
                             max_tokens: int = 1000,
                             temperature: float = 0.7,
                             **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate a streaming completion from OpenAI.

        Args:
            prompt: The prompt to complete.
            max_tokens: Maximum tokens to generate.
            temperature: Controls randomness (0.0 to 1.0).
            **kwargs: Additional parameters to pass to the API.

        Yields:
            Partial API responses as dictionaries.

        Raises:
            Exception: If the API request fails.
        """
        model = kwargs.get("model", self.default_model)
        messages = kwargs.get("messages", [{"role": "user", "content": prompt}])

        # If only prompt is provided, convert to messages format
        if not kwargs.get("messages") and prompt:
            messages = [{"role": "user", "content": prompt}]

        # Prepare the request payload
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
        }

        # Add optional parameters if provided
        for param in ["top_p", "n", "stop", "presence_penalty", "frequency_penalty"]:
            if param in kwargs:
                payload[param] = kwargs[param]

        try:
            # Make the streaming API request
            async with self.http_client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=self.timeout
            ) as response:
                response.raise_for_status()

                # Process the streaming response
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        line = line[6:]  # Remove "data: " prefix

                        # Skip empty lines and "[DONE]" marker
                        if not line or line == "[DONE]":
                            continue

                        try:
                            chunk = json.loads(line)
                            yield chunk
                        except json.JSONDecodeError as e:
                            logger.error(f"Error parsing OpenAI response: {e}")

        except Exception as e:
            logger.error(f"OpenAI streaming API error: {e}")
            raise

    async def close(self):
        """Close the HTTP client."""
        await self.http_client.aclose()