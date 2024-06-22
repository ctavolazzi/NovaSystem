"""
Main application script for the RAG Chatbot.
"""

import gradio as gr
import logging
from chatbot import chat_ollama
from data_loader import get_document_chunks
from vector_store import get_vector_store, VectorStoreError
from config import CONFIG

# Set up logging
logging.basicConfig(
    level=logging.DEBUG if CONFIG['DEBUG'] else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Initialize and run the RAG Chatbot application."""
    try:
        if CONFIG['INITIAL_DB']:
            logger.info("Initializing vector database...")
            document_chunks = get_document_chunks()
            get_vector_store(document_chunks)
        else:
            logger.info("Loading existing vector database...")
            get_vector_store()

        gradio_interface = gr.ChatInterface(
            chat_ollama,
            chatbot=gr.Chatbot(),
            textbox=gr.Textbox(placeholder="Example: Who is Alice?", container=False, scale=7),
            title="The Ollama RAG Chatbot",
            description=f"Ask the {CONFIG['OLLAMA_MODEL']} chatbot a question!",
            theme='gradio/base',
            retry_btn=None,
            undo_btn="Delete Previous",
            clear_btn="Clear",
        )

        logger.info("Starting Gradio interface...")
        gradio_interface.launch()
    except VectorStoreError as e:
        logger.error(f"Vector store error: {str(e)}")
        print(f"An error occurred with the vector store: {str(e)}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()