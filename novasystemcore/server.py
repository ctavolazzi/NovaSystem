import asyncio
import websockets
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)  
logger = logging.getLogger(__name__)

# WebSocket server handler
async def handler(websocket, path):
    try:
        logger.info(f"Client connected at path: {path}")
        async for message in websocket:
            logger.info(f"Received message: {message}")
            response = f"Server received: {message}"
            await websocket.send(response)
    except websockets.ConnectionClosed:
        logger.info("Connection closed")

async def main():
    start_server = websockets.serve(handler, "localhost", 8080)
    logger.info("WebSocket server started on ws://localhost:8080")
    await start_server
    await asyncio.Future()  # Keep the server running

if __name__ == "__main__":
    asyncio.run(main())
