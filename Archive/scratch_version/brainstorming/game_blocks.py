from game_log import GameLog
# from level import Level
from player import Player
import random
import tkinter as tk
from room import Room
import uuid


gl = GameLog()



class Game:
  def __init__(self, master):
    self.master = master
    self.gl = GameLog()
    self.total_size = 10
    self.size = 10
    self.door_pos = None
    self.entry_door = None
    self.id = str(uuid.uuid4())
    self.grid = []
    self.user_pos = []
    self.robots = []
    self.paused = False
    self.game_log = GameLog()
    self.current_room = 0
    self.entry_door = None  # Holds the entry door coordinates
    self.previous_door_pos = None  # Holds the previous door coordinates
    # self.level = Level(self)
    self.canvas = tk.Canvas(self.master, width=500, height=500)
    self.canvas.pack()

  def basic_start(self, door_pos=None):
        # Initialize all cells as open space '.'
        self.grid = [['.' for _ in range(self.total_size)] for _ in range(self.total_size)]

        # Set the outer cells as walls '#'
        for i in range(self.total_size):
            for j in range(self.total_size):
                if i == 0 or i == self.total_size - 1 or j == 0 or j == self.total_size - 1:
                    self.grid[i][j] = '#'

        # Set player's initial position in the middle
        # middle = self.total_size // 2
        # self.grid[middle][middle] = 'P'  # Assuming 'P' denotes the player
        # self.user_pos = [middle, middle]
        # self.player = Player(self, self.user_pos[0], self.user_pos[1])
        # if door_pos is None:  # For the first room, add a door at the top
        #     self.grid[1][middle] = 'D'
        # elif door_pos == 'top':  # If player entered from the top door, draw the door at the bottom
        #     self.grid[self.total_size-2][middle] = 'D'
        # # Add conditions for other doors (left, right, bottom) here

                # Set player's initial position in the middle
        middle = self.total_size // 2
        self.grid[middle][middle] = 'P'  # Assuming 'P' denotes the player
        self.user_pos = [middle, middle]
        self.player = Player(self, self.user_pos[0], self.user_pos[1])

        # Set a door 'D' at a random position on one of the walls
        self.generate_door()

  def display_game(self):
    self.canvas.delete("all")
    for i, row in enumerate(self.grid):
          for j, cell in enumerate(row):
              if cell == 'D' or cell == '.':
                  color = 'white'  # open space or door
              elif cell == 'P':
                color = 'blue'  # player
              else:
                  color = 'black'  # wall or player
              self.canvas.create_rectangle(j * 50, i * 50, (j + 1) * 50, (i + 1) * 50, fill=color)

  def update_view(self):
      self.gl.log('Updating game view')
      self.display_game()

  def start(self):
      # self.basic_start()
      self.basic_start_with_room_at_top()
      self.update_view()

  def calculate_new_position(self, key):
      x, y = self.user_pos
      if key == 'w':
          return [x-1, y]  # Move up
      elif key == 'a':
          return [x, y-1]  # Move left
      elif key == 's':
          return [x+1, y]  # Move down
      elif key == 'd':
          return [x, y+1]  # Move right
      else:
          return [x, y]  # Stay in the same position for any other key

  def is_valid_movement(self, new_pos):
      x, y = new_pos
      return self.grid[x][y] != '#'

  # def make_movement(self, new_pos):
  #     self.grid[self.user_pos[0]][self.user_pos[1]] = '.'
  #     self.grid[new_pos[0]][new_pos[1]] = 'P'
  #     self.user_pos = new_pos
  #     self.update_view()

  # def make_movement(self, new_pos):
  #     self.grid[self.user_pos[0]][self.user_pos[1]] = '.'
  #     self.grid[new_pos[0]][new_pos[1]] = 'P'
  #     self.user_pos = new_pos

  #     # If the new position is a door, generate a new room
  #     if self.grid[new_pos[0]][new_pos[1]] == 'D':
  #         self.current_room += 1
  #         self.generate_new_room()

  #     self.update_view()

  # def make_movement(self, new_pos):
  #     old_pos = self.user_pos[:]
  #     self.grid[old_pos[0]][old_pos[1]] = '.'
  #     self.user_pos = new_pos
  #     if self.grid[new_pos[0]][new_pos[1]] == 'D':  # Player moved through a door
  #         self.previous_door_pos = new_pos
  #         self.current_room += 1
  #         self.generate_new_room()
  #     else:
  #         self.grid[new_pos[0]][new_pos[1]] = 'P'
  #     self.update_view()

  def make_movement(self, new_pos):
      old_pos = self.user_pos[:]
      self.grid[old_pos[0]][old_pos[1]] = '.'
      self.user_pos = new_pos

      if self.grid[new_pos[0]][new_pos[1]] == 'D':  # Player moved through a door
          self.previous_door_pos = new_pos
          self.current_room += 1
          self.generate_new_room()
      else:
          self.grid[new_pos[0]][new_pos[1]] = 'P'

      self.update_view()

  def basic_start_with_room_at_top(self):
    # Initialize all cells as open space '.'
    self.grid = [['.' for _ in range(self.total_size)] for _ in range(self.total_size)]

    # Set the outer cells as walls '#'
    for i in range(self.total_size):
        for j in range(self.total_size):
            if i == 0 or i == self.total_size - 1 or j == 0 or j == self.total_size - 1:
                self.grid[i][j] = '#'

    # Set a door 'D' at the top of the room
    self.grid[0][self.total_size // 2] = 'D'

    # Set player's initial position in the middle
    middle = self.total_size // 2
    self.grid[middle][middle] = 'P'  # Assuming 'P' denotes the player
    self.user_pos = [middle, middle]
    self.player = Player(self, self.user_pos[0], self.user_pos[1])

  def generate_new_room(self):
      # Generate a new room similar to basic_start
      # But with the door in a random position on one of the walls

      # Initialize all cells as open space '.'
      self.grid = [['.' for _ in range(self.total_size)] for _ in range(self.total_size)]

      # Set the outer cells as walls '#'
      for i in range(self.total_size):
          for j in range(self.total_size):
              if i == 0 or i == self.total_size - 1 or j == 0 or j == self.total_size - 1:
                  self.grid[i][j] = '#'

      # if self.previous_door_pos is not None:
      #     if self.previous_door_pos[0] == 0:  # top wall in previous room
      #         self.user_pos = [self.total_size - 1, self.previous_door_pos[1]]  # bottom wall in new room
      #     elif self.previous_door_pos[0] == self.total_size - 1:  # bottom wall in previous room
      #         self.user_pos = [0, self.previous_door_pos[1]]  # top wall in new room
      #     elif self.previous_door_pos[1] == 0:  # left wall in previous room
      #         self.user_pos = [self.previous_door_pos[0], self.total_size - 1]  # right wall in new room
      #     elif self.previous_door_pos[1] == self.total_size - 1:  # right wall in previous room
      #         self.user_pos = [self.previous_door_pos[0], 0]  # left wall in new room
      # else:
      #     # Set player's initial position in the middle
      #     middle = self.total_size // 2
      #     self.user_pos = [middle, middle]

      # self.grid[self.user_pos[0]][self.user_pos[1]] = 'P'  # Assuming 'P' denotes the player
      # self.player = Player(self, self.user_pos[0], self.user_pos[1])
      # self.generate_door()

      # # Set a door 'D' at a random position on one of the walls
      # wall_side = random.choice(['top', 'bottom', 'left', 'right'])
      # if wall_side == 'top':
      #     self.grid[0][random.randint(1, self.total_size-2)] = 'D'
      # elif wall_side == 'bottom':
      #     self.grid[-1][random.randint(1, self.total_size-2)] = 'D'
      # elif wall_side == 'left':
      #     self.grid[random.randint(1, self.total_size-2)][0] = 'D'
      # elif wall_side == 'right':
      #     self.grid[random.randint(1, self.total_size-2)][-1] = 'D'

      # # Set player's initial position in the middle
      # middle = self.total_size // 2
      # self.grid[middle][middle] = 'P'  # Assuming 'P' denotes the player
      # self.user_pos = [middle, middle]
      # self.player = Player(self, self.user_pos[0], self.user_pos[1])
      # self.generate_door()

      # After setting up the new room, instead of placing the player at the middle,
      # place them at the door they just entered from
      if self.previous_door_pos is not None:
        if self.previous_door_pos[0] == 0:  # top wall in previous room
            self.user_pos = [self.total_size - 1, self.previous_door_pos[1]]  # bottom wall in new room
        elif self.previous_door_pos[0] == self.total_size - 1:  # bottom wall in previous room
            self.user_pos = [0, self.previous_door_pos[1]]  # top wall in new room
        elif self.previous_door_pos[1] == 0:  # left wall in previous room
            self.user_pos = [self.previous_door_pos[0], self.total_size - 1]  # right wall in new room
        elif self.previous_door_pos[1] == self.total_size - 1:  # right wall in previous room
            self.user_pos = [self.previous_door_pos[0], 0]  # left wall in new room
      else:
        # If there's no previous door, place the player at the middle
        middle = self.total_size // 2
        self.user_pos = [middle, middle]

      self.grid[self.user_pos[0]][self.user_pos[1]] = 'P'  # Assuming 'P' denotes the player
      self.player = Player(self, self.user_pos[0], self.user_pos[1])
      self.generate_door()

  # def generate_door(self):
  #     if self.previous_door_pos is not None:
  #         # Use the mirrored position of the player to determine which wall to exclude
  #         if self.previous_door_pos[0] == 0:  # top wall in previous room
  #             eligible_walls = bottom_wall + left_wall + right_wall
  #         elif self.previous_door_pos[0] == self.total_size - 1:  #, self.previous_door_pos[1]]  # bottom wall in new room
  #             eligible_walls = top_wall + left_wall + right_wall
  #         elif self.previous_door_pos[0] == self.total_size - 1:  # bottom wall in previous room
  #             door_pos = [0, self.previous_door_pos[1]]  # top wall in new room
  #         elif self.previous_door_pos[1] == 0:  # left wall in previous room
  #             door_pos = [self.previous_door_pos[0], self.total_size - 1]  # right wall in new room
  #         elif self.previous_door_pos[1] == self.total_size - 1:  # right wall in previous room
  #             door_pos = [self.previous_door_pos[0], 0]  # left wall in new room

  #         # Draw the door
  #         self.grid[door_pos[0]][door_pos[1]] = 'D'

  #         # Reset previous_door_pos
  #         self.previous_door_pos = None
  #     else:
  #         # Place the door at a random location as before
  #         top_wall = [[0, i] for i in range(1, self.total_size - 1)]
  #         bottom_wall = [[self.total_size - 1, i] for i in range(1, self.total_size - 1)]
  #         left_wall = [[i, 0] for i in range(1, self.total_size - 1)]
  #         right_wall = [[i, self.total_size - 1] for i in range(1, self.total_size - 1)]

  #         # Combine all walls into a single list
  #         all_walls = top_wall + bottom_wall + left_wall + right_wall

  #         # Select a random position for the door
  #         door_pos = random.choice(all_walls)

  #         # Draw the door
  #         self.grid[door_pos[0]][door_pos[1]] = 'D'



  def generate_door(self):
      # Calculate the positions of all walls
      top_wall = [[0, i] for i in range(1, self.total_size - 1)]
      bottom_wall = [[self.total_size - 1, i] for i in range(1, self.total_size - 1)]
      left_wall = [[i, 0] for i in range(1, self.total_size - 1)]
      right_wall = [[i, self.total_size - 1] for i in range(1, self.total_size - 1)]

      if self.previous_door_pos is not None:
          # Use the mirrored position of the player to determine which wall to exclude
          if self.previous_door_pos[0] == 0:  # top wall in previous room
              eligible_walls = bottom_wall + left_wall + right_wall
          elif self.previous_door_pos[0] == self.total_size - 1:  # bottom wall in previous room
              eligible_walls = top_wall + left_wall + right_wall
          elif self.previous_door_pos[1] == 0:  # left wall in previous room
              eligible_walls = top_wall + bottom_wall + right_wall
          elif self.previous_door_pos[1] == self.total_size - 1:  # right wall in previous room
              eligible_walls = top_wall + bottom_wall + left_wall
      else:
          # If there's no previous door, all walls are eligible for the door placement
          eligible_walls = top_wall + bottom_wall + left_wall + right_wall

      # Select a random position for the door from the eligible walls
      door_pos = random.choice(eligible_walls)

      # Draw the door
      self.grid[door_pos[0]][door_pos[1]] = 'D'
