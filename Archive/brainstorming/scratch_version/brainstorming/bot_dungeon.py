import openai
import os
import tkinter as tk
from dotenv import load_dotenv
from game import Game
# from game_blocks import Game, Room, Item, Robot
from test import Test, log_exceptions as le # Decorator


# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

@le
def on_key_press(event, game):
    if not game.paused:
        new_pos = game.calculate_new_position(event.char)
        if game.is_valid_movement(new_pos):
            game.make_movement(new_pos)

print("Welcome to Bot Dungeon!")

@le
def exception_test():
    raise Exception("This is a test exception.")

# exception_test()


# Create a Tkinter window
root = tk.Tk()
game = Game(root) # Create a Game instance
game.start()
root.bind('<Key>', lambda event: on_key_press(event, game)) # Bind key press events to the on_key_press function
root.mainloop() # Start the Tkinter main loop
