from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame # type: ignore
from Env_view import Renderer
from Env_models import Snake, Food, Obstacle, Vec2
from Env_events import EventManager
from Env_contoller import GameController

DIRECTIONS = {
    'UP': Vec2(0, -1),
    'RIGHT': Vec2(1, 0),
    'LEFT': Vec2(-1, 0),
    'DOWN':Vec2(0, 1)
}

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

    def initialize_game_objects(self):
        self.initialize_obstacles()
        self.initialize_agents()
        self.initialize_food()
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

    def initialize_event_manager(self) -> None:
        self.event_manager = EventManager(self)

    def initialize_renderer(self) -> None:
        self.renderer = Renderer(self)

    def create_key_map(self):
        return {
            self.e.K_w: DIRECTIONS['UP'],
            self.e.K_UP: DIRECTIONS['UP'],
            self.e.K_d: DIRECTIONS['RIGHT'],
            self.e.K_RIGHT: DIRECTIONS['RIGHT'],
            self.e.K_a: DIRECTIONS['LEFT'],
            self.e.K_LEFT: DIRECTIONS['LEFT'],
            self.e.K_s: DIRECTIONS['DOWN'],
            self.e.K_DOWN: DIRECTIONS['DOWN']
        }

    def load_image(self, path: str) -> None:
        image = self.e.image.load(path).convert_alpha()
        return self.e.transform.scale(image, (self.width, self.height))
    
    def update_env_state(self) -> None:
        if not self.snake.direction.zero:
            self.snake.move()
            self.env_state['snake'] = self.snake.body
        self.check_collision()
        for i, v in enumerate(self.fruits):
            self.fruits[i].update(self.env_state)
            self.env_state['food'][i] = v.position

    def check_collision(self) -> None:
        head = self.snake.head
        if head == self.fruits[0].position:
            self.fruits[0].update(self.env_state, True)
            self.snake.grow = True
        elif head == self.fruits[1].position:
            self.fruits[1].update(self.env_state, True)
            self.snake.shrink = True
        elif self.snake.snakeLength <= 1 or len(self.snake.body) != len(set(self.snake.body)):
            self.death = True
        elif not 0 <= head.x < self.cell_number or not 0 <= head.y < self.cell_number:
            self.death = True
        for obs in self.obstacles:
            if self.snake.head in obs.blocks:
                self.death = True
                break

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
        print(self.env_state)
