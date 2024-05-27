from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame # type: ignore
import numpy as np
from Env_view import Renderer
from Env_models import Snake, Food, Obstacle
from Env_events import EventManager
from Env_controller import GameController
from Env_utils import Vec2, Plotter
from StateRep import StateRep

obsBLOCKS = [[Vec2(1, 22), Vec2(1, 23), Vec2(1, 21), Vec2(0, 22), Vec2(0, 21)], [Vec2(17, 4), Vec2(17, 5), Vec2(17, 3), Vec2(16, 5), Vec2(16, 3)], [Vec2(23, 17), Vec2(23, 18), Vec2(22, 17), Vec2(24, 18), Vec2(21, 17)], [Vec2(15, 16), Vec2(15, 15), Vec2(15, 14), Vec2(14, 16), Vec2(14, 14)], [Vec2(11, 13), Vec2(10, 13), Vec2(12, 13), Vec2(11, 14), Vec2(10, 12)], [Vec2(21, 3), Vec2(21, 4), Vec2(21, 5), Vec2(21, 6), Vec2(20, 6)], [Vec2(22, 11), Vec2(22, 10), Vec2(21, 11), Vec2(21, 10), Vec2(21, 12)], [Vec2(7, 23), Vec2(8, 23), Vec2(7, 22), Vec2(7, 24), Vec2(6, 22)], [Vec2(19, 19), Vec2(19, 18), Vec2(20, 18), Vec2(20, 19), Vec2(20, 20)], [Vec2(10, 18), Vec2(10, 19), Vec2(10, 20), Vec2(9, 18), Vec2(10, 17)], [Vec2(17, 13), Vec2(18, 13), Vec2(18, 14), Vec2(17, 14), Vec2(18, 12)], [Vec2(3, 11), Vec2(3, 12), Vec2(4, 11), Vec2(3, 10), Vec2(4, 12)], [Vec2(16, 19), Vec2(16, 20), Vec2(17, 20), Vec2(16, 18), Vec2(17, 18)], [Vec2(8, 5), Vec2(8, 6), Vec2(8, 4), Vec2(7, 5), Vec2(6, 5)], [Vec2(6, 1), Vec2(6, 2), Vec2(5, 1), Vec2(7, 1), Vec2(6, 3)]]

class Environment:
    _instance = None
    
    def __init__(self, cell_size=25, cell_number=25, fps=60) -> None:
        if Environment._instance is not None: 
            raise Exception("This is a singleton class!")
        else: 
            Environment._instance = self
        
        self.initialize_pygame(cell_size, cell_number, fps)
        self.initialize_game_objects()

    def initialize_pygame(self, cell_size, cell_number, fps):
        self.e = pygame
        self.e.init()
        self.cell_size = cell_size
        self.cell_number = cell_number
        self.fps = fps
        self.width = ( self.cell_number * self.cell_size )
        self.side_panel_width = self.width // 3
        self.width += self.side_panel_width
        self.height = self.cell_number * self.cell_size
        self.screen = self.e.display.set_mode((self.width, self.height))
        self.clock = self.e.time.Clock()
        self.SCREEN_UPDATE = self.e.USEREVENT
        self.occupied_positions = set()
        self.death = False
        self.running = False
        self.start_timer = pygame.time.get_ticks()
        self.env_state = {}
        self.reward = -1
        self.DIRECTIONS = [
            Vec2(0, -1),
            Vec2(1, 0),
            Vec2(0, 1),
            Vec2(-1, 0)
        ]
        self.DIR_MAP = {
            Vec2(0, -1) : "UP",
            Vec2(0, 1) : "DOWN",
            Vec2(-1, 0) : "LEFT",
            Vec2(1, 0) : "RIGHT"
        }
        self.key_map = self.create_key_map()

    def initialize_game_objects(self):
        self.initialize_obstacles()
        self.initialize_food()
        self.initialize_agents()
        self.init_state_rep()
        self.initialize_event_manager()
        self.initialize_renderer()

    def initialize_obstacles(self) -> None:
        # self.obstacles = []
        # self.obstacles = 15 * Obstacle(self, 5)
        self.obstacles = [ Obstacle(self, blocks=blocks) for blocks in obsBLOCKS ]
        self.env_state['obstacles'] = [ x.blocks for x in self.obstacles ]
        self.obs1d = [point for sublist in self.env_state['obstacles'] for point in sublist]
        self.occupied_positions = { block for block in self.obs1d }

    def initialize_agents(self) -> None:
        self.snake = Snake(self)
        self.env_state['snake'] = self.snake.body

    def initialize_food(self) -> None:
        self.fruits = [Food(True, self), Food(False, self)]
        self.env_state['food'] = [ x.position for x in self.fruits ]

    def init_state_rep(self) -> None:
        self.rl_STATE = StateRep(self)
        self.rl_state = self.rl_STATE.update()

    def initialize_event_manager(self) -> None:
        self.event_manager = EventManager(self)

    def initialize_renderer(self) -> None:
        self.renderer = Renderer(self)

    def create_key_map(self):
        return {
            self.e.K_w: self.DIRECTIONS[0],
            self.e.K_UP: self.DIRECTIONS[0],
            self.e.K_d: self.DIRECTIONS[1],
            self.e.K_RIGHT: self.DIRECTIONS[1],
            self.e.K_a: self.DIRECTIONS[3],
            self.e.K_LEFT: self.DIRECTIONS[3],
            self.e.K_s: self.DIRECTIONS[2],
            self.e.K_DOWN: self.DIRECTIONS[2]
        }

    def load_image(self, path: str) -> None:
        image = self.e.image.load(path).convert_alpha()
        return self.e.transform.scale(image, (self.width, self.height))

    def update_env_state(self) -> None:
        # Calculate the distance to the good apple before the snake moves
        distance_to_good_apple_before = self.calculate_distance(self.snake.head, self.fruits[0].position)

        # Calculate the distance to the bad apple before the snake moves
        distance_to_bad_apple_before = self.calculate_distance(self.snake.head, self.fruits[1].position)
    
        if not self.snake.direction.zero:
            self.snake.move()
            self.env_state['snake'] = self.snake.body
        
        self.check_collision()
        
        if not self.death or not self.snake.grow or not self.snake.shrink:
            # Calculate the distance to the good apple after the snake moves
            distance_to_good_apple_after = self.calculate_distance(self.snake.head, self.fruits[0].position)

            # Calculate the distance to the bad apple after the snake moves
            distance_to_bad_apple_after = self.calculate_distance(self.snake.head, self.fruits[1].position)

            # Check if the snake got closer or further from the good apple
            if distance_to_good_apple_after < distance_to_good_apple_before:
                self.reward += 3
            elif distance_to_good_apple_after > distance_to_good_apple_before:
                self.reward -= 1.5

            # Check if the snake got closer to the bad apple
            if distance_to_bad_apple_after < distance_to_bad_apple_before:
                self.reward -= 0.5

            for i, v in enumerate(self.fruits):
                self.fruits[i].update()
                self.env_state['food'][i] = v.position
            self.rl_state = self.rl_STATE.update()

        
        self.obs1d = [point for sublist in self.env_state['obstacles'] for point in sublist]
        self.occupied_positions = { block for block in self.obs1d }
        for pos in self.env_state['snake']:
            self.add_occupied_position(pos)
        for food in self.env_state['food']:
            self.add_occupied_position(food)

    def calculate_distance(self, point1, point2) -> np.linalg:
        return np.linalg.norm(np.array(point1.to_list()) - np.array(point2.to_list()))

    def check_collision(self) -> None:
        head = self.snake.head
        if head == self.fruits[0].position:
            self.fruits[0].update(ate=True)
            self.env_state['food'][0] = self.fruits[0].position
            self.snake.grow = True
            self.reward = 10
        elif head == self.fruits[1].position:
            self.fruits[1].update(ate=True)
            self.env_state['food'][1] = self.fruits[1].position
            self.snake.shrink = True
            self.reward = -10
        elif self.snake.snakeLength <= 2 or len(self.snake.body) != len(set(self.snake.body)):
            self.death = True
            self.reward = -100
        elif not 0 <= head.x < self.cell_number or not 0 <= head.y < self.cell_number:
            self.death = True
            self.reward = -100
        elif self.snake.head in self.obs1d:
            self.death = True
            self.reward = -100
        else:
            self.reward = -1

    def is_wall(self, block) -> bool:
        return not 0 <= block.x < self.cell_number or not 0 <= block.y < self.cell_number

    def is_snake_body(self, block) -> bool:
        return block in self.snake.body

    def is_obstacle(self, block) -> bool:
        self.obs1d = [point for sublist in self.env_state['obstacles'] for point in sublist]
        return block in self.obs1d

    def is_bad_apple(self, block) -> bool:
        return block == self.fruits[1].position

    def add_occupied_position(self, position):
        self.occupied_positions.add(position)

    def remove_occupied_position(self, position):
        self.occupied_positions.discard(position)  # discard() won't raise an error if the position is not found

    def reset_occupied_positions(self, positions):
        self.occupied_positions = set(positions)

    def reset_game(self) -> None:
        self.reward = -1
        self.snake.reset()
        self.env_state['snake'] = self.snake.body
        for i, v in enumerate(self.fruits): 
            self.fruits[i].update(died=self.death)
            self.env_state['food'][i] = v.position
        self.death = False
        self.rl_state = self.rl_STATE.update()
