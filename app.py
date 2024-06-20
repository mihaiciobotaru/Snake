import os
import pygame
import time
from game import Game
from geometry import Direction, Point, INFINITY



class GameApp:

    ## CONSTANTS
    # Set up the screen
    WINDOW_SIZE = 500
    GRID_SIZE = 20
    SCORE_TABLE_OFFSET = WINDOW_SIZE // GRID_SIZE 
    NEURAL_NETWORK_VISUALIZER_OFFSET = 300

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
    AI_model = None
    specialText = ""
    initialFruitPosition = None

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
                (self.WINDOW_SIZE + self.NEURAL_NETWORK_VISUALIZER_OFFSET, self.SCORE_TABLE_OFFSET + self.WINDOW_SIZE)
            )
            pygame.display.set_caption("Snake Game")

        # init game
        self.game = Game(self.GRID_SIZE, self.CIRCULAR_BOUNDARIES)
        self.initialFruitPosition = self.game.get_fruit().point
        self.playMode = playMode
        if self.playMode == "human" and self.RUN_HEADLESS:
            raise ValueError("Cannot run human mode in headless mode")

    def set_ai_model(self, model):
        self.AI_model = model

    def set_initial_fruit_position(self, position):
        # make point out of tuple
        position = Point(position[0], position[1])
        self.initialFruitPosition = position
        self.game.set_fruit_position(position)
        

    def setGameSpeed(self, speed):
        self.GAME_SPEED = speed

    def get_ann_input(self):
        # directions are: x-axis, y-axis, upper-left diagonal, upper-right diagonal
        snake = self.game.get_snake()
        fruit = self.game.get_fruit().point
        snake_head = snake.get_snake_body()[0]
        input = []
        left = []
        right = []
        top = []
        bottom = []
        
        # get the distance to the fruit in all 4 directions
        left.append(snake_head.distance_on_left(fruit))
        right.append(snake_head.distance_on_right(fruit))
        top.append(snake_head.distance_on_top(fruit))
        bottom.append(snake_head.distance_on_bottom(fruit))

        # get the distance to the wall on all 4 directions
        right.append(self.GRID_SIZE - snake_head.x)
        left.append(snake_head.x)
        top.append(snake_head.y)
        bottom.append(self.GRID_SIZE - snake_head.y)
        
        # get the min distance to itself in all 8 directions 
        min_list = [INFINITY, INFINITY, INFINITY, INFINITY]#, 999, 999, 999, 999]
        for i in range(1, len(snake.get_snake_body())):
            body_part = snake.get_snake_body()[i]
            min_list[0] = min(min_list[0], snake_head.distance_on_left(body_part))
            min_list[1] = min(min_list[1], snake_head.distance_on_right(body_part))
            min_list[2] = min(min_list[2], snake_head.distance_on_top(body_part))
            min_list[3] = min(min_list[3], snake_head.distance_on_bottom(body_part))
            # min_list[4] = min(min_list[4], snake_head.distance_on_upper_left_diagonal(body_part))
            # min_list[5] = min(min_list[5], snake_head.distance_on_upper_right_diagonal(body_part))
            # min_list[6] = min(min_list[6], snake_head.distance_on_lower_left_diagonal(body_part))
            # min_list[7] = min(min_list[7], snake_head.distance_on_lower_right_diagonal(body_part))
        
        left.append(min_list[0])
        right.append(min_list[1])
        top.append(min_list[2])
        bottom.append(min_list[3])
        input.extend(left)
        input.extend(right)
        input.extend(top)
        input.extend(bottom)
        input = [abs(x) if x == -INFINITY else x for x in input]

        # add everything in the right order
        return input

    def runGame(self):
        running = True
        tick = 0
        game_over = False
        idle_moves = 0
        last_moves = 0
        last_score = 0
        # start game loop
        if not self.RUN_HEADLESS:
            pygame.event.set_allowed([pygame.QUIT, pygame.WINDOWFOCUSGAINED])
            os.environ['SDL_VIDEO_WINDOW_POS'] = '100,100'  # Position the window at (100, 100)
        while running:
            # handle time limit
            if self.RUN_HEADLESS:
                if last_score != self.game.score:
                    last_score = self.game.score
                    idle_moves = 0

                if last_moves != self.game.get_snake().move_count:
                    last_moves = self.game.get_snake().move_count
                    idle_moves +=1

                if idle_moves > 150:
                    running = False

            # Event handling
            if self.playMode == "human":
                # If human player, handle events from keyboard
                for event in pygame.event.get():
                    quit = self.eventHandlingDisplay(event)
                    if quit:
                        running = False
                
                keys = {Direction.UP: keys[pygame.K_UP], 
                        Direction.DOWN: keys[pygame.K_DOWN], 
                        Direction.LEFT: keys[pygame.K_LEFT], 
                        Direction.RIGHT: keys[pygame.K_RIGHT]}
                keys = {key: value for key, value in keys.items() if value}
                if len(keys) > 0:
                    self.game.get_snake().set_direction(list(keys.keys())[0])

            elif self.playMode in ["ann", "q_learning"]:
                if not self.RUN_HEADLESS:
                    for event in pygame.event.get():
                        quit = self.eventHandlingDisplay(event)
                        if quit:
                            running = False
                if not self.game.get_snake().has_direction_changed():
                    input = self.get_ann_input()
                    if input is not None:
                        snake_head = self.game.get_snake().get_snake_body()[0]
                        print("snake head when firing: ", snake_head.x, snake_head.y)
                        output = self.AI_model.predict(input)
                        self.game.get_snake().set_direction(output)
                        self.ann_fired = True

            should_move = False
            if not self.RUN_HEADLESS:
                self.screen.fill(self.BLACK)
                self.drawScore()
                self.drawNetwork()
                self.drawFruit()
                self.drawSnake()
                self.drawGrid()

               

                            
                # handle game speed
                should_move = False
                if tick % self.GAME_SPEED == 0 and not game_over:
                    should_move = True

            if self.RUN_HEADLESS:
                should_move = True

            if game_over and self.QUIT_ON_GAME_OVER:
                running = False
            game_over, has_eaten = self.game.update(should_move) 
            if should_move == False:
                result = self.game.test_if_next_move_is_valid()
                if not result:
                    game_over = True
            if self.playMode == "q_learning":
                if has_eaten:
                    reward = 10
                else:
                    if idle_moves > 30:
                        reward = -0.1
                    else:
                        reward = 0.1
                if game_over:
                    reward = -10
                next_state = self.get_ann_input()
                if self.ann_fired or game_over:
                    print("game_over: ", game_over, "has_eaten: ", has_eaten)
                    snake_head = self.game.get_snake().get_snake_body()[0]
                    print("snake head when learning: ", snake_head.x, snake_head.y)
                    self.AI_model.learn(reward, game_over, next_state)  
                    self.ann_fired = False
            
            
            if not self.RUN_HEADLESS:
                # Update the display
                pygame.display.flip()

                # Cap the frame rate
                pygame.time.Clock().tick(15)
                tick += 1
                tick %= self.GAME_SPEED

        # Quit Pygame
        if not self.RUN_HEADLESS:
            pygame.quit()
            #sys.exit()
        return self.game.score, self.game.get_snake().move_count
    
    def eventHandlingDisplay(self, event):
        if event.type == pygame.QUIT:
            return True
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
                return True
        elif keys[pygame.K_m]:
            self.show_grid = not self.show_grid
            return False
        elif event.type == pygame.WINDOWFOCUSGAINED:
            pygame.display.set_mode(
                (self.WINDOW_SIZE + self.NEURAL_NETWORK_VISUALIZER_OFFSET, self.SCORE_TABLE_OFFSET + self.WINDOW_SIZE)
            )
            return False
        
    def drawNetwork(self):
        if not self.RUN_HEADLESS and self.playMode == "q_learning":
            if self.ann_fired:
                self.update_network = True
            else :
                self.update_network = False
            self.AI_model.visualize_network(self.screen, self.update_network)
            # wait 10 seconds
            #time.sleep(10)
        
    def drawScore(self):
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.game.score}" + self.specialText, True, self.WHITE)
        text_rect = score_text.get_rect(center=
            (self.WINDOW_SIZE/2,self.SCORE_TABLE_OFFSET/2)
        )
        self.screen.blit(score_text, text_rect)

    def drawGrid(self):
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

    def drawSnake(self):
        snake_body = self.game.get_snake().get_snake_body()
        color = self.GREEN
        for point in snake_body:
            color = self.RED if point == snake_body[0] else self.GREEN

            pygame.draw.rect(self.screen, color, (
                point.x * self.square_size,
                point.y * self.square_size + self.SCORE_TABLE_OFFSET, 
                self.square_size, self.square_size))

    def drawFruit(self):
        fruit = self.game.get_fruit().point
        pygame.draw.rect(self.screen, self.BLUE, (
            fruit.x * self.square_size,
            fruit.y * self.square_size + self.SCORE_TABLE_OFFSET, 
            self.square_size, self.square_size))
    
