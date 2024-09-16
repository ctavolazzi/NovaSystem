"""
Configuration settings for the RAG Chatbot application.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

CONFIG = {
    # Paths
    'BASE_DIR': os.path.dirname(os.path.abspath(__file__)),
    'DATA_PATH': os.getenv('DATA_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")),
    'CHROMA_PATH': os.getenv('CHROMA_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma")),

    # Ollama settings
    'OLLAMA_MODEL': os.getenv('OLLAMA_MODEL', "llama2:chat"),
    'OLLAMA_URL': os.getenv('OLLAMA_URL', "http://localhost:11434"),

    # Text splitting settings
    'HEADERS_TO_SPLIT_ON': [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
        ("####", "Header 4"),
    ],
    'CHUNK_SIZE': int(os.getenv('CHUNK_SIZE', 500)),
    'CHUNK_OVERLAP': int(os.getenv('CHUNK_OVERLAP', 100)),

    # Vector DB settings
    'INITIAL_DB': os.getenv('INITIAL_DB', 'False').lower() == 'true',

    # Application settings
    'DEBUG': os.getenv('DEBUG', 'False').lower() == 'true',
}
