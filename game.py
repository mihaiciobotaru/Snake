from geometry import Point
from snake import Snake
import random

class Fruit:
    point = None

    def __init__(self, snake_body, grid_size):
        self.generate_fruit(snake_body, grid_size)

    def generate_fruit(self, snake_body, grid_size):
        while True:
            x = random.randint(0, grid_size - 1)
            y = random.randint(0, grid_size - 1)
            point = Point(x, y)
            if point not in snake_body:
                self.point = point
                break

class Game:
    snake = None
    fruit = None
    grid_size = None
    has_eaten = False
    circular_boundaries = False
    score = 0

    def __init__(self, grid_size, circular_boundaries = False):
        self.grid_size = grid_size
        self.snake = Snake(grid_size, 3, circular_boundaries)
        self.fruit = Fruit(self.snake.get_snake_body(), grid_size)
        self.has_eaten = False
        self.circular_boundaries = circular_boundaries

    def update(self, should_move = False):
        head = self.snake.get_snake_body()[0]
        print("snake before moving" ,head.x, head.y)
        self.score = len(self.snake.get_snake_body())
        if self.snake.get_snake_body()[0] == self.fruit.point:
            self.has_eaten = True
            self.fruit.generate_fruit(self.snake.get_snake_body(), self.grid_size)
        if should_move:
            self.snake.move(self.has_eaten)
            head = self.snake.get_snake_body()[0]
            print("snake after moving" ,head.x, head.y)
            self.has_eaten = False
            self.set_direction_changed(False)
        
        if self.test_game_over():
            return True, False
        return False, self.has_eaten
    
    def test_if_next_move_is_valid(self):
        snake_body_copy = self.snake.get_snake_body()
        self.snake.move(False)
        result = self.test_game_over()
        self.snake.body = snake_body_copy
        self.snake.move_count -= 1
        return not result



    def get_snake(self):
        return self.snake

    def get_fruit(self):
        return self.fruit  

    def set_fruit_position(self, position):
        self.fruit.point = position 

    def test_grid_boundaries(self):
        if self.circular_boundaries:
            return False
        head = self.snake.get_snake_body()[0]
        if head.x < 0 or head.x >= self.grid_size or head.y < 0 or head.y >= self.grid_size:
            return True
        return False

    def test_collision(self):
        head = self.snake.get_snake_body()[0]
        for point in self.snake.get_snake_body()[1:]:
            if head == point:
                return True
        return False

    def test_game_over(self):
        return self.test_grid_boundaries() or self.test_collision() 
    
    def set_direction(self, direction):
        self.snake.set_direction(direction)

    def set_direction_changed(self, value):
        self.snake.set_direction_changed(value)
        