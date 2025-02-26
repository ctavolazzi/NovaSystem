"""
Domain Expert Agent.

This agent provides specialized domain knowledge for specific fields.
It can be instantiated with different domains of expertise.
"""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from agents.base import Agent
from agents.llm.provider import LLMProvider
from agents.llm.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)

# Template for domain expert system prompts
DOMAIN_EXPERT_PROMPT_TEMPLATE = """
You are an expert in {domain}. {domain_description}

Your role is to:
1. Provide specialized knowledge and insights related to {domain}
2. Explain domain-specific concepts clearly
3. Apply best practices and principles from {domain} to the problem
4. Identify domain-specific opportunities and challenges
5. Recommend approaches that align with current standards in {domain}

Your contributions should demonstrate deep expertise while remaining accessible to those
who may not have the same level of specialization.
"""


class DomainExpertAgent(Agent):
    """
    Domain Expert Agent.

    This agent provides specialized knowledge and insights for a specific domain.
    It can be instantiated for different domains of expertise.
    """

    def __init__(self, name: str, domain: str, domain_description: str = "", config: Dict[str, Any] = None):
        """
        Initialize Domain Expert agent.

        Args:
            name: The name of the agent.
            domain: The domain of expertise.
            domain_description: Description of the domain and its relevance.
            config: Configuration dictionary.
        """
        config = config or {}
        super().__init__(name=name, role=f"{domain} Expert", config=config)

        self.domain = domain
        self.domain_description = domain_description or f"expertise in {domain}"

        # Initialize LLM provider (default to OpenAI)
        provider_class = config.get("provider_class", OpenAIProvider)
        provider_config = config.get("provider_config", {})
        self.llm_provider = provider_class(**provider_config)

        # Create system prompt
        self.system_prompt = config.get("system_prompt", self._create_system_prompt())

    def _create_system_prompt(self) -> str:
        """Create the system prompt for this domain expert."""
        return DOMAIN_EXPERT_PROMPT_TEMPLATE.format(
            domain=self.domain,
            domain_description=self.domain_description
        )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input and provide domain-specific expertise.

        Args:
            input_data: Dictionary containing:
                - message: The user's message or question
                - context: Optional additional context
                - problem_statement: Optional problem statement

        Returns:
            Dictionary containing:
                - response: The agent's response with domain expertise
                - domain_insights: Structured insights related to the domain
        """
        # Extract information from input
        message = input_data.get("message", "")
        context = input_data.get("context", {})
        problem_statement = input_data.get("problem_statement", "")

        # Store interaction in memory
        await self.store_in_memory({
            "role": "user",
            "content": message,
            "context": context,
            "problem_statement": problem_statement
        })

        # Retrieve relevant memory
        memory_items = await self.retrieve_from_memory(message)

        # Build prompt for the LLM
        prompt = self._build_prompt(message, context, problem_statement, memory_items)

        # Check if streaming is requested
        use_streaming = input_data.get("stream", False)

        if use_streaming:
            # For streaming, we need to return a generator
            async def response_generator():
                full_response = ""
                # Call LLM provider with streaming
                async for chunk in self.llm_provider.complete_stream(
                    prompt=prompt,
                    system_prompt=self.system_prompt
                ):
                    # Extract content from chunk
                    if "choices" in chunk and len(chunk["choices"]) > 0:
                        delta = chunk["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            full_response += content
                            yield content

                # After streaming completes, store the full response
                domain_insights = self._parse_domain_insights(full_response)
                await self.store_in_memory({
                    "role": "assistant",
                    "content": full_response,
                    "domain_insights": domain_insights
                })

            return {
                "response_generator": response_generator(),
                "is_streaming": True
            }
        else:
            # Call LLM provider
            llm_response = await self.llm_provider.generate_text(
                system_prompt=self.system_prompt,
                user_prompt=prompt
            )

            # Parse the response to extract structured domain insights
            domain_insights = self._parse_domain_insights(llm_response)

            # Store response in memory
            await self.store_in_memory({
                "role": "assistant",
                "content": llm_response,
                "domain_insights": domain_insights
            })

            return {
                "response": llm_response,
                "domain_insights": domain_insights
            }

    def _build_prompt(self, message: str, context: Dict[str, Any],
                     problem_statement: str, memory_items: List[Dict[str, Any]]) -> str:
        """Build a prompt for the LLM."""
        prompt_parts = []

        # Add problem statement if provided
        if problem_statement:
            prompt_parts.append(f"## Problem Statement\n{problem_statement}\n")

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

        # Add instructions for domain-specific response
        prompt_parts.append(f"""
## Instructions
Please provide your expert perspective on this matter as a {self.domain} specialist. Include:
1. Key insights from {self.domain} that apply to this situation
2. Domain-specific considerations or constraints
3. Best practices or methodologies from your field
4. Opportunities or innovative approaches from a {self.domain} perspective
5. Practical recommendations based on your expertise
        """)

        return "\n\n".join(prompt_parts)

    def _parse_domain_insights(self, response: str) -> Dict[str, Any]:
        """
        Parse the LLM response to extract structured domain insights.

        This is a simple implementation that would be enhanced with more
        sophisticated parsing in a production system.
        """
        insights = {
            "key_concepts": [],
            "considerations": [],
            "best_practices": [],
            "opportunities": [],
            "recommendations": []
        }

        # Simple parsing based on headers
        sections = response.split("\n## ")

        for section in sections:
            if section.lower().startswith("key insights") or section.lower().startswith("concepts"):
                lines = section.split("\n")[1:]
                insights["key_concepts"] = [line.strip("- ").strip() for line in lines if line.strip()]

            elif section.lower().startswith("considerations") or section.lower().startswith("constraints"):
                lines = section.split("\n")[1:]
                insights["considerations"] = [line.strip("- ").strip() for line in lines if line.strip()]

            elif section.lower().startswith("best practices") or section.lower().startswith("methodologies"):
                lines = section.split("\n")[1:]
                insights["best_practices"] = [line.strip("- ").strip() for line in lines if line.strip()]

            elif section.lower().startswith("opportunities") or section.lower().startswith("innovative"):
                lines = section.split("\n")[1:]
                insights["opportunities"] = [line.strip("- ").strip() for line in lines if line.strip()]

            elif section.lower().startswith("recommendations") or section.lower().startswith("advice"):
                lines = section.split("\n")[1:]
                insights["recommendations"] = [line.strip("- ").strip() for line in lines if line.strip()]

        return insights

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
        Review your recent performance as a {self.domain} Expert:

        {self._format_memory_items(memory_items)}

        Please reflect on:
        1. The depth and accuracy of your domain expertise
        2. How well you applied {self.domain} knowledge to the problem
        3. The clarity of your explanations of domain-specific concepts
        4. The practicality of your recommendations
        5. Areas where you could expand your domain knowledge
        """

        # Call LLM provider
        reflection_response = await self.llm_provider.generate_text(
            system_prompt=f"You are performing a self-evaluation of your performance as a {self.domain} Expert.",
            user_prompt=reflection_prompt
        )

        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "agent_role": self.role,
            "domain": self.domain,
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