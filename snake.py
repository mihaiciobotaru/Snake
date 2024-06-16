from geometry import Point, Direction

class Snake:
    length: int = None
    body: list = None
    direction: str = Direction.LEFT
    direction_changed: bool = False
    circular_boundaries: bool = False
    grid_size: int = None

    def __init__(self, grid_size, length = 3, circular_boundaries = False):
        startingPoint = Point(grid_size // 2, grid_size // 2)
        self.body = [startingPoint]
        self.grid_size = grid_size
        self.circular_boundaries = circular_boundaries
        
        for i in range(1, length):
            self.body.append(Point(startingPoint.x + i, startingPoint.y))

    def move(self, has_eaten=False):
        new_head = self.body[0]
        if self.direction == Direction.UP:
            new_head = Point(new_head.x, new_head.y - 1)
        elif self.direction == Direction.DOWN:
            new_head = Point(new_head.x, new_head.y + 1)
        elif self.direction == Direction.LEFT:
            new_head = Point(new_head.x - 1, new_head.y)
        elif self.direction == Direction.RIGHT:
            new_head = Point(new_head.x + 1, new_head.y)

        if self.circular_boundaries:
            new_head = Point(new_head.x % self.grid_size, new_head.y % self.grid_size)


        self.body.insert(0, new_head)
        if not has_eaten:
            self.body.pop()

    def set_direction(self, direction):
        if abs(self.direction - direction) == 2 or self.direction_changed:
            return
        self.direction = direction
        self.direction_changed = True

    def set_direction_changed(self, value):
        self.direction_changed = value

    def get_snake_body(self):
        return self.body
    
    def has_direction_changed(self):
        return self.direction_changed