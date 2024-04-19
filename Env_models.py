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

    def move(self) -> None:
        if self.shrink and len(self.body) > 1:
            self.body.pop()
            self.engine.remove_occupied_position(self.tail)
            self.shrink = False
            self.score -= 1
        else:
            self.body.insert(0, self.head + self.direction)
            self.engine.add_occupied_position(self.body[0])
            if self.grow: 
                self.score += 1
                self.grow = False
            else:
                self.body.pop()
                self.engine.remove_occupied_position(self.tail)
                
        self.update_head_tail()

    def find_valid_starting_position(self) -> list:
        # Define the length of the snake to spawn
        snake_length = 3
        # Get all possible starting positions
        all_possible_positions = set(Vec2(x, y) for x in range(self.engine.cell_number) for y in range(self.engine.cell_number))
        # Filter out positions that don't have enough space for the snake's body
        valid_starting_positions = [pos for pos in all_possible_positions if self.has_enough_space(pos, snake_length)]
        # Randomly choose one of the valid starting positions
        if valid_starting_positions:
            start_pos = random.choice(valid_starting_positions)
            # Create the snake's body based on the starting position
            return [start_pos + Vec2(-i, 0) for i in range(snake_length)]
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
        # Find a valid starting position for the snake's head
        self.body = self.find_valid_starting_position()
        if self.body:
            self.direction = Vec2(0, 0)  # Set initial direction to stationary
            self.snakeLength = len(self.body)
            self.score = self.snakeLength
            self.grow = False
            self.shrink = False
            self.death = False
            for pos in self.body:
                self.engine.add_occupied_position(pos)
            self.update_head_tail()
        else:
            print("No valid starting positions available to spawn the snake.")

class Food(GameObject):
    def __init__(self, is_good: bool, engine: object) -> None:
        super().__init__(engine)
        self.is_good = is_good
        self.last_update_time = time.time() if not is_good else None
        self.update_interval = 20 if not is_good else None# update position after every 20seconds
        self.update_position()

    def update_position(self):
        all_possible_positions = set(Vec2(x, y) for x in range(self.engine.cell_number) for y in range(self.engine.cell_number))
        unoccupied_positions = list(all_possible_positions - self.engine.occupied_positions)

        if unoccupied_positions:
            self.position = random.choice(unoccupied_positions)
            self.pos = (int(self.position.x * self.engine.cell_size), int(self.position.y * self.engine.cell_size))
            self.engine.add_occupied_position(self.position)
        else:
            print("No unoccupied positions available")

    def draw(self) -> None:
        color = (0, 178, 0) if self.is_good else (139, 0, 0)
        # Calculate the center of the cell where the food will be drawn
        center_pos = (int(self.position.x * self.engine.cell_size + self.engine.cell_size // 2),
                      int(self.position.y * self.engine.cell_size + self.engine.cell_size // 2))
        # Draw a circle at the center_pos with a radius of half the cell size
        self.engine.e.draw.circle(self.engine.screen, color, center_pos, self.engine.cell_size // 2)

    def update(self, ate : bool = False, died: bool = False) -> None:
        if self.is_good or ate or died: self.update_position()
        else:
            current_time = time.time()
            if current_time - self.last_update_time > self.update_interval:
                self.update_position()
                self.last_update_time = current_time
                self.last_update_time = time.time()

class Obstacle(GameObject):
    def __init__(self, engine: object, num_blocks: int, position: 'Vec2' = None) -> None:
        super().__init__(engine)
        self.num_blocks = num_blocks
        self.blocks = []
        self.blocks = self.generate_blocks(position)
    
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
        all_possible_positions = set(Vec2(x, y) for x in range(self.engine.cell_number)
                                     for y in range(self.engine.cell_number))
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
                if pos not in self.engine.occupied_positions and pos not in existing_blocks:
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
            self.engine.add_occupied_position(block)

    def find_further_position(self) -> 'Vec2':
        min_distance = self.engine.cell_size * 6
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