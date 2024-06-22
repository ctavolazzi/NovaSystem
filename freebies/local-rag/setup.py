"""
Setup script for the RAG Chatbot application.
This script downloads necessary files from the specified repository and sets up the application.
"""

import os
import subprocess
import requests

REPO_OWNER = 'yourusername'
REPO_NAME = 'rag-chatbot'
BRANCH = 'main'
FOLDER_PATH = 'freebies/local-rag'
FILES_TO_DOWNLOAD = [
    'app.py',
    'config.py',
    'data_loader.py',
    'vector_store.py',
    'llm.py',
    'chatbot.py',
    'requirements.txt',
    'README.md'
]

def download_file(file_name):
    """Download a file from the GitHub repository."""
    url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/{FOLDER_PATH}/{file_name}"
    response = requests.get(url)
    if response.status_code == 200:
        with open(file_name, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded {file_name}")
    else:
        print(f"Failed to download {file_name}")

def run_command(command):
    """Run a shell command and handle any errors."""
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(e)

def setup_ollama():
    """Set up Ollama and pull the required model."""
    print("Setting up Ollama...")
    if os.name == 'nt':  # Windows
        print("Please download and install Ollama manually from https://ollama.ai/download")
        input("Press Enter once Ollama is installed...")
    else:  # macOS and Linux
        run_command("curl https://ollama.ai/install.sh | sh")
    
    run_command("ollama pull llama2:chat")

def main():
    print("Setting up the RAG Chatbot application...")

    # Download necessary files
    for file_name in FILES_TO_DOWNLOAD:
        download_file(file_name)

    # Create a virtual environment
    run_command("python -m venv venv")

    # Activate the virtual environment
    if os.name == 'nt':  # Windows
        activate_cmd = r".\venv\Scripts\activate"
    else:  # macOS and Linux
        activate_cmd = "source venv/bin/activate"

    # Install Python dependencies in the virtual environment
    run_command(f"{activate_cmd} && pip install -r requirements.txt")

    # Set up Ollama
    setup_ollama()

    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("chroma", exist_ok=True)

    print("\nSetup complete!")
    print("To run the application:")
    print(f"1. Activate the virtual environment: {activate_cmd}")
    print("2. Run the application: python app.py")

if __name__ == "__main__":
    main()
