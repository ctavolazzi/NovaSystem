class Game:
    def __init__(self, total_size=10, view_size=5):
        self.total_size = total_size
        self.view_size = view_size
        self.user_pos = [total_size//2, total_size//2]  # Starting position
        self.grid = [['.' for _ in range(total_size)] for _ in range(total_size)]  # Initialize environment
        self.grid[self.user_pos[0]][self.user_pos[1]] = '@'  # Place user

    def print_view(self):
        upper_bound = max(0, self.user_pos[0]-self.view_size//2)
        lower_bound = min(self.total_size, upper_bound+self.view_size)
        upper_bound = max(0, lower_bound-self.view_size)
        left_bound = max(0, self.user_pos[1]-self.view_size//2)
        right_bound = min(self.total_size, left_bound+self.view_size)
        left_bound = max(0, right_bound-self.view_size)

        for i in range(upper_bound, lower_bound):
            for j in range(left_bound, right_bound):
                print(self.grid[i][j], end=' ')
            print()

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

        if 0 <= new_pos[0] < self.total_size and 0 <= new_pos[1] < self.total_size:
            self.grid[self.user_pos[0]][self.user_pos[1]] = '.'  # Remove old position
            self.user_pos = new_pos
            self.grid[self.user_pos[0]][self.user_pos[1]] = '@'  # Update new position

game = Game()
game.print_view()

while True:
    move = input("Enter movement (w/a/s/d): ")
    game.move(move)
    game.print_view()
