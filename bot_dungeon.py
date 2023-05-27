import openai
import os
import tkinter as tk
from dotenv import load_dotenv
from game import Game

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

def on_key_press(event, game):
    if not game.paused:
        game.move(event.char)

root = tk.Tk()
game = Game(root)
root.bind('<Key>', lambda event: on_key_press(event, game))
root.mainloop()
