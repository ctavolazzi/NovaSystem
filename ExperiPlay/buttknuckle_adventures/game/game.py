class Game:
    def __init__(self, bots=[], items=[], environment=None):
        self.bots = bots
        self.items = items
        self.environment = environment
        self.attacker = self.bots[0] if self.bots else None
        self.defender = self.bots[1] if len(self.bots) > 1 else None

    def play(self):
        while self.bots and all(bot.hp > 0 for bot in self.bots):
            self.attacker.greet()
            damage = self.attacker.slap()
            if self.defender.dodge():
                print(f"{self.defender.name}: Ha, I dodged your slap!")
            elif self.defender.block():
                print(f"{self.defender.name}: I blocked your slap!")
            else:
                self.defender.hp -= damage
                print(f"{self.defender.name}: Ouch, I have {self.defender.hp} HP left!")

            # Switch attacker and defender for next round
            self.attacker, self.defender = self.defender, self.attacker

    def add_bot(self, bot):
        self.bots.append(bot)
        if len(self.bots) == 1:
            self.attacker = bot
        elif len(self.bots) == 2:
            self.defender = bot

    def add_item(self, item):
        self.items.append(item)

    def set_environment(self, environment):
        self.environment = environment

    def game_loop(self):
        while self.bots and all(bot.hp > 0 for bot in self.bots):
            print ("Game loop")
            for bot in self.bots:
                print(f"{bot.name}'s turn")
                bot.take_turn(self)
