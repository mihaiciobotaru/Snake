# Snake class for handling snake movement, growth

from geometry import Point, Direction
import pygame
import sys



class Snake:
    length: int = None
    body: list = None
    direction: str = Direction.LEFT
    direction_changed: bool = False

    def __init__(self, startingPoint = Point(0, 0), length = 3):
        self.body = [startingPoint]
        
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