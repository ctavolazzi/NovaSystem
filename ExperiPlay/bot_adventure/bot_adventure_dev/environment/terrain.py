# terrain.py
class Terrain:
    def __init__(self, size_x, size_y, size_z):
        self.cells = [[[None for _ in range(size_z)] for _ in range(size_y)] for _ in range(size_x)]
