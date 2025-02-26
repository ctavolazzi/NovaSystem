"""
Discussion Continuity Expert (DCE) Agent.

This agent is responsible for maintaining conversation continuity
and providing a conversational interface to the system.
"""
import logging
from typing import Any, Dict, List, Optional

from agents.base import Agent
from agents.llm.provider import LLMProvider
from agents.llm.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)

# Default system prompt for the DCE
DEFAULT_SYSTEM_PROMPT = """
You are a Discussion Continuity Expert (DCE) for the NovaSystem. Your role is to:

1. Maintain a natural conversation flow with the user
2. Remember important context from previous exchanges
3. Ask clarifying questions when needed
4. Summarize complex information in an accessible way
5. Help the user navigate through the problem-solving process

Always be helpful, concise, and focus on understanding the user's needs.
"""


class DCEAgent(Agent):
    """
    Discussion Continuity Expert Agent.

    This agent maintains conversation continuity and acts as the main
    interface between the user and the system.
    """

    def __init__(self, name: str = "DCE", config: Dict[str, Any] = None):
        """
        Initialize DCE agent.

        Args:
            name: The name of the agent.
            config: Configuration dictionary.
        """
        config = config or {}
        super().__init__(name=name, role="Discussion Continuity Expert", config=config)

        # Initialize LLM provider (default to OpenAI)
        # First check if a provider instance was passed directly
        self.llm_provider = config.get("provider")
        if not self.llm_provider:
            # If not, create a provider with the specified class
            provider_class = config.get("provider_class", OpenAIProvider)
            provider_config = config.get("provider_config", {})
            self.llm_provider = provider_class(**provider_config)

        # Set system prompt
        self.system_prompt = config.get("system_prompt", DEFAULT_SYSTEM_PROMPT)

        # Initialize conversation history
        self.conversation_history = []

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user input and generate a response.

        Args:
            input_data: Dictionary containing user input and context.
                Required keys:
                - "message": The user's message.

                Optional keys:
                - "context": Additional context for the agent.
                - "reset": If true, reset conversation history.

        Returns:
            Dictionary containing the agent's response.
        """
        # Check if we should reset the conversation
        if input_data.get("reset", False):
            self.conversation_history = []
            logger.info(f"DCE: Reset conversation history")

        # Extract the user message
        user_message = input_data.get("message", "")
        if not user_message:
            return {
                "content": "I didn't receive a message to process.",
                "error": "No message provided.",
            }

        # Store user message in memory
        await self.store_in_memory({
            "role": "user",
            "content": user_message,
        })

        # Add user message to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
        })

        # Prepare messages for the LLM
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]

        # Add conversation history (last 10 messages)
        if self.conversation_history:
            messages.extend(self.conversation_history[-10:])

        # Get additional context if provided
        context = input_data.get("context", {})
        if context and isinstance(context, dict):
            context_str = "\n\nAdditional context:\n"
            for key, value in context.items():
                context_str += f"- {key}: {value}\n"

            # Add context as a system message
            messages.append({
                "role": "system",
                "content": context_str
            })

        # Generate response from LLM
        try:
            response = await self.llm_provider.complete(
                prompt="",  # We're using messages instead
                messages=messages,
                max_tokens=self.config.get("max_tokens", 1000),
                temperature=self.config.get("temperature", 0.7),
            )

            # Extract the assistant's message
            if "choices" in response and response["choices"]:
                assistant_message = response["choices"][0]["message"]

                # Store assistant message in memory
                await self.store_in_memory({
                    "role": "assistant",
                    "content": assistant_message["content"],
                })

                # Add assistant message to conversation history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message["content"],
                })

                return {
                    "response": assistant_message["content"],
                    "conversation_history": self.conversation_history
                }
            else:
                logger.error("Invalid response format from LLM provider")
                return {
                    "content": "I'm sorry, I encountered an error while processing your request.",
                    "error": "Invalid response format from LLM provider"
                }

        except Exception as e:
            logger.error(f"Error generating DCE response: {e}")
            return {
                "content": "I'm sorry, I encountered an error while processing your request.",
                "error": str(e)
            }

    async def reflect(self) -> Dict[str, Any]:
        """
        Reflect on the conversation and provide insights.

        Returns:
            Dictionary containing reflection insights.
        """
        if not self.conversation_history:
            return {
                "status": "no conversation to reflect on",
                "agent_id": self.id,
                "agent_name": self.name,
            }

        # Create a reflection prompt
        reflection_prompt = """
        Please analyze the conversation so far and provide:
        1. A brief summary of the main topics discussed
        2. Any potential misunderstandings or areas of confusion
        3. Suggestions for how to improve the conversation
        """

        messages = [
            {"role": "system", "content": reflection_prompt}
        ]

        # Add conversation history
        messages.extend(self.conversation_history)

        try:
            response = await self.llm_provider.complete(
                prompt="",  # We're using messages instead
                messages=messages,
                max_tokens=self.config.get("max_tokens", 1000),
                temperature=0.5,  # Lower temperature for more focused reflection
            )

            if "choices" in response and response["choices"]:
                reflection_content = response["choices"][0]["message"]["content"]
                return {
                    "status": "reflection complete",
                    "agent_id": self.id,
                    "agent_name": self.name,
                    "insights": reflection_content,
                }
            else:
                return {
                    "status": "reflection error",
                    "agent_id": self.id,
                    "agent_name": self.name,
                    "error": "Unexpected response format from LLM",
                }

        except Exception as e:
            logger.error(f"Error generating reflection: {e}")
            return {
                "status": "reflection error",
                "agent_id": self.id,
                "agent_name": self.name,
                "error": str(e),
            }

    async def summarize_conversation(self) -> str:
        """
        Generate a summary of the conversation so far.

        Returns:
            A string containing the conversation summary.
        """
        if not self.conversation_history:
            return "No conversation to summarize."

        # Create a summarization prompt
        summary_prompt = """
        Please provide a concise summary of the conversation so far,
        highlighting the key points and any decisions or conclusions reached.
        """

        messages = [
            {"role": "system", "content": summary_prompt}
        ]

        # Add conversation history
        messages.extend(self.conversation_history)

        try:
            response = await self.llm_provider.complete(
                prompt="",  # We're using messages instead
                messages=messages,
                max_tokens=self.config.get("max_tokens", 500),
                temperature=0.3,  # Lower temperature for more focused summary
            )

            if "choices" in response and response["choices"]:
                return response["choices"][0]["message"]["content"]
            else:
                return "Failed to generate summary due to unexpected response format."

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Failed to generate summary: {str(e)}"