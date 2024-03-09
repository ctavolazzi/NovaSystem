import random
from room import Room

class Game:
    def __init__(self, master):
        self.master = master
        self.total_size = 10
        self.rooms = {}
        self.current_room = None
        self.previous_door_pos = None
        self.entry_door = None
        self.user_pos = None
        # Adding types of rooms and items
        self.room_types = ['normal', 'treasure', 'monster']
        self.items = ['sword', 'shield', 'potion']

        # Create the first room
        self.generate_new_room()

    def generate_new_room(self):
        # door_pos = [random.randint(0, self.total_size - 1), random.randint(0, self.total_size - 1)]
        door_pos = [0, 0]
        if self.previous_door_pos is not None:
            if self.previous_door_pos[0] == 0:  # top wall in previous room
                door_pos = [self.total_size - 1, self.previous_door_pos[1]]  # bottom wall in new room
            elif self.previous_door_pos[0] == self.total_size - 1:  # bottom wall in previous room
                door_pos = [0, self.previous_door_pos[1]]  # top wall in new room
            elif self.previous_door_pos[1] == 0:  # left wall in previous room
                door_pos = [self.previous_door_pos[0], self.total_size - 1]  # right wall in new room
            elif self.previous_door_pos[1] == self.total_size - 1:  # right wall in previous room
                door_pos = [self.previous_door_pos[0], 0]  # left wall in new room

        new_room = Room(self.total_size, door_pos)
        self.rooms[new_room.id] = new_room
        self.current_room = new_room
        self.entry_door = door_pos

        self.set_player_position()
        self.generate_door()

    def set_player_position(self):
        if self.entry_door[0] == 0:  # top wall
            self.user_pos = [self.entry_door[0] + 1, self.entry_door[1]]
        elif self.entry_door[0] == self.total_size - 1:  # bottom wall
            self.user_pos = [self.entry_door[0] - 1, self.entry_door[1]]
        elif self.entry_door[1] == 0:  # left wall
            self.user_pos = [self.entry_door[0], self.entry_door[1] + 1]
        elif self.entry_door[1] == self.total_size - 1:  # right wall
            self.user_pos = [self.entry_door[0], self.entry_door[1] - 1]

        self.current_room.grid[self.user_pos[0]][self.user_pos[1]] = 'P'  # Set the player's position

    def generate_door(self):
        while True:
            wall = random.choice(['top', 'bottom', 'left', 'right'])

            if wall == 'top':
                door_pos = [0, random.randint(1, self.total_size - 2)]
            elif wall == 'bottom':
                door_pos = [self.total_size - 1, random.randint(1, self.total_size - 2)]
            elif wall == 'left':
                door_pos = [random.randint(1, self.total_size - 2), 0]
            elif wall == 'right':
                door_pos = [random.randint(1, self.total_size - 2), self.total_size - 1]

            if door_pos != self.entry_door:
                self.current_room.grid[door_pos[0]][door_pos[1]] = 'D'
                self.previous_door_pos = door_pos
                break

    def print_current_room(self):
        self.current_room.print_room()

    def update_user_pos(self, new_pos):
        if self.current_room.grid[new_pos[0]][new_pos[1]] == 'D':  # If the new position is a Door
            self.generate_new_room()
        else:
            self.current_room.grid[self.user_pos[0]][self.user_pos[1]] = ' '  # Clear old position
            self.current_room.grid[new_pos[0]][new_pos[1]] = 'P'  # Update new position
            self.user_pos = new_pos

    def move(self, direction):
        new_pos = list(self.user_pos)

        if direction.lower() == 'up':
            new_pos[0] -= 1
        elif direction.lower() == 'down':
            new_pos[0] += 1
        elif direction.lower() == 'left':
            new_pos[1] -= 1
        elif direction.lower() == 'right':
            new_pos[1] += 1

        # Check if new position is within the room
        if 0 <= new_pos[0] < self.total_size and 0 <= new_pos[1] < self.total_size:
            self.update_user_pos(new_pos)
        else:
            print("You hit a wall, you can't move in that direction!")

    def start(self):
        while True:
            self.print_current_room()
            direction = input("Enter your move (up, down, left, right): ")
            self.move(direction)

    # def random_start(self):
    #     self.room_type = random.choice(self.room_types)
    #     if self.room_type == 'treasure':
    #         self.grid[middle - 1][middle] = random.choice(self.items)

    def display_game(self):
        self.canvas.delete("all")
        for i, row in enumerate(self.grid):
            for j, cell in enumerate(row):
                if cell == 'D' or cell == '.':
                    color = 'white'  # open space or door
                elif cell == 'P':
                    color = 'blue'  # player
                elif cell in self.items:
                    color = 'green'  # item
                else:
                    color = 'black'  # wall or monster
                self.canvas.create_rectangle(j * 50, i * 50, (j + 1) * 50, (i + 1) * 50, fill=color)

    def make_movement(self, new_pos):
        old_pos = self.user_pos[:]
        self.grid[old_pos[0]][old_pos[1]] = '.'
        self.user_pos = new_pos

        # If the new position is a door, generate a new room
        if self.grid[new_pos[0]][new_pos[1]] == 'D':
            self.previous_door_pos = new_pos
            self.current_room += 1
            self.generate_new_room()
        elif self.grid[new_pos[0]][new_pos[1]] in self.items:
            print(f"You found a {self.grid[new_pos[0]][new_pos[1]]}!")
            self.grid[new_pos[0]][new_pos[1]] = 'P'
        elif self.grid[new_pos[0]][new_pos[1]] == 'M':
            print("You encountered a monster!")
            self.grid[new_pos[0]][new_pos[1]] = 'P'
        else:
            self.grid[new_pos[0]][new_pos[1]] = 'P'

        self.update_view()