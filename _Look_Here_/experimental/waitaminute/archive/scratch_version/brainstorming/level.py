import random
from robot import Robot

class Level:
    def __init__(self, game, min_robots=1, max_robots=5):
        self.game = game
        self.min_robots = min_robots
        self.max_robots = max_robots
        self.door = 'D'
        self.generate_level()

    def generate_level(self):
        self.game.grid = [[' ' for _ in range(self.game.total_size)] for _ in range(self.game.total_size)]
        for i in range(self.game.total_size):
            self.game.grid[i][0] = self.game.grid[i][self.game.total_size-1] = '#'
            self.game.grid[0][i] = self.game.grid[self.game.total_size-1][i] = '#'

        self.add_robots()
        self.add_door()

    def add_robots(self):
        num_robots = random.randint(self.min_robots, self.max_robots)
        for _ in range(num_robots):
            robot_x_pos, robot_y_pos = self.game.user_pos
            while [robot_x_pos, robot_y_pos] == self.game.user_pos:
                robot_x_pos = random.randint(1, self.game.total_size-2)
                robot_y_pos = random.randint(1, self.game.total_size-2)

            self.game.grid[robot_x_pos][robot_y_pos] = 'R'
            robot = Robot('Robbie', 'A friendly robot', robot_x_pos, robot_y_pos, self.game)
            self.game.robots.append(robot)

    def add_door(self):
        door_x_pos, door_y_pos = self.game.user_pos
        while [door_x_pos, door_y_pos] == self.game.user_pos:
            door_x_pos = random.randint(1, self.game.total_size-2)
            door_y_pos = random.randint(1, self.game.total_size-2)

        self.game.grid[door_x_pos][door_y_pos] = self.door
