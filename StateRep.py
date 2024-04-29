import numpy as np

class StateRep:
    def __init__(self, game_engine):
        self.game_engine = game_engine
        self.grid_size = game_engine.cell_number  # Assuming a square grid
        self.grid = np.zeros((self.grid_size, self.grid_size), dtype=np.float32)
        # Additional state features
        self.relative_food_position = np.zeros(2, dtype=np.float32)
        self.relative_obstacle_position = np.zeros(2, dtype=np.float32)
        self.snake_direction = np.zeros(4, dtype=np.float32)  # [up, right, down, left]
        self.snake_head_position = np.zeros(2, dtype=np.float32)
        self.snake_body_positions = []

    def update(self):
        # Reset grid and additional features
        self.grid.fill(0)
        self.snake_body_positions = []

        # Update grid with snake's body
        for segment in self.game_engine.snake.body:
            if 0 <= segment.x < self.grid_size and 0 <= segment.y < self.grid_size:
                self.grid[segment.y, segment.x] = 1
                self.snake_body_positions.append((segment.x, segment.y))

        # Update grid with food
        for food in self.game_engine.fruits:
            if 0 <= food.position.x < self.grid_size and 0 <= food.position.y < self.grid_size:
                self.grid[food.position.y, food.position.x] = 2

        # Update grid with obstacles
        for obstacle in self.game_engine.obstacles:
            for block in obstacle.blocks:
                if 0 <= block.x < self.grid_size and 0 <= block.y < self.grid_size:
                    self.grid[block.y, block.x] = -1

        # Update additional features
        self.update_relative_food_position()
        self.update_relative_obstacle_position()
        self.update_snake_direction()
        self.update_snake_head_position()

        # Flatten the grid and concatenate additional features
        flat_grid = self.grid.flatten()
        state_vector = np.concatenate([
            flat_grid,
            self.relative_food_position,
            self.relative_obstacle_position,
            self.snake_direction,
            self.snake_head_position
        ])

        # Normalize the state vector
        state_vector = self.normalize_state(state_vector)

        return state_vector

    def update_relative_food_position(self):
        # Assuming the first food item in the list is the target
        food = self.game_engine.fruits[0]
        snake_head = self.game_engine.snake.head
        self.relative_food_position[0] = food.position.x - snake_head.x
        self.relative_food_position[1] = food.position.y - snake_head.y

    def update_relative_obstacle_position(self):
        # Find the nearest obstacle block to the snake's head
        snake_head = self.game_engine.snake.head
        min_distance = float('inf')
        nearest_obstacle = None
        for obstacle in self.game_engine.obstacles:
            for block in obstacle.blocks:
                distance = np.linalg.norm(np.array([block.x - snake_head.x, block.y - snake_head.y]))
                if distance < min_distance:
                    min_distance = distance
                    nearest_obstacle = block
        if nearest_obstacle:
            self.relative_obstacle_position[0] = nearest_obstacle.x - snake_head.x
            self.relative_obstacle_position[1] = nearest_obstacle.y - snake_head.y

    def update_snake_direction(self):
        # Update the direction vector based on the snake's current direction
        direction = self.game_engine.snake.direction
        if direction == self.game_engine.DIRECTIONS[0]:  # up
            self.snake_direction = np.array([1, 0, 0, 0])
        elif direction == self.game_engine.DIRECTIONS[1]:  # right
            self.snake_direction = np.array([0, 1, 0, 0])
        elif direction == self.game_engine.DIRECTIONS[2]:  # down
            self.snake_direction = np.array([0, 0, 1, 0])
        elif direction == self.game_engine.DIRECTIONS[3]:  # left
            self.snake_direction = np.array([0, 0, 0, 1])

    def update_snake_head_position(self):
        # Update the snake's head position
        snake_head = self.game_engine.snake.head
        self.snake_head_position[0] = snake_head.x
        self.snake_head_position[1] = snake_head.y

    def normalize_state(self, state_vector):
        # Normalize the state vector to the range [0, 1]
        # Assuming that the grid values are between -1 and 2
        # and the relative positions are within the grid size
        state_vector[:self.grid_size**2] = (state_vector[:self.grid_size**2] + 1) / 3  # Normalize grid values
        # Normalize relative positions
        state_vector[self.grid_size**2:] /= self.grid_size
        return state_vector