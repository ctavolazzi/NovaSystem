import tkinter as tk
from robot import Robot

class Game:
    def __init__(self, master, total_size=10):
        self.total_size = total_size
        self.user_pos = [total_size//2, total_size//2]
        self.grid = [[' ' for _ in range(total_size)] for _ in range(total_size)]

        # Initialize walls (We're just creating a simple box for this example)
        for i in range(total_size):
            self.grid[i][0] = self.grid[i][total_size-1] = '#'
            self.grid[0][i] = self.grid[total_size-1][i] = '#'

        self.grid[self.user_pos[0]][self.user_pos[1]] = '@'

        # Initialize Tkinter grid
        self.labels = [[tk.Label(master, width=2, borderwidth=1) for _ in range(total_size)] for _ in range(total_size)]
        for i in range(total_size):
            for j in range(total_size):
                self.labels[i][j].grid(row=i, column=j)

        self.update_view()

    def update_view(self):
        for i in range(self.total_size):
            for j in range(self.total_size):
                self.labels[i][j].config(text=self.grid[i][j])

    def move(self, direction):
        new_pos = self.user_pos.copy()

        if direction == 'w':  # Up
            new_pos[0] -= 1
        elif direction == 's':  # Down
            new_pos[0] += 1
        elif direction == 'a':  # Left
            new_pos[1] -= 1
        elif direction == 'd':  # Right
            new_pos[1] += 1

        # Add wall collision check
        if self.grid[new_pos[0]][new_pos[1]] != '#':
            self.grid[self.user_pos[0]][self.user_pos[1]] = ' '  # Remove old position
            self.user_pos = new_pos
            self.grid[self.user_pos[0]][self.user_pos[1]] = '@'  # Update new position

        self.update_view()

def on_key_press(event, game):
    game.move(event.char)

root = tk.Tk()
game = Game(root)
root.bind('<Key>', lambda event: on_key_press(event, game))
root.mainloop()
