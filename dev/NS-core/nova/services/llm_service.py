from typing import List, Dict, Union, Any
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
import ollama
import httpx
import asyncio

# Load environment variables
load_dotenv()

class LLMService:
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.ollama_client = ollama.AsyncClient(host="http://localhost:11434")

    async def get_completion(self, messages: List[Dict[str, Any]], model: str = "gpt-4o") -> str:
        """Get completion from either OpenAI or Ollama"""
        try:
            if model.startswith("gpt"):
                # OpenAI API call with exact format
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4o",  # Use gpt-4o exactly as requested
                    messages=messages
                )
                return response.choices[0].message.content

            else:  # Ollama models
                try:
                    # Convert OpenAI format to Ollama format
                    ollama_messages = []
                    for msg in messages:
                        content = msg.get("content", [])
                        if isinstance(content, list):
                            # Extract text from content array
                            text = " ".join(item.get("text", "") for item in content if item.get("type") == "text")
                        else:
                            text = str(content)
                        ollama_messages.append({"role": msg["role"], "content": text})

                    # Ollama API call
                    response = await self.ollama_client.chat(
                        model=model,
                        messages=ollama_messages
                    )
                    return response['message']['content']
                except Exception as e:
                    if "model not found" in str(e).lower():
                        return f"Error: Please run 'ollama pull {model}' first to download the model."
                    elif "connection refused" in str(e).lower():
                        return "Error: Cannot connect to Ollama. Is it running? Start with 'ollama serve'"
                    else:
                        return f"Ollama Error: {str(e)}"

        except Exception as e:
            if isinstance(e, httpx.ReadTimeout):
                return "Error: Request timed out. Please try again."
            return f"Error: {str(e)}"