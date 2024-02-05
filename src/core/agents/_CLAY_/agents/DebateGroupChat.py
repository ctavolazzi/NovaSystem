# File: agents/groupchat/DebateGroupChat.py
from autogen.agentchat.groupchat import GroupChat

class DebateGroupChat(GroupChat):
    """
    Manages the debate group chat, selecting speakers, handling message flow,
    and ensuring debate rules are followed.
    """
    def __init__(self, agents, messages, max_round=10):
        super().__init__(agents, messages, max_round)
        self.previous_speaker = None

    def select_speaker(self, last_speaker, selector):
        # Logic for selecting the next speaker in the debate.
        # ...
