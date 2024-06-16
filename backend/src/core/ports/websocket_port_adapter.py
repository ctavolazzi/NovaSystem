import asyncio
import json
import websockets
from .port_interface import PortInterface
from .json_serializer import JSONSerializer
import logging
from collections import deque  # For implementing a simple token bucket algorithm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WebSocketPortAdapter(PortInterface):
    """
    A concrete implementation of the PortInterface for WebSocket communication.

    Attributes:
        uri (str): The WebSocket URI to connect to or listen on.
        websocket (websockets.WebSocketServerProtocol): The WebSocket server/client object.
        serializer (DataSerializer): The serializer to use for data formatting.
        is_server (bool): Indicates whether the port is acting as a server or a client.
        queue (asyncio.Queue): Queue to store incoming messages for processing.
        connected (asyncio.Event): Event to signal connection status.
        token_bucket (deque): A token bucket for rate limiting.
        token_refill_rate (float): Tokens added to the bucket per second.
        auth_token (str, optional): Authentication token for the bot.
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self.uri = config["uri"]
        self.websocket = None
        self.serializer = JSONSerializer()
        self.is_server = self.uri.startswith("wss://")
        self.queue = asyncio.Queue()
        self.connected = asyncio.Event()

        # Rate limiting
        self.token_bucket = deque(maxlen=config.get("token_bucket_capacity", 10))
        self.token_refill_rate = config.get("token_refill_rate", 1.0)
        
        # Authentication
        self.auth_token = config.get("auth_token", None)

    async def connect(self):
        """
        Establishes a WebSocket connection.

        If the URI starts with 'ws://', it acts as a client connecting to a server.
        If the URI starts with 'wss://', it acts as a server listening for incoming connections.
        """
        try:
            if self.is_server:
                async with websockets.serve(self.handle_connection, *self.uri.split("//")[1].split(":")):
                    self.connected.set()  # Signal successful connection
                    asyncio.create_task(self.refill_token_bucket())  # Start refilling tokens
                    await self.process_queue()
            else:
                async with websockets.connect(self.uri) as websocket:
                    if self.auth_token:  # Send auth token if provided
                        await websocket.send(self.auth_token)
                    self.websocket = websocket
                    self.connected.set()  # Signal successful connection
                    asyncio.create_task(self.refill_token_bucket())  # Start refilling tokens
                    await self.process_queue()
        except (OSError, websockets.exceptions.InvalidURI) as e:
            self.connected.clear()
            raise ConnectionError(f"Could not establish WebSocket connection: {e}") from e

    async def handle_connection(self, websocket, path):
        """
        Handles incoming WebSocket connections on the server side.
        """
        if self.auth_token:
            try:
                auth_message = await asyncio.wait_for(websocket.recv(), timeout=5)  # 5 second timeout for auth
                if auth_message != self.auth_token:
                    logging.warning("Invalid authentication token from %s", websocket.remote_address)
                    await websocket.close(code=1008, reason="Invalid authentication token")
                    return
            except asyncio.TimeoutError:
                logging.warning("Authentication timeout from %s", websocket.remote_address)
                await websocket.close(code=1008, reason="Authentication timeout")
                return

        self.websocket = websocket
        logging.info("WebSocket connection established with %s", websocket.remote_address)

        async for message in websocket:
            try:
                data = self.serializer.deserialize(message)
            except json.JSONDecodeError as e:
                logging.error("Error deserializing message: %s", e)
                continue  # Skip invalid messages

            await self.queue.put(data)  # Queue received data

    async def process_queue(self):
        """
        Continuously processes messages from the queue while connected, respecting rate limits.
        """
        while self.connected.is_set():
            data = await self.queue.get()
            
            if not self.token_bucket:  # Check rate limit
                logging.warning("Rate limit exceeded for port %s", self.name)
                await asyncio.sleep(1 / self.token_refill_rate)  # Wait before processing next message
                continue  # Skip processing this message
            
            self.token_bucket.popleft()  # Consume a token
            try:
                self.receive_data(data)
            except Exception as e:
                logging.error("Error processing received data: %s", e)

    async def refill_token_bucket(self):
        """
        Refills the token bucket at the specified rate.
        """
        while self.connected.is_set():
            if len(self.token_bucket) < self.token_bucket.maxlen:
                self.token_bucket.append(1)
            await asyncio.sleep(1 / self.token_refill_rate)  # Refill tokens at the specified rate
            
    async def send_data(self, data, destination=None):  # Destination is not used
        """
        Sends data to the connected WebSocket endpoint.

        Args:
            data: The data to be sent.
            destination: (Not used for WebSockets as they are bi-directional)
        """
        if not self.websocket:
            raise ConnectionError("Not connected")

        formatted_data = self.serializer.serialize(data)
        try:
            await asyncio.wait_for(self.websocket.send(formatted_data), timeout=5)  # 5 second timeout
        except asyncio.TimeoutError:
            raise TimeoutError("Message sending timed out")

    async def receive_data(self):
        """
        Receives data from the internal message queue.

        Returns:
            Any: The received data, or None if the connection is closed.
        """
        try:
            return await self.queue.get()
        except asyncio.CancelledError:
            # Handle queue cancellation if needed (e.g., when disconnecting)
            return None

   
    async def disconnect(self):
        """
        Closes the WebSocket connection gracefully.
        """
        self.connected.clear()  # Signal to stop processing the queue
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            logging.info("WebSocket connection closed for port %s", self.name)

    def get_status(self) -> str:
        """
        Gets the current connection status of the port.

        Returns:
            str: "CONNECTED" if connected, "DISCONNECTED" otherwise.
        """
        return "CONNECTED" if self.websocket else "DISCONNECTED"
