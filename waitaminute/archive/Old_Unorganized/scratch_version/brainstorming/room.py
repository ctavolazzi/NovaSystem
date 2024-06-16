import uuid

class Room:
    def __init__(self, size, door_pos=None, id=None):
        self.size = size
        self.door_pos = door_pos
        self.id = str(uuid.uuid4()) if id is None else id
        self.grid = [['.' for _ in range(self.size)] for _ in range(self.size)]

        # Set the outer cells as walls '#'
        for i in range(self.size):
            for j in range(self.size):
                if i == 0 or i == self.size - 1 or j == 0 or j == self.size - 1:
                    self.grid[i][j] = '#'

        if self.door_pos is not None:
            self.grid[self.door_pos[0]][self.door_pos[1]] = 'D'

    def print_room(self):
        for row in self.grid:
            print(' '.join(row))
