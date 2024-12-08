from typing import List, Dict, Optional, Any
import asyncio
from uuid import uuid4
import os
from dataclasses import dataclass
import logging

import autogen
from .hub import NovaHub
from utils.console import ConsoleLogger

@dataclass
class DiscussionConfig:
    """Configuration for a discussion."""
    max_rounds: int = 10
    temperature: float = 0.7
    max_tokens: int = 2000
    model: str = "gpt-4"

class OpenAIDiscussionHub(NovaHub):
    """A hub for managing multi-agent discussions using OpenAI's GPT-4."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the hub with OpenAI configuration.

        Args:
            api_key: Optional OpenAI API key. If not provided, will try to get from environment.
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable")

        self.logger = ConsoleLogger()
        self.active_discussions: Dict[str, Dict[str, Any]] = {}

        # Configure OpenAI with more specific settings
        self.llm_config = {
            "config_list": [{
                "model": "gpt-4",
                "api_key": self.api_key,
                "temperature": 0.7,
                "max_tokens": 2000
            }]
        }

    def create_discussion_agents(self, discussion_id: str) -> Dict[str, autogen.Agent]:
        """Create the agents needed for a discussion using GPT-4."""
        try:
            # Create the controller agent with more specific guidance
            controller = autogen.AssistantAgent(
                name="Discussion_Controller",
                system_message="""You are the discussion controller responsible for driving focused technical discussions.
                Key responsibilities:
                1. Break down complex topics into clear, actionable components
                2. Assign specific tasks to each expert
                3. Keep the discussion on track and moving forward
                4. Prevent circular discussions
                5. Ensure each contribution builds on previous ones

                Start each discussion by:
                1. Analyzing the topic
                2. Creating a structured plan
                3. Assigning initial tasks""",
                llm_config=self.llm_config
            )

            # Create specialized discussion agents with more focused roles
            analyst = autogen.AssistantAgent(
                name="Technical_Analyst",
                system_message="""You are a technical analyst focused on practical evaluation.
                Your responsibilities:
                1. Evaluate technical feasibility of proposed solutions
                2. Identify specific technical challenges and bottlenecks
                3. Propose concrete solutions to technical problems
                4. Focus on measurable metrics and performance indicators

                When contributing:
                1. Be specific about technical concerns
                2. Provide actionable feedback
                3. Suggest concrete improvements
                4. Use examples when possible

                Remember: Focus on technical analysis, not process or roles.""",
                llm_config=self.llm_config
            )

            architect = autogen.AssistantAgent(
                name="Solution_Architect",
                system_message="""You are a solution architect focused on system design.
                Your responsibilities:
                1. Design scalable system architectures
                2. Define technical specifications
                3. Make technology choices
                4. Plan implementation phases

                When contributing:
                1. Provide specific architectural decisions
                2. Explain technical tradeoffs
                3. Define clear interfaces and components
                4. Consider scalability and maintenance

                Remember: Focus on concrete design decisions, not process discussions.""",
                llm_config=self.llm_config
            )

            implementer = autogen.AssistantAgent(
                name="Implementation_Expert",
                system_message="""You are an implementation expert focused on coding solutions.
                Your responsibilities:
                1. Provide specific code examples
                2. Define implementation steps
                3. Suggest testing approaches
                4. Identify technical dependencies

                When contributing:
                1. Share concrete code snippets
                2. Explain implementation details
                3. Discuss testing strategies
                4. Consider error handling

                Remember: Focus on practical implementation, not theoretical discussions.""",
                llm_config=self.llm_config
            )

            # Create user proxy with specific termination conditions
            user_proxy = autogen.UserProxyAgent(
                name="Discussion_Coordinator",
                code_execution_config=False,
                human_input_mode="NEVER",
                max_consecutive_auto_reply=10,
                is_termination_msg=lambda x: (
                    x.get("content", "").rstrip().endswith("TERMINATE") or
                    "final summary" in x.get("content", "").lower() or
                    "discussion complete" in x.get("content", "").lower()
                )
            )

            return {
                "controller": controller,
                "analyst": analyst,
                "architect": architect,
                "implementer": implementer,
                "user_proxy": user_proxy
            }

        except Exception as e:
            self.logger.error(f"Failed to create discussion agents", e)
            raise

    def create_discussion_group(self, agents: Dict, max_rounds: int = 10) -> autogen.GroupChat:
        """Create a group chat with improved conversation flow."""

        # Order matters - controller first, then experts in logical order
        agent_list = [
            agents["controller"],
            agents["architect"],
            agents["analyst"],
            agents["implementer"],
            agents["user_proxy"]
        ]

        return autogen.GroupChat(
            agents=agent_list,
            messages=[],
            max_round=max_rounds,
            speaker_selection_method="round_robin",  # More predictable flow
            speaker_transitions_type="allowed",  # Control conversation flow
            allowed_or_disallowed_speaker_transitions={
                agents["controller"]: [agents["architect"], agents["analyst"], agents["implementer"]],
                agents["architect"]: [agents["analyst"], agents["controller"]],
                agents["analyst"]: [agents["implementer"], agents["controller"]],
                agents["implementer"]: [agents["controller"]],
                agents["user_proxy"]: [agents["controller"]]
            }
        )

    async def start_discussion(self, topic: str, config: Optional[DiscussionConfig] = None) -> str:
        """Start a new discussion with improved error handling and configuration."""
        try:
            discussion_id = str(uuid4())
            config = config or DiscussionConfig()

            agents = self.create_discussion_agents(discussion_id)
            group_chat = self.create_discussion_group(agents, config.max_rounds)

            manager = autogen.GroupChatManager(
                groupchat=group_chat,
                llm_config={
                    "config_list": [{
                        "model": config.model,
                        "api_key": self.api_key,
                        "temperature": config.temperature,
                        "max_tokens": config.max_tokens
                    }]
                }
            )

            self.active_discussions[discussion_id] = {
                "agents": agents,
                "group_chat": group_chat,
                "manager": manager,
                "topic": topic,
                "config": config
            }

            initial_message = self._format_initial_message(topic)

            response = await agents["user_proxy"].initiate_chat(
                manager,
                message=initial_message
            )

            self.logger.info(f"Started discussion {discussion_id} on topic: {topic}")
            return discussion_id

        except Exception as e:
            self.logger.error("Failed to start discussion", e)
            raise

    def _format_initial_message(self, topic: str) -> str:
        """Format the initial message for a discussion."""
        return f"""Let's discuss: {topic}

        Guidelines for this discussion:
        1. Each expert should provide specific, actionable input
        2. Focus on technical solutions, not process discussions
        3. Build on previous contributions
        4. Avoid repeating information

        Controller: Please break down this topic and assign specific tasks."""

    async def add_message_to_discussion(self, discussion_id: str, message: str) -> Optional[str]:
        """Add a message to an ongoing discussion."""
        if discussion_id not in self.active_discussions:
            raise ValueError(f"Discussion {discussion_id} not found")

        discussion = self.active_discussions[discussion_id]
        user_proxy = discussion["agents"]["user_proxy"]
        manager = discussion["manager"]

        try:
            response = await user_proxy.initiate_chat(
                manager,
                message=message
            )

            return response.summary if response else None
        except Exception as e:
            self.logger.error("Failed to add message to discussion", e)
            raise

    async def end_discussion(self, discussion_id: str) -> Optional[str]:
        """End a discussion and get final summary."""
        if discussion_id not in self.active_discussions:
            raise ValueError(f"Discussion {discussion_id} not found")

        discussion = self.active_discussions[discussion_id]

        # Ask controller for final summary
        final_message = """Please provide a final summary of the discussion, including:
        1. Key points and decisions
        2. Action items or next steps
        3. Open questions or areas for future discussion"""

        response = await self.add_message_to_discussion(discussion_id, final_message)

        # Cleanup
        del self.active_discussions[discussion_id]

        return response