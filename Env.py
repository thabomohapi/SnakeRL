from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
from Env_models import Snake, Food, Obstacle, Vec2
from Env_view import GameView

class Engine:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self, cell_size=25, cell_number=30, fps=45) -> None:
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
        self.width = self.cell_number * self.cell_size
        self.height = self.cell_number * self.cell_size
        self.screen = self.e.display.set_mode((self.width, self.height))
        self.clock = self.e.time.Clock()
        self.SCREEN_UPDATE = self.e.USEREVENT

    def initialize_game_objects(self):
        self.occupied_positions = set()
        self.obstacles = []
        self.obstacles = 7 * Obstacle(self, 10)
        self.snake = Snake(self)
        self.fruits = (Food(True, self), Food(False, self))
        self.view = GameView(self)
        self.death = False
        self.key_map = self.create_key_map()
        self.start_timer = pygame.time.get_ticks()
        self.key_press_queue = []

    def create_key_map(self):
        return {
            pygame.K_w: Vec2(0, -1),
            pygame.K_UP: Vec2(0, -1),
            pygame.K_d: Vec2(1, 0),
            pygame.K_RIGHT: Vec2(1, 0),
            pygame.K_a: Vec2(-1, 0),
            pygame.K_LEFT: Vec2(-1, 0),
            pygame.K_s: Vec2(0, 1),
            pygame.K_DOWN: Vec2(0, 1)
        }

    def load_image(self, path: str) -> None:
        image = self.e.image.load(path).convert_alpha()
        return self.e.transform.scale(image, (self.width, self.height))
    
    def update(self) -> None:
        self.process_key_press_queue()
        if not self.snake.direction.zero:
            self.snake.move()
        self.check_collision()
        self.fruits[1].update()
        for obs in self.obstacles:
            obs.update_occupied_positions()

    def process_key_press_queue(self) -> None:
        while self.key_press_queue:
            key = self.key_press_queue.pop(0)
            direction = self.key_map.get(key)
            if direction and self.snake.direction != direction.negate():
                self.snake.direction = direction
                break

    def check_collision(self) -> None:
        head = self.snake.head
        if head == self.fruits[0].position:
            self.fruits[0].update()
            self.snake.grow = True
        elif head == self.fruits[1].position:
            self.fruits[1].update(True)
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

    def handle_keys(self, keys) -> None:
        for key, direction in self.key_map.items():
            if keys[key] and self.snake.direction != direction.negate():
                self.snake.direction = direction
                break

    def reset_game(self) -> None:
        self.snake.reset()
        for fruit in self.fruits:
            fruit.update(self.death)
        self.death = False