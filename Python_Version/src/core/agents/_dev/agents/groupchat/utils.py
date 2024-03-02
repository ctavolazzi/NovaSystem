# File: agents/groupchat/utils.py
def is_termination_msg(content) -> bool:
    """
    Checks if the message content contains the termination keyword, indicating 
    the debate has reached a conclusion.
    """
    return "TERMINATE" in content["content"]
