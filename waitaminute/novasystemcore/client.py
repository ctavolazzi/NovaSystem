import asyncio
import websockets
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test():
    uri = "ws://localhost:8080"  
    async with websockets.connect(uri) as websocket:
        logger.info(f"Connected to server at {uri}")
        await websocket.send("Hello from the client!")
        response = await websocket.recv()
        logger.info(f"Received from server: {response}")

if __name__ == "__main__":
    asyncio.run(test())
