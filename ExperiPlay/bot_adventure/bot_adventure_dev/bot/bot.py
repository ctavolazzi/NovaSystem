# bot.py
from .state import State
from .inventory import Inventory
from .dialogue import Dialogue

class Bot:
    def __init__(self, name, position):
        self.name = name
        self.position = position  # A tuple of (x, y, z)
        self.state = State()
        self.inventory = Inventory()
        self.dialogue = Dialogue()

    def move(self, direction):
        """Move the bot in the specified direction."""
        pass

    def attack(self, target_bot):
        """Attack another bot."""
        pass

    def defend(self):
        """Defend against an attack."""
        pass

    def talk(self, target_bot):
        """Initiate a dialogue with another bot."""
        pass
