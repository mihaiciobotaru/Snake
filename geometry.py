INFINITY = 50

class Point:
    x: int = None
    y: int = None

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    # operator overloading for addition
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)
    
    # operator overloading for subtraction
    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)
    
    # compute distance to other
    # get the distance to the fruit in all 4 directions
    # directions are: x-axis, y-axis, upper-left diagonal, upper-right diagonal

    # distance from upper left diagonal of the point to the other point
    def distance_on_upper_left_diagonal(self, other):
        return self.x - other.x if self.are_on_upper_left_diagonal(other) else INFINITY
    
    # distance from upper right diagonal of the point to the other point
    def distance_on_upper_right_diagonal(self, other):
        return self.x - other.x if self.are_on_upper_right_diagonal(other) else INFINITY
    
    def distance_on_lower_left_diagonal(self, other):
        return self.x - other.x if self.are_on_lower_left_diagonal(other) else INFINITY
    
    def distance_on_lower_right_diagonal(self, other):
        return self.x - other.x if self.are_on_lower_right_diagonal(other) else INFINITY
    
    # distance from the left of the point to the other point
    def distance_on_left(self, other):
        return self.x - other.x if self.are_on_left(other) else -INFINITY

    # distance from the right of the point to the other point
    def distance_on_right(self, other):
        return other.x - self.x if self.are_on_right(other) else -INFINITY

    
    # distance from the top of the point to the other point
    def distance_on_top(self, other):
        return self.y - other.y if self.are_on_top(other) else -INFINITY

    # distance from the bottom of the point to the other point
    def distance_on_bottom(self, other):
        return other.y - self.y if self.are_on_bottom(other) else -INFINITY
    
    def are_on_left(self, other):
        return self.x > other.x
    
    def are_on_right(self, other):
        return self.x < other.x
    
    def are_on_top(self, other):
        return self.y > other.y
    
    def are_on_bottom(self, other):
        return self.y < other.y
    
    def are_on_upper_left_diagonal(self, other):
        return self.x - other.x == self.y - other.y
    
    def are_on_upper_right_diagonal(self, other):
        return self.x - other.x == other.y - self.y
    
    def are_on_lower_left_diagonal(self, other):
        return other.x - self.x == self.y - other.y
    
    def are_on_lower_right_diagonal(self, other):
        return other.x - self.x == other.y - self.y
  

class Direction:
    UP = 2
    DOWN = 4
    LEFT = 1
    RIGHT = 3
 

    