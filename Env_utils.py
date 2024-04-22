import random, time

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