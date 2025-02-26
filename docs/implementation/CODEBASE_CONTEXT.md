# NovaSystem Codebase Context

## Project Overview
NovaSystem is a pioneering problem-solving framework that harnesses the power of multiple AI models working together. The project implements the "Nova Process," which utilizes a team of virtual experts to tackle complex problems. The current priority is developing a SvelteKit front end.

## Key Components

### 1. NovaSystem Core (Original Implementation)
- Located in `/NovaSystem/`
- Contains:
  - `main.py`: Web application using Flask with an OpenAI/Ollama chat interface
  - `core/`: Core functionality including bots, controllers, ports, hubs
  - `demo.py`: Demonstration script
  - `backend/`: Backend services
  - `toolbox/`: Utility tools and specialized components
    - `local-rag/`: Retrieval Augmented Generation system with langchain, chromadb, and pdfplumber

### 2. NS-bytesize
- Located in `/dev/NS-bytesize/`
- Lightweight, modular FastAPI implementation
- Features:
  - REST API for bot creation and chat interaction
  - FastAPI backend with static file serving
  - Hub-based architecture for bot management
  - Integrated testing framework with pytest
  - Required packages: aiohttp, openai, fastapi, uvicorn, etc.
- Recent development (December 2023):
  - Integration with Autogen and Ollama for creating AI agent workflows
  - Streaming functionality for real-time response display
  - Examples like `ollama_agent_stream.py` demonstrate advanced multi-agent conversations

### 3. NS-core
- Located in `/dev/NS-core/`
- Features:
  - Async FastAPI backend with uvicorn
  - SQLite database with SQLAlchemy ORM
  - OpenAI and Ollama LLM integration
  - Session management
  - Comprehensive logging
  - Full test coverage with pytest

### 4. NS-lite
- Located in `/dev/NS-lite/`
- Simplified implementation with multiple interface options
- Features files:
  - `app.py`: Flask-based implementation with streaming responses
  - `main.py`: Similar to app.py but with different approach
  - `gradio_app.py`: Gradio-based user interface
- Makes heavy use of the Ollama client for local LLM integration

### 5. MCP-Claude (Newest Development)
- Located in `/dev/mcp-claude/`
- Implements the Model Context Protocol (MCP) for Claude AI integration
- Features:
  - Weather service integration with OpenWeatherMap API
  - MCP server for providing resources and tools to Claude
  - Structured data exchange between the application and Claude AI
  - Support for both current weather and forecasts
  - Follows a modern, modular design
- Dependencies: httpx, python-dotenv, pydantic, starlette, uvicorn

## Testing Architecture
- Pytest-based testing framework
- Integration tests verify system component interactions
- Task-based processing model with queue management
- Progress tracking and reporting capabilities
- Asynchronous testing with pytest-asyncio

## Environment Requirements
- Python 3.10+
- Virtual environment in `venv/`
- Required environment variables:
  - `OPENAI_API_KEY`: For accessing OpenAI models
  - `DATABASE_URL`: SQLite connection string
  - `OLLAMA_HOST`: For local LLM hosting (typically http://localhost:11434)
  - `DEFAULT_MODEL`: Default LLM model (e.g., gpt-4)
  - `DEFAULT_TEMPERATURE`: Generation temperature
  - `OPENWEATHER_API_KEY`: For weather service integration

## Key Python Dependencies by Component

### Common Dependencies
- openai: OpenAI API client
- python-dotenv: Environment variable management
- httpx: Asynchronous HTTP client
- pytest: Testing framework

### NS-bytesize Dependencies
- aiohttp: Async HTTP client/server
- autogen: Autonomous agent framework
- fastapi: Web API framework
- uvicorn: ASGI server
- jinja2: Templating engine

### NS-core Dependencies
- fastapi: Web API framework
- uvicorn: ASGI server
- sqlalchemy: ORM for database
- aiosqlite: Async SQLite adapter
- pydantic: Data validation and settings

### NS-lite Dependencies
- flask: Web framework
- ollama: Local LLM integration
- asyncio: Asynchronous I/O
- markdown2: Markdown processing

### MCP-Claude Dependencies
- httpx: HTTP client
- pydantic: Data validation
- starlette: ASGI framework
- uvicorn: ASGI server
- mcp: Model Context Protocol library

### RAG (Retrieval Augmented Generation) Dependencies
- langchain: Framework for LLM applications
- chromadb: Vector database
- pdfplumber: PDF text extraction
- gradio: Web UI creation

## Front-end Development
- Current focus is on developing a SvelteKit front end
- PocketBase may be used for backend services
- Various frontend implementations exist in the different versions

## Development Workflow
- The project appears to have multiple implementations in different stages
- Development is active in the `dev/` directory, with multiple approaches being explored
- There's a focus on testing and validation (tests/ directory, coverage reports)
- Recent work shows a trend toward modular, independent services and protocols

## Current Status
- The project is under active development
- Multiple approaches are being explored in parallel
- Most recent work (December 2023) focuses on:
  1. Claude integration via MCP protocol
  2. Autogen integration for multi-agent conversations
  3. Streaming responses for better user experience
  4. Weather services as an external data source
  5. RAG capabilities for knowledge retrieval