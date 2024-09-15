import os
import uuid
import random
import string
import logging
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Any
import asyncio
import openai

class Bot(ABC):
    """
    The Bot class represents a fundamental unit in a modular intelligence system.
    It contains a unique identifier, a randomly generated name, a port for communication,
    onboard and offboard memory, and methods for interaction.
    """

    def __init__(self, log_dir: Optional[str] = None):
        """
        Initialize the Bot instance with unique ID, random name, port, memory, and logger.

        :param log_dir: Optional directory for log files. Defaults to the current working directory.
        """
        # Unique identifier for the bot
        self.id: uuid.UUID = uuid.uuid4()

        # Randomly generated name
        self.name: str = self._generate_random_name()

        # Logging setup
        self.log_dir: str = log_dir or os.getcwd()
        self.logger: logging.Logger = self._setup_logger()
        self.log(f"Bot '{self.name}' with ID {self.id} initialized.")

        # Port for input/output with a unique identifier
        self.port: Port = Port(self)
        self.log(f"Port created with ID {self.port.port_id}.")

        # Onboard memory (volatile)
        self.onboard_memory: dict = {}

        # Offboard memory (persistent)
        self.offboard_memory_file: str = self._setup_offboard_memory()

        # OpenAI API Key
        self.api_key: str = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            self.log("OpenAI API key not found. Please set the 'OPENAI_API_KEY' environment variable.", level=logging.ERROR)
            raise ValueError("OpenAI API key not found.")
        openai.api_key = self.api_key

        # Default model parameters
        self.model: str = "text-davinci-003"
        self.max_tokens: int = 150
        self.temperature: float = 0.7

    @staticmethod
    def _generate_random_name(length: int = 8) -> str:
        """
        Generate a random name for the bot.

        :param length: Length of the generated name. Defaults to 8.
        :return: Randomly generated name.
        """
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def _setup_logger(self) -> logging.Logger:
        """
        Set up the logger to output to both console and file.

        :return: Configured logger.
        """
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)

        # Avoid adding handlers multiple times
        if not logger.handlers:
            # Create log directory if it doesn't exist
            os.makedirs(self.log_dir, exist_ok=True)

            # Log file handler
            log_file = os.path.join(self.log_dir, f"{self.name}.log")
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)

            # Console handler
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(console_formatter)

            # Add handlers to the logger
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)

        return logger

    def log(self, message: str, level: int = logging.INFO):
        """
        Log the message to both console and file.

        :param message: Message to log.
        :param level: Logging level. Defaults to logging.INFO.
        """
        self.logger.log(level, message)

    def say(self, data: str):
        """
        Output the provided data through the port and log the action.

        :param data: Data to send.
        """
        # Send data through the port
        self.port.send(data)
        self.log(f"Bot says through port {self.port.port_id}: {data}")

    def listen(self) -> Tuple[bool, Any]:
        """
        Receive input data through the port.

        :return: Tuple of success status and data or error message.
        """
        try:
            data = self.port.receive()
            self.log(f"Bot received data through port {self.port.port_id}: {data}")
            return True, data
        except Exception as e:
            self.log(f"Error while receiving data through port: {str(e)}", level=logging.ERROR)
            return False, str(e)

    def _setup_offboard_memory(self) -> str:
        """
        Set up the offboard memory storage.

        :return: Path to the offboard memory file.
        """
        memory_file = os.path.join(self.log_dir, f"{self.name}_memory.txt")
        # Ensure the file exists
        open(memory_file, 'a', encoding='utf-8').close()
        return memory_file

    def write_offboard_memory(self, data: str):
        """
        Write data to offboard memory.

        :param data: Data to write.
        """
        try:
            with open(self.offboard_memory_file, 'a', encoding='utf-8') as f:
                f.write(data + '\n')
            self.log("Wrote data to offboard memory.")
        except Exception as e:
            self.log(f"Error writing to offboard memory: {str(e)}", level=logging.ERROR)

    def read_offboard_memory(self) -> Optional[str]:
        """
        Read data from offboard memory.

        :return: Data read from offboard memory, or None if an error occurred.
        """
        try:
            with open(self.offboard_memory_file, 'r', encoding='utf-8') as f:
                data = f.read()
            self.log("Read data from offboard memory.")
            return data
        except Exception as e:
            self.log(f"Error reading from offboard memory: {str(e)}", level=logging.ERROR)
            return None

    async def generate_response(self, prompt: str) -> Optional[str]:
        """
        Generate a response from the OpenAI API based on the given prompt.
        All communication with the API is logged and occurs through the port.

        :param prompt: The prompt to send to the OpenAI API.
        :return: Generated response, or None if an error occurred.
        """
        # Sanitize prompt to prevent disallowed content
        if not await self._is_content_allowed(prompt):
            self.log("Prompt contains disallowed content.", level=logging.WARNING)
            return None

        self.log(f"Generating response for prompt: {prompt}")
        try:
            response = await openai.Completion.acreate(
                engine=self.model,
                prompt=prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            message = response.choices[0].text.strip()
            # Sanitize response
            if not await self._is_content_allowed(message):
                self.log("Generated response contains disallowed content.", level=logging.WARNING)
                return None
            self.log("Response generated successfully.")
            return message
        except openai.error.OpenAIError as e:
            self.log(f"Error generating response: {str(e)}", level=logging.ERROR)
            return None

    async def _is_content_allowed(self, content: str) -> bool:
        """
        Check if the content is allowed according to OpenAI's policies.

        :param content: Content to check.
        :return: True if content is allowed, False otherwise.
        """
        try:
            response = await openai.Moderation.acreate(input=content)
            results = response["results"][0]
            if results["flagged"]:
                self.log("Content flagged by OpenAI's moderation API.", level=logging.WARNING)
                return False
            return True
        except openai.error.OpenAIError as e:
            self.log(f"Error during content moderation: {str(e)}", level=logging.ERROR)
            # Default to not allowing the content if moderation fails
            return False

    @abstractmethod
    def base_action(self):
        """
        The base action method to be implemented by subclasses.
        """
        pass

class Port:
    """
    The Port class represents a communication interface for the bot.
    It has a unique identifier and methods for sending and receiving data.
    """

    def __init__(self, bot: Bot):
        """
        Initialize the Port with a reference to the bot and a unique identifier.

        :param bot: The bot instance to which this port belongs.
        """
        self.bot = bot
        self.port_id: uuid.UUID = uuid.uuid4()

    def send(self, data: str):
        """
        Simulate sending data through the port.

        :param data: Data to send.
        """
        # For demonstration, we'll log the data being sent.
        self.bot.log(f"Port {self.port_id} sending data: {data}")
        # In a real implementation, this method would handle actual data transmission.

    def receive(self) -> str:
        """
        Simulate receiving data through the port.

        :return: Received data.
        """
        # For demonstration, we'll simulate data reception.
        data = "Simulated input data"
        self.bot.log(f"Port {self.port_id} received data: {data}")
        return data

class ChatBot(Bot):
    """
    ChatBot is a subclass of Bot that implements the base_action method.
    It uses OpenAI's API to generate responses to input received through its port.
    """

    def base_action(self):
        """
        Implement the bot's primary behavior using AI capabilities.
        """
        # Run the main logic in an asynchronous context
        asyncio.run(self._main_loop())

    async def _main_loop(self):
        """
        Asynchronous main loop for handling input and generating responses via the port.
        """
        # Listen for input via the port
        success, data = self.listen()
        if success:
            # Generate a response using OpenAI API
            response = await self.generate_response(data)
            if response:
                # Send the response via the port
                self.say(response)
                # Optionally, write to offboard memory
                self.write_offboard_memory(f"User input: {data}")
                self.write_offboard_memory(f"Bot response: {response}")
            else:
                self.say("Sorry, I couldn't generate a response.")
        else:
            self.say("Failed to receive input.")

# Example usage
if __name__ == '__main__':
    try:
        bot = ChatBot(log_dir='logs')
        bot.base_action()
    except ValueError as e:
        print(e)
