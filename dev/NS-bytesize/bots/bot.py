from typing import Optional, List, Dict, Any, Union, Protocol
from uuid import uuid4
from hubs.hub import NovaHub

class Agent(Protocol):
    """AutoGen Agent Protocol"""
    @property
    def name(self) -> str:
        """The name of the agent."""
        ...

    @property
    def description(self) -> str:
        """The description of the agent."""
        ...

    def send(self, message: Union[Dict[str, Any], str], recipient: "Agent", request_reply: Optional[bool] = None) -> None:
        """Send a message to another agent."""
        ...

    async def a_send(self, message: Union[Dict[str, Any], str], recipient: "Agent", request_reply: Optional[bool] = None) -> None:
        """Async send a message to another agent."""
        ...

    def receive(self, message: Union[Dict[str, Any], str], sender: "Agent", request_reply: Optional[bool] = None) -> None:
        """Receive a message from another agent."""
        ...

    async def a_receive(self, message: Union[Dict[str, Any], str], sender: "Agent", request_reply: Optional[bool] = None) -> None:
        """Asynchronously receive a message from another agent."""
        if not self.session_id:
            await self.initialize()

        if isinstance(message, str):
            message_dict = {"role": "user", "content": message}
        else:
            message_dict = message

        self.message_history.append(message_dict)

        if request_reply:
            reply = await self.a_generate_reply([message_dict], sender)
            return reply

    def generate_reply(self, messages: Optional[List[Dict[str, Any]]] = None, sender: Optional["Agent"] = None, **kwargs: Any) -> Union[str, Dict[str, Any], None]:
        """Synchronously generate a reply."""
        import asyncio
        return asyncio.run(self.a_generate_reply(messages, sender, **kwargs))

    async def a_generate_reply(self, messages: Optional[List[Dict[str, Any]]] = None, sender: Optional["Agent"] = None, **kwargs: Any) -> Union[str, Dict[str, Any], None]:
        """Generate a reply using the hub."""
        if not messages:
            return None

        # Get the last message content
        last_message = messages[-1]["content"] if messages else ""

        # Generate response using the hub
        response = await self.hub.generate_response(
            prompt=last_message,
            system=self.system_prompt,
            **kwargs
        )

        # Add response to history
        response_dict = {"role": "assistant", "content": response}
        self.message_history.append(response_dict)

        return response_dict

    async def process_message(self, message: str, model: str = "mistral") -> str:
        """Legacy method: Process a user message and return a response"""
        if not self.session_id:
            await self.initialize()

        reply = await self.a_generate_reply(
            messages=[{"role": "user", "content": message}],
            model=model
        )
        return reply["content"] if reply else ""

    async def get_history(self) -> List[dict]:
        """Get the chat history"""
        if not self.session_id:
            raise Exception("Bot not initialized")
        return self.message_history

    async def cleanup(self):
        """Cleanup bot resources"""
        self.session_id = None
        self.message_history = []

class NovaBot(Agent):
    """NovaSystem Bot implementing AutoGen's Agent protocol"""
    def __init__(self, hub: NovaHub, name: str = "NovaBot", description: Optional[str] = None):
        self.hub = hub
        self._name = name
        self._description = description or f"A NovaSystem bot named {name}"
        self.session_id: Optional[str] = None
        self.system_prompt = """You are a helpful AI assistant.
        You provide clear, concise, and accurate responses."""
        self.message_history: List[dict] = []

    @property
    def name(self) -> str:
        """Get the agent's name."""
        return self._name

    @property
    def description(self) -> str:
        """Get the agent's description."""
        return self._description

    async def initialize(self) -> str:
        """Initialize the bot and return a session ID"""
        self.session_id = str(uuid4())
        self.message_history = []
        return self.session_id

    def send(self, message: Union[Dict[str, Any], str], recipient: "Agent", request_reply: Optional[bool] = None) -> None:
        """Synchronously send a message to another agent."""
        import asyncio
        asyncio.run(self.a_send(message, recipient, request_reply))

    async def a_send(self, message: Union[Dict[str, Any], str], recipient: "Agent", request_reply: Optional[bool] = None) -> None:
        """Asynchronously send a message to another agent."""
        if isinstance(message, str):
            message_dict = {"role": "assistant", "content": message}
        else:
            message_dict = message

        await recipient.a_receive(message_dict, self, request_reply)

    def receive(self, message: Union[Dict[str, Any], str], sender: "Agent", request_reply: Optional[bool] = None) -> None:
        """Synchronously receive a message from another agent."""
        import asyncio
        asyncio.run(self.a_receive(message, sender, request_reply))

    async def a_receive(self, message: Union[Dict[str, Any], str], sender: "Agent", request_reply: Optional[bool] = None) -> None:
        """Asynchronously receive a message from another agent."""
        if not self.session_id:
            await self.initialize()

        if isinstance(message, str):
            message_dict = {"role": "user", "content": message}
        else:
            message_dict = message

        self.message_history.append(message_dict)

        if request_reply:
            reply = await self.a_generate_reply([message_dict], sender)
            return reply

    def generate_reply(self, messages: Optional[List[Dict[str, Any]]] = None, sender: Optional["Agent"] = None, **kwargs: Any) -> Union[str, Dict[str, Any], None]:
        """Synchronously generate a reply."""
        import asyncio
        return asyncio.run(self.a_generate_reply(messages, sender, **kwargs))

    async def a_generate_reply(self, messages: Optional[List[Dict[str, Any]]] = None, sender: Optional["Agent"] = None, **kwargs: Any) -> Union[str, Dict[str, Any], None]:
        """Generate a reply using the hub."""
        if not messages:
            return None

        # Get the last message content
        last_message = messages[-1]["content"] if messages else ""

        # Generate response using the hub
        response = await self.hub.generate_response(
            prompt=last_message,
            system=self.system_prompt,
            **kwargs
        )

        # Add response to history
        response_dict = {"role": "assistant", "content": response}
        self.message_history.append(response_dict)

        return response_dict

    async def process_message(self, message: str, model: str = "mistral") -> str:
        """Legacy method: Process a user message and return a response"""
        if not self.session_id:
            await self.initialize()

        reply = await self.a_generate_reply(
            messages=[{"role": "user", "content": message}],
            model=model
        )
        return reply["content"] if reply else ""

    async def get_history(self) -> List[dict]:
        """Get the chat history"""
        if not self.session_id:
            raise Exception("Bot not initialized")
        return self.message_history

    async def cleanup(self):
        """Cleanup bot resources"""
        self.session_id = None
        self.message_history = []
