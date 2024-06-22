"""
Module for loading and preprocessing documents for the RAG Chatbot.
"""

import os
import logging
from langchain.document_loaders import TextLoader
from langchain.text_splitter import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from config import CONFIG

logger = logging.getLogger(__name__)

def load_documents():
    """Load documents from the data directory."""
    documents = []
    for file in os.listdir(CONFIG['DATA_PATH']):
        try:
            loader = TextLoader(os.path.join(CONFIG['DATA_PATH'], file))
            documents.append(loader.load()[0])
            logger.info(f"Loaded document: {file}")
        except Exception as e:
            logger.error(f"Error loading document {file}: {str(e)}")
    return documents

def split_documents(documents):
    """Split documents into chunks."""
    try:
        md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=CONFIG['HEADERS_TO_SPLIT_ON'], strip_headers=False)
        chunks_array = []

        for doc in documents:
            md_chunks = md_splitter.split_text(doc.page_content)
            for chunk in md_chunks:
                chunk.metadata.update(doc.metadata)
            
            txt_splitter = RecursiveCharacterTextSplitter(
                chunk_size=CONFIG['CHUNK_SIZE'], 
                chunk_overlap=CONFIG['CHUNK_OVERLAP'], 
                length_function=len, 
                add_start_index=True
            )
            txt_chunks = txt_splitter.split_documents(md_chunks)
            chunks_array.extend(txt_chunks)

        logger.info(f"Split documents into {len(chunks_array)} chunks")
        return chunks_array
    except Exception as e:
        logger.error(f"Error splitting documents: {str(e)}")
        raise

def get_document_chunks():
    """Load and split documents into chunks."""
    documents = load_documents()
    return split_documents(documents)

def add_new_document(file_path):
    """Add a new document to the existing database."""
    try:
        loader = TextLoader(file_path)
        new_doc = loader.load()[0]
        chunks = split_documents([new_doc])
        logger.info(f"Added new document: {file_path}")
        return chunks
    except Exception as e:
        logger.error(f"Error adding new document {file_path}: {str(e)}")
        raise