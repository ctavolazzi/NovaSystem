# File: agents/DebateCoordinator.py
from autogen.agentchat.assistant_agent import AssistantAgent

class DebateCoordinator(AssistantAgent):
    """
    This agent coordinates the debate, ensuring it progresses smoothly 
    and terminates when a conclusion is reached.
    """
    def __init__(self, llm_config):
        super().__init__(name='DebateCoordinator', system_message="You are the debate coordinator responsible for overseeing the debate flow and ensuring a clear resolution.", llm_config=llm_config)
        # Additional properties and methods specific to the Debate Coordinator.
