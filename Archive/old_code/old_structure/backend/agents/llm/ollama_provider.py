"""
Ollama implementation of the LLM provider.
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

# Default Ollama host from environment
DEFAULT_OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_OLLAMA_MODEL = os.getenv("DEFAULT_OLLAMA_MODEL", "llama3")


class OllamaProvider(LLMProvider):
    """Ollama implementation of the LLM provider."""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize Ollama provider.

        Args:
            api_key: Not used for Ollama, included for interface compatibility
            **kwargs: Additional configuration options.
        """
        super().__init__(api_key=None, **kwargs)
        self.base_url = kwargs.get("base_url", DEFAULT_OLLAMA_HOST)
        self.default_model = kwargs.get("default_model", DEFAULT_OLLAMA_MODEL)
        self.timeout = kwargs.get("timeout", 60)
        self.http_client = httpx.AsyncClient(timeout=self.timeout)

    async def complete(self,
                       prompt: str,
                       max_tokens: int = 1000,
                       temperature: float = 0.7,
                       **kwargs) -> Dict[str, Any]:
        """
        Generate a completion from Ollama.

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

        # Convert messages format to a prompt if provided
        messages = kwargs.get("messages", [])
        if messages and not prompt:
            # Simple conversion of messages to a text prompt
            prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

        # Prepare the request payload
        payload = {
            "model": model,
            "prompt": prompt,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            }
        }

        # Add optional parameters if provided
        if "top_p" in kwargs:
            payload["options"]["top_p"] = kwargs["top_p"]
        if "top_k" in kwargs:
            payload["options"]["top_k"] = kwargs["top_k"]
        if "system" in kwargs:
            payload["system"] = kwargs["system"]

        try:
            # Make the API request
            response = await self.http_client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            response.raise_for_status()
            response_data = response.json()

            # Convert Ollama response format to be similar to OpenAI for compatibility
            return {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": response_data.get("response", "")
                    },
                    "finish_reason": "stop"
                }],
                "model": model,
                "usage": {
                    "completion_tokens": response_data.get("eval_count", 0),
                    "prompt_tokens": response_data.get("prompt_eval_count", 0),
                    "total_tokens": response_data.get("eval_count", 0) + response_data.get("prompt_eval_count", 0)
                },
                "raw_response": response_data  # Include the raw response for debugging
            }
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise

    async def complete_stream(self,
                             prompt: str,
                             max_tokens: int = 1000,
                             temperature: float = 0.7,
                             **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate a streaming completion from Ollama.

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

        # Convert messages format to a prompt if provided
        messages = kwargs.get("messages", [])
        if messages and not prompt:
            # Simple conversion of messages to a text prompt
            prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

        # Prepare the request payload
        payload = {
            "model": model,
            "prompt": prompt,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            },
            "stream": True
        }

        # Add optional parameters if provided
        if "top_p" in kwargs:
            payload["options"]["top_p"] = kwargs["top_p"]
        if "top_k" in kwargs:
            payload["options"]["top_k"] = kwargs["top_k"]
        if "system" in kwargs:
            payload["system"] = kwargs["system"]

        try:
            # Make the streaming API request
            async with self.http_client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            ) as response:
                response.raise_for_status()

                # Process the streaming response
                buffer = ""
                async for chunk in response.aiter_bytes():
                    if not chunk:
                        continue

                    try:
                        # Decode and process the chunk
                        chunk_str = chunk.decode('utf-8')
                        lines = (buffer + chunk_str).split('\n')
                        buffer = lines.pop()  # Keep the last possibly incomplete line

                        for line in lines:
                            if not line.strip():
                                continue

                            data = json.loads(line)

                            # Convert to a format similar to OpenAI's streaming format
                            yield {
                                "choices": [{
                                    "delta": {
                                        "role": "assistant",
                                        "content": data.get("response", "")
                                    },
                                    "finish_reason": None if not data.get("done", False) else "stop"
                                }],
                                "model": model,
                                "raw_response": data  # Include the raw response
                            }

                            if data.get("done", False):
                                break

                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing Ollama response: {e}")
                    except Exception as e:
                        logger.error(f"Error processing Ollama stream: {e}")
                        raise

        except Exception as e:
            logger.error(f"Ollama streaming API error: {e}")
            raise

    async def close(self):
        """Close the HTTP client."""
        await self.http_client.aclose()