# Standard library
from typing import Optional
import os
from pathlib import Path
import aiohttp

class NovaHub:
    def __init__(self, host: str = "http://localhost:11434"):
        self.base_url = host

    async def generate_response(self, prompt: str, system: Optional[str] = None) -> str:
        """Generate a response using Ollama"""
        async with aiohttp.ClientSession() as session:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            data = {
                "model": "llama2",  # Using llama2 as default model
                "messages": messages
            }

            try:
                async with session.post(f"{self.base_url}/v1/chat/completions", json=data) as response:
                    if response.status != 200:
                        return "I'm having trouble connecting to the language model. Make sure Ollama is running and you've pulled the llama2 model."
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
            except Exception as e:
                return f"Error connecting to Ollama: {str(e)}. Make sure Ollama is running and you've pulled the llama2 model using 'ollama pull llama2'"

    async def cleanup(self):
        pass  # No cleanup needed
