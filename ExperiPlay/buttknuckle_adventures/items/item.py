class Item:
    def __init__(self, name, description, symbol):
        self.name = name
        self.description = description
        self.symbol = symbol
        self.location = None

    def use(self, user):
        # Define what happens when the item is used by a bot (user)
        pass

    def pick_up(self, picker):
        # Define what happens when the item is picked up by a bot (picker)
        pass

    def drop(self, dropper):
        # Define what happens when the item is dropped by a bot (dropper)
        pass
