# Import necessary modules
from game import Game
from environments import Environment
from bots import Bot
from items import Item

# Create our environment instance
environment = Environment("Planet Country", "A barren wasteland, devoid of life.")

# Item details
item_name = 'Sword'
item_description = 'An ancient blade, gleaming with unknown power'
item_symbol = '⚔️'

# Create items
sword = Item(item_name, item_description, item_symbol)

# Bot details
cal_name = 'Californicus Knuckle'
cal_symbol = '🤖'
cal_backstory = 'Cal was once a cowboy on the deserted plains of Planet Country. He is a lone wanderer, constantly in search of adventure.'

gus_name = 'Agarnigus Butt'
gus_symbol = '🤖'
gus_backstory = 'Gus is an old friend, and sometimes adversary, of Cal. He was once a renowned botanist, but now he roams Planet Country with Cal, seeking new plant life in the barren world.'

# Create bots
cal = Bot(cal_name, cal_symbol, cal_backstory)
gus = Bot(gus_name, gus_symbol, gus_backstory)

# Add bots to game
# Create our game instance
game = Game([cal, gus])
# game.add_bot(cal)
# game.add_bot(gus)

# Start the game loop
game.game_loop()
