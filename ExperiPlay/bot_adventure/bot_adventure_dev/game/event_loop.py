# event_loop.py
class EventLoop:
    def __init__(self, environment):
        self.environment = environment

    def run(self):
        for bot in self.environment.bots:
            # For now, each bot simply says "Hello" on its turn
            print(bot.dialogue.say_hello())
