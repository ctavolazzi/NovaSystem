import tkinter as tk
import random
from typing import Any
from robot import Robot
from welcome_ascii_art import welcome_ascii_art_2
from level import Level
from test import log_exceptions as le # Decorator
from game_log import GameLog

gl = GameLog()

# Define the player, wall, and robot as classes
class Player:
    symbol = '@'

class Wall:
    symbol = '#'

class Game:
    def __init__(self, master, total_size=10):
        # Constants
        print("Welcome to Bot Dungeon!")
        gl.log("Welcome to Bot Dungeon!")
        self.master = master
        self.total_size = total_size
        self.grid = [[' ' for _ in range(total_size)] for _ in range(total_size)]
        self.label_ids = [[None for _ in range(total_size)] for _ in range(total_size)]
        self.paused = False
        self.messages = [{"role": "system", "content": "You are facilitating a text-based game of Bot Dungeon."}]
        self.is_streaming = False
        self.loading = False
        self.loading_message = "Loading"
        self.player = Player()
        self.player_position = [total_size//2, total_size//2]

        # GUI Elements
        self.master.geometry("800x600")
        # self.master.withdraw()
        self.canvas = tk.Canvas(self.master, width=800, height=600)
        self.canvas.pack(fill='both', expand=True)
        print("Loading...")

    def generate_element(self, element):
        valid_positions = [
            [i, j]
            for i in range(1, self.total_size - 1)
            for j in range(1, self.total_size - 1)
            if self.grid[i][j] != Wall.symbol and [i, j] != self.player_position
        ]
        element_position = random.choice(valid_positions)
        if isinstance(element, Robot):
            self.robot = element
            self.robot.x_pos, self.robot.y_pos = element_position
        self.grid[element_position[0]][element_position[1]] = element.symbol

    def generate_grid(self):
        for i in range(self.total_size):
            for j in range(self.total_size):
                if i == 0 or i == self.total_size - 1 or j == 0 or j == self.total_size - 1:
                    self.grid[i][j] = Wall.symbol
                elif [i, j] == self.player_position:
                    self.grid[i][j] = self.player.symbol
                elif [i, j] == [self.robot.x_pos, self.robot.y_pos]:
                    self.grid[i][j] = self.robot.symbol
                else:
                    self.grid[i][j] = ' '

    def calculate_new_position(self, direction):
        new_pos = self.player_position.copy()
        if direction == 'w':  # Up
            new_pos[0] -= 1
        elif direction == 's':  # Down
            new_pos[0] += 1
        elif direction == 'a':  # Left
            new_pos[1] -= 1
        elif direction == 'd':  # Right
            new_pos[1] += 1
        return new_pos

    def is_valid_movement(self, new_pos):
        return self.grid[new_pos[0]][new_pos[1]] != Wall.symbol

    def make_movement(self, new_pos):
        self.grid[self.player_position[0]][self.player_position[1]] = ' '
        self.grid[new_pos[0]][new_pos[1]] = self.player.symbol
        self.player_position = new_pos
        self.update_view()

    def update_view(self):
        self.canvas.delete('all')
        self.create_labels()

    def create_labels(self):
        for i in range(self.total_size):
            for j in range(self.total_size):
                label = tk.Label(self.canvas, width=2, borderwidth=1, text=self.grid[i][j])
                id_ = self.canvas.create_window(i*20, j*20, window=label)
                self.label_ids[i][j] = id_  # Store the canvas object ID

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def open_chat_window(self, welcome_message):
        self.chat_manager = ChatManager(self)
        self.chat_manager.create_chat_window()
        self.chat_manager.add_message('system', welcome_message)
        self.chat_manager.add_start_adventure_button()

    def show_welcome_screen(self):
        self.welcome_screen = WelcomeScreen(self)
        self.welcome_screen.show()

    def start_adventure(self):
        self.chat_manager.chat_window.destroy()
        self.master.deiconify()
        self.resume()  # it should be self.resume(), not self.game.resume()

    def update_view(self):
        for i in range(self.total_size):
            for j in range(self.total_size):
                if i == self.player.x_pos and j == self.player.y_pos:
                    self.labels[i][j].config(text=self.player.symbol)
                elif i == self.robot.x_pos and j == self.robot.y_pos:
                    self.labels[i][j].config(text=self.robot.symbol)
                else:
                    self.labels[i][j].config(text=self.grid[i][j])

    # No need for move function in Game class as it is handled by the player now

    def start_game(self):
        self.welcome_screen.destroy()
        if self.master.state() == 'withdrawn':
            self.master.deiconify()
        self.player = Player() # Initialize player
        self.generate_element(self.player) # Generate player on grid
        self.robot = Robot("Robot", "I'm a robot.", 2, 2, self) # Initialize robot
        self.generate_element(self.robot) # Generate robot on grid
        self.generate_grid() # Generate the game grid
        self.open_chat_window("Welcome to the adventure!")  # Open chat window when game starts

    def close_chat_window(self):
        self.chat_manager.close_chat_window()

    @le
    def throw_exception(self, exception):
        #this method alwyaas throws an exception for testing purposes
        raise exception

class ChatManager:
    def __init__(self, game):
        self.game = game
        self.chat_window = None
        self.chat_text_box = None
        self.messages = []
        self.create_chat_window()

    def create_chat_window(self):
        self.chat_window = tk.Toplevel(self.game.master)
        self.chat_window.title("Chat Window")
        self.chat_text_box = tk.Text(self.chat_window)
        self.chat_text_box.pack()

    def add_message(self, role, message):
        self.messages.append((role, message))

    def display_messages(self):
        for role, message in self.messages:
            if role == 'user':
                self.chat_text_box.insert(tk.END, f"{role}: {message}\n")
            else:
                self.stream_message(role, message)

    def stream_message(self, role, message, index=0):
        if index == 0:
            self.chat_text_box.insert(tk.END, f"{role}: ")
        if index < len(message):
            self.chat_text_box.insert(tk.END, message[index])
            self.chat_text_box.see(tk.END)
            self.chat_window.after(35, self.stream_message, role, message, index + 1)
        else:
            self.chat_text_box.insert(tk.END, "\n")

    def add_start_adventure_button(self):
        button = tk.Button(self.chat_window, text="Start adventure", command=self.game.start_adventure)
        button.pack()

    def close_chat_window(self):
        self.chat_window.destroy()
        if self.game.master.state() == 'withdrawn':
            self.game.master.deiconify()
        if self.game.paused:
            self.game.resume()

    # All other Chat related methods here.
    # ChatManager is a separate class because it's responsibility is to handle chats and streaming,
    # not directly related to the Game logic

class WelcomeScreen:
    def __init__(self, game):
        self.game = game
        self.chat_manager = None

    def show(self):
        gl.log("Showing welcome screen")
        self.welcome_window = tk.Toplevel(self.game.master)
        self.welcome_window.minsize(800, 600)
        self.welcome_window.geometry("800x600")
        self.welcome_window.title("Welcome to the game!")
        label = tk.Label(self.welcome_window, text=welcome_ascii_art_2, font=("Courier", 16))
        label.pack(pady=100)
        button = tk.Button(self.welcome_window, text="Start game", command=self.game.start_game)
        button.pack()

        # Create chat manager and chat window
        self.chat_manager = ChatManager(self.game)
        self.chat_manager.create_chat_window()
        self.chat_manager.add_message('system', "Welcome to the game chat!")
        self.chat_manager.add_start_adventure_button()

    def destroy(self):
        gl.log("Destroying welcome screen")
        self.chat_manager.close_chat_window()
        self.welcome_window.destroy()

if __name__ == "__main__":
    # Create a Tkinter window
    root = tk.Tk()

    # Create a Game instance
    game = Game(root)

    # Start the game
    game.show_welcome_screen()

    # Start the Tkinter main loop
    root.mainloop()