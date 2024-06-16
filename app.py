import pygame
import time
from game import Game
from geometry import Direction, Point



class GameApp:

    ## CONSTANTS
    # Set up the screen
    WINDOW_SIZE = 500
    GRID_SIZE = 20
    SCORE_TABLE_OFFSET = WINDOW_SIZE // GRID_SIZE 

    # Set up the game rules
    GAME_SPEED = 8
    QUIT_ON_GAME_OVER = True
    CIRCULAR_BOUNDARIES = False
    RUN_HEADLESS = False
    show_grid = True

    # selfs:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    GRAY = (128, 128, 128)
    
    # variables
    game = None
    screen = None
    square_size = WINDOW_SIZE // GRID_SIZE
    playMode = None
    ANN_model = None
    specialText = ""

    def __init__(self, startHeadless = False, playMode = "human", specialText = ""):
        self.RUN_HEADLESS = startHeadless
        self.specialText = specialText
        ## INIT
        # initialize pygame

        if self.WINDOW_SIZE % self.GRID_SIZE != 0:
            raise ValueError("Window size must be divisible by grid size")

        if not self.RUN_HEADLESS:
            pygame.init()
            self.screen = pygame.display.set_mode(
                (self.WINDOW_SIZE, self.SCORE_TABLE_OFFSET + self.WINDOW_SIZE)
            )
            pygame.display.set_caption("Snake Game")

        # init game
        self.game = Game(self.GRID_SIZE, self.CIRCULAR_BOUNDARIES)
        self.playMode = playMode

    def set_ann_model(self, model):
        self.ANN_model = model

    def setGameSpeed(self, speed):
        self.GAME_SPEED = speed

    def get_ann_input(self):
        # directions are: x-axis, y-axis, upper-left diagonal, upper-right diagonal
        snake = self.game.get_snake()
        fruit = self.game.get_fruit().point
        snake_head = snake.get_snake_body()[0]
        input = []
        
        # get the distance to the fruit in all 4 directions

        input.append(snake_head.distance_on_left(fruit))
        input.append(snake_head.distance_on_right(fruit))
        input.append(snake_head.distance_on_top(fruit))
        input.append(snake_head.distance_on_bottom(fruit))
        input.append(snake_head.distance_on_upper_left_diagonal(fruit))
        input.append(snake_head.distance_on_upper_right_diagonal(fruit))
        input.append(snake_head.distance_on_lower_left_diagonal(fruit))
        input.append(snake_head.distance_on_lower_right_diagonal(fruit))

        # get the distance to the wall in all 8 directions
        input.append(snake_head.x)
        input.append(snake_head.y)
        input.append(self.GRID_SIZE - snake_head.x)
        input.append(self.GRID_SIZE - snake_head.y)
        input.append(min(snake_head.x, snake_head.y))
        input.append(min(snake_head.x, self.GRID_SIZE - snake_head.y))
        input.append(min(self.GRID_SIZE - snake_head.x, snake_head.y))
        input.append(min(self.GRID_SIZE - snake_head.x, self.GRID_SIZE - snake_head.y))        
        
        # get the min distance to itself in all 8 directions 
        min_list = [999, 999, 999, 999, 999, 999, 999, 999]
        for i in range(1, len(snake.get_snake_body())):
            body_part = snake.get_snake_body()[i]
            min_list[0] = min(min_list[0], snake_head.distance_on_left(body_part))
            min_list[1] = min(min_list[1], snake_head.distance_on_right(body_part))
            min_list[2] = min(min_list[2], snake_head.distance_on_top(body_part))
            min_list[3] = min(min_list[3], snake_head.distance_on_bottom(body_part))
            min_list[4] = min(min_list[4], snake_head.distance_on_upper_left_diagonal(body_part))
            min_list[5] = min(min_list[5], snake_head.distance_on_upper_right_diagonal(body_part))
            min_list[6] = min(min_list[6], snake_head.distance_on_lower_left_diagonal(body_part))
            min_list[7] = min(min_list[7], snake_head.distance_on_lower_right_diagonal(body_part))
        
        input.extend(min_list)
        return input

    def runGame(self):
        tick = 0
        moves = 0
        game_over = False
        time_start = time.time()
        last_score = 0
        # start game loop
        while True:

            if last_score != self.game.score:
                last_score = self.game.score
                time_start = time.time()


            if time.time() - time_start > 20:
                break
            # Clear the screen
            if not self.RUN_HEADLESS:
                self.screen.fill(self.BLACK)

            # Event handling
            if self.playMode == "human" and not self.RUN_HEADLESS:
                # If human player, handle events from keyboard
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        break

                keys = pygame.key.get_pressed()
                if keys[pygame.K_q]:
                        break
                elif keys[pygame.K_m]:
                    self.show_grid = not self.show_grid
                else:
                    # leave only the arrow keys
                    keys = {Direction.UP: keys[pygame.K_UP], 
                            Direction.DOWN: keys[pygame.K_DOWN], 
                            Direction.LEFT: keys[pygame.K_LEFT], 
                            Direction.RIGHT: keys[pygame.K_RIGHT]}
                    # filter out the keys that are false
                    keys = {key: value for key, value in keys.items() if value}
                    if len(keys) > 0:
                        self.game.get_snake().set_direction(list(keys.keys())[0])
            elif self.playMode == "ai":
                if not self.RUN_HEADLESS:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            break

                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_q]:
                            break
                    elif keys[pygame.K_m]:
                        self.show_grid = not self.show_grid
                if not self.game.get_snake().has_direction_changed():
                    # If AI player, handle events from ANN model
                    input = self.get_ann_input()
                    if input is not None:
                        moves += 1
                        output = self.ANN_model.predict(input)
                        self.game.get_snake().set_direction(output)
                
            should_move = False
            if not self.RUN_HEADLESS:
            # Draw the score
                font = pygame.font.Font(None, 36)
                score_text = font.render(f"Score: {self.game.score}" + self.specialText, True, self.WHITE)
                text_rect = score_text.get_rect(center=
                    (self.WINDOW_SIZE/2,self.SCORE_TABLE_OFFSET/2)
                )
                self.screen.blit(score_text, text_rect)


                # Draw the fruit
                fruit = self.game.get_fruit().point
                pygame.draw.rect(self.screen, self.BLUE, (
                    fruit.x * self.square_size,
                    fruit.y * self.square_size + self.SCORE_TABLE_OFFSET, 
                    self.square_size, self.square_size))
                
                # Draw the snake
                snake_body = self.game.get_snake().get_snake_body()
                color = self.GREEN
                for point in snake_body:
                    color = self.RED if point == snake_body[0] else self.GREEN

                    pygame.draw.rect(self.screen, color, (
                        point.x * self.square_size,
                        point.y * self.square_size + self.SCORE_TABLE_OFFSET, 
                        self.square_size, self.square_size))
                


                # Draw the grid
                if self.show_grid:
                    for i in range(0, self.WINDOW_SIZE, self.square_size):
                        pygame.draw.line(self.screen, self.GRAY, 
                                        (i, self.SCORE_TABLE_OFFSET), 
                                        (i, self.WINDOW_SIZE + self.SCORE_TABLE_OFFSET), 2)
                        pygame.draw.line(self.screen, self.GRAY, 
                                        (0, i + self.SCORE_TABLE_OFFSET), 
                                        (self.WINDOW_SIZE, i + self.SCORE_TABLE_OFFSET), 2)

                # draw gray border
                pygame.draw.rect(self.screen, self.GRAY, 
                                (0, 0, self.WINDOW_SIZE, self.WINDOW_SIZE + self.SCORE_TABLE_OFFSET), 2)

                # handle game speed
                should_move = False
                if tick % self.GAME_SPEED == 0 and not game_over:
                    should_move = True

            game_over = not self.game.update(should_move)    
            if game_over and self.QUIT_ON_GAME_OVER:
                break
            
            
            if not self.RUN_HEADLESS:
                # Update the display
                pygame.display.flip()

                # Cap the frame rate
                pygame.time.Clock().tick(30)
                tick += 1
                tick %= self.GAME_SPEED

        # Quit Pygame
        if not self.RUN_HEADLESS:
            pygame.quit()
            #sys.exit()
        return self.game.score, moves
