"""
Simple example of a two-agent chat solving a math problem.
This example uses Ollama's OpenAI compatibility layer.
"""
from utils.autogen_setup import AutogenSetup

def run_math_chat(use_ollama: bool = True):
    """
    Run a simple chat between a math expert and a user.

    Args:
        use_ollama: If True, uses llama3.2, otherwise uses gpt-4o
    """
    # Initialize with chosen backend
    setup = AutogenSetup(
        use_ollama=use_ollama,
        model_name="llama3.2" if use_ollama else "gpt-4o"
    )

    # Create a math expert assistant
    math_expert = setup.create_assistant(
        name="Math_Expert",
        system_message="""You are a mathematics expert.
        You solve math problems step by step, showing your work clearly.
        You verify your answers and point out any assumptions made.
        Keep your responses focused and precise."""
    )

    # Create a user proxy (no code execution needed for math)
    user_proxy = setup.create_user_proxy(
        name="User",
        code_execution=False,
        code_execution_config={}  # Empty dict to avoid deprecation warning
    )

    # Create a group chat with specific speaker selection
    group_chat = setup.create_group_chat(
        agents=[user_proxy, math_expert],
        max_round=5,  # Limit rounds since this is a simple problem
        speaker_selection_method="round_robin",
        allow_repeat_speaker=False
    )

    # Create a manager
    manager = setup.create_group_chat_manager(group_chat)

    # Start the conversation with a math problem
    user_proxy.initiate_chat(
        manager,
        message="""Please solve this step by step:
        If a triangle has sides of length 3, 4, and 5,
        what is its area? Use Heron's formula."""
    )

if __name__ == "__main__":
    # Use Ollama by default
    run_math_chat(use_ollama=True)
