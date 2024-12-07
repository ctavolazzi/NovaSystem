# Standard library
import os
from pathlib import Path
from typing import Optional, Dict, Any

# Third party
from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv

class OpenAIConnection:
    """
    Manages OpenAI API connections and provides utility methods for API interactions.
    """
    def __init__(self):
        self._sync_client: Optional[OpenAI] = None
        self._async_client: Optional[AsyncOpenAI] = None
        self._api_key: Optional[str] = None
        self._initialize()

    def _initialize(self) -> None:
        """Initialize the connection by loading environment variables and setting up clients."""
        # Find and load .env file
        env_file = Path(__file__).parent.parent.parent.parent / '.env'
        if env_file.exists():
            load_dotenv(env_file, override=True)

        # Get API key
        self._api_key = os.getenv('OPENAI_API_KEY')
        if not self._api_key:
            raise ValueError("OpenAI API key not found in environment variables")

    @property
    def sync_client(self) -> OpenAI:
        """Get or create synchronous OpenAI client."""
        if not self._sync_client:
            self._sync_client = OpenAI(api_key=self._api_key)
        return self._sync_client

    @property
    def async_client(self) -> AsyncOpenAI:
        """Get or create asynchronous OpenAI client."""
        if not self._async_client:
            self._async_client = AsyncOpenAI(api_key=self._api_key)
        return self._async_client

    def create_chat_message(self, role: str, content: str) -> Dict[str, Any]:
        """
        Create a properly formatted chat message.

        Args:
            role: The role (e.g., "system", "user", "assistant")
            content: The message content

        Returns:
            Dict containing the formatted message
        """
        return {
            "role": role,
            "content": [{
                "type": "text",
                "text": content
            }]
        }

    def format_messages(self, prompt: str, system_prompt: Optional[str] = None) -> list:
        """
        Format messages for the chat completion API.

        Args:
            prompt: The user's prompt
            system_prompt: Optional system prompt

        Returns:
            List of formatted messages
        """
        messages = []
        if system_prompt:
            messages.append(self.create_chat_message("system", system_prompt))
        messages.append(self.create_chat_message("user", prompt))
        return messages

    async def test_connection(self) -> bool:
        """
        Test the OpenAI API connection.

        Returns:
            bool: True if connection is successful
        """
        try:
            response = await self.async_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[self.create_chat_message("user", "Test connection")],
                max_tokens=5
            )
            return bool(response.choices[0].message.content)
        except Exception as e:
            print(f"Connection test failed: {str(e)}")
            return False

# Example usage
if __name__ == "__main__":
    import asyncio

    async def main():
        try:
            # Initialize connection
            connection = OpenAIConnection()

            # Test connection
            print("\n=== Testing OpenAI Connection ===")
            is_connected = await connection.test_connection()
            print(f"Connection status: {'✅ Connected' if is_connected else '❌ Failed'}")

            if is_connected:
                # Try a simple completion
                messages = connection.format_messages(
                    prompt="Say 'Hello, Nova!' in a cheerful way",
                    system_prompt="You are a helpful and enthusiastic assistant"
                )

                response = await connection.async_client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    max_tokens=50
                )

                print("\n=== Test Response ===")
                print(response.choices[0].message.content)

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()

    asyncio.run(main())