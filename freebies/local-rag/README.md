# RAG Chatbot Application

This is a Retrieval-Augmented Generation (RAG) chatbot application using Langchain, Ollama, and Gradio.

## Features

- Uses Ollama for local language model inference
- Implements RAG for more accurate and contextual responses
- Uses Chroma as a vector store for efficient similarity search
- Provides a user-friendly chat interface with Gradio

## Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/rag-chatbot.git
   cd rag-chatbot
   ```

2. Run the setup script:
   ```
   python setup.py
   ```
   This will download necessary files, install dependencies, and set up Ollama.

3. Activate the virtual environment:
   - On Windows: `.\venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`

4. Run the application:
   ```
   python app.py
   ```

5. Open your web browser and go to `http://localhost:7860` to interact with the chatbot.

## Configuration

You can configure the application by editing the `.env` file. Available options include:

- `OLLAMA_MODEL`: The Ollama model to use (default: "llama2:chat")
- `OLLAMA_URL`: The URL of the Ollama server (default: "http://localhost:11434")
- `INITIAL_DB`: Whether to initialize a new vector database (default: False)
- `DEBUG`: Enable debug logging (default: False)

## Adding New Documents

To add a new document to the existing knowledge base:

1. Place the new document in the `data/` directory.
2. Run the following Python code:

```python
from data_loader import add_new_document
from vector_store import get_vector_store, add_documents_to_store

new_chunks = add_new_document('path/to/your/new/document.txt')
vector_store = get_vector_store()
add_documents_to_store(vector_store, new_chunks)
```

## Troubleshooting

If you encounter any issues, please check the application logs or file an issue on the GitHub repository.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.