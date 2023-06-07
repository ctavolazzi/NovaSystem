# environment.py
from .terrain import Terrain
from .collision import check_collision

class Environment:
    def __init__(self, size_x, size_y, size_z):
        self.terrain = Terrain(size_x, size_y, size_z)
        self.bots = []

    def add_bot(self, bot):
        if not check_collision(self, bot.position):
            self.bots.append(bot)
        else:
            print(f"Couldn't add bot {bot.name} due to collision.")

    def remove_bot(self, bot):
        if bot in self.bots:
            self.bots.remove(bot)
