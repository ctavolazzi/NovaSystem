# NovaSystem/main.py

import os
import time
import typer
import subprocess
import logging
from src.utils.stream_to_console import stream_to_console as stc, apply_color
from src.utils.generate_file_structure import generate_file_structure
from src.utils.ascii_art_utils import display_random_rainbow_art
from src.utils.border_maker import border_maker
import random
from art import text2art
from openai import OpenAI
from transformers import pipeline
from dotenv import load_dotenv
from src.AI.AIJournal import AIJournal
from src.AI.AIForum import AIForum, AIUser
from src.AI.openai_guy import OpenAIGuy
from src.AI.huggingface_guy import HuggingFaceGuy

print("NovaSystem version 0.1.0")

load_dotenv()

app = typer.Typer()
client = OpenAI()

# Initialize AI components
ai_journal = AIJournal("NovaSystem_AI")

# # Extract the username
# username = os.getlogin()  # or use the os.environ method
# print(f"Username: {username}")

# username = os.environ.get('SUDO_USER', os.environ.get('USER', os.environ.get('USERNAME')))
# print(f"Username: {username}")

def get_username():
    """Retrieves the current username."""
    return os.environ.get('USER') or os.environ.get('USERNAME')

username = get_username()

# This huggingface stuff should be extracted to a module in the future
def setup_huggingface_pipeline():
    """Sets up the HuggingFace text generation pipeline."""
    # Assuming you have a token for authenticated access to HuggingFace models
    huggingface_token = os.getenv("HUGGINGFACE_API_KEY")
    return pipeline('text-generation', model='gpt2', use_auth_token=huggingface_token)

def generate_text_with_huggingface(prompt, generator):
    """Generates text response using HuggingFace pipeline."""
    try:
        generated_texts = generator(prompt, max_length=50, num_return_sequences=1)
        return generated_texts[0]['generated_text']
    except Exception as e:
        logging.error(f"Error in generating text with HuggingFace: {e}")
        return "An error occurred in generating the response."

# Initialize the HuggingFace pipeline
huggingface_generator = setup_huggingface_pipeline()

def handle_user_request(request):
    """Handles user request, generates AI response, and logs the interaction."""
    try:
        # Journal entry for user request
        ai_journal.create_journal_entry("User Request", "NovaSystem", request)

        # Generating AI response using HuggingFace pipeline
        ai_response = generate_text_with_huggingface(request, huggingface_generator)

        # Displaying AI response
        stc("AI Response: " + ai_response, foreground_color="CYAN")

        # Journal entry for AI response
        ai_journal.create_journal_entry("AI Response", "NovaSystem", ai_response)
    except Exception as e:
        logging.error(f"Error in handling user request: {e}")
        stc("An error occurred while processing your request.", foreground_color="RED")

    return ai_response  # Returning AI response for any further use


def generate_ai_response(request):
    """Generates an AI response to the user's request."""
    # Placeholder for actual AI response generation logic
    # Example: return openai_guy.get_response(request) or huggingface_guy.get_response(request)
    return "AI Response to: " + request



# Use the username in defining the default directory
DEFAULT_DIR = f"NovaSystem-{username}"

def run_tests():
    # Placeholder for actual test functions
    tests = []
    results = [test() for test in tests]
    return results

def install_requirements():
    """Installs required packages."""
    stc("Installing required packages...", foreground_color="MAGENTA")
    subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)

def start_components():
    """Starts various system components like database, server, etc."""
    # Placeholder for starting system components
    # Example: Start a database, internal server, etc.
    stc("Starting system components...", foreground_color="CYAN")

def start_operation():
    """Starts the standard operation of the NovaSystem."""
    root_directory = os.path.dirname(os.path.abspath(__file__))
    output_directory = os.path.join(root_directory, 'output')
    os.makedirs(output_directory, exist_ok=True)

    output_filename = f'NovaSystem_file_structure_{time.time()}_new.txt'
    generate_file_structure(root_directory, os.path.join(output_directory, output_filename))

    stc("NovaSystem is up and running.", foreground_color="GREEN")

def check_or_create_directory(directory_name):
    """Check if a directory exists, and create it if it doesn't."""
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
        stc(f"Created directory: {directory_name}\n", foreground_color="GREEN")

@app.command()
def start():
    """Starts the NovaSystem application."""
    username = get_username()
    DEFAULT_DIR = f"NovaSystem-{username}"
    stc("Starting NovaSystem...\n", foreground_color="BLUE", bold=True)

    def setup_huggingface_pipeline():
        huggingface_token = os.getenv("HUGGINGFACE_API_KEY")
        return pipeline('text-generation', model='gpt2', use_auth_token=huggingface_token)

    def generate_text_with_huggingface(prompt, generator):
        generated_texts = generator(prompt, max_length=50, num_return_sequences=1)
        return generated_texts[0]['generated_text']

    huggingface_generator = setup_huggingface_pipeline()


    # Check if the default directory exists
    if not os.path.exists(DEFAULT_DIR):
        stc("Default directory not found.\n", foreground_color="YELLOW")
        user_choice = typer.confirm(f"Do you want to use the default directory '{DEFAULT_DIR}'?")
        if user_choice:
            check_or_create_directory(DEFAULT_DIR)
        else:
            custom_dir = typer.prompt("Please enter a custom directory name")
            check_or_create_directory(custom_dir)
    else:
        stc(f"Using existing directory: {DEFAULT_DIR}\n", foreground_color="GREEN")

    """Interactive CLI for NovaSystem."""
    stc("Initializing NovaSystem...", foreground_color="BLUE", bold=True)

    stc("Running system checks...", foreground_color="CYAN")
    run_tests()

    stc("Setting up the environment...", foreground_color="GREEN")
    # install_requirements()

    start_components()

    start_operation()

    display_random_rainbow_art("Welcome\nto the\nNovaSystem")

    user_request = typer.prompt(stc("What can NovaSystem help you with?", foreground_color="YELLOW"))
    # Here, integrate with the LLM (like OpenAI API) to process user_request
    # Example: response = process_with_llm(user_request)
    # stc(response, "CYAN")
    stc("Processing your request...\nUser Request:", foreground_color="CYAN")
    # bordered_user_request = border_maker(user_request, border_color="CYAN", border_char='*', padding=1)
    stc(f"{user_request}", rainbow_effect=True, bold=True, fg_style="BRIGHT")

    # user_request = typer.prompt("What do you want NovaSystem to help you with?")
    response = generate_text_with_huggingface(user_request, huggingface_generator)
    stc("AI Response: " + response, foreground_color="CYAN")


@app.command()
def art():
    """Displays random ASCII art with rainbow effect."""
    display_random_rainbow_art()


@app.command()
def forum():
    """Simulates a conversation between two AIs in the AI forum."""
    hfg= HuggingFaceGuy("distilgpt2")
    ai_forum = AIForum()
    ai_user1 = AIUser("AI_1", hfg)
    ai_user2 = AIUser("AI_2", hfg)

    # Number of message exchanges you want
    number_of_exchanges = 5

    ai_forum.simulate_ai_conversation(ai_user1, ai_user2, number_of_exchanges)

    # Optionally, log the conversation in AIJournal
    for message in ai_forum.forum.messages:
        ai_journal.create_journal_entry("AI Conversation", "NovaSystem", message)

    # Display the conversation
    ai_forum.display_forum_messages()


@app.command()
def test():
    """Tests the NovaSystem application."""
    stc("\n=== Running System Tests ===\n", foreground_color="MAGENTA", bold=True)

    # Test the default directory
    stc("Checking for default directory...", foreground_color="CYAN")
    report = analyze_directory(DEFAULT_DIR)
    stc(report, foreground_color="GREEN")

    # Header for file structure display
    stc("\n=== File Structure of src Folder ===\n", foreground_color="CYAN", bold=True)

    # Displaying the file structure
    generate_file_structure('./src', 'output.txt')
    with open('output.txt', 'r') as file:
        file_contents = file.read()
        # Formatting the file structure for better readability
        formatted_contents = format_file_structure(file_contents)
        stc(formatted_contents, foreground_color="GREEN")

def format_file_structure(contents):
    """Apply additional formatting to file structure contents for better readability."""
    # Example formatting: Add indentation, bullet points, or color coding
    formatted_contents = ""
    for line in contents.split('\n'):
        if line.strip():
            formatted_contents += "    • " + line + "\n"
    return formatted_contents

def analyze_directory(directory):
    """Analyzes the directory and returns a summary report."""
    if not os.path.exists(directory):
        return f"Directory '{directory}' does not exist."

    file_count = 0
    dir_count = 0
    for entry in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, entry)):
            file_count += 1
        elif os.path.isdir(os.path.join(directory, entry)):
            dir_count += 1

    report = f"Directory '{directory}' contains {file_count} files and {dir_count} subdirectories."
    return report

@app.command()
def quit():
    """Quits the NovaSystem."""
    stc("Exiting NovaSystem.", background_color="RED", foreground_color="WHITE", bold=True)
    raise typer.Exit()

if __name__ == "__main__":
    app()