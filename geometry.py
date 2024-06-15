class Point:
    x: int = None
    y: int = None

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    

class Direction:
    UP = 1
    DOWN = 3
    LEFT = 0
    RIGHT = 2

    