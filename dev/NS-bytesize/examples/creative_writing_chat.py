"""
Multi-agent creative writing system.
This example demonstrates collaboration between specialized writing agents.
"""
from utils.autogen_setup import AutogenSetup

def run_writing_team(use_ollama: bool = True):
    """
    Run a creative writing team with multiple specialized agents.

    Args:
        use_ollama: If True, uses llama3.2, otherwise uses gpt-4o
    """
    # Initialize with chosen backend
    setup = AutogenSetup(
        use_ollama=use_ollama,
        model_name="llama3.2" if use_ollama else "gpt-4o"
    )

    # Create specialized agents
    plotter = setup.create_assistant(
        name="Story_Plotter",
        system_message="""You are an expert story plotter and outline creator.
        You excel at creating compelling story structures and plot points.
        You understand the three-act structure, plot devices, and narrative arcs.
        You create clear, concise outlines that others can build upon."""
    )

    character_dev = setup.create_assistant(
        name="Character_Developer",
        system_message="""You are an expert character developer.
        You create deep, believable characters with clear motivations and arcs.
        You understand character psychology, relationships, and growth.
        You provide detailed character profiles that writers can use."""
    )

    writer = setup.create_assistant(
        name="Creative_Writer",
        system_message="""You are a skilled creative writer.
        You turn outlines and character profiles into engaging prose.
        You excel at description, dialogue, and narrative flow.
        You maintain consistency with the plot and character profiles provided."""
    )

    # Create a user proxy to coordinate
    user_proxy = setup.create_user_proxy(
        name="Editor",
        code_execution=False,
        code_execution_config={}
    )

    # Create group chat
    group_chat = setup.create_group_chat(
        agents=[user_proxy, plotter, character_dev, writer],
        max_round=12,
        speaker_selection_method="round_robin",
        allow_repeat_speaker=False
    )

    # Create manager
    manager = setup.create_group_chat_manager(group_chat)

    # Start the creative process
    user_proxy.initiate_chat(
        manager,
        message="""Let's create a short story together. The theme is 'unexpected friendship'.
        Story_Plotter: Start by creating a basic outline.
        Character_Developer: Once we have an outline, develop the main characters.
        Creative_Writer: Finally, write the opening scene based on the outline and characters."""
    )

if __name__ == "__main__":
    run_writing_team(use_ollama=True)