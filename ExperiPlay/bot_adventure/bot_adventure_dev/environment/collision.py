# collision.py
def check_collision(environment, position):
    x, y, z = position
    return environment.terrain.cells[x][y][z] is not None
