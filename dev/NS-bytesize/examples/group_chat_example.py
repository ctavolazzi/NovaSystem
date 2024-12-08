import os
from pathlib import Path
from utils.autogen_setup import AutogenSetup

def run_group_chat():
    """
    Example of running a group chat with multiple agents.
    """
    # Initialize AutogenSetup with Ollama backend
    setup = AutogenSetup(use_ollama=True)  # Will use llama3.2 by default

    # Create an assistant for coding tasks
    coder = setup.create_assistant(
        name="Coder",
        system_message="You are an expert Python programmer. Write clear, efficient code with good documentation."
    )

    # Create an assistant for reviewing code
    reviewer = setup.create_assistant(
        name="Reviewer",
        system_message="You are a code reviewer focused on best practices, security, and performance."
    )

    # Create a user proxy for code execution
    user_proxy = setup.create_user_proxy(
        name="User",
        code_execution=True
    )

    # Create a group chat with all agents
    group_chat = setup.create_group_chat(
        agents=[user_proxy, coder, reviewer],
        max_round=10
    )

    # Create a manager for the group chat
    manager = setup.create_group_chat_manager(group_chat)

    # Start the conversation with a coding task
    user_proxy.initiate_chat(
        manager,
        message="Please write a Python function that calculates the Fibonacci sequence up to n terms, then review the code for improvements."
    )

if __name__ == "__main__":
    run_group_chat()