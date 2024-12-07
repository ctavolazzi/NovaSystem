from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from typing import Dict, List
import os
from pydantic import BaseModel

from nova.services.llm_service import LLMService

# Initialize FastAPI app
app = FastAPI(title="NovaSystem LITE")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
static_dir = os.path.join(os.path.dirname(__file__), "static")
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# Initialize LLM service
llm_service = LLMService()

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the chat interface"""
    return templates.TemplateResponse("index.html", {"request": request})

class MessageRequest(BaseModel):
    messages: List[Dict[str, str]]
    model: str = "gpt4o"  # Default to gpt4o

@app.post("/chat")
async def chat(request: MessageRequest) -> Dict[str, str]:
    """Get a response from the selected model"""
    response = await llm_service.get_completion(
        messages=request.messages,
        model=request.model
    )
    return {"response": response}