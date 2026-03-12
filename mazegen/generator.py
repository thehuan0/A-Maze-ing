"""
Maze generator DFS, Prim, Kruskal.
Heart mode (seed=42, perfect=False):
"""
import random
from collections import deque
from typing import Iterator, Optional

NORTH: int = 1
EAST: int = 2
SOUTH: int = 4
WEST: int = 8
ALL_WALLS: int = NORTH | EAST | SOUTH | WEST

DIR_DELTA: dict[int, tuple[int, int]] = {
    NORTH: (0, -1), EAST: (1, 0), SOUTH: (0, 1), WEST: (-1, 0),
}
OPPOSITE: dict[int, int] = {
    NORTH: SOUTH, EAST: WEST, SOUTH: NORTH, WEST: EAST,
}
DIR_CHAR: dict[int, str] = {
    NORTH: 'N', EAST: 'E', SOUTH: 'S', WEST: 'W',
}

# 42 pattern
PATTERN_H: int = 7
PATTERN_W: int = 11
MIN_MAZE_W: int = PATTERN_W + 4
MIN_MAZE_H: int = PATTERN_H + 2

_D4: list[list[int]] = [
    [1, 0, 0, 0, 1], [1, 0, 0, 0, 1], [1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1], [0, 0, 0, 0, 1], [0, 0, 0, 0, 1], [0, 0, 0, 0, 1],
]
_D2: list[list[int]] = [
    [0, 1, 1, 1, 0], [1, 0, 0, 0, 1], [0, 0, 0, 0, 1],
    [0, 0, 1, 1, 0], [0, 1, 0, 0, 0], [1, 0, 0, 0, 0], [1, 1, 1, 1, 1],
]

# heart shape
_HEART_ORIG_W: int = 13
_HEART_ORIG_H: int = 11
_HEART_SCALE: int = 2
_HEART_W: int = _HEART_ORIG_W * _HEART_SCALE
_HEART_H: int = _HEART_ORIG_H * _HEART_SCALE
MIN_HEART_W: int = _HEART_W + 4
MIN_HEART_H: int = _HEART_H + 2

_HEART_ORIG: list[list[int]] = [
    [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
    [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
    [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
]


def _build_pattern(ox: int, oy: int) -> set[tuple[int, int]]:
    """
    Build the set of cells that form the '42' obstacle pattern.

    Args:
        ox: Column offset for the left edge of the pattern.
        oy: Row offset for the top edge of the pattern.

    Returns:
        Set of (x, y) cell coordinates occupied by the '42' digits.
    """
    cells: set[tuple[int, int]] = set()
    for r in range(PATTERN_H):
        for c in range(5):
            if _D4[r][c]:
                cells.add((ox + c, oy + r))
            if _D2[r][c]:
                cells.add((ox + 6 + c, oy + r))
    return cells


def _build_heart(ox: int, oy: int) -> set[tuple[int, int]]:
    """Build the set of cells inside the heart silhouette.

    Args:
        ox: Column offset for the left edge of the heart bounding box.
        oy: Row offset for the top edge of the heart bounding box.

    Returns:
        Set of (x, y) cell coordinates that are inside the heart shape.
    """
    cells: set[tuple[int, int]] = set()
    for r in range(_HEART_ORIG_H):
        for c in range(_HEART_ORIG_W):
            if _HEART_ORIG[r][c]:
                for dr in range(_HEART_SCALE):
                    for dc in range(_HEART_SCALE):
                        cells.add((
                            ox + c * _HEART_SCALE + dc,
                            oy + r * _HEART_SCALE + dr,
                        ))
    return cells


# union-find

class _UF:
    """
    Path-compressed, union-by-rank disjoint-set data structure.
    Used by the Kruskal maze-generation algorithm to detect cycles.
    """

    def __init__(self, n: int) -> None:
        """Initialise n singleton sets numbered 0..n-1.
        Args:
            n: Number of elements.
        """
        self.p = list(range(n))
        self.r = [0] * n

    def find(self, x: int) -> int:
        """
        Find the representative of the set containing x.
        Uses path compression (halving variant).
        Args:
            x: Element to look up.
        Returns:
            Root representative of x's set.
        """
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a: int, b: int) -> bool:
        """
        Merge the sets containing a and b.
        Args:
            a: First element.
            b: Second element.
        Returns:
            True if a and b were in different sets (merge occurred),
            False if they were already in the same set.
        """
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.r[ra] < self.r[rb]:
            ra, rb = rb, ra
        self.p[rb] = ra
        if self.r[ra] == self.r[rb]:
            self.r[ra] += 1
        return True


class MazeGenerator:
    """
    Generate rectangular mazes using DFS, Prim, or Kruskal.
    - Full connectivity (all passable cells reachable from entry).
    - No 3x3 or larger open zone without a wall.
    - A '42' digit obstacle (or heart silhouette when seed=42, perfect=False).
    - Optional perfect mode: exactly one path between any two cells.

    Custom parameters:
        MazeGenerator(width, height, entry, exit_,
                      perfect=False, seed=None, algorithm='prim')
    """
    ALGORITHMS: tuple[str, ...] = ("dfs", "prim", "kruskal")

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit_: tuple[int, int],
        perfect: bool = True,
        seed: Optional[int] = None,
        algorithm: str = "dfs",
    ) -> None:
        """
        Initialise the generator without running it yet.
        Args:
            width:     Number of columns in the maze.
            height:    Number of rows in the maze.
            entry:     (x, y) coordinates of the entrance cell.
            exit_:     (x, y) coordinates of the exit cell.
            perfect:   If True, carve a spanning-tree maze (unique solution).
                       If False, add extra loop passages after carving.
            seed:      Random seed for reproducible mazes. None for random.
            algorithm: One of 'dfs', 'prim', or 'kruskal'.

        Raises:
            ValueError: If algorithm is not one of the supported values.
        """
        if algorithm not in self.ALGORITHMS:
            raise ValueError(f"algorithm must be one of {self.ALGORITHMS}")
        self.width = width
        self.height = height
        self.entry = entry
        self.exit_ = exit_
        self.perfect = perfect
        self.seed = seed
        self.algorithm = algorithm
        self._rng: random.Random = random.Random(seed)
        self._grid: list[list[int]] = []
        self._pattern: set[tuple[int, int]] = set()
        self._heart_cells: set[tuple[int, int]] = set()
        self._solution: list[str] = []

    def generate(self) -> None:
        """Generate the maze, consuming all intermediate steps."""
        for _ in self.generate_steps():
            pass

    def generate_steps(self) -> Iterator[list[list[int]]]:
        """
        Generate the maze incrementally, yielding the grid after each step.

        Each yielded value is a snapshot copy of the current wall grid,
        suitable for animated rendering. The final yield is the completed
        maze including the solved path.

        Yields:
            Snapshots of the wall grid (list[list[int]]) during carving.
        """
        self._rng = random.Random(self.seed)
        self._grid = [[ALL_WALLS] * self.width for _ in range(self.height)]
        self._place_pattern()

        if self.algorithm == "dfs":
            algo_iter = self._gen_dfs()
        elif self.algorithm == "prim":
            algo_iter = self._gen_prim()
        else:
            algo_iter = self._gen_kruskal()
        yield from algo_iter

        if not self.perfect:
            yield from self._add_loops()

        if self._heart_cells:
            self._seal_heart_boundary()

        self._solution = self._solve()
        yield [r[:] for r in self._grid]

    def get_grid(self) -> list[list[int]]:
        """
        Return a deep copy of the current wall grid.
        Each cell value is a bitmask: NORTH=1, EAST=2, SOUTH=4, WEST=8.
        A set bit means the wall in that direction is present (closed).

        Returns:
            list[list[int]] with dimensions [height][width].
        """
        return [r[:] for r in self._grid]

    def get_solution(self) -> list[str]:
        """
        Return the shortest path from entry to exit as direction characters.
        Returns:
            List of 'N', 'E', 'S', 'W' characters. Empty if no path exists.
        """
        return self._solution[:]

    def get_pattern_cells(self) -> set[tuple[int, int]]:
        """
        Return the set of impassable cells forming the '42' obstacle.
        Returns:
            Set of (x, y) cell coordinates that are blocked.
        """
        return self._pattern.copy()

    def get_heart_cells(self) -> set[tuple[int, int]]:
        """
        Return the set of playable cells inside the heart silhouette.
        Returns:
            Set of (x, y) cells inside the heart (empty in non-heart modes).
        """
        return self._heart_cells.copy()

    def get_hex_output(self) -> str:
        """
        Serialise the maze to the hex output-file format.
        Format: HEIGHT rows of WIDTH hex digits, then a blank line,
        then the entry coordinates, exit coordinates, and shortest path.

        Returns:
            Multi-line string ready to be written to the output file.
        """
        rows = [''.join(f'{c:X}' for c in row) for row in self._grid]
        path = ''.join(self._solution)
        ex, ey = self.entry
        xx, xy = self.exit_
        return '\n'.join(rows) + f"\n\n{ex},{ey}\n{xx},{xy}\n{path}\n"

    @staticmethod
    def pattern_cells(width: int, height: int) -> set[tuple[int, int]]:
        """
        Return the '42' obstacle cells for a maze of the given dimensions.

        Useful for pre-validating entry/exit positions before constructing
        a full generator instance.

        Args:
            width:  Number of columns in the maze.
            height: Number of rows in the maze.

        Returns:
            Set of blocked (x, y) cells, or empty set if maze is too small.
        """
        if width < MIN_MAZE_W or height < MIN_MAZE_H:
            return set()
        ox = (width - PATTERN_W) // 2
        oy = (height - PATTERN_H) // 2
        return _build_pattern(ox, oy)

    def _place_pattern(self) -> None:
        """
        Populate self._pattern (and self._heart_cells for heart mode).

        In heart mode (seed=42, perfect=False, maze large enough), the
        pattern is the complement of the heart silhouette.  Otherwise, the
        standard '42' digit obstacle is placed in the centre.
        """
        if self.seed == 42 and not self.perfect:
            if self.width >= MIN_HEART_W and self.height >= MIN_HEART_H:
                ox = (self.width - _HEART_W) // 2
                oy = (self.height - _HEART_H) // 2
                self._heart_cells = _build_heart(ox, oy)
                self._pattern = {
                    (x, y)
                    for y in range(self.height)
                    for x in range(self.width)
                    if (x, y) not in self._heart_cells
                }
                return
        if self.width < MIN_MAZE_W or self.height < MIN_MAZE_H:
            return
        ox = (self.width - PATTERN_W) // 2
        oy = (self.height - PATTERN_H) // 2
        self._pattern = _build_pattern(ox, oy)

    def _seal_heart_boundary(self) -> None:
        """
        Re-close any wall bit facing outside the heart after loop carving.

        The carving algorithms never visit _pattern cells, but _add_loops
        could occasionally leave a cleared wall bit on a boundary cell.
        This pass enforces a clean silhouette.
        """
        for (x, y) in self._heart_cells:
            for d, (dx, dy) in DIR_DELTA.items():
                nx, ny = x + dx, y + dy
                if (nx, ny) not in self._heart_cells:
                    self._grid[y][x] |= d

    def _ok(self, x: int, y: int) -> bool:
        """
        Return True if (x, y) is a valid, passable cell.
        Args:
            x: Column index.
            y: Row index.

        Returns:
            True if the cell is inside the maze bounds and not in the pattern.
        """
        return (
            0 <= x < self.width
            and 0 <= y < self.height
            and (x, y) not in self._pattern
        )

    def _carve(self, x: int, y: int, d: int) -> None:
        """
        Remove the wall between (x, y) and its neighbour in direction d.

        Always updates both sides of the shared wall to keep the grid
        coherent: cell (x, y) loses its d-wall and the neighbour loses the
        opposite wall.

        Args:
            x: Column of the source cell.
            y: Row of the source cell.
            d: Direction constant (NORTH, EAST, SOUTH, or WEST).
        """
        nx, ny = x + DIR_DELTA[d][0], y + DIR_DELTA[d][1]
        self._grid[y][x] &= ~d
        self._grid[ny][nx] &= ~OPPOSITE[d]

    def _makes_3x3(self, x: int, y: int, d: int) -> bool:
        """
        Check whether carving the wall at (x, y, d) would create a 3x3 zone.

        The check works by tentatively carving the wall, scanning the
        neighbourhood for any 3x3 block of cells that has no internal walls,
        then rolling back the carve. The grid is restored even if an
        unexpected exception occurs because the rollback is unconditional.

        Args:
            x: Column of the source cell.
            y: Row of the source cell.
            d: Direction to carve.

        Returns:
            True if the carve would produce a forbidden open zone.
        """
        nx, ny = x + DIR_DELTA[d][0], y + DIR_DELTA[d][1]
        self._grid[y][x] &= ~d
        self._grid[ny][nx] &= ~OPPOSITE[d]
        found = False
        for bx in range(max(0, x - 2), min(self.width - 2, x + 1)):
            for by in range(max(0, y - 2), min(self.height - 2, y + 1)):
                h = all(
                    not (self._grid[by + r][bx + c] & EAST)
                    for r in range(3) for c in range(2)
                )
                v = all(
                    not (self._grid[by + r][bx + c] & SOUTH)
                    for r in range(2) for c in range(3)
                )
                if h and v:
                    found = True
                    break
            if found:
                break
        self._grid[y][x] |= d
        self._grid[ny][nx] |= OPPOSITE[d]
        return found

    def _safe_carve(self, x: int, y: int, d: int) -> bool:
        """
        Carve the wall only if doing so does not create a 3x3 open zone.

        Args:
            x: Column of the source cell.
            y: Row of the source cell.
            d: Direction to carve.

        Returns:
            True if the wall was successfully carved, False if refused.
        """
        if self._makes_3x3(x, y, d):
            return False
        self._carve(x, y, d)
        return True

    def _start(self) -> tuple[int, int]:
        """
        Return a valid starting cell for carving (preferably the entry).
        Falls back to the first passable cell if entry is inside the pattern.

        Returns:
            (x, y) coordinates of the carving start cell.
        """
        if self.entry not in self._pattern:
            return self.entry
        return next(
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if (x, y) not in self._pattern
        )

    def _gen_dfs(self) -> Iterator[list[list[int]]]:
        """
        Carve the maze using iterative DFS (recursive backtracker).
        Yields:
            Intermediate grid snapshots every 3 steps.
        """
        visited: set[tuple[int, int]] = {self._start()}
        stack: list[tuple[int, int]] = [self._start()]
        step = 0
        while stack:
            cx, cy = stack[-1]
            dirs = list(DIR_DELTA.keys())
            self._rng.shuffle(dirs)
            moved = False
            for d in dirs:
                nx, ny = cx + DIR_DELTA[d][0], cy + DIR_DELTA[d][1]
                if self._ok(nx, ny) and (nx, ny) not in visited:
                    if self._safe_carve(cx, cy, d):
                        visited.add((nx, ny))
                        stack.append((nx, ny))
                        moved = True
                        step += 1
                        if step % 3 == 0:
                            yield [r[:] for r in self._grid]
                        break
            if not moved:
                stack.pop()

    def _gen_prim(self) -> Iterator[list[list[int]]]:
        """
        Carve the maze using a randomised Prim's algorithm.
        Yields:
            Intermediate grid snapshots every 3 steps.
        """
        in_maze: set[tuple[int, int]] = {self._start()}
        frontier: list[tuple[int, int, int]] = []
        step = 0

        def add(x: int, y: int) -> None:
            """Add all unvisited neighbours of (x, y) to the frontier."""
            for d in DIR_DELTA:
                nx, ny = x + DIR_DELTA[d][0], y + DIR_DELTA[d][1]
                if self._ok(nx, ny) and (nx, ny) not in in_maze:
                    frontier.append((x, y, d))

        add(*self._start())
        while frontier:
            i = self._rng.randrange(len(frontier))
            frontier[i], frontier[-1] = frontier[-1], frontier[i]
            fx, fy, fd = frontier.pop()
            nx, ny = fx + DIR_DELTA[fd][0], fy + DIR_DELTA[fd][1]
            if (nx, ny) in in_maze:
                continue
            if self._safe_carve(fx, fy, fd):
                in_maze.add((nx, ny))
                add(nx, ny)
                step += 1
                if step % 3 == 0:
                    yield [r[:] for r in self._grid]

    def _gen_kruskal(self) -> Iterator[list[list[int]]]:
        """
        Carve the maze using a randomised Kruskal's algorithm.
        Yields:
            Intermediate grid snapshots every 3 steps.
        """
        edges: list[tuple[int, int, int]] = []
        for y in range(self.height):
            for x in range(self.width):
                if not self._ok(x, y):
                    continue
                if self._ok(x + 1, y):
                    edges.append((x, y, EAST))
                if self._ok(x, y + 1):
                    edges.append((x, y, SOUTH))
        self._rng.shuffle(edges)
        uf = _UF(self.width * self.height)
        step = 0
        for ex, ey, ed in edges:
            nx, ny = ex + DIR_DELTA[ed][0], ey + DIR_DELTA[ed][1]
            a = ey * self.width + ex
            b = ny * self.width + nx
            if uf.find(a) != uf.find(b):
                if self._safe_carve(ex, ey, ed):
                    uf.union(a, b)
                    step += 1
                    if step % 3 == 0:
                        yield [r[:] for r in self._grid]

    def _add_loops(self) -> Iterator[list[list[int]]]:
        """
        Remove a fraction of remaining walls to add extra passages.
        Yields:
            Intermediate grid snapshots every 5 removals.
        """
        cands = [
            (x, y, d)
            for y in range(self.height)
            for x in range(self.width)
            if (x, y) not in self._pattern
            for d in (EAST, SOUTH)
            if self._ok(
                x + DIR_DELTA[d][0],
                y + DIR_DELTA[d][1],
            )
            and bool(self._grid[y][x] & d)
        ]
        self._rng.shuffle(cands)
        step = 0
        for wx, wy, d in cands[:max(1, len(cands) // 7)]:
            if self._grid[wy][wx] & d:
                if self._safe_carve(wx, wy, d):
                    step += 1
                    if step % 5 == 0:
                        yield [r[:] for r in self._grid]

    def _solve(self) -> list[str]:
        """
        Find the shortest path from entry to exit using BFS.

        Returns:
            List of direction characters ('N', 'E', 'S', 'W') describing
            the shortest path, or an empty list if no path exists.
        """
        queue: deque[tuple[int, int]] = deque([self.entry])
        came: dict[
            tuple[int, int],
            Optional[tuple[tuple[int, int], int]],
        ] = {self.entry: None}
        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) == self.exit_:
                break
            for d, (dx, dy) in DIR_DELTA.items():
                nx, ny = cx + dx, cy + dy
                if (
                    0 <= nx < self.width
                    and 0 <= ny < self.height
                    and (nx, ny) not in came
                    and not (self._grid[cy][cx] & d)
                ):
                    came[(nx, ny)] = ((cx, cy), d)
                    queue.append((nx, ny))
        if self.exit_ not in came:
            return []
        path: list[str] = []
        pos: tuple[int, int] = self.exit_
        while came[pos] is not None:
            info = came[pos]
            assert info is not None
            path.append(DIR_CHAR[info[1]])
            pos = info[0]
        return path[::-1]
