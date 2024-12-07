from typing import Optional, List
from uuid import uuid4
from hubs.hub import NovaHub

class NovaBot:
    def __init__(self, hub: NovaHub):
        self.hub = hub
        self.session_id: Optional[str] = None
        self.system_prompt = """You are a helpful AI assistant.
        You provide clear, concise, and accurate responses."""
        self.message_history: List[dict] = []

    async def initialize(self) -> str:
        """Initialize the bot and return a session ID"""
        self.session_id = str(uuid4())
        self.message_history = []
        return self.session_id

    async def process_message(self, message: str, model: str = "mistral") -> str:
        """Process a user message and return a response"""
        if not self.session_id:
            raise Exception("Bot not initialized")

        # Add user message to history
        self.message_history.append({
            "role": "user",
            "content": message
        })

        response = await self.hub.generate_response(
            prompt=message,
            system=self.system_prompt,
            model=model
        )

        # Add assistant response to history
        self.message_history.append({
            "role": "assistant",
            "content": response
        })

        return response

    async def get_history(self) -> List[dict]:
        """Get the chat history"""
        if not self.session_id:
            raise Exception("Bot not initialized")
        return self.message_history

    async def cleanup(self):
        """Cleanup bot resources"""
        self.session_id = None
        self.message_history = []
