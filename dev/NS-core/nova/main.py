from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.requests import Request
from typing import Dict, List, Optional, Union, AsyncGenerator
import os
import re
import json
from pydantic import BaseModel
import autogen
import logging
from openai import OpenAI
from dotenv import load_dotenv
import asyncio

# First set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Then load environment variables
env_path = '/Users/ctavolazzi/Code/NovaSystem/dev/NS-core/.env'
load_dotenv(env_path)
logger.info(f"Looking for .env file at: {env_path}")
logger.info(f"File exists: {os.path.exists(env_path)}")
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OpenAI API key not found in environment variables")
logger.info(f"OpenAI API Key loaded: {api_key is not None}")
logger.info(f"OpenAI API Key starts with: {api_key[:8] if api_key else 'None'}")
logger.info(f"OpenAI API Key length: {len(api_key) if api_key else 0}")

# Initialize OpenAI clients with explicit error handling
try:
    openai_client = OpenAI(
        api_key=api_key
    )
    logger.info("OpenAI client initialized successfully")
except Exception as e:
    logger.error(f"Error initializing OpenAI client: {str(e)}")

ollama_client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama'
)

def get_client_for_model(model_config: Dict[str, str]) -> OpenAI:
    """Get the appropriate client based on the model configuration"""
    if model_config['model'].startswith("gpt"):
        return openai_client
    else:
        return ollama_client

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

# AutoGen configuration
def get_llm_config(model_config: Dict[str, str]) -> Dict:
    """Get LLM configuration based on the model selection"""
    logger.info(f"Selected model: {model_config['model']}")

    if model_config['model'].startswith("gpt"):
        config_list = [{
            "model": "gpt-4",  # Use gpt-4 for OpenAI
            "api_key": api_key
        }]
        logger.info("Using OpenAI configuration")
        debug_config(config_list)
    else:
        config_list = [{
            "model": "llama3.2",
            "base_url": "http://localhost:11434/v1",
            "api_key": "ollama"
        }]
        logger.info("Using Ollama configuration")
        debug_config(config_list)

    return {
        "temperature": 0,
        "config_list": config_list,
        "timeout": 120,
        "cache_seed": 42
    }

class Agent(BaseModel):
    id: int
    name: str
    role: str
    instructions: str

class ChainRequest(BaseModel):
    systemPrompt: str
    agents: List[Agent]
    modelConfig: Dict[str, str]

class AgentResult(BaseModel):
    agentName: str
    thought: str
    output: str

class ChainResponse(BaseModel):
    results: Optional[List[AgentResult]] = []
    error: Optional[str] = None

class MessageRequest(BaseModel):
    messages: List[Dict[str, str]]
    model: str = "llama3.2"

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the chat interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(request: MessageRequest) -> Dict[str, str]:
    """Get a response from the selected model"""
    try:
        client = get_client_for_model({
            "model": request.model,
            "baseUrl": "http://localhost:11434/v1" if request.model == "llama3.2" else "/v1"
        })

        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=request.model,
            messages=request.messages,
            temperature=0
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def stream_agent_messages(groupchat, agents) -> AsyncGenerator[str, None]:
    """Stream agent messages as they come in"""
    processed_messages = set()

    while True:
        current_messages = groupchat.messages

        for message in current_messages:
            message_id = f"{message.get('name')}_{message.get('content')}"
            if message_id not in processed_messages:
                agent_name = message.get('name')
                content = message.get('content')

                original_name = agent_name
                for agent in agents:
                    if sanitize_name(agent.name) == agent_name:
                        original_name = agent.name
                        break

                if "Thought:" in content and "Output:" in content:
                    thought, output = content.split("Output:", 1)
                    thought = thought.replace("Thought:", "").strip()
                else:
                    thought = content
                    output = content

                result = AgentResult(
                    agentName=original_name,
                    thought=thought,
                    output=output
                )

                yield f"data: {json.dumps(result.dict())}\n\n"
                processed_messages.add(message_id)

        if not groupchat.messages or len(groupchat.messages) >= 50:
            break

        await asyncio.sleep(0.5)

@app.post("/execute-chain-stream")
async def execute_chain_stream(request: ChainRequest):
    """Execute the agent chain using AutoGen with streaming responses"""
    try:
        # Validate we have at least 2 agents
        if len(request.agents) < 2:
            raise ValueError("At least 2 agents are required for a group chat")

        # Get LLM configuration based on selected model
        llm_config = get_llm_config(request.modelConfig)

        # Create a user proxy agent for code execution
        user_proxy = autogen.UserProxyAgent(
            name=sanitize_name("user_proxy"),
            system_message="A human user who can help execute code and provide feedback.",
            code_execution_config={
                "last_n_messages": 3,
                "work_dir": os.path.join(os.path.dirname(__file__), "workspace"),
                "use_docker": False
            },
            human_input_mode="NEVER",
            llm_config=llm_config
        )

        # Create agents based on the request
        agents = []
        for agent_config in request.agents:
            assistant = autogen.AssistantAgent(
                name=sanitize_name(agent_config.name),
                system_message=f"{agent_config.instructions}\n\nYou are part of a multi-agent system. Work collaboratively with other agents to solve tasks. Format your responses with 'Thought:' for your reasoning and 'Output:' for your final response.",
                llm_config=llm_config
            )
            agents.append(assistant)

        # Create group chat with all agents
        groupchat = autogen.GroupChat(
            agents=agents,  # Don't include user_proxy in the group chat
            messages=[],
            max_round=12
        )

        # Create manager
        manager = autogen.GroupChatManager(
            groupchat=groupchat,
            llm_config=llm_config
        )

        # Start the chat in a background task
        async def start_chat():
            # Send the initial message to the first agent directly
            first_agent = agents[0]
            await first_agent.a_receive(
                message={"role": "user", "content": request.systemPrompt},
                sender=user_proxy,
                request_reply=True,
                silent=False
            )

        asyncio.create_task(start_chat())

        # Return streaming response
        return StreamingResponse(
            stream_agent_messages(groupchat, request.agents),
            media_type="text/event-stream"
        )

    except Exception as e:
        logger.error(f"Error in execute_chain_stream: {str(e)}")
        return StreamingResponse(
            iter([f"data: {json.dumps({'error': str(e)})}\n\n"]),
            media_type="text/event-stream"
        )

def sanitize_name(name: str) -> str:
    """Sanitize name to match OpenAI's pattern ^[a-zA-Z0-9_-]+$"""
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
    if not sanitized[0].isalpha():
        sanitized = 'agent_' + sanitized
    return sanitized

def debug_config(config_list):
    """Debug the configuration being used"""
    logger.info("Debug config:")
    logger.info(f"Config list: {json.dumps(config_list, indent=2)}")
    if config_list and isinstance(config_list, list):
        for cfg in config_list:
            logger.info(f"Model: {cfg.get('model')}")
            api_key = cfg.get('api_key', '')
            logger.info(f"API key starts with: {api_key[:8] if api_key else 'None'}")
