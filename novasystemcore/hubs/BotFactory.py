from hubs import Hub
from bots import Bot
from ports import Port

class BotFactory(Hub):
    def __init__(self, config):
        super().__init__(config)
        self.bot_types = {
            "worker": self.create_worker_bot,
            "supervisor": self.create_supervisor_bot,
            "manager": self.create_manager_bot
        }

    def create_bot(self, config):
        bot_type = config["type"]
        if bot_type not in self.bot_types:
            raise ValueError(f"Invalid bot type: {bot_type}")

        bot = Bot(config)
        self.bot_types[bot_type](bot)
        self.check_initialization(bot)
        bot.attach_port(Port({"name": f"{bot.name}_Port", "router": {"name": "DefaultRouter", "available_destinations": []}}))
        self.bots.append(bot)
        return bot

    def create_worker_bot(self, bot):
        bot.attach_method(self.worker_method1)
        bot.attach_method(self.worker_method2)

    def create_supervisor_bot(self, bot):
        bot.attach_method(self.supervisor_method1)
        bot.attach_method(self.supervisor_method2)

    def create_manager_bot(self, bot):
        bot.attach_method(self.manager_method1)
        bot.attach_method(self.manager_method2)

    def check_initialization(self, bot):
        if not bot.port:
            raise ValueError(f"Bot {bot.name} is missing a port")
        if not bot.methods:
            raise ValueError(f"Bot {bot.name} has no methods attached")

    def worker_method1(self, bot):
        print(f"Worker bot {bot.name} executing method 1")

    def worker_method2(self, bot):
        print(f"Worker bot {bot.name} executing method 2")

    def supervisor_method1(self, bot):
        print(f"Supervisor bot {bot.name} executing method 1")

    def supervisor_method2(self, bot):
        print(f"Supervisor bot {bot.name} executing method 2")

    def manager_method1(self, bot):
        print(f"Manager bot {bot.name} executing method 1")

    def manager_method2(self, bot):
        print(f"Manager bot {bot.name} executing method 2")