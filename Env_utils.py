import random, time, cProfile, pstats, matplotlib.pyplot as plt
from IPython import display

class Profiler:
    def __init__(self) -> None:
        self.profiler = cProfile.Profile()
        self.profiler.enable()

    def get_stats(self) -> None:
        self.profiler.disable()
        self.stats = pstats.Stats(self.profiler).sort_stats('cumtime')
        self.stats.print_stats() 

    

class Vec2:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.reward = -1

    @property
    def zero(self) -> bool:
        return self.x == 0 and self.y == 0

    def negate(self) -> 'Vec2':
        return Vec2(-self.x, -self.y)
    
    def swap(self) -> 'Vec2':
        return Vec2(self.y, self.x)

    def __add__(self, other: 'Vec2') -> 'Vec2':
        if not isinstance(other, Vec2):
            return NotImplemented
        return Vec2(self.x + other.x, self.y + other.y)
    
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
    def __init__(self, scores, mean_scores) -> None:
        plt.ion()
        self.scores = scores
        self.mean_scores = mean_scores

    def plot(self) -> None:
        display.clear_output(wait=True)
        # display.display(plt.gcf())
        plt.clf()
        plt.title('Training...')
        plt.xlabel('Number of games')
        plt.ylabel('Score')
        plt.plot(self.scores)
        plt.plot(self.mean_scores)
        plt.ylim(ymin = 0)
        plt.text(len(self.scores) - 1, self.scores[-1], str(self.scores[-1]))
        plt.text(len(self.mean_scores) - 1, self.mean_scores[-1], str(self.mean_scores[-1]))