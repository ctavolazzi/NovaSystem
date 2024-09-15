import os
import logging
from abc import ABC, abstractmethod
import random
import string
from datetime import datetime
from queue import Queue
from threading import Thread
import time

class Task:
    def __init__(self, action, data=None):
        self.action = action
        self.data = data
        self.retry_count = 0

    def __str__(self):
        return f"Task(action={self.action}, data={self.data}, retry_count={self.retry_count})"

class Bot(ABC):
    MAX_RETRIES = 3

    def __init__(self, config, network):
        self.config = config
        self.name = config.get('name', self.generate_random_name())
        self.model = config.get('model', 'default_model')
        self.log_dir = self._setup_log_directory()
        self.logger = self._setup_logger(config.get('log_level', 'INFO'))
        self.logger.info(f"Bot '{self.name}' initialized with configuration.")
        self.task_queue = Queue()
        self.is_running = False
        self.worker_thread = None
        self.network = network
        self.network.register_bot(self.name, self)

    @staticmethod
    def generate_random_name(length=8):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def _setup_log_directory(self):
        base_log_dir = self.config.get('log_dir') or os.environ.get('NOVA_LOG_DIR')
        if not base_log_dir:
            raise ValueError("Log directory not specified. Set 'log_dir' in config or NOVA_LOG_DIR environment variable.")
        log_dir = os.path.join(base_log_dir, self.name)
        os.makedirs(log_dir, exist_ok=True)
        return log_dir

    def _setup_logger(self, log_level):
        logger = logging.getLogger(self.name)
        logger.setLevel(log_level)

        log_file = os.path.join(self.log_dir, f"{self.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        return logger

    def log_action(self, action, details=None):
        log_message = f"Action: {action}"
        if details:
            log_message += f" - Details: {details}"
        self.logger.info(log_message)

    def add_task(self, action, data=None):
        task = Task(action, data)
        self.task_queue.put(task)
        self.logger.info(f"Task added: {task}")

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.worker_thread = Thread(target=self._process_tasks)
            self.worker_thread.start()
            self.logger.info("Bot started processing tasks")

    def stop(self):
        if self.is_running:
            self.is_running = False
            self.worker_thread.join()
            self.logger.info("Bot stopped processing tasks")

    def _process_tasks(self):
        while self.is_running:
            try:
                self.process_messages()
                task = self.task_queue.get(timeout=1)
                try:
                    self.execute_task(task)
                except Exception as e:
                    self.handle_task_error(task, e)
                finally:
                    self.task_queue.task_done()
            except Queue.Empty:
                continue

    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def execute_task(self, task):
        pass

    @classmethod
    def create(cls, network, **kwargs):
        return cls(kwargs, network)

    def should_retry(self, task):
        task.retry_count += 1
        return task.retry_count <= self.MAX_RETRIES

    def handle_task_error(self, task, error):
        self.logger.error(f"Error processing task {task}: {str(error)}")
        if self.should_retry(task):
            self.add_task(task.action, task.data)
        else:
            self.log_action("Task failed", f"Task {task} failed after {self.MAX_RETRIES} retries: {str(error)}")

    def send_message_to_bot(self, to_bot, message):
        self.network.send_message(self.name, to_bot, message)
        self.log_action(f"Sent message to {to_bot}", message)

    def process_messages(self):
        messages = self.network.receive_messages(self.name)
        for from_bot, message in messages:
            self.log_action(f"Received message from {from_bot}", message)
            self.handle_message(from_bot, message)

    @abstractmethod
    def handle_message(self, from_bot, message):
        pass

    def shutdown(self):
        self.stop()
        self.task_queue.join()
        self.logger.info(f"Bot '{self.name}' has been shut down.")

class CustomBot(Bot):
    def execute(self):
        self.log_action("Starting execution")
        self.add_task("process_data", "sample data")
        self.add_task("generate_report")

    def execute_task(self, task):
        method_name = f"handle_{task.action}"
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            method(task.data)
        else:
            raise ValueError(f"Unknown task action: {task.action}")

    def handle_process_data(self, data):
        self.log_action("Processing data", data)
        time.sleep(1)

    def handle_generate_report(self, data):
        self.log_action("Generating report")
        time.sleep(1)

    def handle_message(self, from_bot, message):
        self.log_action(f"Handling message from {from_bot}", message)

def create_bot(bot_type, network, **kwargs):
    if bot_type == 'custom':
        return CustomBot.create(network, **kwargs)
    else:
        raise ValueError(f"Unknown bot type: {bot_type}")

if __name__ == '__main__':
    import unittest

    class BotNetwork:
        def __init__(self):
            self.bots = {}
            self.message_queues = {}

        def register_bot(self, bot_name, bot):
            self.bots[bot_name] = bot
            self.message_queues[bot_name] = Queue()

        def send_message(self, from_bot, to_bot, message):
            if to_bot in self.message_queues:
                self.message_queues[to_bot].put((from_bot, message))
            else:
                raise ValueError(f"Unknown bot: {to_bot}")

        def receive_messages(self, bot_name):
            if bot_name in self.message_queues:
                messages = []
                while not self.message_queues[bot_name].empty():
                    messages.append(self.message_queues[bot_name].get())
                return messages
            else:
                raise ValueError(f"Unknown bot: {bot_name}")

    network = BotNetwork()
    
    config1 = {'name': 'DataBot', 'model': 'gpt-3.5-turbo', 'log_dir': '/path/to/logs'}
    config2 = {'name': 'ReportBot', 'model': 'gpt-4', 'log_dir': '/path/to/logs'}
    
    data_bot = create_bot('custom', network, **config1)
    report_bot = create_bot('custom', network, **config2)

    data_bot.start()
    report_bot.start()

    data_bot.execute()
    data_bot.send_message_to_bot('ReportBot', "Data processing complete")

    time.sleep(10)

    data_bot.shutdown()
    report_bot.shutdown()

    unittest.main()