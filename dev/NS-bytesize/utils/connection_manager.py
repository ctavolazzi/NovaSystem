from typing import Optional, Any, Dict
from openai import AsyncOpenAI
import aiohttp
import asyncio
from contextlib import asynccontextmanager

class ConnectionManager:
    """Manages API connections for NovaSystem"""

    def __init__(self):
        self._clients: Dict[str, AsyncOpenAI] = {}
        self._session: Optional[aiohttp.ClientSession] = None

    @asynccontextmanager
    async def get_connection(self):
        """Get a connection to use for API calls"""
        if not self._session:
            self._session = aiohttp.ClientSession()
        try:
            yield self._session
        finally:
            pass  # Keep session open for reuse

    def format_messages(self, prompt: str, system: Optional[str] = None) -> list[dict]:
        """Format messages for API calls"""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return messages

    async def cleanup(self):
        """Cleanup resources"""
        if self._session:
            await self._session.close()
            self._session = None