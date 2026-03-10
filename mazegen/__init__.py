from mazegen.generator import (
    ALL_WALLS,
    DIR_CHAR,
    DIR_DELTA,
    EAST,
    MazeGenerator,
    MIN_MAZE_H,
    MIN_MAZE_W,
    NORTH,
    OPPOSITE,
    PATTERN_H,
    PATTERN_W,
    SOUTH,
    WEST,
)

__all__ = [
    "MazeGenerator",
    "NORTH", "EAST", "SOUTH", "WEST", "ALL_WALLS",
    "DIR_DELTA", "OPPOSITE", "DIR_CHAR",
    "PATTERN_W", "PATTERN_H", "MIN_MAZE_W", "MIN_MAZE_H",
]

__version__ = "1.0.0"
__author__ = '@jperez-s & @josjimen'
