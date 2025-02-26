"""
API endpoints for agent interactions.
"""
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from agents.dce import DCEAgent
from agents.base import Agent
from agents.factory import create_agent

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/agents", tags=["Agents"])

# Keep a registry of active agents
# In a production system, this would be stored in a database
agents = {}


# ----- Pydantic models for requests and responses -----

class AgentConfig(BaseModel):
    """Configuration for an agent."""
    agent_type: str = Field(..., description="Type of agent to create")
    name: str = Field(..., description="Name of the agent")
    config: Dict[str, Any] = Field(default_factory=dict, description="Agent configuration")


class MessageRequest(BaseModel):
    """Request to send a message to an agent."""
    message: str = Field(..., description="Message content")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    reset: bool = Field(False, description="Whether to reset conversation history")


class MessageResponse(BaseModel):
    """Response from an agent."""
    agent_id: str = Field(..., description="ID of the agent")
    agent_name: str = Field(..., description="Name of the agent")
    content: str = Field(..., description="Message content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")
    error: Optional[str] = Field(None, description="Error message, if any")


class AgentInfo(BaseModel):
    """Information about an agent."""
    id: str = Field(..., description="Agent ID")
    name: str = Field(..., description="Agent name")
    type: str = Field(..., description="Agent type")
    role: str = Field(..., description="Agent role")


# ----- API endpoints -----

@router.post("/create", response_model=AgentInfo, status_code=status.HTTP_201_CREATED)
async def create_agent_endpoint(
    config: AgentConfig,
) -> Dict[str, Any]:
    """
    Create a new agent.

    Args:
        config: Agent configuration.

    Returns:
        Information about the created agent.
    """
    try:
        # Create agent using the factory
        agent = create_agent(
            agent_type=config.agent_type,
            name=config.name,
            config=config.config
        )

        # Store agent in registry
        agents[agent.id] = agent

        logger.info(f"Created agent: {agent.id} ({agent.name})")

        # Return agent info
        return {
            "id": agent.id,
            "name": agent.name,
            "type": config.agent_type,
            "role": agent.role,
        }

    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create agent: {str(e)}",
        )


@router.get("/list", response_model=List[AgentInfo])
async def list_agents() -> List[Dict[str, Any]]:
    """
    List all active agents.

    Returns:
        List of agent information.
    """
    return [
        {
            "id": agent.id,
            "name": agent.name,
            "type": agent.__class__.__name__.replace("Agent", ""),
            "role": agent.role,
        }
        for agent in agents.values()
    ]


@router.get("/{agent_id}", response_model=AgentInfo)
async def get_agent(agent_id: str) -> Dict[str, Any]:
    """
    Get information about a specific agent.

    Args:
        agent_id: ID of the agent.

    Returns:
        Agent information.
    """
    if agent_id not in agents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent not found: {agent_id}",
        )

    agent = agents[agent_id]
    return {
        "id": agent.id,
        "name": agent.name,
        "type": agent.__class__.__name__.replace("Agent", ""),
        "role": agent.role,
    }


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: str) -> None:
    """
    Delete an agent.

    Args:
        agent_id: ID of the agent to delete.
    """
    if agent_id not in agents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent not found: {agent_id}",
        )

    # Remove agent from registry
    del agents[agent_id]
    logger.info(f"Deleted agent: {agent_id}")


@router.post("/{agent_id}/message", response_model=MessageResponse)
async def send_message(
    agent_id: str,
    request: MessageRequest,
) -> Dict[str, Any]:
    """
    Send a message to an agent.

    Args:
        agent_id: ID of the agent to send the message to.
        request: Message request.

    Returns:
        Agent's response.
    """
    if agent_id not in agents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent not found: {agent_id}",
        )

    agent = agents[agent_id]
    try:
        # Process the message
        response = await agent.process({
            "message": request.message,
            "context": request.context,
            "reset": request.reset,
        })

        # Return the response
        return {
            "agent_id": agent.id,
            "agent_name": agent.name,
            "content": response.get("content", ""),
            "metadata": response.get("metadata", {}),
            "error": response.get("error"),
        }

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}",
        )


@router.post("/{agent_id}/reflect", response_model=Dict[str, Any])
async def reflect(agent_id: str) -> Dict[str, Any]:
    """
    Trigger agent reflection.

    Args:
        agent_id: ID of the agent to reflect.

    Returns:
        Reflection results.
    """
    if agent_id not in agents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent not found: {agent_id}",
        )

    agent = agents[agent_id]
    try:
        # Trigger reflection
        reflection = await agent.reflect()
        return reflection

    except Exception as e:
        logger.error(f"Error during reflection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reflect: {str(e)}",
        )


@router.post("/{agent_id}/summarize", response_model=Dict[str, str])
async def summarize(agent_id: str) -> Dict[str, str]:
    """
    Generate a summary of the agent's conversation.

    Args:
        agent_id: ID of the agent.

    Returns:
        Conversation summary.
    """
    if agent_id not in agents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent not found: {agent_id}",
        )

    agent = agents[agent_id]

    # Check if the agent has a summarize_conversation method
    if not hasattr(agent, "summarize_conversation"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent {agent_id} does not support summarization",
        )

    try:
        # Generate summary
        summary = await agent.summarize_conversation()
        return {"summary": summary}

    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate summary: {str(e)}",
        )


@router.post("/{agent_id}/message/stream", response_class=StreamingResponse)
async def send_message_stream(
    agent_id: str,
    request: MessageRequest,
) -> StreamingResponse:
    """
    Send a message to an agent and receive a streaming response.

    Args:
        agent_id: ID of the agent to send the message to.
        request: Message request.

    Returns:
        A streaming response with the agent's output.
    """
    if agent_id not in agents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent not found: {agent_id}",
        )

    agent = agents[agent_id]
    try:
        # Add streaming flag to the input data
        input_data = {
            "message": request.message,
            "context": request.context,
            "reset": request.reset,
            "stream": True,
        }

        # Process the message with streaming enabled
        response = await agent.process(input_data)

        if not response.get("is_streaming", False) or "response_generator" not in response:
            # Agent doesn't support streaming, return an error
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Agent does not support streaming responses",
            )

        # Return a streaming response
        async def stream_generator():
            try:
                async for chunk in response["response_generator"]:
                    # Format each chunk as SSE
                    yield f"data: {chunk}\n\n"
                # End the stream
                yield "data: [DONE]\n\n"
            except Exception as e:
                logger.error(f"Error during streaming: {e}")
                yield f"data: Error during streaming: {str(e)}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(
            stream_generator(),
            media_type="text/event-stream",
        )

    except Exception as e:
        logger.error(f"Error processing streaming message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process streaming message: {str(e)}",
        )