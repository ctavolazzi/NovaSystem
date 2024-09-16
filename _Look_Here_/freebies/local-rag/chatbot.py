"""
Core chatbot functionality for the RAG Chatbot application.
"""

import logging
from llm import get_ollama, OllamaError
from vector_store import get_vector_store, VectorStoreError

logger = logging.getLogger(__name__)

MAX_HISTORY_LENGTH = 5  # Adjust as needed

def validate_input(message):
    """
    Validate the user input.
    
    Args:
        message (str): The user's input message.
    
    Returns:
        bool: True if input is valid, False otherwise.
    """
    if not message or not isinstance(message, str):
        return False
    if len(message.strip()) == 0:
        return False
    # Add more validation rules as needed
    return True

def chat_ollama(message, history):
    """
    Generate a response using the Ollama model and RAG.
    
    Args:
        message (str): The user's input message.
        history (list): The chat history.
    
    Returns:
        str: The generated response.
    """
    if not validate_input(message):
        return "I'm sorry, but I couldn't understand your input. Could you please rephrase your question?"

    try:
        ollama = get_ollama()
        chroma_db = get_vector_store()
        
        result_chunks = chroma_db.similarity_search(message)
        
        chroma_knowledge = ""
        sources = ""
        for idx, chunk in enumerate(result_chunks, 1):
            chroma_knowledge += f"[{idx}]\n{chunk.page_content}\n"
            sources += f"[{idx}]\n{chunk.metadata['source']}\n"

        # Limit the history to the last MAX_HISTORY_LENGTH exchanges
        limited_history = history[-MAX_HISTORY_LENGTH:]
        history_str = "\n".join([f"Human: {h[0]}\nAI: {h[1]}" for h in limited_history])

        prompt = f"""Answer the following question using the provided knowledge and the chat history:

    ###KNOWLEDGE: {chroma_knowledge}

    ###CHAT-HISTORY: {history_str}

    ###QUESTION: {message}"""

        result = ollama(prompt)
        return f"{result}\n\n\nReferences:\n{sources}"
    except VectorStoreError as e:
        logger.error(f"Vector store error in chat_ollama: {str(e)}")
        return "I'm sorry, but I'm having trouble accessing my knowledge base right now."
    except OllamaError as e:
        logger.error(f"Ollama error in chat_ollama: {str(e)}")
        return "I'm sorry, but I'm having trouble generating a response right now."
    except Exception as e:
        logger.error(f"Unexpected error in chat_ollama: {str(e)}")
        return "I apologize, but I'm experiencing an unexpected issue. Please try again later."
