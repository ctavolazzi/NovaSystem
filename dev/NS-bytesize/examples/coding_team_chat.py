"""
Multi-agent coding team that can break down, implement, and review code.
Uses Docker for safe code execution and testing.
"""
from utils.autogen_setup import AutogenSetup

def run_coding_team(use_ollama: bool = True):
    """
    Run a coding team with multiple specialized agents.

    Args:
        use_ollama: If True, uses llama3.2, otherwise uses gpt-4o
    """
    # Initialize with chosen backend
    setup = AutogenSetup(
        use_ollama=use_ollama,
        model_name="llama3.2" if use_ollama else "gpt-4o"
    )

    # Create specialized agents
    architect = setup.create_assistant(
        name="Software_Architect",
        system_message="""You are an experienced software architect.
        You break down complex tasks into smaller, manageable components.
        You provide clear technical specifications and requirements.
        You consider scalability, maintainability, and best practices."""
    )

    programmer = setup.create_assistant(
        name="Programmer",
        system_message="""You are a skilled programmer.
        You write clean, efficient, and well-documented code.
        You follow best practices and design patterns.
        You implement solutions based on technical specifications."""
    )

    reviewer = setup.create_assistant(
        name="Code_Reviewer",
        system_message="""You are a thorough code reviewer.
        You check for bugs, security issues, and performance problems.
        You suggest improvements and optimizations.
        You ensure code follows best practices and is well-documented."""
    )

    tester = setup.create_assistant(
        name="QA_Engineer",
        system_message="""You are a detail-oriented QA engineer.
        You write and execute test cases.
        You verify functionality and edge cases.
        You report bugs clearly and suggest fixes."""
    )

    # Create a user proxy with Docker for code execution
    user_proxy = setup.create_user_proxy(
        name="Project_Manager",
        code_execution=True,  # Enable code execution
        code_execution_config={
            "work_dir": "coding_workspace",
            "use_docker": True
        }
    )

    # Create group chat
    group_chat = setup.create_group_chat(
        agents=[user_proxy, architect, programmer, reviewer, tester],
        max_round=15,
        speaker_selection_method="round_robin",
        allow_repeat_speaker=False
    )

    # Create manager
    manager = setup.create_group_chat_manager(group_chat)

    # Start the development process
    user_proxy.initiate_chat(
        manager,
        message="""Let's create a Python function that:
        1. Takes a list of numbers
        2. Removes duplicates
        3. Sorts them in descending order
        4. Returns both the sorted list and the count of duplicates removed

        Software_Architect: Please break this down into clear requirements.
        Programmer: Once we have the requirements, implement the solution.
        Code_Reviewer: Review the implementation.
        QA_Engineer: Write and run tests to verify the solution."""
    )

if __name__ == "__main__":
    run_coding_team(use_ollama=True)