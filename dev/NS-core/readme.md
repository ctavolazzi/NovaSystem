# NovaSystem LITE

A lightweight implementation of the NovaSystem framework for AI-powered chat interactions.

## Features

- Async FastAPI backend
- SQLite database with SQLAlchemy ORM
- OpenAI and Ollama LLM integration
- Session management
- Comprehensive logging
- Full test coverage

## Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/NovaSystem.git
cd NovaSystem/dev/NS-core
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=sqlite+aiosqlite:///./nova.db
OLLAMA_HOST=http://localhost:11434
DEBUG=False
LOG_LEVEL=INFO
```

5. Initialize the database:

```bash
alembic upgrade head
```

## Running the Application

Start the FastAPI server:

```bash
uvicorn nova.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `POST /chat/` - Create a new chat session
- `POST /chat/{session_id}/message` - Send a message in a session
- `GET /chat/{session_id}/history` - Get chat history
- `POST /chat/{session_id}/end` - End a chat session

## Running Tests

```bash
pytest --cov=nova --cov-report=term-missing
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[MIT License](LICENSE)
