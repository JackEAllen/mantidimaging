from typing import List, Union


class CloseEnoughPoint:
    """
    Rounds down point values to the closest integers so it can be used as a pixel coordinate
    """
    __slots__ = ("y", "x")
    y: int
    x: int

    def __init__(self, points: List[Union[int, float]]):
        self.y = int(points[1])
        self.x = int(points[0])

    def __str__(self):
        return f"({self.x}, {self.y})"
