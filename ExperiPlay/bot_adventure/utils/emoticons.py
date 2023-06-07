class GameEntity:
    def __init__(self, name, symbol, properties=None):
        self.name = name
        self.symbol = symbol
        self.properties = properties if properties else []

class Property:
    def __init__(self, name, value):
        self.name = name
        self.value = value

class Furniture(GameEntity):
    def __init__(self, name, symbol, properties=None):
        super().__init__(name, symbol, properties)
        self.properties.append(Property('type', 'furniture'))

    def use(self):
        # Implement the use function here
        pass

class Character(GameEntity):
    def __init__(self, name, symbol, properties=None, health=100, strength=10):
        super().__init__(name, symbol, properties)
        self.properties.append(Property('type', 'character'))
        self._health = health
        self._strength = strength

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, value):
        if value < 0:
            self._health = 0
        else:
            self._health = value

    @property
    def strength(self):
        return self._strength

    @strength.setter
    def strength(self, value):
        if value < 0:
            self._strength = 0
        else:
            self._strength = value

    def move(self, direction):
        # Implement the move function here
        pass

class PlayerCharacter(Character):
    def __init__(self, name, symbol, properties=None, health=100, strength=10):
        super().__init__(name, symbol, properties, health, strength)
        self.properties.append(Property('role', 'player'))

class NPC(Character):
    def __init__(self, name, symbol, properties=None, health=100, strength=10):
        super().__init__(name, symbol, properties, health, strength)
        self.properties.append(Property('role', 'npc'))

# The dictionary now stores instances of more specific subclasses
emoticon_dict = {
    'fireplace': Furniture('fireplace', '🔥', [Property('decoration', True), Property('warm', True), Property('light', True)]),
    'chair': Furniture('chair', '🪑', [Property('sitting', True), Property('wood', True), Property('seat', True)]),
    'bot': PlayerCharacter('bot', '🤖', [Property('role', 'player')]),
}
