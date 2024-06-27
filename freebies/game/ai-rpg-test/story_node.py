# story_node.py

from utils import ensure_game_directory
from character import Character
from item import Item
from loot import Loot
import json
import os

class StoryNode:
    def __init__(self, id, title, text, choices, characters, items, loot):
        self.id = id
        self.title = title
        self.text = text
        self.choices = choices
        self.characters = characters
        self.items = items
        self.loot = loot

    def save_to_file(self, game_id):
        data = {
            "id": self.id,
            "title": self.title,
            "text": self.text,
            "choices": self.choices,
            "characters": [char.__dict__ for char in self.characters],
            "items": [item.__dict__ for item in self.items],
            "loot": [loot.__dict__ for loot in self.loot]
        }
        game_dir = ensure_game_directory(game_id, "nodes")
        file_path = os.path.join(game_dir, f"node_{self.id}.json")
        with open(file_path, "w") as file:
            json.dump(data, file)

    @staticmethod
    def load_from_file(game_id, node_id):
        game_dir = ensure_game_directory(game_id, "nodes")
        file_path = os.path.join(game_dir, f"node_{node_id}.json")
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                data = json.load(file)
                characters = [Character(**char) for char in data["characters"]]
                items = [Item(**item) for item in data["items"]]
                loot = [Loot(**loot) for loot in data["loot"]]
                return StoryNode(data["id"], data["title"], data["text"], data["choices"], characters, items, loot)
        return None

    def __str__(self):
        return f"StoryNode(id={self.id}, title='{self.title}')"

    def __repr__(self):
        return self.__str__()

# Add this method to serialize the StoryNode for JSON
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "text": self.text,
            "choices": self.choices,
            "characters": [char.__dict__ for char in self.characters],
            "items": [item.__dict__ for item in self.items],
            "loot": [loot.__dict__ for loot in self.loot]
        }