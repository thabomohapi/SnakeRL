from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame # type: ignore
import numpy as np
from Env_view import Renderer
from Env_models import Snake, Food, Obstacle
from Env_events import EventManager
from Env_controller import GameController
from Env_utils import Profiler, Vec2, Plotter
from StateRep import StateRep

DIRECTIONS = [
    Vec2(0, -1),
    Vec2(1, 0),
    Vec2(0, 1),
    Vec2(-1, 0)
]

class Engine:
    _instance = None
    
    def __init__(self, cell_size=25, cell_number=25, fps=60) -> None:
        if Engine._instance is not None: 
            raise Exception("This is a singleton class!")
        else: 
            Engine._instance = self
        
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
        self.key_map = self.create_key_map()
        self.start_timer = pygame.time.get_ticks()
        self.env_state = {}
        self.reward = -1
        self.DIRECTIONS = [
            Vec2(0, -1),
            Vec2(1, 0),
            Vec2(0, 1),
            Vec2(-1, 0)
        ]

    def initialize_game_objects(self):
        self.initialize_obstacles()
        self.initialize_food()
        self.initialize_agents()
        self.init_state_rep()
        # self.create_grid_representation()
        self.initialize_event_manager()
        self.initialize_renderer()

    def initialize_obstacles(self) -> None:
        self.obstacles = []
        self.obstacles = 15 * Obstacle(self, 5)
        self.env_state['obstacles'] = [ x.blocks for x in self.obstacles ]

    def initialize_agents(self) -> None:
        self.snake = Snake(self)
        self.env_state['snake'] = self.snake.body

    def initialize_food(self) -> None:
        self.fruits = (Food(True, self), Food(False, self))
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
            self.e.K_w: DIRECTIONS[3],
            self.e.K_UP: DIRECTIONS[3],
            self.e.K_d: DIRECTIONS[0],
            self.e.K_RIGHT: DIRECTIONS[0],
            self.e.K_a: DIRECTIONS[3],
            self.e.K_LEFT: DIRECTIONS[3],
            self.e.K_s: DIRECTIONS[1],
            self.e.K_DOWN: DIRECTIONS[1]
        }

    def load_image(self, path: str) -> None:
        image = self.e.image.load(path).convert_alpha()
        return self.e.transform.scale(image, (self.width, self.height))
    
    def create_grid_representation(self) -> None:
        grid = np.full((self.cell_number, self.cell_number), 0)

        head = self.env_state['snake'][0]
        tail = self.env_state['snake'][-1]
        # print(f"head = {head}")
        obs_1d = [point for sublist in self.env_state['obstacles'] for point in sublist]
        
        if 0 <= head.x < self.cell_number and 0 <= head.y < self.cell_number and head not in obs_1d:
            for obs in obs_1d:
                grid[obs.x][obs.y] = 1

            for food in self.env_state['food']:
                grid[food.x][food.y] = 0

            for body_part in self.env_state['snake']:
                if body_part != tail and body_part != head:
                    grid[body_part.x][body_part.y] = 1

            self.rl_state = grid.flatten()
            # print(self.rl_state)

    def update_env_state(self) -> None:
        if not self.snake.direction.zero:
            self.snake.move()
            self.env_state['snake'] = self.snake.body
        self.check_collision()
        for i, v in enumerate(self.fruits):
            self.fruits[i].update(self.env_state)
            self.env_state['food'][i] = v.position
        self.rl_state = self.rl_STATE.update()


    def check_collision(self) -> None:
        head = self.snake.head
        if head == self.fruits[0].position:
            self.fruits[0].update(self.env_state, True)
            self.snake.grow = True
            self.reward = 10
        elif head == self.fruits[1].position:
            self.fruits[1].update(self.env_state, True)
            self.snake.shrink = True
            self.reward = -10
        elif self.snake.snakeLength <= 1 or len(self.snake.body) != len(set(self.snake.body)):
            self.death = True
            self.reward = -100
        elif not 0 <= head.x < self.cell_number or not 0 <= head.y < self.cell_number:
            self.death = True
            self.reward = -100
        for obs in self.obstacles:
            if self.snake.head in obs.blocks:
                self.death = True
                self.reward = -100
                break
        if not self.death:
            self.reward = -1

    def add_occupied_position(self, position):
        self.occupied_positions.add(position)

    def remove_occupied_position(self, position):
        self.occupied_positions.discard(position)  # discard() won't raise an error if the position is not found

    def reset_occupied_positions(self, positions):
        self.occupied_positions = set(positions)

    def reset_game(self) -> None:
        self.snake.reset(self.env_state)
        for fruit in self.fruits:
            fruit.update(self.env_state, self.death)
        self.death = False
        # print(self.env_state)
        self.rl_state = self.rl_STATE.update()
