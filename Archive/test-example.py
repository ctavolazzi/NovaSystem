# import asyncio
# import logging

# from novasystemcore.ports.port_factory import PortFactory

# def test_create_websocket_port(config):
#     config = config
#     port_factory = PortFactory()

#     port = port_factory.create_port(config)
#     if port:
#         logging.info("Port created successfully!")
#     else:
#         logging.error("Port creation failed")
 
# if __name__ == "__main__":
#     config = {"protocol": "websocket", "uri": "ws://localhost:8765", "port": 8765, "name": "test"}
#     test_create_websocket_port(config)


# import asyncio
# import logging
# from novasystemcore.ports.port_factory import PortFactory

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S,%03d",  # Custom timestamp format (milliseconds)
#     handlers=[logging.StreamHandler()] # Add the stream handler

# )

# async def main():
#     config = {
#         "protocol": "websocket",
#         "uri": "ws://localhost:8080",  # Connect to port 8080
#         "name": "test_websocket_connection"
#     }

#     port_factory = PortFactory()
#     port = port_factory.create_port(config)
    
#     if not port:
#         logging.error("Failed to create port")
#         return
    
#     logging.info(f"Port created successfully: {port.name}")

#     try:
#         await port.connect()
#         logging.info(f"Connected to {config['uri']}")

#         while True:  # Keep the connection open
#             data = await port.receive_data()
#             if data is not None:
#                 print(data)  # Display the received message on the screen
    
#     except Exception as e:  # Basic error handling
#         logging.error(f"Error during connection or receiving data: {e}")
#     finally:
#         await port.disconnect()
#         logging.info("Disconnected")

# if __name__ == "__main__":
#     asyncio.run(main())


# import asyncio
# import logging
# from novasystemcore.ports.port_factory import PortFactory

# # Create and configure your custom logger
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# stream_handler = logging.StreamHandler()
# logger.addHandler(stream_handler)

# async def main():
#     config = {
#         "protocol": "websocket",
#         "uri": "ws://localhost:8080",
#         "name": "test_websocket_connection"
#     }

#     port_factory = PortFactory()
#     port = port_factory.create_port(config)
    
#     if not port:
#         logger.error("Failed to create port")
#         return
    
#     logger.info(f"Port created successfully: {port.name}")

#     try:
#         await port.connect()
#         logger.info(f"Connected to {config['uri']}")

#         while True:  
#             data = await port.receive_data()
#             if data is not None:
#                 print(data)  # Display received message on the screen
    
#     except Exception as e:  
#         logger.error(f"Error during connection or receiving data: {e}")
#     finally:
#         await port.disconnect()
#         logger.info("Disconnected")

# if __name__ == "__main__":
#     asyncio.run(main())

# import asyncio
# import websockets
# import logging
# import sys
# from novasystemcore.ports.port_factory import PortFactory

# # Create and configure your custom logger
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

# # Create a StreamHandler for console output
# stream_handler = logging.StreamHandler(sys.stdout)  # Set stream to sys.stdout
# stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
# logger.addHandler(stream_handler)  # Add the stream handler

# # (Optional) If you want the log to save to a file too, you can keep this:
# file_handler = logging.FileHandler("test_example.log")  # Create a file handler
# file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))  
# logger.addHandler(file_handler)  # Add the file handler to the logger

# async def echo(websocket, path):
#     """Echoes messages back to the connected client."""
#     async for message in websocket:
#         await websocket.send(message)

# async def main():
#     # Create a WebSocket server on port 8080
#     print("Starting WebSocket server test...")
#     print("Does this one?")
#     async with websockets.serve(echo, "localhost", 8080) as server:
#         logging.info(f"WebSocket server started on ws://localhost:8080")

#     # Start the server and get the task to wait for it
#     config = {
#         "protocol": "websocket",
#         "uri": "ws://localhost:8080",
#         "name": "test_websocket_connection"
#     }

#     port_factory = PortFactory()
#     port = port_factory.create_port(config)

#     if not port:
#         logging.error("Failed to create port")
#         return
    
#     logging.info(f"Port created successfully: {port.name}")

#     try:
#         await port.connect()
#         logging.info(f"Connected to {config['uri']}")

#         while True:
#             data = await port.receive_data()
#             if data is not None:
#                 print(data) 
#     except Exception as e: 
#         logging.error(f"Error during connection or receiving data: {e}")
#     finally:
#         await port.disconnect()
#         # No need to cancel server_task as async with handles it
#         logging.info("Disconnected")

# if __name__ == "__main__":
#     asyncio.run(main())


# import asyncio
# import websockets
# import logging
# import sys
# from novasystemcore.ports.port_factory import PortFactory

# # Create and configure your custom logger
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

# # Create a StreamHandler for console output
# stream_handler = logging.StreamHandler(sys.stdout)
# stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
# logger.addHandler(stream_handler)

# # (Optional) If you want the log to save to a file too, you can keep this:
# file_handler = logging.FileHandler("test_example.log")
# file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
# logger.addHandler(file_handler)

# async def echo(websocket, path):
#     """Echoes messages back to the connected client."""
#     async for message in websocket:
#         await websocket.send(message)

# logging.info("This should work.")

# async def main():
#     # Create a WebSocket server on port 8080
#     print("Starting WebSocket server test...") #Keep this to have instant feedback in the terminal
#     logging.info("Does this fucking work or not?") #Log this so it appears in the logs
#     async with websockets.serve(echo, "localhost", 8080) as server:
#         logging.info(f"WebSocket server started on ws://localhost:8080") #Log this after the async server is set up

#         # ... rest of the code (PortFactory, connection, etc.)
#         # Ensure logging.info statements are used for messages you want in the logs
#         config = {
#             "protocol": "websocket",
#             "uri": "ws://localhost:8080",
#             "name": "test_websocket_connection"
#         }

#         port_factory = PortFactory()
#         port = port_factory.create_port(config)
#         if not port:
#             logging.error("Failed to create port")
#             return
        
#         logging.info(f"Port created successfully: {port.name}")

#         try:
#             await port.connect()
#             logging.info(f"Connected to {config['uri']}")
#             while True:
#                 data = await port.receive_data()
#                 if data is not None:
#                     logging.info(f"Received data: {data}")  # Log received data instead of printing
#         except Exception as e:
#             logging.error(f"Error during connection or receiving data: {e}")
#         finally:
#             await port.disconnect()
#             logging.info("Disconnected")

# if __name__ == "__main__":
#     asyncio.run(main())

# import logging

# # Create a logger object.
# logger = logging.getLogger(__name__)

# # Set the logging level.
# logger.setLevel(logging.DEBUG)

# # Create a handler to print to the terminal.
# stream_handler = logging.StreamHandler()

# # Add the handler to the logger.
# logger.addHandler(stream_handler)

# # Create a handler to print to a file.
# file_handler = logging.FileHandler('my_log.txt')

# # Add the handler to the logger.
# logger.addHandler(file_handler)

# # # Log a message.
# # logger.info('This is a message.')
# # logger.info("This should work.")
# import asyncio
# import websockets
# import logging
# import sys
# from novasystemcore.ports.port_factory import PortFactory

# # Create and configure your custom logger
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

# # Create a StreamHandler for console output
# stream_handler = logging.StreamHandler(sys.stdout)
# stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
# logger.addHandler(stream_handler)

# # Create a handler to print to a file.
# file_handler = logging.FileHandler('my_log.txt')
# file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
# logger.addHandler(file_handler)

# async def echo(websocket, path):
#     """Echoes messages back to the connected client."""
#     async for message in websocket:
#         await websocket.send(message)


# async def main():
#     logger.info('This is a message.')  # Log before starting the server
#     logger.info("This should work.")

#     # Create a WebSocket server on port 8080
#     print("Starting WebSocket server test...") 

#     async with websockets.serve(echo, "localhost", 8080) as server:
#         logger.info(f"WebSocket server started on ws://localhost:8080")  # Log after the server starts

#         # ... (rest of your code for port factory, connection, etc.)
#         config = {
#             "protocol": "websocket",
#             "uri": "ws://localhost:8080",
#             "name": "test_websocket_connection"
#         }

#         port_factory = PortFactory()
#         port = port_factory.create_port(config)
#         if not port:
#             logger.error("Failed to create port")
#             return
        
#         logger.info(f"Port created successfully: {port.name}")

#         try:
#             await port.connect()
#             logger.info(f"Connected to {config['uri']}")
#             while True:
#                 data = await port.receive_data()
#                 if data is not None:
#                     logger.info(f"Received data: {data}")  
#         except Exception as e:
#             logger.error(f"Error during connection or receiving data: {e}")
#         finally:
#             await port.disconnect()
#             logger.info("Disconnected")

# if __name__ == "__main__":
#     asyncio.run(main())


# import asyncio
# import websockets
# import logging
# import sys

# # Logging configuration 
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# stream_handler = logging.StreamHandler(sys.stdout)
# stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
# logger.addHandler(stream_handler)
# file_handler = logging.FileHandler('my_log.txt')
# file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
# logger.addHandler(file_handler)

# logger.info('This is a message.')
# logger.info("This should work.")
# logger.info("Let's see if it will print.")
# print("Starting WebSocket server test...")

# async def echo(websocket, path):
#     async for message in websocket:
#         await websocket.send(message)

# async def run_client(uri):
#     from novasystemcore.ports.port_factory import PortFactory
#     config = {
#         "protocol": "websocket",
#         "uri": uri,
#         "name": "test_websocket_connection"
#     }

#     port_factory = PortFactory()
#     port = port_factory.create_port(config)

#     if not port:
#         logger.error("Failed to create port")
#         return

#     logger.info(f"Port created successfully: {port.name}")

#     try:
#         await port.connect()
#         logger.info(f"Connected to {config['uri']}")
#         while True:
#             data = await port.receive_data()
#             if data is not None:
#                 logger.info(f"Received data: {data}")
#     except Exception as e:
#         logger.error(f"Error during connection or receiving data: {e}")
#     finally:
#         await port.disconnect()
#         logger.info("Disconnected")

# async def main():
#     async with websockets.serve(echo, 'localhost', 8080) as server:  
#         logging.info(f"WebSocket server started on ws://localhost:8080")  

#         await asyncio.sleep(1)  # Give the server a moment to start

#         client_task = asyncio.create_task(run_client("ws://localhost:8080"))

#         # You don't need the server_task anymore
#         await client_task

#     logger.info("Shutting down")

# if __name__ == "__main__":
#     asyncio.run(main())



# import asyncio
# import websockets
# import logging
# import sys
# import json

# # Logging configuration 
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# stream_handler = logging.StreamHandler(sys.stdout)
# stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
# logger.addHandler(stream_handler)
# file_handler = logging.FileHandler('my_log.txt')
# file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
# logger.addHandler(file_handler)

# import asyncio
# import websockets
# import logging

# # Logging setup
# logging.basicConfig(level=logging.INFO)  
# logger = logging.getLogger(__name__)

# # WebSocket server handler
# async def handler(websocket, path):
#     try:
#         logger.info(f"Client connected at path: {path}")
#         async for message in websocket:
#             logger.info(f"Received message: {message}")
#             response = f"Server received: {message}"
#             await websocket.send(response)
#     except websockets.ConnectionClosed:
#         logger.info("Connection closed")

# async def main():
#     start_server = websockets.serve(handler, "localhost", 8080)
#     logger.info("WebSocket server started on ws://localhost:8080")
#     await start_server
#     await asyncio.Future()  # Keep the server running

# if __name__ == "__main__":
#     asyncio.run(main())


# import asyncio
# import websockets
# import logging
# import sys

# # Logging Configuration (Combined)
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
#     handlers=[
#         logging.StreamHandler(sys.stdout),  # Log to console
#         logging.FileHandler('combined_log.txt')  # Log to file
#     ]
# )
# logger = logging.getLogger(__name__)

# # WebSocket Echo Server
# async def echo(websocket, path):
#     try:
#         logger.info(f"Client connected at path: {path}")
#         async for message in websocket:
#             logger.info(f"Received message: {message}")
#             response = f"Server received: {message}"
#             await websocket.send(response)
#     except websockets.ConnectionClosed:
#         logger.info("Connection closed")

# # WebSocket Client 
# async def run_client(uri):
#     try:
#         async with websockets.connect(uri) as websocket:
#             logging.info(f"Client connected to {uri}")
#             while True:  # Continuously send messages
#                 await asyncio.sleep(2) 
#                 await websocket.send("Hello from the client!")
#     except websockets.ConnectionClosed:
#         logging.info("Client connection closed")

# # Main Function
# async def main():
#     logger.info("Starting WebSocket server and client...")

#     # Start the server
#     start_server = websockets.serve(echo, "localhost", 8080)

#     # Run server and client concurrently
#     await asyncio.gather(
#         start_server,  # Start server
#         run_client("ws://localhost:8080")  # Start client after a short delay
#     )
    
# if __name__ == "__main__":
#     asyncio.run(main())

# import asyncio
# import websockets
# import logging
# import sys
# from threading import Thread
# import aioconsole

# # Logging Configuration 
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# stream_handler = logging.StreamHandler(sys.stdout)
# stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
# logger.addHandler(stream_handler)
# file_handler = logging.FileHandler('combined_log.txt')
# file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
# logger.addHandler(file_handler)

# # WebSocket Echo Server (Modified)
# connected_clients = set()  # Track connected clients

# async def echo(websocket):
#     connected_clients.add(websocket)
#     try:
#         logger.info("Client connected")
#         async for message in websocket:
#             logger.info(f"Received: {message}")
#             websockets.broadcast(connected_clients, message)  # Broadcast to all clients
#     finally:
#         connected_clients.remove(websocket)
#         logger.info("Client disconnected")

# # WebSocket Client (Modified)
# # async def run_client(uri):
# #     async with websockets.connect(uri) as websocket:
# #         logging.info(f"Client connected to {uri}")
# #         while True:
# #             message = input("Enter message to send: ")  # Get message from user
# #             await websocket.send(message)
# async def run_client(uri):
#     async with websockets.connect(uri) as websocket:
#         logging.info(f"Client connected to {uri}")
#         while True:
#             message = await aioconsole.ainput("Enter message to send: ")  # Asynchronous input
#             await websocket.send(message)

# # Main Function
# async def main():
#     logger.info("Starting WebSocket server and client...")

#     # Start the server and get it running
#     server = await websockets.serve(echo, 'localhost', 8080)
#     logging.info(f"WebSocket server started on ws://localhost:8080")
    
#     # Start the client in the background while the server is running
#     client_task = asyncio.create_task(run_client("ws://localhost:8080"))

#     # You could also use asyncio.gather here:
#     # await asyncio.gather(server, client_task)

#     try:
#         await asyncio.wait_for(client_task, None)  # Wait for the client to finish, no timeout
#     except asyncio.CancelledError:  
#         # Handle client cancellation if needed
#         pass

#     # Stop the server when the client is done
#     server.close()
#     await server.wait_closed()  # Wait for the server to close completely

#     logger.info("Shutting down")


# if __name__ == "__main__":
#     asyncio.run(main())

# import asyncio
# import websockets
# import logging
# import sys
# import aioconsole


# # Logging Configuration 
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# stream_handler = logging.StreamHandler(sys.stdout)
# stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
# logger.addHandler(stream_handler)
# file_handler = logging.FileHandler('combined_log.txt')
# file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
# logger.addHandler(file_handler)

# # Simple HTML Page (embedded in Python)
# html_content = """
# <!DOCTYPE html>
# <html>
# <head>
#     <title>WebSocket Test</title>
#     <script>
#         var websocket = new WebSocket("ws://localhost:8080/ws");
#         websocket.onmessage = function(event) {
#             var message = event.data;
#             document.getElementById("messages").innerHTML += message + "<br>";
#         };

#         function sendMessage() {
#             var messageInput = document.getElementById("messageInput");
#             var message = messageInput.value;
#             websocket.send(message);
#             messageInput.value = '';
#         }
#     </script>
# </head>
# <body>
#     <h1>WebSocket Test</h1>
#     <input type="text" id="messageInput" />
#     <button onclick="sendMessage()">Send</button>
#     <div id="messages"></div>
# </body>
# </html>
# """

# # WebSocket Echo Server
# async def echo(websocket):
#     try:
#         logger.info("Client connected")
#         async for message in websocket:
#             logger.info(f"Received: {message}")
#             await websocket.send(message)
#     except websockets.ConnectionClosed:
#         logger.info("Client disconnected")

# async def server_handler(websocket, path):
#     if path == "/":
#         await websocket.send(html_content)
#     elif path == "/ws":
#         try:
#             await echo(websocket)
#         except websockets.exceptions.ConnectionClosedError as e:
#             logger.error(f"WebSocket connection closed: {e}")
#     else:
#         logger.info("Invalid WebSocket request")

# async def run_client(uri):
#     async with websockets.connect(uri) as websocket:
#         logging.info(f"Client connected to {uri}")
#         while True:
#             message = await aioconsole.ainput("Enter message to send: ")
#             await websocket.send(message)


# # Main Function (Combined Server and Client)
# async def main():
#     logger.info("Starting WebSocket server and client...")
#     # Use asyncio.Event to manage the server's lifecycle
#     stop_event = asyncio.Event()

#     async def start_server():
#         async with websockets.serve(server_handler, 'localhost', 8080):
#             logging.info(f"WebSocket server started on ws://localhost:8080")  
#             await stop_event.wait()  # Keep the server running until the event is set
#             logger.info("WebSocket server stopped")


#     # Start the server and client tasks
#     server_task = asyncio.create_task(start_server())
#     client_task = asyncio.create_task(run_client("ws://localhost:8080/ws")) 

#     # Wait for the client task to finish, then stop the server
#     try:
#         await client_task
#     finally:
#         stop_event.set()  # Signal the server to stop
#         await server_task  # Wait for the server to shut down gracefully

#     logger.info("Shutting down")

# if __name__ == "__main__":
#     asyncio.run(main())


# import asyncio
# import websockets
# from aiohttp import web

# # Simple HTML Page (embedded in Python)
# html_content = """
# <!DOCTYPE html>
# <html>
# <head>
#     <title>WebSocket Test</title>
#     <script>
#         var websocket = new WebSocket("ws://localhost:8080");
#         websocket.onmessage = function(event) {
#             var message = event.data;
#             document.getElementById("messages").innerHTML += message + "<br>";
#         };

#         function sendMessage() {
#             var messageInput = document.getElementById("messageInput");
#             var message = messageInput.value;
#             websocket.send(message);
#             messageInput.value = '';
#         }
#     </script>
# </head>
# <body>
#     <h1>WebSocket Test</h1>
#     <input type="text" id="messageInput" />
#     <button onclick="sendMessage()">Send</button>
#     <div id="messages"></div>
# </body>
# </html>
# """

# # WebSocket Echo Server
# async def echo(websocket, path):
#     async for message in websocket:
#         await websocket.send(message)

# async def handle_http_request(request):
#     if request.path == "/":
#         return web.Response(text=html_content, content_type="text/html")
#     else:
#         return web.Response(status=404)

# async def main():
#     app = web.Application()
#     app.router.add_get("/", handle_http_request)
#     runner = web.AppRunner(app)
#     await runner.setup()
#     site = web.TCPSite(runner, "localhost", 8080)
#     await site.start()

#     async with websockets.serve(echo, "localhost", 8081):
#         print("WebSocket server started on ws://localhost:8080")
#         await asyncio.Future()  # Run forever

# if __name__ == "__main__":
#     asyncio.run(main())


# import asyncio
# import websockets
# from aiohttp import web
# import aioconsole

# # Simple HTML Page (embedded in Python)
# html_content = """
# <!DOCTYPE html>
# <html>
# <head>
#     <title>WebSocket Test</title>
#     <script>
#         var websocket = new WebSocket("ws://localhost:8081");
#         websocket.onmessage = function(event) {
#             var message = event.data;
#             document.getElementById("messages").innerHTML += message + "<br>";
#         };

#         function sendMessage() {
#             var messageInput = document.getElementById("messageInput");
#             var message = messageInput.value;
#             websocket.send(message);
#             messageInput.value = '';
#         }
#     </script>
# </head>
# <body>
#     <h1>WebSocket Test</h1>
#     <input type="text" id="messageInput" />
#     <button onclick="sendMessage()">Send</button>
#     <div id="messages"></div>
# </body>
# </html>
# """

# # WebSocket Echo Server
# async def echo(websocket, path):
#     async for message in websocket:
#         print(f"Received message from browser: {message}")
#         await websocket.send(message)

# async def send_console_message(websocket):
#     while True:
#         message = await aioconsole.ainput("Enter a message to send to the browser: ")
#         await websocket.send(message)

# async def handle_http_request(request):
#     if request.path == "/":
#         return web.Response(text=html_content, content_type="text/html")
#     else:
#         return web.Response(status=404)

# async def main():
#     app = web.Application()
#     app.router.add_get("/", handle_http_request)
#     runner = web.AppRunner(app)
#     await runner.setup()
#     site = web.TCPSite(runner, "localhost", 8080)
#     await site.start()

#     async with websockets.serve(echo, "localhost", 8081):
#         print("WebSocket server started on ws://localhost:8081")
#         async with websockets.connect("ws://localhost:8081") as websocket:
#             await send_console_message(websocket)

# if __name__ == "__main__":
#     asyncio.run(main())


# import asyncio
# import websockets
# from aiohttp import web
# import aioconsole

# # Simple HTML Page (embedded in Python)
# html_content = """
# <!DOCTYPE html>
# <html>
# <head>
#     <title>WebSocket Test</title>
#     <script>
#         var websocket = new WebSocket("ws://localhost:8081");
#         websocket.onmessage = function(event) {
#             var message = event.data;
#             document.getElementById("messages").innerHTML += message + "<br>";
#         };
#             function sendMessage() {
#             var messageInput = document.getElementById("messageInput");
#             var message = messageInput.value;
#             websocket.send("Browser: " + message);
#             document.getElementById("messages").innerHTML += "Browser: " + message + "<br>";
#             messageInput.value = '';
#         }
#     </script>
# </head>
# <body>
# <body>
#     <h1>WebSocket Test</h1>
#     <input type="text" id="messageInput" />
#     <button onclick="sendMessage()">Send</button>
#     <div id="messages"></div>
# </body>
# </html>
# """

# async def send_console_message(websocket):
#     while True:
#         try:
#             message = await aioconsole.ainput("Enter a message to send to the browser: ")
#             await websocket.send(message)
#         except websockets.exceptions.ConnectionClosed:
#             print("WebSocket connection closed. Reconnecting...")
#             await asyncio.sleep(1)
#             await websocket.connect("ws://localhost:8081")

# async def handle_http_request(request):
#     if request.path == "/":
#         return web.Response(text=html_content, content_type="text/html")
#     else:
#         return web.Response(status=404)

# async def main():
#     app = web.Application()
#     app.router.add_get("/", handle_http_request)
#     runner = web.AppRunner(app)
#     await runner.setup()
#     site = web.TCPSite(runner, "localhost", 8080)
#     await site.start()

#     async with websockets.serve(lambda websocket, path: send_console_message(websocket), "localhost", 8081):
#         print("WebSocket server started on ws://localhost:8081")
#         await asyncio.Future()  # Run forever

# if __name__ == "__main__":
#     asyncio.run(main())


## WORKING!!! ##
# import asyncio
# import websockets
# from aiohttp import web
# import aioconsole

# # Simple HTML Page (embedded in Python)
# html_content = """
# <!DOCTYPE html>
# <html>
# <head>
#     <title>WebSocket Test</title>
#     <script>
#         var websocket = new WebSocket("ws://localhost:8081");
#         websocket.onmessage = function(event) {
#             var message = event.data;
#             document.getElementById("messages").innerHTML += message + "<br>";
#         };

#         function sendMessage() {
#             var messageInput = document.getElementById("messageInput");
#             var message = messageInput.value;
#             websocket.send("Browser: " + message);
#             document.getElementById("messages").innerHTML += "Browser: " + message + "<br>";
#             messageInput.value = '';
#         }
#     </script>
# </head>
# <body>
#     <h1>WebSocket Test</h1>
#     <input type="text" id="messageInput" />
#     <button onclick="sendMessage()">Send</button>
#     <div id="messages"></div>
# </body>
# </html>
# """

# async def handle_websocket(websocket):
#     async for message in websocket:
#         if message.startswith("Browser: "):
#             print(message)
#         else:
#             await websocket.send(message)

# async def send_console_message(websocket):
#     while True:
#         try:
#             message = await aioconsole.ainput("Enter a message to send to the browser: ")
#             await websocket.send(message)
#         except websockets.exceptions.ConnectionClosed:
#             print("WebSocket connection closed. Reconnecting...")
#             await asyncio.sleep(1)
#             await websocket.connect("ws://localhost:8081")

# async def handle_http_request(request):
#     if request.path == "/":
#         return web.Response(text=html_content, content_type="text/html")
#     else:
#         return web.Response(status=404)

# async def main():
#     app = web.Application()
#     app.router.add_get("/", handle_http_request)
#     runner = web.AppRunner(app)
#     await runner.setup()
#     site = web.TCPSite(runner, "localhost", 8080)
#     await site.start()

#     async with websockets.serve(handle_websocket, "localhost", 8081):
#         print("WebSocket server started on ws://localhost:8081")
#         async with websockets.connect("ws://localhost:8081") as websocket:
#             await send_console_message(websocket)

# if __name__ == "__main__":
#     asyncio.run(main())
## WORKING!!! ##

# import asyncio
# import websockets
# from aiohttp import web
# import aioconsole
# import logging
# import sys

# # 1. Logging Setup
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s",
#     handlers=[
#         logging.StreamHandler(sys.stdout),  # Log to console
#         logging.FileHandler("combined_log.txt"),  # Log to file
#     ],
# )

# # Get the logger for this module
# logger = logging.getLogger(__name__)

# # Simple HTML Page (embedded in Python)
# html_content = """
# <!DOCTYPE html>
# <html>
# <head>
#     <title>WebSocket Test</title>
#     <script>
#         var websocket = new WebSocket("ws://localhost:8081");
#         websocket.onmessage = function(event) {
#             var message = event.data;
#             document.getElementById("messages").innerHTML += message + "<br>";
#         };

#         function sendMessage() {
#             var messageInput = document.getElementById("messageInput");
#             var message = messageInput.value;
#             websocket.send("Browser: " + message);
#             document.getElementById("messages").innerHTML += "Browser: " + message + "<br>";
#             messageInput.value = '';
#         }
#     </script>
# </head>
# <body>
#     <h1>WebSocket Test</h1>
#     <input type="text" id="messageInput" />
#     <button onclick="sendMessage()">Send</button>
#     <div id="messages"></div>
# </body>
# </html>
# """


# async def send_console_message(websocket):
#     while True:
#         try:
#             message = await aioconsole.ainput("Enter a message to send to the browser: ")
#             logger.info(f"Sending message to browser: {message}")
#             await websocket.send("Console: "+message)
#         except websockets.exceptions.ConnectionClosed:
#             logger.error("WebSocket connection closed. Reconnecting...")
#             await asyncio.sleep(1)
#             await websocket.connect("ws://localhost:8081")

# async def handle_http_request(request):
#     if request.path == "/":
#         logger.info("Serving HTML page")
#         return web.Response(text=html_content, content_type="text/html")
#     else:
#         logger.warning(f"404 Not Found: {request.path}")
#         return web.Response(status=404)

# async def main():
#     app = web.Application()
#     app.router.add_get("/", handle_http_request)
#     runner = web.AppRunner(app)
#     await runner.setup()
#     site = web.TCPSite(runner, "localhost", 8080)
#     await site.start()

#     async with websockets.serve(lambda websocket, path: send_console_message(websocket), "localhost", 8081):
#         print("WebSocket server started on ws://localhost:8081")
#         await asyncio.Future()  # Run forever

# if __name__ == "__main__":
#     asyncio.run(main())

# import asyncio
# import websockets
# from aiohttp import web
# import aioconsole
# import logging
# import sys

# # 1. Logging Setup
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s",
#     handlers=[
#         logging.StreamHandler(sys.stdout),  # Log to console
#         logging.FileHandler("combined_log.txt"),  # Log to file
#     ],
# )

# # Get the logger for this module
# logger = logging.getLogger(__name__)

# # Simple HTML Page (embedded in Python)
# html_content = """
# <!DOCTYPE html>
# <html>
# <head>
#     <title>WebSocket Test</title>
#     <script>
#         var websocket = new WebSocket("ws://localhost:8081");
#         websocket.onmessage = function(event) {
#             var message = event.data;
#             document.getElementById("messages").innerHTML += message + "<br>";
#         };

#         function sendMessage() {
#             var messageInput = document.getElementById("messageInput");
#             var message = messageInput.value;
#             websocket.send("Browser: " + message);
#             document.getElementById("messages").innerHTML += "Browser: " + message + "<br>";
#             messageInput.value = '';
#         }
#     </script>
# </head>
# <body>
#     <h1>WebSocket Test</h1>
#     <input type="text" id="messageInput" />
#     <button onclick="sendMessage()">Send</button>
#     <div id="messages"></div>
# </body>
# </html>
# """


# async def send_console_message(websocket):
#     while True:
#         try:
#             message = await aioconsole.ainput("Enter a message to send to the browser: ")
#             logger.info(f"Sending message to browser: {message}")
#             await websocket.send("Console: "+message)
#         except websockets.exceptions.ConnectionClosed:
#             logger.error("WebSocket connection closed. Reconnecting...")
#             await asyncio.sleep(1)
#             await websocket.connect("ws://localhost:8081")


# async def handle_http_request(request):
#     if request.path == "/":
#         logger.info("Serving HTML page")
#         return web.Response(text=html_content, content_type="text/html")
#     else:
#         logger.warning(f"404 Not Found: {request.path}")
#         return web.Response(status=404)


# async def main():
#     app = web.Application()
#     app.router.add_get("/", handle_http_request)
#     runner = web.AppRunner(app)
#     await runner.setup()
#     site = web.TCPSite(runner, "localhost", 8080)
#     await site.start()

#     async def handle_websocket(websocket, path):
#         logger.info(f"WebSocket connection opened: {websocket.remote_address}")
#         await send_console_message(websocket)
#         try:
#             async for message in websocket:
#                 logger.info(f"Received message from browser: {message}")
#                 print(f"\nBrowser: {message}")  # Print to the terminal
#         except websockets.exceptions.ConnectionClosed:
#             logger.info(f"WebSocket connection closed: {websocket.remote_address}")

#     async with websockets.serve(handle_websocket, "localhost", 8081):  
#         print("WebSocket server started on ws://localhost:8081")
#         await asyncio.Future()  # Run forever


# if __name__ == "__main__":
#     asyncio.run(main())


# import asyncio
# import websockets
# from aiohttp import web
# import aioconsole
# import logging
# import sys

# # 1. Logging Setup (no changes)
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s",
#     handlers=[
#         logging.StreamHandler(sys.stdout),  # Log to console
#         logging.FileHandler("combined_log.txt"),  # Log to file
#     ],
# )

# logger = logging.getLogger(__name__)

# # Simple HTML Page (embedded in Python)
# html_content = """
# <!DOCTYPE html>
# <html>
# <head>
#     <title>WebSocket Test</title>
#     <script>
#         var websocket = new WebSocket("ws://localhost:8081");
#         websocket.onmessage = function(event) {
#             var message = event.data;
#             document.getElementById("messages").innerHTML += message + "<br>";
#         };

#         function sendMessage() {
#             var messageInput = document.getElementById("messageInput");
#             var message = messageInput.value;
#             websocket.send("Browser: " + message);
#             document.getElementById("messages").innerHTML += "Browser: " + message + "<br>";
#             messageInput.value = '';
#         }
#     </script>
# </head>
# <body>
#     <h1>WebSocket Test</h1>
#     <input type="text" id="messageInput" />
#     <button onclick="sendMessage()">Send</button>
#     <div id="messages"></div>
# </body>
# </html>
# """


# async def handle_websocket(websocket, path):
#     logger.info(f"WebSocket connection opened: {websocket.remote_address}")
    
#     # Function to send messages from the console
#     async def send_from_console(websocket):
#         while True:
#             try:
#                 message = await aioconsole.ainput("\nEnter a message to send to the browser: ")  
#                 logger.info(f"Sending message to browser: {message}")
#                 await websocket.send("Console: " + message)
#             except websockets.exceptions.ConnectionClosed:
#                 logger.error("WebSocket connection closed. Exiting console sender...")
#                 break  # Exit loop on connection closed

#     # Function to handle messages from the browser
#     async def receive_from_browser(websocket):
#         async for message in websocket:
#             logger.info(f"Received message from browser: {message}")
#             # Clear the current input line and reprint the prompt
#             print("\r", end="") 
#             print("Browser: ", message)  # Print browser message on the same line
#             await websocket.send(f"Server received: {message}")  # Echo back to browser

#             # Wait for a brief moment before printing the prompt again
#             await asyncio.sleep(0.1)  
#             print("\nEnter a message to send to the browser: ", end="")

#     # Create tasks for sending and receiving concurrently
#     sender_task = asyncio.create_task(send_from_console())
#     receiver_task = asyncio.create_task(receive_from_browser())

#     # Wait for either task to finish
#     done, pending = await asyncio.wait(
#         [sender_task, receiver_task], return_when=asyncio.FIRST_COMPLETED
#     )

# async def handle_websocket(websocket, path):
#     logger.info(f"WebSocket connection opened: {websocket.remote_address}")

#     # Create tasks for sending and receiving concurrently
#     sender_task = asyncio.create_task(send_from_console(websocket)) # Pass the websocket object here!
#     receiver_task = asyncio.create_task(receive_from_browser(websocket))

#     # Wait for either task to finish
#     done, pending = await asyncio.wait(
#         [sender_task, receiver_task], return_when=asyncio.FIRST_COMPLETED
#     )

#     # Cancel any remaining tasks
#     for task in pending:
#         task.cancel()

# async def handle_http_request(request):
#     if request.path == "/":
#         logger.info("Serving HTML page")
#         return web.Response(text=html_content, content_type="text/html")
#     else:
#         logger.warning(f"404 Not Found: {request.path}")
#         return web.Response(status=404)


# async def main():
#     app = web.Application()
#     app.router.add_get("/", handle_http_request)
#     runner = web.AppRunner(app)
#     await runner.setup()
#     site = web.TCPSite(runner, "localhost", 8080)
#     await site.start()

#     async with websockets.serve(handle_websocket, "localhost", 8081):
#         print("WebSocket server started on ws://localhost:8081")
#         await asyncio.Future()  # Run forever


# if __name__ == "__main__":
#     asyncio.run(main())


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
        logging.FileHandler("combined_log.txt"),
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
        var websocket = new WebSocket("ws://localhost:8081");
        websocket.onmessage = function(event) {
            var message = event.data;
            document.getElementById("messages").innerHTML += message + "<br>";
        };

        // Add event listener for Enter key press
        document.getElementById("messageInput").addEventListener("keyup", function(event) {
            if (event.key === 'Enter') { // Check if Enter key is pressed
                sendMessage(); // Call sendMessage function if Enter is pressed
            }
        });

        function sendMessage() {
            var messageInput = document.getElementById("messageInput");
            var message = messageInput.value;
            websocket.send("Browser: " + message);
            document.getElementById("messages").innerHTML += "Browser: " + message + "<br>";
            messageInput.value = '';
        }
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

# Function to send messages from the console
# async def send_from_console(websocket):
#     while True:
#         try:
#             message = await aioconsole.ainput("\nEnter a message to send to the browser: ") 
#             logger.info(f"Sending message to browser: {message}")
#             await websocket.send("Console: " + message)
#         except websockets.exceptions.ConnectionClosed:
#             logger.error("WebSocket connection closed. Exiting console sender...")
#             break  # Exit loop on connection closed

# # Function to handle messages from the browser
# async def receive_from_browser(websocket):
#     async for message in websocket:
#         logger.info(f"Received message from browser: {message}")
#         # Clear the current input line and reprint the prompt
#         print("\r", end="") 
#         print("Browser: ", message, end="")  # Print browser message on the same line
#         # await websocket.send(f"Server received: {message}")  # Echo back to browser

#         # Wait for a brief moment before printing the prompt again
#         await asyncio.sleep(0.1)  
#         print("\nEnter a message to send to the browser: ", end="")
async def send_from_console(websocket):
    while True:
        try:
            message = await aioconsole.ainput(prompt_message)  
            logger.info(f"Sending message to browser:\nConsole: {message}")
            await websocket.send("Console: " + message)
        except websockets.exceptions.ConnectionClosed:
            logger.error("WebSocket connection closed. Exiting console sender...")
            break  # Exit loop on connection closed

# async def receive_from_browser(websocket):
#     async for message in websocket:
#         # print('\n')
#         logger.info(f"Received message from browser:\n{message}")
#         # Clear the line and update the prompt
#         print(f"\r\033[KEnter a message to send to the browser: ")

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
