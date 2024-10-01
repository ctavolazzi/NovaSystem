import os
import uuid
import json
import logging
from datetime import datetime
import asyncio
from openai import OpenAI
from abc import ABC, abstractmethod

class Bot(ABC):
    def __init__(self, log_dir: str = './logs', report_directory: str = './reports'):
        self.id: str = str(uuid.uuid4())  # Ensure ID is a string
        self.name: str = self._generate_random_name()
        self.log_dir = log_dir
        self.report_directory = report_directory
        self.logger = self._setup_logger()
        self.offboard_memory_file = self._setup_offboard_memory()
        self.onboard_memory = {}  # Initialize onboard memory
        self.log(f"Bot '{self.name}' with ID {self.id} initialized.")
        self.port = Port(self)

    def base_action(self):
        pass

    def _generate_random_name(self, length: int = 8) -> str:
        return uuid.uuid4().hex[:length]

    def _setup_logger(self) -> logging.Logger:
        try:
            if not os.path.exists(self.log_dir):
                os.makedirs(self.log_dir, exist_ok=True)
            logger = logging.getLogger(self.name)
            logger.setLevel(logging.INFO)
            fh = logging.FileHandler(os.path.join(self.log_dir, f"{self.name}.log"))
            formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)
            logger.addHandler(fh)
            return logger
        except PermissionError as e:
            print(f"PermissionError during logger setup: {e}")
            raise

    def log(self, message: str, level=logging.INFO):
        self.logger.log(level, message)

    def say(self, message: str):
        if not isinstance(message, str):
            raise TypeError("Message must be a string.")
        self.port.send(message)
        return message

    def listen(self):
        try:
            data = self.port.receive()
            return True, data
        except Exception as e:
            self.log(f"Error receiving data: {e}", level=logging.ERROR)
            return False, None

    def _setup_offboard_memory(self) -> str:
        try:
            memory_dir = os.path.join(self.log_dir, 'memory')
            if not os.path.exists(memory_dir):
                os.makedirs(memory_dir, exist_ok=True)
            memory_file = os.path.join(memory_dir, f"{self.name}_memory.txt")
            with open(memory_file, 'w', encoding='utf-8') as f:
                f.write('')
            return memory_file
        except PermissionError as e:
            self.log(f"PermissionError during offboard memory setup: {e}", level=logging.ERROR)
            raise

    def write_offboard_memory(self, data: str):
        try:
            with open(self.offboard_memory_file, 'a', encoding='utf-8') as f:
                f.write(f"{data}\n")
            self.log("Wrote data to offboard memory.")
        except Exception as e:
            self.log(f"Error writing to offboard memory: {e}", level=logging.ERROR)

    def read_offboard_memory(self):
        try:
            with open(self.offboard_memory_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.log(f"Error reading from offboard memory: {e}", level=logging.ERROR)
            return None

    async def generate_report(self):
        report_content = f"Bot ID: {self.id}\nBot Name: {self.name}\n"
        print(report_content)
        os.makedirs(self.report_directory, exist_ok=True)
        report_file = os.path.join(self.report_directory, 'report.txt')
        with open(report_file, 'w') as f:
            f.write(report_content)

    def close(self):
        handlers = self.logger.handlers[:]
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)

class Port:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.port_id: str = str(uuid.uuid4())  # Ensure port_id is a string
        self.logger = bot.logger
        self.logger.info(f"Port created with ID {self.port_id}.")

    def send(self, data: str):
        if not isinstance(data, str):
            raise TypeError("Data must be a string.")
        self.logger.info(f"Sending data: {data}")

    def receive(self) -> str:
        data = "Simulated input data"
        self.logger.info(f"Received data: {data}")
        return data

class ChatBot(Bot):
    def __init__(self, log_dir: str = './logs', api_key: str = None, report_directory: str = './reports'):
        super().__init__(log_dir, report_directory)
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            self.logger.error("OpenAI API key not found. Please set the 'OPENAI_API_KEY' environment variable.")
            raise ValueError("OpenAI API key not found. Please set the 'OPENAI_API_KEY' environment variable.")
        self.client = OpenAI(api_key=self.api_key)
        self.running = False
        self.conversations = {}
        self.conversation_file = os.path.join(self.report_directory, 'conversations.json')
        self.load_conversations()

    def load_conversations(self):
        try:
            with open(self.conversation_file, 'r') as f:
                self.conversations = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.logger.info("No existing conversation file found. Starting fresh.")
            self.conversations = {}

    def save_conversations(self):
        try:
            with open(self.conversation_file, 'w') as f:
                json.dump(self.conversations, f, indent=2)
            self.logger.info("Conversations saved successfully.")
        except Exception as e:
            self.logger.error(f"Failed to save conversations: {e}")

    def save_interaction(self, conversation_id: str, role: str, content: str):
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        self.conversations[conversation_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.save_conversations()

    async def generate_response(self, prompt: str, conversation_id: str = None) -> str:
        if not isinstance(prompt, str) or not prompt.strip():
            self.logger.error("Invalid prompt provided to generate_response.")
            return "Invalid prompt"
        
        if conversation_id is None:
            conversation_id = str(uuid.uuid4())
        
        try:
            self.logger.info(f"Generating response for prompt: {prompt}")
            loop = asyncio.get_event_loop()
            stream = await loop.run_in_executor(None, lambda: self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                stream=True,
            ))
            
            response_content = ""
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    response_content += content
                    self.logger.debug(f"Received chunk: {content}")

            self.logger.info(f"Generated response: {response_content}")
            
            self.save_interaction(conversation_id, "user", prompt)
            self.save_interaction(conversation_id, "assistant", response_content)
            
            return f"Response to: {prompt}\n{response_content}"
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return f"Error: {str(e)}"

    async def _is_content_allowed(self, content: str) -> bool:
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: self.client.moderations.create(input=content))
            flagged = response.results[0].flagged
            self.logger.info(f"Content flagged: {flagged}")
            return not flagged
        except Exception as e:
            self.logger.error(f"Error during content moderation: {e}")
            return False

    def get_conversation(self, conversation_id: str) -> list:
        return self.conversations.get(conversation_id, [])

    def list_conversations(self) -> list:
        return list(self.conversations.keys())

    async def _main_loop(self):
        self.running = True
        while self.running:
            success, data = self.listen()
            if success:
                response = await self.generate_response(data)
                self.say(response)
                self.write_offboard_memory(response)
            await asyncio.sleep(0.1)

    def stop(self):
        self.running = False

    def base_action(self):
        asyncio.run(self._main_loop())

if __name__ == '__main__':
    try:
        bot = ChatBot(log_dir='logs')
        bot.base_action()
    except ValueError as e:
        print(e)
