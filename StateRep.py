import numpy as np
from Env_utils import Vec2

class StateRep:
    def __init__(self, game_engine):
        """Initialize the State Representation with the game engine."""
        self.game_engine = game_engine
        self.reset_indicators()

    def reset_indicators(self):
        """Reset the danger and food direction indicators."""
        self.danger_straight = 0
        self.danger_right = 0
        self.danger_left = 0
        self.directions = { 'west': 0, 'east': 0, 'north': 0, 'south': 0 }
        self.food_directions = { 'westwards': 0, 'eastwards': 0, 'northwards': 0, 'southwards': 0 }

    def update(self):
        """Update the state representation."""
        self.reset_indicators()
        self.update_dangers()
        self.update_food_direction()

        # Create the state vector
        state_vector = np.array([
            self.danger_straight,
            self.danger_right,
            self.danger_left,
            self.directions['west'],
            self.directions['east'],
            self.directions['north'],
            self.directions['south'],
            self.food_directions['westwards'],
            self.food_directions['eastwards'],
            self.food_directions['northwards'],
            self.food_directions['southwards'],
        ])

        return state_vector

    def update_dangers(self):
        head = self.game_engine.snake.head
        neck = self.game_engine.snake.body[1]
        dir = self.engine.snake.direction if head == neck else head - neck

        self.danger_straight = self.check_danger(dir)

        self.danger_right = self.check_danger(dir.swap() if dir.x != 0 else dir.swap().negate())

        self.danger_left = self.check_danger(dir.swap().negate() if dir.x != 0 else dir.swap())

    def check_danger(self, direction):
        # Check if the next cell in the given direction is dangerous (wall, snake's body, or obstacle)
        next_cell = self.game_engine.snake.head + direction
        return self.game_engine.is_wall(next_cell) or self.game_engine.is_snake_body(next_cell) or self.game_engine.is_obstacle(next_cell)
 
    def update_food_direction(self):
        # Assuming the first food item in the list is the target
        food = self.game_engine.fruits[0] if self.game_engine.fruits else None
        if food:
            food_direction = food.position - self.game_engine.snake.head
            if food_direction.x < 0:
                self.food_directions['westwards'] = 1
            elif food_direction.x > 0:
                self.food_directions['eastwards'] = 1
            if food_direction.y < 0:
                self.food_directions['northwards'] = 1
            elif food_direction.y > 0:
                self.food_directions['southwards'] = 1

        # Update the snake's current direction
        head = self.game_engine.snake.head
        neck = self.game_engine.snake.body[1]
        current_direction = self.engine.snake.direction if head == neck else head - neck
        # current_direction = self.game_engine.snake.direction
        if current_direction == Vec2(-1, 0):
            self.directions['west'] = 1
        elif current_direction == Vec2(1, 0):
            self.directions['east'] = 1
        elif current_direction == Vec2(0, -1):
            self.directions['north'] = 1
        elif current_direction == Vec2(0, 1):
            self.directions['south'] = 1