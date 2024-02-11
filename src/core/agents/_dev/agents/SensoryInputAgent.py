# File: agents/SensoryInputAgent.py
from autogen.agentchat.assistant_agent import AssistantAgent

class SensoryInputAgent(AssistantAgent):
    """
    This agent acts as the sensory system within the AGI, responsible for 
    receiving external inputs and directing the flow of the debate.
    """
    def __init__(self, llm_config):
        super().__init__(name='SensoryInputAgent', system_message="You represent the sensory input for the AGI system, initiating and guiding the debate based on external stimuli.", llm_config=llm_config)
        # Additional properties and methods specific to the Sensory Input Agent.
