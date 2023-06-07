# game_loop.py
from .event_loop import EventLoop

class GameLoop:
    def __init__(self, environment):
        self.environment = environment
        self.event_loop = EventLoop(environment)

    def run(self):
        while self.is_game_running():
            self.event_loop.run()

    def is_game_running(self):
        # For simplicity, the game continues as long as there are bots in the environment
        return len(self.environment.bots) > 0
