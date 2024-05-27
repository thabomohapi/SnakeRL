import random, time, matplotlib.pyplot as plt, numpy as np
from IPython import display
class Vec2:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.reward = -1

    @property
    def zero(self) -> bool:
        return self.x == 0 and self.y == 0
    
    def to_list(self) -> list:
        return [self.x, self.y]

    def to_tuple(self):
        return (self.x, self.y)

    def negate(self) -> 'Vec2':
        return Vec2(-self.x, -self.y)
    
    def __neg__(self) -> 'Vec2':
        return Vec2(-self.x, -self.y)
    
    def swap(self) -> 'Vec2':
        return Vec2(self.y, self.x)
    
    def distance(self, other: 'Vec2') -> float:
        return np.linalg.norm(np.array(self.to_list()) - np.array(other.to_list()))
    
    def magnitude(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5
    
    def normalize(self):
        norm = (self.x ** 2 + self.y ** 2) ** 0.5
        if norm == 0:
            return Vec2(0, 0)  # Return a zero vector if the norm is zero
        return Vec2(self.x / norm, self.y / norm)

    def __add__(self, other: 'Vec2') -> 'Vec2':
        if not isinstance(other, Vec2):
            return NotImplemented
        return Vec2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Vec2') -> 'Vec2':
        if not isinstance(other, Vec2):
            return NotImplemented
        return self + -other
    
    def __mul__(self, other: float) -> 'Vec2':
        return Vec2(self.x * other, self.y * other)
    
    def __eq__(self, other: object) -> bool:
        return isinstance(other, Vec2) and self.x == other.x and self.y == other.y
    
    def __hash__(self) -> int:
        return hash((self.x, self.y))
    
    def __repr__(self) -> str:
        return f"Vec2({self.x}, {self.y})"
    
    def __str__(self) -> str:
        return f"Vec2({self.x}, {self.y})"
    

class Plotter:
    def __init__(self) -> None:
        plt.ion()
        self.fig = plt.figure() 

    def plot(self, scores, mean_scores) -> None:
        display.clear_output(wait=True)
        # display.display(plt.gcf())
        plt.clf()
        plt.title('Training...')
        plt.xlabel('Number of games')
        plt.ylabel('Score')
        plt.plot(scores)
        plt.plot(mean_scores)
        plt.ylim(ymin = 0)
        plt.text(len(scores) - 1, scores[-1], str(scores[-1]))
        plt.text(len(mean_scores) - 1, mean_scores[-1], str(mean_scores[-1]))

    def save(self) -> None:
        self.fig.savefig('training_progress.png', bbox_inches='tight')