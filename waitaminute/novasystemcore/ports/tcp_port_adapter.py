import socket
import json
import ssl
import logging
from collections import deque
from .port_interface import PortInterface
from .data_serializer import DataSerializer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename="port_log.txt",  # Log to a file
    filemode='a'  # Append to the log file
)

class TCPPortAdapter(PortInterface):
    """
    A concrete implementation of the PortInterface for TCP communication.

    Attributes:
        host (str): The hostname or IP address of the destination.
        port (int): The port number to connect to.
        socket (socket.socket): The TCP socket object.
        max_retries (int): Maximum number of connection retry attempts.
        retry_delay (float): Delay in seconds between retry attempts.
        tls_enabled (bool): Whether to enable TLS encryption.
        certfile (str): Path to the certificate file for TLS (if enabled).
        keyfile (str): Path to the private key file for TLS (if enabled).
        connected (threading.Event): Event to signal connection status.
        token_bucket (deque): A token bucket for rate limiting.
        token_refill_rate (float): Tokens added to the bucket per second.
        auth_token (str, optional): Authentication token for the bot.
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self.host = config["host"]
        self.port = config["port"]
        self.socket = None
        self.max_retries = config.get("max_retries", 3)
        self.retry_delay = config.get("retry_delay", 1.0)

        self.tls_enabled = config.get("tls", False)
        if self.tls_enabled:
            self.certfile = config["certfile"]
            self.keyfile = config["keyfile"]

        # Rate limiting
        self.token_bucket = deque(maxlen=config.get("token_bucket_capacity", 10))
        self.token_refill_rate = config.get("token_refill_rate", 1.0)

        # Authentication
        self.auth_token = config.get("auth_token", None)

        self.connected = threading.Event()

    def connect(self):
        retries = 0
        while retries < self.max_retries:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                if self.tls_enabled:
                    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
                    context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)
                    self.socket = context.wrap_socket(self.socket, server_hostname=self.host)

                self.socket.connect((self.host, self.port))

                if self.auth_token:
                    self.send_data(self.auth_token, None)
                    response = self.receive_data()
                    if response != "AUTH_SUCCESS":
                        raise AuthenticationError("Authentication failed")

                self.connected.set()
                logging.info("Connected to %s:%s", self.host, self.port)
                return

            except (socket.timeout, ConnectionRefusedError) as e:
                logging.warning("Connection attempt %d failed: %s", retries + 1, e)
                retries += 1
                time.sleep(self.retry_delay)

        raise ConnectionError(f"Could not connect to {self.host}:{self.port} after {self.max_retries} attempts")

    def disconnect(self):
        if self.socket:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass  # Socket might already be closed
            finally:
                self.socket.close()
                self.socket = None
                self.connected.clear()
                logging.info("Disconnected from %s:%s", self.host, self.port)

    def send_data(self, data, destination):
        if not self.connected.is_set():
            raise ConnectionError("Not connected")

        if not self.token_bucket:  # Check if token bucket is empty
            logging.warning("Rate limit exceeded for port %s", self.name)
            time.sleep(1 / self.token_refill_rate)  # Wait before sending
            return  # Skip sending this message

        self.token_bucket.popleft()

        formatted_data = self.serializer.serialize(data)

        # Send data with length prefix
        length_prefix = len(formatted_data).to_bytes(4, byteorder='big')
        try:
            self.socket.sendall(length_prefix + formatted_data.encode())
            logging.info("Sent message to %s: %s", destination, data)
        except OSError as e:
            logging.error("Error sending data: %s", e)

    def receive_data(self):
        if not self.connected.is_set():
            raise ConnectionError("Not connected")

        try:
            length_prefix = self.socket.recv(4)
            if not length_prefix:
                raise ConnectionError("Connection closed by peer")
            length = int.from_bytes(length_prefix, byteorder='big')

            data = b""
            while len(data) < length:
                packet = self.socket.recv(length - len(data))
                if not packet:
                    raise ConnectionError("Connection closed by peer")
                data += packet

            return self.serializer.deserialize(data.decode())
        except OSError as e:
            logging.error("Error receiving data: %s", e)
            return None

    def _is_destination_valid(self, destination):
        # Assuming you have a way to check valid destinations
        return destination in self.router.available_destinations
    
    def _format_data(self, data):
        # Assuming you have a way to format data for the specific protocol
        return data
