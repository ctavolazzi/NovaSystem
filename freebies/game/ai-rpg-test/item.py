# item.py

class Item:
    def __init__(self, id, name, description, effect):
        self.id = id
        self.name = name
        self.description = description
        self.effect = effect

    def __repr__(self):
        return f"Item(id={self.id}, name={self.name}, description={self.description}, effect={self.effect})"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "effect": self.effect
        }