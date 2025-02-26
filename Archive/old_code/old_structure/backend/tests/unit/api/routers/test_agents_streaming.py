"""
Unit tests for streaming responses from agents through the API.
"""
import asyncio
import pytest
from typing import List, Dict, Any, AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient

from api.routers.agents import router as agents_router
from agents.base import Agent


# Test data
TEST_AGENT_ID = "test-agent-id"
TEST_AGENT_NAME = "Test Agent"
TEST_AGENT_ROLE = "Test Role"


class MockResponseGenerator:
    """Mock response generator for streaming responses."""

    def __init__(self, chunks: List[str]):
        self.chunks = chunks
        self.index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index >= len(self.chunks):
            raise StopAsyncIteration
        chunk = self.chunks[self.index]
        self.index += 1
        return chunk


class MockAgent(Agent):
    """Mock agent for testing streaming responses."""

    def __init__(self, **kwargs):
        super().__init__(name=TEST_AGENT_NAME, role=TEST_AGENT_ROLE)
        self.id = TEST_AGENT_ID

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock process method that returns either streaming or regular response."""
        if input_data.get("stream", False):
            chunks = ["Hello", " World", "!"]
            return {
                "response_generator": MockResponseGenerator(chunks),
                "is_streaming": True
            }
        else:
            return {
                "response": "Hello World!",
                "metadata": {}
            }

    async def reflect(self) -> Dict[str, Any]:
        """Mock reflect method."""
        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "reflection": "Test reflection"
        }


@pytest.fixture
def app() -> FastAPI:
    """Create a test app with the agents router."""
    app = FastAPI()
    app.include_router(agents_router)

    # Register the mock agent
    from api.routers.agents import agents
    mock_agent = MockAgent()
    agents[TEST_AGENT_ID] = mock_agent

    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create a test client."""
    return TestClient(app)


@pytest.mark.asyncio
async def test_send_message_stream(app: FastAPI):
    """Test streaming response from the agent."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            f"/agents/{TEST_AGENT_ID}/message/stream",
            json={
                "message": "Test message",
                "context": {}
            }
        )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")

        # Collect all chunks
        content = response.content.decode()
        lines = [line for line in content.split("\n\n") if line.startswith("data: ")]

        # Check that we received the expected chunks
        assert len(lines) >= 3  # At least 3 chunks: "Hello", " World", "!"
        assert lines[0] == "data: Hello"
        assert lines[1] == "data:  World"
        assert lines[2] == "data: !"
        assert "data: [DONE]" in content


@pytest.mark.asyncio
async def test_send_message_stream_agent_not_found(app: FastAPI):
    """Test streaming response when agent is not found."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/agents/non-existent-agent/message/stream",
            json={
                "message": "Test message",
                "context": {}
            }
        )

        assert response.status_code == 404
        data = response.json()
        assert "Agent not found" in data["detail"]