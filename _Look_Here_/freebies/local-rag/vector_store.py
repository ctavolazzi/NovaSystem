"""
Module for managing the vector database (Chroma) for the RAG Chatbot.
"""

import logging
from langchain.embeddings import OllamaEmbeddings
from langchain.vectorstores import Chroma
from config import CONFIG

logger = logging.getLogger(__name__)

class VectorStoreError(Exception):
    """Custom exception for vector store related errors."""
    pass

def get_vector_store(document_chunks=None):
    """
    Get or create the Chroma vector store.
    
    If INITIAL_DB is True or document_chunks are provided, create a new database.
    Otherwise, load the existing database.
    """
    try:
        embeddings = OllamaEmbeddings(base_url=CONFIG['OLLAMA_URL'], model=CONFIG['OLLAMA_MODEL'])
        
        if CONFIG['INITIAL_DB'] or document_chunks:
            logger.info("Creating new vector store...")
            vector_store = Chroma.from_documents(
                document_chunks, 
                embeddings, 
                persist_directory=CONFIG['CHROMA_PATH']
            )
            vector_store.persist()
            logger.info("New vector store created and persisted.")
            return vector_store
        else:
            logger.info("Loading existing vector store...")
            return Chroma(
                persist_directory=CONFIG['CHROMA_PATH'], 
                embedding_function=embeddings
            )
    except Exception as e:
        logger.error(f"Error in get_vector_store: {str(e)}")
        raise VectorStoreError(f"Failed to get or create vector store: {str(e)}")

def add_documents_to_store(vector_store, new_chunks):
    """
    Add new document chunks to the existing vector store.
    
    Args:
        vector_store (Chroma): The existing Chroma vector store.
        new_chunks (list): List of new document chunks to add.
    """
    try:
        vector_store.add_documents(new_chunks)
        vector_store.persist()
        logger.info(f"Added {len(new_chunks)} new chunks to the vector store")
    except Exception as e:
        logger.error(f"Error adding new documents to vector store: {str(e)}")
        raise VectorStoreError(f"Failed to add new documents to vector store: {str(e)}")
