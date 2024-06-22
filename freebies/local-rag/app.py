import gradio as gr
import logging
from scrapegraphai.graphs import SmartScraperGraph
from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OllamaEmbeddings
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from config import CONFIG
from vector_store import VectorStoreError, get_vector_store
from chatbot import chat_ollama

# Set up logging
logging.basicConfig(
    level=logging.DEBUG if CONFIG['DEBUG'] else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def scrape_with_scrapegraphai(url):
    """Scrape content using ScrapeGraphAI library."""
    graph_config = {
        "llm": {
            "model": CONFIG['OLLAMA_MODEL'],
            "temperature": 0,
            "format": "json",  
            "base_url": CONFIG['OLLAMA_URL'],  
        },
        "embeddings": {
            "model": "ollama/nomic-embed-text",
            "base_url": CONFIG['OLLAMA_URL'],  
        },
        "verbose": True,
    }
    smart_scraper_graph = SmartScraperGraph(
        prompt="Extract all the text content",
        source=url,
        config=graph_config
    )
    result = smart_scraper_graph.run()
    markdown_path = "scraped_content.md"
    with open(markdown_path, "w", encoding="utf-8") as file:
        for item in result['content']:
            file.write(item + "\n")
    
    return markdown_path

def ingest_markdown(markdown_path):
    """Ingest the markdown content into the vector store."""
    loader = UnstructuredMarkdownLoader(markdown_path)
    docs = loader.load()

    chunk_size = CONFIG['CHUNK_SIZE']
    chunk_overlap = CONFIG['CHUNK_OVERLAP']
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    splits = text_splitter.split_documents(docs)

    embeddings = OllamaEmbeddings(base_url=CONFIG['OLLAMA_URL'], model=CONFIG['OLLAMA_MODEL'])
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory=CONFIG['CHROMA_PATH'])
    retriever = vectorstore.as_retriever()

    prompt_template = "Your local prompt template here"

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt_template
        | chat_ollama  # Using local Ollama model for processing
        | StrOutputParser()
    )
    
    return vectorstore, rag_chain

def ingest_url(url):
    """Ingest content from the URL into the vector store."""
    try:
        markdown_path = scrape_with_scrapegraphai(url)
        vectorstore, rag_chain = ingest_markdown(markdown_path)
        return "Content ingested successfully!", vectorstore, rag_chain
    except Exception as e:
        logger.error(f"Error ingesting content from {url}: {str(e)}")
        return f"Failed to ingest content from {url}: {str(e)}", None, None

def query_vectorstore(query, rag_chain):
    """Query the vector store with a given query."""
    if rag_chain:
        response = rag_chain.invoke(query)
        return response
    else:
        return "Vector store not initialized."

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

        with gr.Blocks() as gradio_interface:
            gr.Markdown("## The Ollama RAG Chatbot")
            with gr.Row():
                with gr.Column():
                    url_input = gr.Textbox(label="Enter URL to Ingest", placeholder="Example: https://example.com/article")
                    ingest_button = gr.Button("Ingest URL")
                    ingestion_status = gr.Textbox(label="Ingestion Status", interactive=False)
                    chatbot = gr.Chatbot()
                    user_input = gr.Textbox(placeholder="Example: Who is Alice?", container=False, scale=7)
                    send_button = gr.Button("Send")
                    
                    def ingest_callback(url):
                        status, vectorstore, rag_chain = ingest_url(url)
                        return status, vectorstore, rag_chain
                    
                    def query_callback(user_input, rag_chain):
                        response = query_vectorstore(user_input, rag_chain)
                        return response
                    
                    ingest_button.click(ingest_callback, inputs=url_input, outputs=[ingestion_status, chatbot, None])
                    send_button.click(query_callback, inputs=user_input, outputs=chatbot)

        logger.info("Starting Gradio interface...")
        gradio_interface.launch(server_name="0.0.0.0", server_port=7860, inbrowser=True)
    except VectorStoreError as e:
        logger.error(f"Vector store error: {str(e)}")
        print(f"An error occurred with the vector store: {str(e)}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
