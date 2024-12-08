from typing import List, Dict, Optional
import asyncio
from uuid import uuid4

import autogen
from .hub import NovaHub
from utils.autogen_setup import AutogenSetup
from utils.console import ConsoleLogger

class DiscussionHub(NovaHub):
    """A hub for managing multi-agent discussions with a controller overseeing the chat."""

    def __init__(self, host: str = "http://localhost:11434"):
        super().__init__(host)
        self.setup = AutogenSetup(use_ollama=True)
        self.logger = ConsoleLogger()
        self.active_discussions: Dict[str, Dict] = {}

    def create_discussion_agents(self, discussion_id: str):
        """Create the agents needed for a discussion."""

        # Create the controller agent that oversees the discussion
        controller = self.setup.create_assistant(
            name="Discussion_Controller",
            system_message="""You are the discussion controller responsible for managing a focused technical discussion.
            Your responsibilities:
            1. Guide the discussion flow:
               - Start by breaking down the topic into clear components
               - Assign specific aspects to each expert
               - Ensure discussions stay on track
            2. Manage participation:
               - Call on specific experts when their expertise is needed
               - Prevent overlapping or chaotic discussions
               - Ensure each expert contributes in their area
            3. Maintain progress:
               - Regularly summarize key points
               - Identify when consensus is reached
               - Flag unresolved issues
            4. Drive conclusions:
               - Synthesize final outcomes
               - List action items
               - Highlight open questions

            Start each discussion by:
            1. Analyzing the topic
            2. Creating a structured discussion plan
            3. Assigning initial tasks to experts

            When experts speak, ensure they stay focused on their expertise area."""
        )

        # Create specialized discussion agents
        analyst = self.setup.create_assistant(
            name="Critical_Analyst",
            system_message="""You are a critical analyst focused on technical evaluation and risk assessment.
            Your responsibilities:
            1. Technical Analysis:
               - Evaluate proposed solutions for technical soundness
               - Identify potential bottlenecks and failure points
               - Assess scalability implications
            2. Risk Assessment:
               - Highlight security considerations
               - Point out potential performance issues
               - Identify maintenance challenges
            3. Quality Assurance:
               - Suggest testing strategies
               - Propose validation methods
               - Recommend quality metrics

            Wait for the controller's guidance before contributing.
            Keep responses focused on analysis and evaluation."""
        )

        synthesizer = self.setup.create_assistant(
            name="Idea_Synthesizer",
            system_message="""You are an idea synthesizer focused on integration and optimization.
            Your responsibilities:
            1. Solution Integration:
               - Combine different viewpoints into cohesive solutions
               - Identify synergies between proposals
               - Resolve conflicts in approaches
            2. Pattern Recognition:
               - Identify common themes
               - Spot potential design patterns
               - Suggest architectural improvements
            3. Innovation:
               - Propose creative solutions
               - Suggest alternative approaches
               - Identify optimization opportunities

            Wait for the controller's guidance before contributing.
            Focus on building upon and combining others' ideas."""
        )

        implementer = self.setup.create_assistant(
            name="Implementation_Expert",
            system_message="""You are an implementation expert focused on practical execution.
            Your responsibilities:
            1. Technical Implementation:
               - Propose specific technologies and libraries
               - Outline code structure and organization
               - Suggest concrete implementation steps
            2. Resource Planning:
               - Estimate implementation effort
               - Identify required dependencies
               - Suggest development phases
            3. Best Practices:
               - Recommend coding standards
               - Suggest testing approaches
               - Propose documentation needs

            Wait for the controller's guidance before contributing.
            Provide specific, actionable implementation details."""
        )

        # Create user proxy for coordination
        user_proxy = self.setup.create_user_proxy(
            name="Discussion_Coordinator",
            code_execution=False,
            code_execution_config={},  # Empty dict for no code execution
            description="Coordinates the discussion and relays messages between agents"
        )

        return {
            "controller": controller,
            "analyst": analyst,
            "synthesizer": synthesizer,
            "implementer": implementer,
            "user_proxy": user_proxy
        }

    def create_discussion_group(self, agents: Dict, max_rounds: int = 10) -> autogen.GroupChat:
        """Create a group chat with the controller as the speaker selection agent."""

        # Order matters - controller first, then other agents, user_proxy last
        agent_list = [
            agents["controller"],
            agents["analyst"],
            agents["synthesizer"],
            agents["implementer"],
            agents["user_proxy"]
        ]

        return self.setup.create_group_chat(
            agents=agent_list,
            max_round=max_rounds,
            speaker_selection_method="round_robin",  # Use round_robin for more predictable flow
            allow_repeat_speaker=True  # Allow agents to speak multiple times if needed
        )

    async def start_discussion(self, topic: str) -> str:
        """Start a new discussion on the given topic."""

        # Generate unique discussion ID
        discussion_id = str(uuid4())

        # Create agents
        agents = self.create_discussion_agents(discussion_id)

        # Create group chat
        group_chat = self.create_discussion_group(agents)

        # Create manager with the controller's config
        manager = self.setup.create_group_chat_manager(group_chat)

        # Store discussion info
        self.active_discussions[discussion_id] = {
            "agents": agents,
            "group_chat": group_chat,
            "manager": manager,
            "topic": topic
        }

        # Format initial message to structure the discussion
        initial_message = f"""Let's discuss the topic: {topic}

        Controller: Please guide this discussion. Start by:
        1. Breaking down the topic into key aspects to explore
        2. Identifying which expert should address each aspect
        3. Setting clear objectives for the discussion

        Other agents: Please wait for the controller's guidance before contributing."""

        # Start the discussion using async method
        await agents["user_proxy"].a_initiate_chat(
            manager,
            message=initial_message
        )

        return discussion_id

    async def add_message_to_discussion(self, discussion_id: str, message: str) -> Optional[str]:
        """Add a message to an ongoing discussion."""
        if discussion_id not in self.active_discussions:
            raise ValueError(f"Discussion {discussion_id} not found")

        discussion = self.active_discussions[discussion_id]
        user_proxy = discussion["agents"]["user_proxy"]
        manager = discussion["manager"]

        # Send message through user proxy
        response = await user_proxy.a_initiate_chat(
            manager,
            message=message
        )

        return response.summary if response else None

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