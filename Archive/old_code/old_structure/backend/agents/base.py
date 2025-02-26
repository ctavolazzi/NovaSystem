"""
Base Agent class for NovaSystem.

This module defines the core Agent abstract class that all specialized agents will extend.
"""
import json
import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class AgentMemory:
    """Memory system for agents."""

    def __init__(self):
        """Initialize agent memory."""
        self.short_term = []  # List of recent interactions
        self.long_term = []  # List of important historical information
        self.short_term_limit = 10  # Default limit

    async def store(self, data: Dict[str, Any], memory_type: str = "short_term") -> None:
        """Store information in memory."""
        data["timestamp"] = datetime.utcnow().isoformat()

        if memory_type == "short_term" or memory_type == "both":
            self.short_term.append(data)
            # Trim short-term memory if it exceeds the limit
            if len(self.short_term) > self.short_term_limit:
                self.short_term = self.short_term[-self.short_term_limit:]

        if memory_type == "long_term" or memory_type == "both":
            self.long_term.append(data)

    async def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant information from memory.

        In a real implementation, this would use semantic search for long-term memory.
        This is a simplified version that just returns recent items.
        """
        # For now, just return the most recent k items from short-term memory
        return self.short_term[-k:]

    async def compress(self) -> None:
        """
        Compress and optimize memory storage.

        This is a placeholder for future implementation.
        """
        logger.info("Memory compression not yet implemented")


class ToolRegistry:
    """Registry of tools available to the agent."""

    def __init__(self):
        """Initialize tool registry."""
        self.tools = {}  # Dictionary of available tools

    def register_tool(self, name: str, tool_func: callable, description: str = "") -> None:
        """Register a tool in the registry."""
        self.tools[name] = {
            "func": tool_func,
            "description": description
        }

    def get_tool(self, name: str) -> Optional[callable]:
        """Get a tool by name."""
        if name in self.tools:
            return self.tools[name]["func"]
        return None

    async def execute_tool(self, name: str, **kwargs) -> Any:
        """Execute a tool by name with the given arguments."""
        tool = self.get_tool(name)
        if tool:
            try:
                return await tool(**kwargs)
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                return {"error": str(e)}
        else:
            logger.warning(f"Tool {name} not found")
            return {"error": f"Tool {name} not found"}


class Agent(ABC):
    """
    Abstract base class for all agents in the system.

    This class defines the core interface and behavior for agents.
    """

    def __init__(self, name: str, role: str, config: Dict[str, Any] = None):
        """Initialize agent."""
        self.id = str(uuid.uuid4())
        self.name = name
        self.role = role
        self.config = config or {}
        self.memory = AgentMemory()
        self.tools = ToolRegistry()

        # Configure memory based on config
        if "memory_config" in self.config:
            memory_config = self.config["memory_config"]
            if "short_term_limit" in memory_config:
                self.memory.short_term_limit = memory_config["short_term_limit"]

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input and generate a response.

        This is the main method that specialized agents must implement.
        """
        pass

    async def reflect(self) -> Dict[str, Any]:
        """
        Self-evaluate performance and adjust approach.

        This is an optional method that specialized agents can override.
        """
        return {
            "status": "reflection not implemented",
            "agent_id": self.id,
            "agent_name": self.name,
            "agent_role": self.role,
        }

    def register_tools(self, tools: Dict[str, Dict[str, Any]]) -> None:
        """Register multiple tools at once."""
        for name, tool_info in tools.items():
            self.tools.register_tool(
                name=name,
                tool_func=tool_info["func"],
                description=tool_info.get("description", "")
            )

    async def store_in_memory(self, data: Dict[str, Any], memory_type: str = "short_term") -> None:
        """Store data in the agent's memory."""
        await self.memory.store(data, memory_type)

    async def retrieve_from_memory(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve data from the agent's memory."""
        return await self.memory.retrieve(query, k)

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent instance to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "config": self.config,
        }

    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"<Agent {self.name} ({self.role})>"