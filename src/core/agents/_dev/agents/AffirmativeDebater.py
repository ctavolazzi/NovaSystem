# File: agents/AffirmativeDebater.py
from autogen.agentchat.assistant_agent import AssistantAgent

class AffirmativeDebater(AssistantAgent):
    """
    This agent specializes in arguing affirmative positions in debates, 
    supporting the given proposition.
    """
    def __init__(self, llm_config):
        super().__init__(name='AffirmativeDebater', system_message="Your role is to support the debate topic affirmatively, presenting arguments and countering opposition.", llm_config=llm_config)
        # Additional properties and methods specific to the Affirmative Debater.
