"""
Critical Analysis Expert (CAE) Agent.

This agent is responsible for critically evaluating proposals,
identifying weaknesses, and suggesting improvements.
"""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from agents.base import Agent
from agents.llm.provider import LLMProvider
from agents.llm.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)

# Default system prompt for the CAE
DEFAULT_SYSTEM_PROMPT = """
You are a Critical Analysis Expert (CAE) for the NovaSystem. Your role is to:

1. Identify logical flaws or inconsistencies in proposed solutions
2. Highlight potential risks, limitations, or edge cases
3. Propose improvements or alternatives to address identified weaknesses
4. Evaluate solutions against the stated requirements
5. Ensure recommendations are evidence-based and logical

Your analysis should be constructive, specific, and aimed at strengthening the proposed solutions.
"""


class CAEAgent(Agent):
    """
    Critical Analysis Expert Agent.

    This agent critically evaluates proposals, identifies weaknesses,
    and suggests improvements.
    """

    def __init__(self, name: str = "CAE", config: Dict[str, Any] = None):
        """
        Initialize CAE agent.

        Args:
            name: The name of the agent.
            config: Configuration dictionary.
        """
        config = config or {}
        super().__init__(name=name, role="Critical Analysis Expert", config=config)

        # Initialize LLM provider (default to OpenAI)
        # First check if a provider instance was passed directly
        self.llm_provider = config.get("provider")
        if not self.llm_provider:
            # If not, create a provider with the specified class
            provider_class = config.get("provider_class", OpenAIProvider)
            provider_config = config.get("provider_config", {})
            self.llm_provider = provider_class(**provider_config)

        # Get system prompt (default or from config)
        self.system_prompt = config.get("system_prompt", DEFAULT_SYSTEM_PROMPT)

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input and generate a critical analysis.

        Args:
            input_data: Dictionary containing:
                - message: The user's message or content to analyze
                - context: Optional additional context
                - proposed_solution: The solution to be critically analyzed

        Returns:
            Dictionary containing:
                - response: The agent's response (critical analysis)
                - analysis: Structured analysis data
        """
        # Extract information from input
        message = input_data.get("message", "")
        context = input_data.get("context", {})
        proposed_solution = input_data.get("proposed_solution", "")

        # Store interaction in memory
        await self.store_in_memory({
            "role": "user",
            "content": message,
            "context": context,
            "proposed_solution": proposed_solution
        })

        # Retrieve relevant memory
        memory_items = await self.retrieve_from_memory(message)

        # Build prompt for the LLM
        prompt = self._build_prompt(message, context, proposed_solution, memory_items)

        # Check if streaming is requested
        use_streaming = input_data.get("stream", False)

        if use_streaming:
            # For streaming, we need to return a generator
            async def response_generator():
                full_response = ""
                # Call LLM provider with streaming
                async for chunk in self.llm_provider.complete_stream(
                    prompt="",  # Using messages instead
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt}
                    ]
                ):
                    # Extract content from chunk
                    if "choices" in chunk and len(chunk["choices"]) > 0:
                        delta = chunk["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            full_response += content
                            yield content

                # After streaming completes, store the full response
                analysis = self._parse_analysis(full_response)
                await self.store_in_memory({
                    "role": "assistant",
                    "content": full_response,
                    "analysis": analysis
                })

            return {
                "response_generator": response_generator(),
                "is_streaming": True
            }
        else:
            # Call LLM provider
            llm_response = await self.llm_provider.complete(
                prompt="",  # Using messages instead of prompt
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract content from the response
            content = llm_response.get("choices", [{}])[0].get("message", {}).get("content", "")

            # Parse the response to extract structured analysis
            analysis = self._parse_analysis(content)

            # Store response in memory
            await self.store_in_memory({
                "role": "assistant",
                "content": content,
                "analysis": analysis
            })

            return {
                "response": content,
                "analysis": analysis
            }

    def _build_prompt(self, message: str, context: Dict[str, Any],
                      proposed_solution: str, memory_items: List[Dict[str, Any]]) -> str:
        """Build a prompt for the LLM."""
        prompt_parts = []

        # Add proposed solution if provided
        if proposed_solution:
            prompt_parts.append(f"## Proposed Solution to Analyze\n{proposed_solution}\n")

        # Add user message
        prompt_parts.append(f"## Current Request\n{message}\n")

        # Add relevant context
        if context:
            context_str = "\n".join([f"- {k}: {v}" for k, v in context.items()])
            prompt_parts.append(f"## Context\n{context_str}\n")

        # Add relevant memory items if available
        if memory_items:
            memory_str = "\n\n".join([
                f"Previous interaction: {item.get('content', '')}"
                for item in memory_items
            ])
            prompt_parts.append(f"## Relevant History\n{memory_str}\n")

        # Add instructions for structured analysis
        prompt_parts.append("""
## Instructions
Please provide a critical analysis of the proposed solution with the following structure:
1. Summary of the proposed approach
2. Strengths of the proposal
3. Weaknesses, limitations, or risks
4. Suggested improvements
5. Overall assessment
        """)

        return "\n\n".join(prompt_parts)

    def _parse_analysis(self, response: str) -> Dict[str, Any]:
        """
        Parse the LLM response to extract structured analysis information.

        This is a simple implementation that would be enhanced with more
        sophisticated parsing in a production system.
        """
        analysis = {
            "strengths": [],
            "weaknesses": [],
            "improvements": [],
            "overall_assessment": ""
        }

        # Simple parsing based on headers
        sections = response.split("\n## ")

        for section in sections:
            if section.lower().startswith("strengths"):
                lines = section.split("\n")[1:]
                analysis["strengths"] = [line.strip("- ").strip() for line in lines if line.strip()]

            elif section.lower().startswith("weaknesses") or section.lower().startswith("limitations"):
                lines = section.split("\n")[1:]
                analysis["weaknesses"] = [line.strip("- ").strip() for line in lines if line.strip()]

            elif section.lower().startswith("improvements") or section.lower().startswith("suggested"):
                lines = section.split("\n")[1:]
                analysis["improvements"] = [line.strip("- ").strip() for line in lines if line.strip()]

            elif section.lower().startswith("overall") or section.lower().startswith("assessment"):
                lines = section.split("\n")[1:]
                analysis["overall_assessment"] = "\n".join(lines).strip()

        return analysis

    async def reflect(self) -> Dict[str, Any]:
        """
        Self-evaluate performance and identify areas for improvement.

        Returns:
            Dictionary containing reflection data.
        """
        # Retrieve recent memory items
        memory_items = await self.retrieve_from_memory("", k=10)

        # Build prompt for self-reflection
        reflection_prompt = f"""
        Review your recent performance as a Critical Analysis Expert:

        {self._format_memory_items(memory_items)}

        Please reflect on:
        1. The quality and depth of your critical analysis
        2. Whether you identified meaningful weaknesses and risks
        3. Whether your improvement suggestions were practical and specific
        4. How balanced your analysis was (constructive rather than just negative)
        5. Areas where you could improve your analysis approach
        """

        # Call LLM provider
        reflection_response = await self.llm_provider.generate_text(
            system_prompt="You are performing a self-evaluation of your performance as a Critical Analysis Expert.",
            user_prompt=reflection_prompt
        )

        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "agent_role": self.role,
            "reflection": reflection_response,
            "timestamp": str(datetime.utcnow())
        }

    def _format_memory_items(self, items: List[Dict[str, Any]]) -> str:
        """Format memory items for inclusion in prompts."""
        formatted = []
        for item in items:
            role = item.get("role", "unknown")
            content = item.get("content", "")
            formatted.append(f"{role.upper()}: {content}")

        return "\n\n".join(formatted)