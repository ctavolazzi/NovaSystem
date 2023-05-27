import tkinter as tk
import random
from robot import Robot
from welcome_ascii_art import welcome_ascii_art_2

class Game:
    def __init__(self, master, total_size=10):
        self.welcome_ascii_art = welcome_ascii_art_2()
        self.master = master
        self.total_size = total_size
        self.user_pos = [total_size//2, total_size//2]
        self.grid = [[' ' for _ in range(total_size)] for _ in range(total_size)]
        self.paused = False

        robot_x_pos, robot_y_pos = self.user_pos
        while [robot_x_pos, robot_y_pos] == self.user_pos:
            robot_x_pos = random.randint(1, total_size-2)
            robot_y_pos = random.randint(1, total_size-2)

        self.robot = Robot('Robbie', 'A friendly robot', robot_x_pos, robot_y_pos, self)

        for i in range(total_size):
            self.grid[i][0] = self.grid[i][total_size-1] = '#'
            self.grid[0][i] = self.grid[total_size-1][i] = '#'

        self.grid[self.user_pos[0]][self.user_pos[1]] = '@'
        self.grid[self.robot.x_pos][self.robot.y_pos] = self.robot.ascii_art

        self.labels = [[tk.Label(master, width=2, borderwidth=1) for _ in range(total_size)] for _ in range(total_size)]
        for i in range(total_size):
            for j in range(total_size):
                self.labels[i][j].grid(row=i, column=j)

        self.update_view()

    def update_view(self):
        for i in range(self.total_size):
            for j in range(self.total_size):
                self.labels[i][j].config(text=self.grid[i][j])

    def unpause(self):
        self.paused = False

    def move(self, direction):
        if self.paused:
            return
        new_pos = self.user_pos.copy()
        if direction == 'w':  # Up
            new_pos[0] -= 1
        elif direction == 's':  # Down
            new_pos[0] += 1
        elif direction == 'a':  # Left
            new_pos[1] -= 1
        elif direction == 'd':  # Right
            new_pos[1] += 1

        if self.grid[new_pos[0]][new_pos[1]] == 'R':
            self.robot.open_chat_window()
            return

        self.grid[self.user_pos[0]][self.user_pos[1]] = ' '
        self.grid[new_pos[0]][new_pos[1]] = '@'
        self.user_pos = new_pos
        self.update_view()

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def quit(self):
        self.master.destroy()
