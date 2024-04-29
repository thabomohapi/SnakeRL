import heapq, random
from Env_utils import Vec2
from collections import deque

class Node:
    def __init__(self, position: 'Vec2', parent = None) -> None:
        self.position = position
        self.parent = parent
        self.g = 0 # cost from start to current node 
        self.h = 0 # heuristic cost to goal
        self.f = 0 # total cost

    def __lt__(self, other) -> bool:
        return self.f < other.f

# heuristic function using Chebyshev distance
def heuristic(pos, goal, voronoi_area, weight = 1.0):
    return (weight * (abs(pos.x - goal.x) + abs(pos.y - goal.y))) - voronoi_area

def generate_voronoi_map(start, obstacles, grid_size):
    # Initialize the Voronoi map with infinite distances
    voronoi_map = {Vec2(x, y): float('inf') for x in range(grid_size) for y in range(grid_size)}
    
    # Set the distance from the start node to itself as 0
    voronoi_map[start] = 0

    # Use a queue to perform a breadth-first search
    queue = deque([start])

    # Define possible movements (up, down, left, right)
    movements = [Vec2(0, -1), Vec2(0, 1), Vec2(-1, 0), Vec2(1, 0)]

    # Perform the breadth-first search
    while queue:
        current = queue.popleft()
        for move in movements:
            neighbor = current + move
            if (0 <= neighbor.x < grid_size and 0 <= neighbor.y < grid_size and
                neighbor not in obstacles and voronoi_map[neighbor] == float('inf')):
                voronoi_map[neighbor] = voronoi_map[current] + 1
                queue.append(neighbor)

    return voronoi_map

def generate_voronoi_area(start, obstacles,snake, grid_size):
    visited = set([start])
    queue = deque([start])
    area = 0

    while queue:
        current = queue.popleft()
        for direction in [Vec2(0, -1), Vec2(0, 1), Vec2(-1, 0), Vec2(1, 0)]:
            neighbor = current + direction
            if (0 <= neighbor.x < grid_size and
                0 <= neighbor.y < grid_size and
                neighbor not in obstacles and
                neighbor not in snake and
                neighbor not in visited):
                visited.add(neighbor)
                queue.append(neighbor)
                area += 1

    return area

def find_stalling_path(start, obstacles, grid_size):
    # Find the path that maximizes the distance traveled without hitting obstacles or borders
    path = [start]
    current_position = start
    visited = set([start])

    directions = [Vec2(0, -1), Vec2(0, 1), Vec2(-1, 0), Vec2(1, 0)]
    while True:
        next_steps = []
        for direction in directions:
            next_position = current_position + direction
            if (next_position.x >= 0 and next_position.x < grid_size and
                next_position.y >= 0 and next_position.y < grid_size and
                next_position not in obstacles and
                next_position not in visited):
                next_steps.append(next_position)

        if not next_steps:
            break  # No more steps available, end stalling

        # Choose the step that keeps the snake furthest from the walls and obstacles
        next_position = max(next_steps, key=lambda pos: min(pos.x, grid_size - 1 - pos.x, pos.y, grid_size - 1 - pos.y))
        path.append(next_position)
        current_position = next_position
        visited.add(next_position)

        # Check if the snake is about to trap itself
        if len(next_steps) == 1:
            break

    return path

def is_position_dangerous(head, pos, obstacles, grid_size):
    signal = 0
    for direction in [Vec2(0, -1), Vec2(0, 1), Vec2(-1, 0), Vec2(1, 0)]:
        neighbor = pos + direction
        if (neighbor.x > (grid_size - 1) or
            neighbor.x < 0 or
            neighbor.y > (grid_size - 1) or
            neighbor.y < 0 or
            neighbor in obstacles and
            neighbor != head 
        ):
            signal += 1
    if signal > 2:
        return True
    return False

def a_star_search(start: 'Vec2', goal: 'Vec2', obstacles, grid_size, snake, weight = 1.0):
    voronoi_area = generate_voronoi_area(goal, obstacles,snake, grid_size)
    # Create start and goal nodes
    start_node = Node(start, None)
    start_node.g = start_node.h = start_node.f = 0
    goal_node = Node(goal, None)
    goal_node.g = goal_node.h = goal_node.f = 0

    # Initialize open and closed lists
    open_list = []
    closed_list = set()

    # Add the start node to the open list
    heapq.heappush(open_list, start_node)

    stall = find_stalling_path(start, obstacles, grid_size)

    # Loop until the open list is empty
    while open_list:
        # Get the current node (node with the lowest f value)
        current_node = heapq.heappop(open_list)
        closed_list.add(current_node.position)

        # Check if we have reached the goal
        if current_node.position == goal:
            if voronoi_area >= (pow(grid_size, 2) * 0.1):
                path = []
                while current_node is not None:
                    path.append(current_node.position)
                    current_node = current_node.parent
                return path[::-1]  # Return reversed path
            else:
                return stall

        # Generate children (adjacent positions)
        children = []
        for new_position in [Vec2(0, -1), Vec2(0, 1), Vec2(-1, 0), Vec2(1, 0)]:  # Adjacent squares
            node_position = current_node.position + new_position

            # Make sure within range and not in obstacles
            if (node_position.x > (grid_size - 1) or
                node_position.x < 0 or
                node_position.y > (grid_size - 1) or
                node_position.y < 0 or
                node_position in obstacles or
                node_position in closed_list
            ):
                continue

            # Create new node and set parent
            new_node = Node(node_position, current_node)
            # Append to children list
            children.append(new_node)

        # Loop through children
        for child in children:
            # Child is on the closed list
            if child.position in closed_list:
                continue

            # Create the f, g, and h values
            child.g = current_node.g + 1
            child.h = heuristic(child.position, goal, voronoi_area, weight)
            child.f = child.g + child.h

            # Check if child is in the open list and if it has a higher g value
            in_open_list = False
            for open_node in open_list:
                if open_node.position == child.position:
                    in_open_list = True
                    if child.g > open_node.g:
                        break
            if in_open_list:
                continue

            # Add the child to the open list
            heapq.heappush(open_list, child)


    # # Path extensions when snake is trapped
    # if not open_list:
    #     # Find the largest open area using Voronoi regions
    #     max_voronoi_value = max(voronoi_map.values())
    #     largest_open_areas = [pos for pos, value in voronoi_map.items() if value == max_voronoi_value]
    #     if largest_open_areas:
    #         # Choose a random position from the largest open areas
    #         return [start, random.choice(largest_open_areas)]
    return stall