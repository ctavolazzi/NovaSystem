
# File: agents/NegativeDebater.py
from autogen.agentchat.assistant_agent import AssistantAgent

class NegativeDebater(AssistantAgent):
    """
    This agent specializes in arguing negative positions in debates, 
    opposing the given proposition.
    """
    def __init__(self, llm_config):
        super().__init__(name='NegativeDebater', system_message="Your role is to oppose the debate topic, presenting counterarguments and challenging the affirmative position.", llm_config=llm_config)
        # Additional properties and methods specific to the Negative Debater.
