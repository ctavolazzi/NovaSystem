from abc import ABC, abstractmethod
import threading

# Step 1: Dynamic Bot Factory Interface
class Factory(ABC):
    @abstractmethod
    def create_bot(self, bot_type):
        pass

    @abstractmethod
    def register_new_bot_type(self, bot_type, bot_creator):
        pass

# Step 2: Polymorphic Concrete Bot Factories
class BotFactory(Factory):
    def __init__(self):
        self.bot_creators = {}

    def create_bot(self, bot_type):
        return self.bot_creators[bot_type]()

    def register_new_bot_type(self, bot_type, bot_creator):
        self.bot_creators[bot_type] = bot_creator

# Step 3: Abstract Bot Interface
class AbstractBot(ABC):
    @abstractmethod
    def perform_task(self):
        pass

    @abstractmethod
    def learn_new_skill(self, skill):
        pass

# Step 4: Various AI Bots
class ChatBot(AbstractBot):
    def perform_task(self):
        return "ChatBot engaging in conversation."

    def learn_new_skill(self, skill):
        return f"ChatBot learning {skill}."

class DataAnalysisBot(AbstractBot):
    def perform_task(self):
        return "DataAnalysisBot analyzing data."

    def learn_new_skill(self, skill):
        return f"DataAnalysisBot learning {skill}."

# Step 5: Concurrency in Bots
class ConcurrentBot(AbstractBot):
    def __init__(self, bot):
        self.bot = bot
        self.lock = threading.Lock()

    def perform_task(self):
        with self.lock:
            return self.bot.perform_task()

    def learn_new_skill(self, skill):
        with self.lock:
            return self.bot.learn_new_skill(skill)

# Step 6: Client Code Demonstration
def client_code(factory: BotFactory):
    factory.register_new_bot_type("chat", ChatBot)
    factory.register_new_bot_type("data", DataAnalysisBot)

    chat_bot = factory.create_bot("chat")
    print(chat_bot.perform_task())

    # Dynamically registering a new bot type
    factory.register_new_bot_type("concurrent", lambda: ConcurrentBot(ChatBot()))
    concurrent_bot = factory.create_bot("concurrent")
    print(concurrent_bot.perform_task())

# Demonstration
if __name__ == "__main__":
    bot_factory = BotFactory()
    client_code(bot_factory)
