# Standard library
from typing import Dict, Optional, List

# Third party
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Local
from hubs.hub import NovaHub
from bots.bot import NovaBot
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="NovaSystem LITE")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
hub = NovaHub()
active_sessions: Dict[str, NovaBot] = {}

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    model: Optional[str] = "gpt-4o"

class ChatResponse(BaseModel):
    response: str
    session_id: str

class ChatHistory(BaseModel):
    messages: List[dict]
    session_id: str

async def get_bot(session_id: str) -> NovaBot:
    """Dependency to get bot instance"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return active_sessions[session_id]

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown"""
    logger.info("Shutting down application...")
    for session_id in list(active_sessions.keys()):
        await active_sessions[session_id].cleanup()
    await hub.cleanup()

@app.post("/chat/", response_model=ChatResponse)
async def create_chat():
    """Create a new chat session"""
    try:
        bot = NovaBot(hub)
        session_id = await bot.initialize()
        active_sessions[session_id] = bot
        logger.info(f"Created new chat session: {session_id}")
        return ChatResponse(response="Chat session created", session_id=session_id)
    except Exception as e:
        logger.error(f"Error creating chat session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create chat session")

@app.post("/chat/{session_id}/message", response_model=ChatResponse)
async def send_message(
    chat_message: ChatMessage,
    bot: NovaBot = Depends(get_bot)
):
    """Send a message in an existing chat session"""
    try:
        response = await bot.process_message(
            chat_message.message,
            model=chat_message.model
        )
        return ChatResponse(response=response, session_id=bot.session_id)
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process message")

@app.get("/chat/{session_id}/history", response_model=ChatHistory)
async def get_history(bot: NovaBot = Depends(get_bot)):
    """Get chat history for a session"""
    try:
        history = await bot.get_history()
        return ChatHistory(messages=history, session_id=bot.session_id)
    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch chat history")

@app.post("/chat/{session_id}/end")
async def end_chat(bot: NovaBot = Depends(get_bot)):
    """End a chat session"""
    try:
        session_id = bot.session_id
        await bot.cleanup()
        del active_sessions[session_id]
        logger.info(f"Ended chat session: {session_id}")
        return {"message": "Chat session ended"}
    except Exception as e:
        logger.error(f"Error ending chat session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to end chat session")

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NovaSystem LITE Chat</title>
        <style>
            body { max-width: 800px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif; }
            #chat-box { height: 400px; border: 1px solid #ccc; overflow-y: auto; padding: 10px; margin: 20px 0; }
            #message-input { width: 80%; padding: 5px; }
            button { padding: 5px 15px; }
        </style>
    </head>
    <body>
        <h1>NovaSystem LITE Chat</h1>
        <select id="model-select">
            <option value="gpt-4o" selected>GPT-4o</option>
            <option value="llama3.2">Llama 3.2</option>
        </select>
        <div id="chat-box"></div>
        <input type="text" id="message-input" placeholder="Type your message...">
        <button onclick="sendMessage()">Send</button>

        <script>
            let sessionId = null;

            async function createSession() {
                const response = await fetch('/chat/', { method: 'POST' });
                const data = await response.json();
                sessionId = data.session_id;
                appendMessage('System', 'Chat session created');
            }

            async function sendMessage() {
                if (!sessionId) await createSession();

                const input = document.getElementById('message-input');
                const model = document.getElementById('model-select').value;
                const message = input.value;
                if (!message) return;

                appendMessage('You', message);
                input.value = '';

                try {
                    const response = await fetch(`/chat/${sessionId}/message`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message, model })
                    });
                    if (!response.ok) {
                        const error = await response.json();
                        throw new Error(error.detail || 'Failed to get response');
                    }
                    const data = await response.json();
                    appendMessage('Assistant', data.response);
                } catch (error) {
                    appendMessage('System', 'Error: ' + error.message);
                }
            }

            function appendMessage(sender, message) {
                const chatBox = document.getElementById('chat-box');
                chatBox.innerHTML += `<p><strong>${sender}:</strong> ${message}</p>`;
                chatBox.scrollTop = chatBox.scrollHeight;
            }

            // Handle Enter key
            document.getElementById('message-input').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') sendMessage();
            });
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
