# loot.py

class Loot:
    def __init__(self, id, name, description, attributes):
        self.id = id
        self.name = name
        self.description = description
        self.attributes = attributes

    def __repr__(self):
        return f"Loot(id={self.id}, name={self.name}, description={self.description}, attributes={self.attributes})"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "attributes": self.attributes
        }