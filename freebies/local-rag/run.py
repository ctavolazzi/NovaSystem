import streamlit as st
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from langchain.chains.combine_documents import create_stuff_documents_chain
import os
from pathlib import Path

# Constants
DATA_DIR = Path("data")
DB_DIR = Path("db")

def init_ui():
    st.set_page_config(page_title="Langchain RAG Bot", layout="wide")
    st.title("Langchain RAG Bot")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage(content="Hello, I'm here to help. Ask me anything!")
        ]

    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None

    with st.sidebar:
        st.header("Document Capture")
        st.write("Please select a single document to use as context")
        st.markdown("**Please fill the below form :**")
        with st.form(key="Form", clear_on_submit=True):
            uploaded_file = st.file_uploader("Upload", type=["pdf"], key="pdf_upload")
            submit = st.form_submit_button(label="Upload")

        if submit:
            persist_file(uploaded_file)

def persist_file(uploaded_file):
    if uploaded_file is not None:
        DATA_DIR.mkdir(exist_ok=True)
        file_path = DATA_DIR / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"File {uploaded_file.name} saved successfully.")
        st.session_state.vector_store = init_vector_store()

def init_vector_store():
    files = [f for f in DATA_DIR.iterdir() if f.is_file()]
    if not files:
        st.error("No files uploaded")
        return None

    first_file = files[0].resolve()
    loader = PyPDFLoader(str(first_file))
    document = loader.load_and_split()

    text_splitter = RecursiveCharacterTextSplitter()
    document_chunks = text_splitter.split_documents(document)

    DB_DIR.mkdir(exist_ok=True)
    vector_store = Chroma.from_documents(
        documents=document_chunks,
        embedding=OllamaEmbeddings(),
        persist_directory=str(DB_DIR),
        collection_name="pdf_v_db"
    )

    return vector_store

def get_related_context(vector_store: Chroma):
    llm = Ollama(model="llama2")
    retriever = vector_store.as_retriever()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that can answer the user's questions. Use provided context to answer the question as accurately as possible:\n\n{context}"),
        ("human", "{input}")
    ])

    chain_element = create_history_aware_retriever(llm, retriever, prompt)
    return chain_element

def get_context_aware_prompt(context_chain):
    llm = Ollama(model="llama2")

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that can answer the user's questions. Use provided context to answer the question as accurately as possible:\n\n{context}"),
        ("human", "{input}")
    ])

    docs_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(context_chain, docs_chain)
    return rag_chain

def get_response(user_query: str) -> str:
    context_chain = get_related_context(st.session_state.vector_store)
    rag_chain = get_context_aware_prompt(context_chain)

    res = rag_chain.invoke({
        "chat_history": st.session_state.chat_history,
        "input": user_query
    })
    return res["answer"]

def init_chat_interface():
    user_query = st.chat_input("Ask a question....")
    if user_query is not None and user_query != "":
        response = get_response(user_query)
        
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        st.session_state.chat_history.append(AIMessage(content=response))

    for message in st.session_state.chat_history:
        if isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.write(message.content)
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.write(message.content)

def main():
    init_ui()
    if st.session_state.vector_store is not None:
        init_chat_interface()

if __name__ == "__main__":
    main()