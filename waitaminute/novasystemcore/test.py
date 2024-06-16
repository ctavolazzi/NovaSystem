import asyncio
import websockets
from aiohttp import web
import aioconsole
import logging
import sys

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("websocket_test.txt"),
    ],
)

logger = logging.getLogger(__name__)
prompt_message = "Enter a message to send to the browser: "

# Simple HTML Page (embedded in Python)
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>WebSocket Test</title>
    <script>
        document.addEventListener('DOMContentLoaded', function () { // Wrap in DOMContentLoaded
            var websocket = new WebSocket("ws://localhost:8081");
            websocket.onmessage = function(event) {
                var message = event.data;
                document.getElementById("messages").innerHTML += message + "<br>";
            };

            // Modified event listener to use keydown instead of keyup
            document.getElementById("messageInput").addEventListener("keydown", function(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                    event.preventDefault();
                }
            });

            function sendMessage() {
                var messageInput = document.getElementById("messageInput");
                var message = messageInput.value;
                websocket.send("Browser: " + message);
                document.getElementById("messages").innerHTML += "Browser: " + message + "<br>";
                messageInput.value = '';
            }
        }); 
    </script>
</head>
<body>
    <h1>WebSocket Test</h1>
    <input type="text" id="messageInput" />
    <button onclick="sendMessage()">Send</button>
    <div id="messages"></div>
</body>
</html>
"""

async def send_from_console(websocket):
    while True:
        try:
            message = await aioconsole.ainput(prompt_message)  
            logger.info(f"Sending message to browser: Console: {message}")
            await websocket.send("Console: " + message)
        except websockets.exceptions.ConnectionClosed:
            logger.error("WebSocket connection closed. Exiting console sender...")
            break  # Exit loop on connection closed

async def receive_from_browser(websocket):
    async for message in websocket:
        logger.info(f"Received message from browser: {message}")
        # Clear the entire line, including the prompt (go all the way to the beginning)
        sys.stdout.write("\r\033[K") 
        sys.stdout.write(f"Browser: {message}")  # Print to console without newline
        sys.stdout.flush() # Ensure the message is displayed immediately
        # Reprint the prompt after the browser's message
        sys.stdout.write(f"\r{prompt_message}") 


async def handle_http_request(request):
    if request.path == "/":
        logger.info("Serving HTML page")
        return web.Response(text=html_content, content_type="text/html")
    else:
        logger.warning(f"404 Not Found: {request.path}")
        return web.Response(status=404)

async def handle_websocket(websocket, path):
    logger.info(f"WebSocket connection opened: {websocket.remote_address}")

    # Create tasks for sending and receiving concurrently
    sender_task = asyncio.create_task(send_from_console(websocket))
    receiver_task = asyncio.create_task(receive_from_browser(websocket))

    # Wait for either task to finish
    done, pending = await asyncio.wait(
        [sender_task, receiver_task], return_when=asyncio.FIRST_COMPLETED
    )

    # Cancel any remaining tasks
    for task in pending:
        task.cancel()



async def main():
    app = web.Application()
    app.router.add_get("/", handle_http_request)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "localhost", 8080)
    await site.start()

    async with websockets.serve(handle_websocket, "localhost", 8081):
        print("WebSocket server started on ws://localhost:8081")
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())
