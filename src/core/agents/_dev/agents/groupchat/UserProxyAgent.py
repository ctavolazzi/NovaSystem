# File: agents/groupchat/UserProxyAgent.py
from autogen import UserProxyAgent

class DebateTerminator(UserProxyAgent):
    """
    Acts as a terminator for the debate, ending the group chat when a 
    conclusive result is acknowledged by the agents.
    """
    def __init__(self):
        super().__init__(name="DebateTerminator", system_message="This agent ends the debate when a conclusive result is reached.", code_execution_config=False, is_termination_msg=is_termination_msg)
        # Additional initialization for the Debate Terminator.
