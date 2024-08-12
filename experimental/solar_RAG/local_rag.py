import os
import logging
from typing import List, Dict, Any

from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOllama
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
CONFIG = {
    "chunk_size": 7500,
    "chunk_overlap": 100,
    "embedding_model": "nomic-embed-text",
    "llm_model": "mistral",
    "vector_store_path": "./vector_store"
}

def load_and_split_document(file_path: str) -> List[Any]:
    """Load a PDF document and split it into chunks."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    logging.info(f"Loading document: {file_path}")
    loader = UnstructuredPDFLoader(file_path)
    data = loader.load()
    
    logging.info("Splitting document into chunks")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CONFIG["chunk_size"], 
        chunk_overlap=CONFIG["chunk_overlap"]
    )
    chunks = text_splitter.split_documents(data)
    
    logging.info(f"Document split into {len(chunks)} chunks")
    return chunks

def setup_vector_store(chunks: List[Any]) -> Chroma:
    """Set up the vector store with document chunks."""
    logging.info("Setting up vector store")
    embeddings = OllamaEmbeddings(model=CONFIG["embedding_model"])
    
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CONFIG["vector_store_path"]
    )
    vector_store.persist()
    logging.info("Vector store created and persisted")
    return vector_store

def setup_query_processor() -> LLMChain:
    """Set up the query processor for generating multiple query versions."""
    logging.info("Setting up query processor")
    llm = ChatOllama(model=CONFIG["llm_model"])
    
    query_prompt = PromptTemplate(
        input_variables=["question"],
        template="""Generate three different versions of the given question to retrieve relevant documents.
        Original question: {question}"""
    )
    
    return LLMChain(llm=llm, prompt=query_prompt)

def setup_retriever(vector_store: Chroma, query_processor: LLMChain) -> MultiQueryRetriever:
    """Set up the multi-query retriever."""
    logging.info("Setting up retriever")
    return MultiQueryRetriever(
        retriever=vector_store.as_retriever(),
        llm_chain=query_processor,
        parser_key="text"
    )

def setup_rag_chain(retriever: MultiQueryRetriever, llm: ChatOllama) -> Any:
    """Set up the RAG chain for question answering."""
    logging.info("Setting up RAG chain")
    rag_prompt = ChatPromptTemplate.from_template("""
    Answer the question based ONLY on the following context:
    {context}
    Question: {question}
    If the answer cannot be found in the context, say "I don't have enough information to answer this question."
    """)
    
    return (
        {"context": retriever, "question": RunnablePassthrough()}
        | rag_prompt
        | llm
        | StrOutputParser()
    )

def main():
    file_path = input("Enter the path to your PDF document: ")
    
    try:
        chunks = load_and_split_document(file_path)
        vector_store = setup_vector_store(chunks)
        query_processor = setup_query_processor()
        retriever = setup_retriever(vector_store, query_processor)
        llm = ChatOllama(model=CONFIG["llm_model"])
        rag_chain = setup_rag_chain(retriever, llm)
        
        logging.info("Setup complete. Ready to answer questions.")
        
        while True:
            question = input("Enter your question (or 'quit' to exit): ")
            if question.lower() == 'quit':
                break
            
            logging.info(f"Processing question: {question}")
            answer = rag_chain.invoke(question)
            print(f"Answer: {answer}")
    
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()