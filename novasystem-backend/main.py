import os
import sys
from pathlib import Path

# Ensure project root is in path to find core_components
PROJECT_ROOT = Path(__file__).parent.parent # Assumes backend is one level down
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Attempt to import core components (will use dummy data if fails)
try:
    from core_components.hub import Hub
    from core_components.base_bot import BaseBot
    CORE_COMPONENTS_AVAILABLE = True
except ImportError:
    print("WARNING: core_components not found. Using dummy data for initial state.")
    CORE_COMPONENTS_AVAILABLE = False
    # Define dummy classes if needed, or just use dicts

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration (Load from .env or defaults)
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", 5002))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173") # Default Vite port
OLLAMA_HOST_URL = os.getenv("OLLAMA_HOST_URL", "http://localhost:11434") # Default Ollama

# --- FastAPI App --- #
app = FastAPI(title="NovaSystem Backend")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL], # Allow frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Socket.IO Server --- #
# Mount Socket.IO app
sio_server = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=[FRONTEND_URL]
)
sio_app = socketio.ASGIApp(
    socketio_server=sio_server,
    socketio_path='' # Explicitly set path relative to mount point
)
app.mount("/socket.io", sio_app) # Mount ASGI app on FastAPI

# --- Basic State (Will be expanded) --- #
# Define initial state with some dummy data
def get_initial_state():
    hub1_id = "hub-dummy-1"
    bot1_id = "bot-dummy-a"
    bot2_id = "bot-dummy-b"
    return {
        "systemStatus": "initializing",
        "hubs": {
            hub1_id: {
                "id": hub1_id,
                "name": "Alpha Hub (Dummy)",
                "botIds": [bot1_id, bot2_id] # List of bot IDs managed by this hub
            }
        },
        "bots": {
            bot1_id: {
                "id": bot1_id,
                "name": "Bot A (Dummy)",
                "status": "idle",
                "hubId": hub1_id
            },
            bot2_id: {
                "id": bot2_id,
                "name": "Bot B (Dummy)",
                "status": "idle",
                "hubId": hub1_id
            }
        }
    }

system_state = get_initial_state() # Initialize state

# --- Socket.IO Event Handlers --- #
@sio_server.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    # Send initial state to the newly connected client
    global system_state # Ensure we modify the global state
    await sio_server.emit('system_state', system_state, room=sid)
    # Update status after first connection (if needed)
    if system_state["systemStatus"] == "initializing":
         print("System moving to idle state.")
         system_state["systemStatus"] = "idle"
         # Broadcast the updated state to all clients
         await sio_server.emit('system_state', system_state)

@sio_server.event
def disconnect(sid):
    print(f"Client disconnected: {sid}")

# --- Basic REST Endpoint (Example) --- #
@app.get("/")
async def read_root():
    return {"message": "NovaSystem Backend is running"}

# --- Main --- #
if __name__ == "__main__":
    import uvicorn
    # Note: Uvicorn should run this file, e.g.: uvicorn main:app --reload --port 5002
    # This block might only be useful for direct debugging, not production run
    print(f"Starting backend on {BACKEND_HOST}:{BACKEND_PORT}")
    print(f"Allowing connections from {FRONTEND_URL}")
    print(f"Expecting Ollama at {OLLAMA_HOST_URL}")
    uvicorn.run(
        "main:app", # Reference the app instance in this file (assuming saved as main.py)
        host=BACKEND_HOST,
        port=BACKEND_PORT,
        reload=True # Enable auto-reload for development
    )