import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

def setup_logger(log_file_path='logs/rag_system.log'):
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    # Create logger
    logger = logging.getLogger('RAGSystem')
    logger.setLevel(logging.DEBUG)

    # Create handlers
    console_handler = logging.StreamHandler()
    file_handler = RotatingFileHandler(log_file_path, maxBytes=10485760, backupCount=5)

    # Create formatters and add it to handlers
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    console_format = logging.Formatter(log_format)
    file_format = logging.Formatter(log_format)
    console_handler.setFormatter(console_format)
    file_handler.setFormatter(file_format)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

# Usage in main script
logger = setup_logger()

def log_query(query, query_type, response):
    logger.info(f"Query: {query}")
    logger.info(f"Query Type: {query_type}")
    logger.info(f"Response: {response}")

# Example usage in process_query function
def process_query(query, conn, cursor, chroma_collection):
    query_type = classify_query(query)
    
    if query_type == 'SQL':
        sql = generate_sql(query)
        results = execute_sql(cursor, sql)
        response = generate_response_summary(sql, results)
        log_query(query, 'SQL', response)
        return response
    else:
        context = query_chroma(chroma_collection, query)
        response = generate_rag_response(query, context)
        log_query(query, 'RAG', response)
        return response

# Add performance logging
def log_performance(function_name, execution_time):
    logger.debug(f"Performance: {function_name} took {execution_time:.2f} seconds")

# Example usage with a decorator
import time
from functools import wraps

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        log_performance(func.__name__, end_time - start_time)
        return result
    return wrapper

@timer
def generate_sql(query):
    # Existing code here
    pass