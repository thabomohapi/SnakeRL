import heapq
from Env_utils import Vec2

class Node:
    def __init__(self, position, parent = None) -> None:
        self.position = position
        self.parent = parent
        self.g = 0 # cost from start to current node 
        self.h = 0 # heuristic cost to goal
        self.f = 0 # total cost

    def __lt__(self, other) -> bool:
        return self.f < other.f
    
class Search:
    def __init__(self) -> None:
        pass

    def heuristic(pos, goal):
        # Use Manhattan distance as heuristic
        return abs(pos.x - goal.x) + abs(pos.y - goal.y)

    def a_star_search(self, start: 'Node', goal: 'Node', obstacles, grid_size):
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

        # Loop until the open list is empty
        while open_list:
            # Get the current node (node with the lowest f value)
            current_node = heapq.heappop(open_list)
            closed_list.add(current_node.position)

            # Check if we have reached the goal
            if current_node.position == goal:
                path = []
                while current_node is not None:
                    path.append(current_node.position)
                    current_node = current_node.parent
                return path[::-1]  # Return reversed path

            # Generate children (adjacent positions)
            children = []
            for new_position in [Vec2(0, -1), Vec2(0, 1), Vec2(-1, 0), Vec2(1, 0)]:  # Adjacent squares
                node_position = current_node.position + new_position

                # Make sure within range and not in obstacles
                if (node_position.x > (grid_size - 1) or
                    node_position.x < 0 or
                    node_position.y > (grid_size - 1) or
                    node_position.y < 0 or
                    node_position in obstacles):
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
                child.h = self.heuristic(child.position, goal)
                child.f = child.g + child.h

                # Child is already in the open list
                if any(open_node.position == child.position and child.g > open_node.g for open_node in open_list):
                    continue

                # Add the child to the open list
                heapq.heappush(open_list, child)

        return None  # No path found