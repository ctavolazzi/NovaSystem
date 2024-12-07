# Standard library
from typing import Optional
import os
from pathlib import Path

# Third party
from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv
from utils.connection_manager import ConnectionManager
from utils.openai_key_validator import OpenAIKeyValidator

class NovaHub:
    def __init__(self, host: str = "http://localhost:11434"):
        self.connection_manager = ConnectionManager()
        # Get and validate API key
        self.key_validator = OpenAIKeyValidator()

        # Initialize OpenAI client with validated key
        self.openai_client = AsyncOpenAI(api_key=self.key_validator.key)

        # Initialize Ollama client
        self.ollama_client = AsyncOpenAI(
            base_url=f"{host}/v1",
            api_key="ollama"
        )

    async def generate_response(self, prompt: str, model: str = "gpt-4", system: Optional[str] = None) -> str:
        async with self.connection_manager.get_connection() as client:
            messages = self.connection_manager.format_messages(prompt, system)
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=50
            )
            return response.choices[0].message.content

    async def cleanup(self):
        pass  # OpenAI clients don't need cleanup
