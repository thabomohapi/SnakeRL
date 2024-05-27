# import numpy as np
# from Env_utils import Vec2

# class StateRep:
#     def __init__(self, game_engine):
#         self.game_engine = game_engine
#         self.grid_size = game_engine.cell_number  # Assuming a square grid
#         self.grid = np.zeros((self.grid_size, self.grid_size), dtype=np.float32)
#         # Additional state features
#         self.relative_food_position = np.zeros(2, dtype=np.float32)
#         self.relative_obstacle_position = np.zeros(2, dtype=np.float32)
#         self.snake_direction = np.zeros(3, dtype=np.float32)  # [straight, right, left]
#         self.snake_head_position = np.zeros(2, dtype=np.float32)
#         self.snake_tail_position = np.zeros(2, dtype=np.float32)
#         self.snake_body_positions = []

#     def update(self):
#         # Reset grid and additional features
#         self.grid.fill(1)
#         # self.snake_body_positions = []

#         # Update grid with snake's body
#         for segment in self.game_engine.snake.body:
#             if 0 <= segment.x < self.grid_size and 0 <= segment.y < self.grid_size:
#                 self.grid[segment.y, segment.x] = 0
#                 # self.snake_body_positions.append((segment.x, segment.y))

#         # Update grid with food
#         for food in self.game_engine.fruits:
#             if 0 <= food.position.x < self.grid_size and 0 <= food.position.y < self.grid_size:
#                 self.grid[food.position.y, food.position.x] = 2

#         # Update grid with obstacles
#         for obstacle in self.game_engine.obstacles:
#             for block in obstacle.blocks:
#                 if 0 <= block.x < self.grid_size and 0 <= block.y < self.grid_size:
#                     self.grid[block.y, block.x] = -1

#         # Update additional features
#         self.update_relative_food_position()
#         self.update_relative_obstacle_position()
#         self.update_snake_direction()
#         self.update_snake_head_position()
#         self.update_snake_tail_position()

#         # Flatten the grid and concatenate additional features
#         flat_grid = self.grid.flatten()
#         state_vector = np.concatenate([
#             flat_grid,
#             self.relative_food_position,
#             self.relative_obstacle_position,
#             self.snake_direction,
#             self.snake_head_position, 
#             self.snake_tail_position
#         ])

#         # Normalize the state vector
#         state_vector = self.normalize_state(state_vector)

#         return state_vector

#     def update_relative_food_position(self):
#         # Assuming the first food item in the list is the target
#         food: any = None
#         for foo in self.game_engine.fruits:
#             if foo.is_good:
#                 food = foo
#         snake_head = self.game_engine.snake.head
#         self.relative_food_position[0] = food.position.x - snake_head.x
#         self.relative_food_position[1] = food.position.y - snake_head.y

#     def update_relative_obstacle_position(self):
#         # Find the nearest obstacle block to the snake's head
#         snake_head = self.game_engine.snake.head
#         min_distance = float('inf')
#         nearest_obstacle = None
#         for obstacle in self.game_engine.obstacles:
#             for block in obstacle.blocks:
#                 distance = np.linalg.norm(np.array([block.x - snake_head.x, block.y - snake_head.y]))
#                 if distance < min_distance:
#                     min_distance = distance
#                     nearest_obstacle = block
#         if nearest_obstacle:
#             self.relative_obstacle_position[0] = nearest_obstacle.x - snake_head.x
#             self.relative_obstacle_position[1] = nearest_obstacle.y - snake_head.y

#     def update_snake_direction(self):
#         # Get the current direction of the snake
#         current_direction = self.game_engine.snake.direction
#         # Get the direction of the snake's body (from head to second segment)
#         if len(self.game_engine.snake.body) > 1:
#             body_direction = self.game_engine.snake.body[0] - self.game_engine.snake.body[1]
#         else:
#             body_direction = current_direction  # Default to current direction if the snake has only one segment

#         # Define the relative directions
#         straight = body_direction
#         right = Vec2(body_direction.y, -body_direction.x)  # Rotate 90 degrees clockwise
#         left = Vec2(-body_direction.y, body_direction.x)   # Rotate 90 degrees counter-clockwise

#         # Update the snake_direction list with 1 if the direction is possible, else 0
#         self.snake_direction = np.array([
#             1 if straight == current_direction else 0,  # Straight
#             1 if right == current_direction else 0,     # Right
#             1 if left == current_direction else 0       # Left
#         ])

#     def update_snake_head_position(self):
#         # Update the snake's head position
#         snake_head = self.game_engine.snake.head
#         self.snake_head_position[0] = snake_head.x
#         self.snake_head_position[1] = snake_head.y

#     def update_snake_tail_position(self):
#         # Update the snake's tail position
#         snake_tail = self.game_engine.snake.tail
#         self.snake_tail_position[0] = snake_tail.x
#         self.snake_tail_position[1] = snake_tail.y

#     def normalize_state(self, state_vector):
#         # Normalize the state vector to the range [0, 1]
#         # Assuming that the grid values are between -1 and 2
#         # and the relative positions are within the grid size
#         state_vector[ : pow(self.grid_size, 2)] = (state_vector[ : pow(self.grid_size, 2)] + 1) / 3  # Normalize grid values
#         # Normalize relative positions
#         state_vector[pow(self.grid_size, 2) : ] /= self.grid_size
#         # print(f"state_vector = {state_vector}")
#         return state_vector

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
            self.food_directions['southwards']
        ])

        return state_vector

    def update_dangers(self):
        # Check for danger in the direction the snake is moving
        self.danger_straight = self.check_danger(self.game_engine.snake.direction)

        # Check for danger to the right
        right_direction = Vec2(self.game_engine.snake.direction.y, -self.game_engine.snake.direction.x)
        self.danger_right = self.check_danger(right_direction)

        # Check for danger to the left
        left_direction = Vec2(-self.game_engine.snake.direction.y, self.game_engine.snake.direction.x)
        self.danger_left = self.check_danger(left_direction)

    # def update_dangers(self):
    #     head = self.game_engine.snake.head
    #     neck = self.game_engine.snake.body[1]
    #     dir = self.engine.snake.direction if head == neck else head - neck

    #     self.danger_straight = self.check_danger(dir)

    #     self.danger_right = self.check_danger(dir.swap() if dir.x != 0 else dir.swap().negate())

    #     self.danger_left = self.check_danger(dir.swap().negate() if dir.x != 0 else dir.swap())

    def check_danger(self, direction):
        # Check if the next cell in the given direction is dangerous (wall, snake's body, or obstacle)
        next_cell = self.game_engine.snake.head + direction
        return self.game_engine.is_wall(next_cell) or self.game_engine.is_snake_body(next_cell) or self.game_engine.is_obstacle(next_cell) or self.game_engine.is_bad_apple(next_cell)
 
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
        # head = self.game_engine.snake.head
        # neck = head if not len(self.game_engine.snake.body) > 0 else self.game_engine.snake.body[1]
        # current_direction = self.engine.snake.direction if head == neck else head - neck
        current_direction = self.game_engine.snake.direction
        if current_direction == Vec2(-1, 0):
            self.directions['west'] = 1
        elif current_direction == Vec2(1, 0):
            self.directions['east'] = 1
        elif current_direction == Vec2(0, -1):
            self.directions['north'] = 1
        elif current_direction == Vec2(0, 1):
            self.directions['south'] = 1