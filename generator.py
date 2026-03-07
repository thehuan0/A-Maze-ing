
import random
from collections import deque

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8
ALL_WALLS = NORTH | EAST | SOUTH | WEST

DIR_DELTA = {
    NORTH: (0, -1),
    EAST: (1, 0),
    SOUTH: (0, 1),
    WEST: (-1, 0),
}

OPPOSITE = {
    NORTH: SOUTH,
    EAST: WEST,
    SOUTH: NORTH,
    WEST: EAST,
}

DIR_CHAR = {NORTH: 'N', EAST: 'E', SOUTH: 'S', WEST: 'W'}


class MazeGenerator:
    """A basic perfect maze generator using DFS."""

    def __init__(self, width, height, entry, exit_):
        """Initialize the maze grid with all walls closed."""
        self.width = width
        self.height = height
        self.entry = entry
        self.exit_ = exit_
        self.rng = random.Random()

        self.grid = [[ALL_WALLS for _ in range(width)] for _ in range(height)]
        self.solution = []

    def generate(self):
        """Run the DFS algorithm to carve the maze, then solve it."""
        self._gen_dfs()
        self.solution = self._solve()

    def _carve(self, x, y, direction):
        """Remove the wall between (x,y) and the next cell."""
        dx, dy = DIR_DELTA[direction]
        nx, ny = x + dx, y + dy

        self.grid[y][x] &= ~direction
        self.grid[ny][nx] &= ~OPPOSITE[direction]

    def _gen_dfs(self):
        """Depth-First Search (Recursive Backtracker) algorithm."""
        visited = {self.entry}
        stack = [self.entry]

        while stack:
            cx, cy = stack[-1]

            dirs = list(DIR_DELTA.keys())
            self.rng.shuffle(dirs)

            moved = False
            for d in dirs:
                nx = cx + DIR_DELTA[d][0]
                ny = cy + DIR_DELTA[d][1]

                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if (nx, ny) not in visited:
                        self._carve(cx, cy, d)

                        visited.add((nx, ny))
                        stack.append((nx, ny))
                        moved = True
                        break

            if not moved:
                stack.pop()

    def _solve(self):
        """Find the shortest path from entry to exit using BFS."""
        queue = deque([self.entry])
        came_from = {self.entry: None}

        while queue:
            cx, cy = queue.popleft()

            if (cx, cy) == self.exit_:
                break

            for d, (dx, dy) in DIR_DELTA.items():
                nx, ny = cx + dx, cy + dy

                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if (nx, ny) not in came_from and not (self.grid[cy][cx] & d):
                        came_from[(nx, ny)] = ((cx, cy), d)
                        queue.append((nx, ny))

        path = []
        pos = self.exit_

        if pos not in came_from:
            return []

        while came_from[pos] is not None:
            prev_cell, direction = came_from[pos]
            path.append(DIR_CHAR[direction])
            pos = prev_cell

        return path[::-1]

    def get_hex_output(self):
        """Format the maze for the output file."""
        rows = [''.join(f'{cell:X}' for cell in row) for row in self.grid]
        path_str = ''.join(self.solution)

        ex, ey = self.entry
        xx, xy = self.exit_

        return '\n'.join(rows) + f"\n\n{ex},{ey}\n{xx},{xy}\n{path_str}\n"


if __name__ == "__main__":
    gen = MazeGenerator(5, 5, entry=(0, 0), exit_=(4, 4))
    gen.generate()
    print(gen.get_hex_output())
