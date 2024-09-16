# character.py

from utils import ensure_game_directory
import json
import os

class Character:
    def __init__(self, id, name, description, attributes, level=1, experience=0):
        self.id = id
        self.name = name
        self.description = description
        self.attributes = attributes if attributes else self.default_attributes()
        self.level = level
        self.experience = experience
        self.skills = {}
        self.traits = {}
        self.inventory = []
        self.equipped_items = []

    def default_attributes(self):
        return {
            'strength': 0,
            'dexterity': 0,
            'intelligence': 0,
            'constitution': 0
        }

    def gain_experience(self, xp):
        self.experience += xp
        while self.experience >= self.xp_for_next_level():
            self.level_up()

    def xp_for_next_level(self):
        return 100 * self.level

    def level_up(self):
        self.level += 1
        self.experience -= self.xp_for_next_level()
        self.improve_attributes()
        self.unlock_new_skills()

    def improve_attributes(self):
        self.attributes['strength'] += 1  # Example attribute improvement

    def unlock_new_skills(self):
        pass

    def evolve_traits(self, choice):
        pass

    def equip_item(self, item):
        self.equipped_items.append(item)
        self.apply_item_effect(item)

    def apply_item_effect(self, item):
        if isinstance(item.effect, dict):
            for stat, value in item.effect.items():
                if stat in self.attributes:
                    self.attributes[stat] += value
                else:
                    self.attributes[stat] = value

    def unequip_item(self, item):
        if item in self.equipped_items:
            self.equipped_items.remove(item)
            self.remove_item_effect(item)

    def remove_item_effect(self, item):
        if isinstance(item.effect, dict):
            for stat, value in item.effect.items():
                if stat in self.attributes:
                    self.attributes[stat] -= value

    def save_to_file(self, game_id):
        data = self.__dict__.copy()
        data['attributes'] = self.attributes
        game_dir = ensure_game_directory(game_id, "characters")
        file_path = os.path.join(game_dir, f"character_{self.id}.json")
        with open(file_path, "w") as file:
            json.dump(data, file)

    @staticmethod
    def load_from_file(game_id, character_id):
        game_dir = ensure_game_directory(game_id, "characters")
        file_path = os.path.join(game_dir, f"character_{character_id}.json")
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                data = json.load(file)
                return Character(**data)
        return None

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "attributes": self.attributes
        }