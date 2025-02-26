from typing import List, Dict, Any, Optional, AsyncIterator
import ollama
import json
import requests
from dataclasses import dataclass

@dataclass
class OllamaConfig:
    """Configuration for Ollama service"""
    host: str = "http://localhost:11434"
    default_model: str = "llama3"
    timeout: int = 120

class OllamaService:
    """Service for interacting with Ollama models"""

    def __init__(self, config: Optional[OllamaConfig] = None):
        self.config = config or OllamaConfig()
        self.async_client = ollama.AsyncClient(host=self.config.host)

    async def get_completion(self, messages: List[Dict[str, Any]], model: Optional[str] = None) -> str:
        """
        Get a completion from Ollama

        Args:
            messages: List of message dictionaries in OpenAI format
            model: Optional model name, defaults to config.default_model

        Returns:
            The completion text
        """
        try:
            # Convert OpenAI format to Ollama format if needed
            ollama_messages = self._convert_to_ollama_format(messages)

            response = await self.async_client.chat(
                model=model or self.config.default_model,
                messages=ollama_messages
            )
            return response['message']['content']

        except Exception as e:
            return self._handle_error(e, model)

    async def get_streaming_completion(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None
    ) -> AsyncIterator[str]:
        """
        Get a streaming completion from Ollama

        Args:
            messages: List of message dictionaries in OpenAI format
            model: Optional model name, defaults to config.default_model

        Yields:
            Tokens as they arrive
        """
        try:
            ollama_messages = self._convert_to_ollama_format(messages)

            stream = await self.async_client.chat(
                model=model or self.config.default_model,
                messages=ollama_messages,
                stream=True
            )

            async for part in stream:
                if 'message' in part and 'content' in part['message']:
                    yield part['message']['content']

        except Exception as e:
            yield self._handle_error(e, model)

    def _convert_to_ollama_format(self, messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Convert OpenAI message format to Ollama format"""
        ollama_messages = []
        for msg in messages:
            content = msg.get("content", [])
            if isinstance(content, list):
                # Extract text from content array
                text = " ".join(item.get("text", "") for item in content if item.get("type") == "text")
            else:
                text = str(content)
            ollama_messages.append({"role": msg["role"], "content": text})
        return ollama_messages

    def _handle_error(self, error: Exception, model: Optional[str] = None) -> str:
        """Handle common Ollama errors with helpful messages"""
        error_str = str(error).lower()

        if "model not found" in error_str:
            return f"Error: Please run 'ollama pull {model or self.config.default_model}' first to download the model."
        elif "connection refused" in error_str:
            return "Error: Cannot connect to Ollama. Is it running? Start with 'ollama serve'"
        else:
            return f"Ollama Error: {str(error)}"

    async def test_connection(self) -> bool:
        """Test the connection to Ollama server"""
        try:
            test_messages = [{"role": "user", "content": "test"}]
            await self.get_completion(test_messages)
            return True
        except Exception:
            return False

# Example usage
if __name__ == "__main__":
    import asyncio

    async def main():
        # Create service with custom config
        config = OllamaConfig(
            host="http://localhost:11434",
            default_model="llama3",
            timeout=60
        )
        service = OllamaService(config)

        # Test connection
        is_connected = await service.test_connection()
        print(f"Connection status: {'✅ Connected' if is_connected else '❌ Failed'}")

        if is_connected:
            # Test completion
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello!"}
            ]

            # Test regular completion
            response = await service.get_completion(messages)
            print("\nRegular completion:")
            print(response)

            # Test streaming completion
            print("\nStreaming completion:")
            async for token in service.get_streaming_completion(messages):
                print(token, end="", flush=True)
            print()

    asyncio.run(main())