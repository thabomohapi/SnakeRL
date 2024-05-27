import sys
from Env_utils import Vec2, random, time

class GameObject:
    def __init__(self, engine: object) -> None:
        self.engine = engine

    def draw(self) -> None:
        raise NotImplementedError("Draw method must be implemented!")
    
    def update(self) -> None:
        raise NotImplementedError("Update method must be implemented!")
    
class Snake(GameObject):
    def __init__(self, engine: object, size: int = 3) -> None:
        super().__init__(engine)
        self.init_snakeLength = size
        self.body = None
        self.reset()

    def update_head_tail(self):
        self.head = self.body[0]
        self.tail = self.body[-1]
        self.snakeLength = len(self.body)

    def draw(self) -> None:
        for block in self.body:
            color = (0, 11, 254) if block == self.head else (51, 153, 254)
            self.draw_block(block, color)

    def draw_block(self, block, color):
        rect = self.engine.e.Rect(int(block.x * self.engine.cell_size),
                           int(block.y * self.engine.cell_size),
                           self.engine.cell_size, self.engine.cell_size)
        self.engine.e.draw.rect(self.engine.screen, color, rect)

    def bad_block(self, block) -> bool:
        return self.engine.is_wall(block) or self.engine.is_obstacle(block) or self.engine.is_snake_body(block)

    def move(self) -> None:
        if self.shrink and len(self.body) > 1:
            self.body.pop()
            self.shrink = False
            self.score -= 1
        else:
            self.body.insert(0, self.head + self.direction)
            if self.grow: 
                self.score += 1
                self.grow = False
            else:
                self.body.pop()
                
        self.update_head_tail()

    def find_valid_starting_position(self) -> list:
        # Define the length of the snake to spawn
        snake_length = self.init_snakeLength
        # Get all possible starting positions
        all_possible_positions = set(Vec2(x, y) for x in range(self.engine.cell_number) for y in range(self.engine.cell_number))
        all_possible_positions = all_possible_positions - self.engine.occupied_positions
        # Filter out positions that don't have enough space for the snake's body
        valid_starting_positions = [pos for pos in all_possible_positions if self.has_enough_space(pos, self.init_snakeLength)]
        # Randomly choose one of the valid starting positions
        if valid_starting_positions:
            start_pos = random.choice(valid_starting_positions)
            # Create the snake's body based on the starting position
            body = [start_pos + Vec2(-i, 0) for i in range(snake_length)]
            # for block in body:
            #     self.engine.add_occupied_position(block)
            return body
        return None
    
    def has_enough_space(self, start_pos: 'Vec2', length: int) -> bool:
        # Check if there's enough unoccupied space to spawn the snake
        for i in range(length):
            next_pos = start_pos + Vec2(-i, 0)
            if not (0 <= next_pos.x < self.engine.cell_number and
                    0 <= next_pos.y < self.engine.cell_number and
                    next_pos not in self.engine.occupied_positions):
                return False
        return True

    def reset(self) -> None:
        # if self.body is not None:
        #     for block in self.body:
        #         self.engine.remove_occupied_position(block)
        # Find a valid starting position for the snake's head
        self.body = self.find_valid_starting_position()
        if self.body:
            self.direction = Vec2(0, 0)  # Set initial direction to stationary
            self.snakeLength = len(self.body)
            self.score = 0
            self.grow = False
            self.shrink = False
            self.death = False
            self.update_head_tail()
        else:
            print("No valid starting positions available to spawn the snake.")
            sys.exit()

class Food(GameObject):
    def __init__(self, is_good: bool, engine: object) -> None:
        super().__init__(engine)
        self.is_good = is_good
        self.last_update_time = time.time()
        self.update_interval = 20 # update position after every 20seconds
        self.position = None
        self.update_position()

    def update_position(self):
        valid_positions = self.find_valid_food_positions()
        if valid_positions:
            self.engine.remove_occupied_position(self.position)
            self.position = random.choice(valid_positions)
            self.position.reward = -1
            self.pos = (int(self.position.x * self.engine.cell_size), int(self.position.y * self.engine.cell_size))
            if self.is_good:
                self.position.reward = 10
            else: self.position.reward = -10
            # self.engine.add_occupied_position(self.position)
        else:
            print("No valid food positions available")
            self.engine.create_grid_representation()

    def find_valid_food_positions(self):
        # Get all possible positions on the board
        all_possible_positions = set(Vec2(x, y) for x in range(self.engine.cell_number) for y in range(self.engine.cell_number))
        # Filter out positions occupied by the snake or obstacles
        valid_positions = all_possible_positions - self.engine.occupied_positions
        # Filter out positions that would trap the snake
        # valid_positions = [pos for pos in valid_positions if self.is_reachable_by_snake(pos)]
        valid_positions = [pos for pos in valid_positions]
        return valid_positions
    
    def is_reachable_by_snake(self, pos: Vec2) -> bool:
        # Check if the position is reachable by the snake
        # i.e., not blocked by obstacles
        return pos not in self.engine.obstacles

    def draw(self) -> None:
        color = (0, 178, 0) if self.is_good else (139, 0, 0)
        # Calculate the center of the cell where the food will be drawn
        center_pos = (int(self.position.x * self.engine.cell_size + self.engine.cell_size // 2),
                      int(self.position.y * self.engine.cell_size + self.engine.cell_size // 2))
        # Draw a circle at the center_pos with a radius of half the cell size
        self.engine.e.draw.circle(self.engine.screen, color, center_pos, self.engine.cell_size // 2)

    def update(self, ate : bool = False, died: bool = False) -> None:
        if ate or died: 
            self.update_position()
            self.last_update_time = time.time()
            # print(state)
        else:
            current_time = time.time()
            if current_time - self.last_update_time > self.update_interval:
                self.update_position()
                self.last_update_time = current_time
                self.last_update_time = time.time()

class Obstacle(GameObject):
    def __init__(self, engine: object, num_blocks: int = 1, position: 'Vec2' = None, blocks: list = None) -> None:
        super().__init__(engine)
        self.num_blocks = num_blocks
        self.blocks = []
        self.blocks = self.generate_blocks(position) if blocks is None else blocks
    
    def generate_blocks(self, start_position: 'Vec2') -> list:
        if start_position is None:
            start_position = self.randomize_position()

        blocks = [start_position]
        for _ in range(1, self.num_blocks):
            # generate the rest of the blocks based on the start_position
            new_block = self.randomize_adjacent(blocks)
            blocks.append(new_block)
            
        self.update_occupied_positions()
        return blocks

    def randomize_position(self) -> 'Vec2':
        # randomize position ensuring it's not occupied by any of the existing game objects
        all_possible_positions = set(Vec2(x, y) for x in range(self.engine.cell_number - 1)
                                     for y in range(self.engine.cell_number - 1))
        unoccupied_positions = list(all_possible_positions - self.engine.occupied_positions)

        if unoccupied_positions: return random.choice(unoccupied_positions)
        else: raise ValueError("No unoccupied positions available for the obstacle")

    def randomize_adjacent(self, existing_blocks: list) -> None:
        # randomize a position adjacent to the existing blocks of the obstacle
        adjacent_positions = []
        for block in existing_blocks:
            potential_positions = [
                Vec2(block.x + 1, block.y),
                Vec2(block.x - 1, block.y),
                Vec2(block.x, block.y + 1),
                Vec2(block.x, block.y - 1)
            ]
            for pos in potential_positions:
                if pos not in self.engine.occupied_positions and pos not in existing_blocks and pos.x < self.engine.cell_number and pos.y < self.engine.cell_number:
                    adjacent_positions.append(pos)

        if adjacent_positions: return random.choice(adjacent_positions)
        else: ValueError("No adjacent positions available to place the obstacle block")

    def draw(self) -> None:
        color = (30, 30, 30)
        for block in self.blocks:
            rect = self.engine.e.Rect(int(block.x * self.engine.cell_size),
                                      int(block.y * self.engine.cell_size),
                                      self.engine.cell_size, self.engine.cell_size)
            self.engine.e.draw.rect(self.engine.screen, color, rect)

    def update_occupied_positions(self) -> None:
        for block in self.blocks:
            block.reward = -100
            self.engine.add_occupied_position(block)

    def find_further_position(self) -> 'Vec2':
        min_distance = self.engine.cell_size * 10
        attempts = 0
        while attempts < 100: # limit the number of attempts to find a position from distance
            position = self.randomize_position()
            if all(position.distance_to(other_block) >= min_distance for obstacle
                   in self.engine.obstacles for other_block in obstacle.blocks):
                return position
            attempts += 1
        raise ValueError("Failed to find positon for obstacle that is far enough from others.")

    def __rmul__(self, other) -> list:
        if isinstance(other, int):
            # return a list with 'other' number of Obstacle instances
            # make sure they are placed from a distance within each other
            obstacles = []
            for _ in range(other):
                position = self.find_further_position()
                obstacle = self.__class__(self.engine, self.num_blocks, position)
                obstacles.append(obstacle)
                # update the occupied positions with the new obstacle
                obstacle.update_occupied_positions()
            return obstacles
        return NotImplemented
    


# 1. ================================ Todo [Later On!] ================================
# class Obstacle:
#     def __init__(self, engine, position):
#         self.engine = engine
#         self.position = position
#         self.blocks = [position]  # List of positions this obstacle occupies

#     def draw(self):
#         # Draw the obstacle on the screen
#         pass

#     def update_occupied_positions(self):
#         # Update the set of occupied positions in the engine
#         for pos in self.blocks:
#             self.engine.add_occupied_position(pos)

# # Specialized obstacle types
# class Wall(Obstacle):
#     def __init__(self, engine, position, length, orientation):
#         super().__init__(engine, position)
#         self.length = length
#         self.orientation = orientation
#         self.create_wall()

#     def create_wall(self):
#         # Create a wall of blocks based on length and orientation
#         pass

#     def draw(self):
#         # Draw the wall on the screen
#         pass

# class MovingObstacle(Obstacle):
#     def __init__(self, engine, position, path):
#         super().__init__(engine, position)
#         self.path = path  # Path the obstacle will move along
#         self.current_path_index = 0

#     def move(self):
#         # Move the obstacle along its path
#         pass

#     def draw(self):
#         # Draw the moving obstacle on the screen
#         pass

# # How to add these obstacles to the game
# def add_obstacles(engine):
#     # Add a static wall
#     wall = Wall(engine, Vec2(5, 5), length=10, orientation='horizontal')
#     engine.obstacles.append(wall)

#     # Add a moving obstacle
#     moving_obstacle = MovingObstacle(engine, Vec2(10, 10), path=[Vec2(0, 1), Vec2(1, 0)])
#     engine.obstacles.append(moving_obstacle)

# 2. ============================ Todo [Power-Ups] =================================
# class PowerUp(GameObject):
#     def __init__(self, engine, position):
#         super().__init__(engine)
#         self.position = position
#         self.collected = False

#     def apply_effect(self, player):
#         # Apply the power-up effect to the player
#         pass

#     def draw(self):
#         # Draw the power-up on the screen
#         pass

# class SpeedBoost(PowerUp):
#     def apply_effect(self, player):
#         # Increase the player's speed
#         player.speed *= 1.5
#         # Set a timer to end the effect
#         self.engine.set_timer('speed_boost_end', 10)  # Ends after 10 seconds

# class ExtraLife(PowerUp):
#     def apply_effect(self, player):
#         # Give the player an extra life
#         player.lives += 1

# # Method of adding power-ups to the game
# def add_power_ups(engine):
#     # Add a speed boost power-up
#     speed_boost = SpeedBoost(engine, Vec2(10, 10))
#     engine.power_ups.append(speed_boost)

#     # Add an extra life power-up
#     extra_life = ExtraLife(engine, Vec2(15, 15))
#     engine.power_ups.append(extra_life)