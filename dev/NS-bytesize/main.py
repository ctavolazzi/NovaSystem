from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4

from hubs.hub import NovaHub
from bots.bot import NovaBot

app = FastAPI(title="NovaSystem API")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (our frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """Redirect root to the static index.html"""
    return RedirectResponse(url="/static/index.html")

# Initialize hub
hub = NovaHub()
bots = {}

class Bot(BaseModel):
    id: str
    name: str

class BotCreate(BaseModel):
    name: str

class ChatMessage(BaseModel):
    sender_id: str
    receiver_id: str
    message: str

class ChatResponse(BaseModel):
    response: str

@app.get("/bots", response_model=List[Bot])
async def get_bots():
    """Get list of all bots"""
    return [Bot(id=id, name=bot.name) for id, bot in bots.items()]

@app.post("/bots", response_model=Bot)
async def create_bot(bot_data: BotCreate):
    """Create a new bot"""
    bot = NovaBot(hub, name=bot_data.name)
    bot_id = str(uuid4())
    await bot.initialize()
    bots[bot_id] = bot
    return Bot(id=bot_id, name=bot.name)

@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Send a message between bots"""
    if message.sender_id not in bots or message.receiver_id not in bots:
        raise HTTPException(status_code=404, detail="Bot not found")

    sender = bots[message.sender_id]
    receiver = bots[message.receiver_id]

    try:
        # Send message from sender to receiver
        await sender.a_send(message.message, receiver, request_reply=True)

        # Generate receiver's response
        response = await receiver.a_generate_reply(sender=sender)

        if not response:
            raise HTTPException(status_code=500, detail="Failed to generate response")

        return ChatResponse(response=str(response))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
