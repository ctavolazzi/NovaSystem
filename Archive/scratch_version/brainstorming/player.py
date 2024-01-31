class Player:
    def __init__(self, game, x_pos, y_pos):
        self.symbol = '@'
        self.game = game
        self.x_pos = x_pos
        self.y_pos = y_pos

    def move(self, direction):
        if self.game.paused:
            return

        directions = {'w': [-1, 0], 's': [1, 0], 'a': [0, -1], 'd': [0, 1]}  # Define movements
        new_pos = [self.x_pos + directions[direction][0], self.y_pos + directions[direction][1]]  # Get new position

        if self.game.grid[new_pos[0]][new_pos[1]] == 'R':
            self.game.robot.open_chat_window()
            return

        self.game.grid[self.x_pos][self.y_pos] = ' '
        self.game.grid[new_pos[0]][new_pos[1]] = self.symbol
        self.x_pos, self.y_pos = new_pos  # Update player position
        self.game.update_view()