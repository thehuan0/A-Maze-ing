"""Maze display: game loop, animated victory overlay, leaderboard."""
import json
import math
import os
import pathlib
import struct
import sys
import time
from typing import Any, Iterator, Optional

import mlx

from mazegen import (
    DIR_DELTA,
    EAST,
    MazeGenerator,
    NORTH,
    SOUTH,
    WEST,
)
from config.parser_config import Config

# cell and wall sizes
CELL_PX: int = 28
WALL_PX: int = 3

PALETTES: list[tuple[int, int, int]] = [
    (220, 220, 230),   # 0 – white  (default)
    (0, 0, 204),       # 1 – cyan
    (80, 230, 100),    # 2 – green
    (255, 210, 50),    # 3 – yellow
    (200, 70, 255),    # 4 – purple
    (255, 90, 70),     # 5 – red/orange
    (255, 80, 200),    # 6 – hot pink
]

HEART_PALETTE_IDX: int = 4   # 42 heart mode

COL_BG: tuple[int, int, int] = (0, 0, 0)
COL_PASSAGE: tuple[int, int, int] = (28, 28, 42)
COL_ENTRY: tuple[int, int, int] = (90, 255, 130)
COL_EXIT: tuple[int, int, int] = (255, 80, 80)
COL_PATH: tuple[int, int, int] = (40, 190, 255)
COL_PLAYER: tuple[int, int, int] = (255, 255, 0)
COL_GEN: tuple[int, int, int] = (180, 80, 255)

WHITE: tuple[int, int, int] = (255, 255, 255)
BLACK: tuple[int, int, int] = (0, 0, 0)
GOLD: tuple[int, int, int] = (255, 215, 0)
SILVER_C: tuple[int, int, int] = (192, 192, 192)
BRONZE: tuple[int, int, int] = (205, 127, 50)
DIM: tuple[int, int, int] = (100, 100, 100)
LB_HIGHLIGHT: tuple[int, int, int] = (90, 255, 130)
PINK: tuple[int, int, int] = (255, 80, 200)


# X11 key codes
KEY_R: int = 114
KEY_P: int = 112
KEY_C: int = 99
KEY_Q: int = 113
KEY_L: int = 108
KEY_ESC: int = 65307
KEY_W: int = 119
KEY_A: int = 97
KEY_S: int = 115
KEY_D: int = 100
KEY_UP: int = 65362
KEY_DOWN: int = 65364
KEY_LEFT: int = 65361
KEY_RIGHT: int = 65363

OVL_NONE: str = "NONE"
OVL_VICTORY: str = "VICTORY"
OVL_LEADERBOARD: str = "LEADERBOARD"

LEADERBOARD_TOP: int = 5
MAX_NAME_LEN: int = 10

# animation parameters
BOUNCE_AMP_WIN: int = 14
BOUNCE_AMP_SUB: int = 8
BOUNCE_AMP_TITLE: int = 10
BOUNCE_FREQ: float = 3.0
BOUNCE_PHASE: float = 0.35
COLOR_SPEED: float = 0.4
COLOR_SPREAD: float = 0.06

CURSOR_BLINK_HZ: float = 1.667

# leaderboard persistence
_LB_PATH: str = str(pathlib.Path(__file__).parent / 'leaderboard.json')

# 5x7 pixel bitmap font
# Each list entry is a row bitmask (7 rows).
# Bit 4 = leftmost column, bit 0 = rightmost column.
CHAR_COLS: int = 5
CHAR_ROWS: int = 7

_FONT: dict[str, list[int]] = {
    '0': [14, 17, 19, 21, 25, 17, 14],
    '1': [4, 12, 4, 4, 4, 4, 14],
    '2': [14, 17, 1, 6, 8, 16, 31],
    '3': [31, 1, 2, 6, 1, 17, 14],
    '4': [2, 6, 10, 18, 31, 2, 2],
    '5': [31, 16, 30, 1, 1, 17, 14],
    '6': [6, 8, 16, 30, 17, 17, 14],
    '7': [31, 1, 2, 4, 8, 8, 8],
    '8': [14, 17, 17, 14, 17, 17, 14],
    '9': [14, 17, 17, 15, 1, 2, 12],
    #  uppercase alphabet
    'A': [14, 17, 17, 31, 17, 17, 17],
    'B': [30, 17, 17, 30, 17, 17, 30],
    'C': [14, 17, 16, 16, 16, 17, 14],
    'D': [28, 18, 17, 17, 17, 18, 28],
    'E': [31, 16, 16, 30, 16, 16, 31],
    'F': [31, 16, 16, 30, 16, 16, 16],
    'G': [14, 17, 16, 23, 17, 17, 14],
    'H': [17, 17, 17, 31, 17, 17, 17],
    'I': [31, 4, 4, 4, 4, 4, 31],
    'J': [15, 2, 2, 2, 2, 18, 12],
    'K': [17, 18, 20, 24, 20, 18, 17],
    'L': [16, 16, 16, 16, 16, 16, 31],
    'M': [17, 27, 21, 17, 17, 17, 17],
    'N': [17, 25, 21, 19, 17, 17, 17],
    'O': [14, 17, 17, 17, 17, 17, 14],
    'P': [30, 17, 17, 30, 16, 16, 16],
    'Q': [14, 17, 17, 17, 21, 18, 13],
    'R': [30, 17, 17, 30, 18, 17, 17],
    'S': [14, 17, 16, 14, 1, 17, 14],
    'T': [31, 4, 4, 4, 4, 4, 4],
    'U': [17, 17, 17, 17, 17, 17, 14],
    'V': [17, 17, 17, 17, 17, 10, 4],
    'W': [17, 17, 17, 21, 21, 27, 17],
    'X': [17, 17, 10, 4, 10, 17, 17],
    'Y': [17, 17, 10, 4, 4, 4, 4],
    'Z': [31, 1, 2, 4, 8, 16, 31],
    '#': [10, 10, 31, 10, 31, 10, 10],
    '<': [2, 4, 8, 16, 8, 4, 2],
    '!': [4, 4, 4, 4, 4, 0, 4],
    '-': [0, 0, 0, 31, 0, 0, 0],
    ' ': [0, 0, 0, 0, 0, 0, 0],
}


#  leaderboard helpers

def _load_lb() -> list[dict[str, Any]]:
    """Load entries from leaderboard.json; return [] on any error."""
    try:
        with open(_LB_PATH, encoding='utf-8') as fh:
            data = json.load(fh)
        if isinstance(data, list):
            return data
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    return []


def _save_lb(entries: list[dict[str, Any]]) -> None:
    """Persist entries to leaderboard.json, ignoring IO errors."""
    try:
        with open(_LB_PATH, 'w', encoding='utf-8') as fh:
            json.dump(entries, fh, indent=2)
    except OSError:
        pass


def _top_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return top LEADERBOARD_TOP entries sorted by score."""
    return sorted(entries, key=lambda e: int(e.get(
        'score', 999_999
        )), reverse=True)[:LEADERBOARD_TOP]


def _fmt_time(secs: int) -> str:
    """Format seconds as 'XM YS' or 'YS'."""
    if secs >= 60:
        return f"{secs // 60}M {secs % 60}S"
    return f"{secs}S"


# pixel helpers

def _pack(r: int, g: int, b: int) -> int:
    """Pack RGB into a 32-bit ARGB integer for the MLX image buffer."""
    return (0xFF << 24) | (r << 16) | (g << 8) | b


def _mlx_col(r: int, g: int, b: int) -> int:
    """Pack RGB into the integer format expected by mlx.string_put."""
    return (r << 16) | (g << 8) | b


def _blit(
    buf: bytearray,
    sl: int,
    bpp: int,
    x: int,
    y: int,
    w: int,
    h: int,
    col: int,
    cw: int,
    ch: int,
) -> None:
    """Write a filled rectangle of a single colour into the MLX image buffer.

    Args:
        buf:     Raw image bytearray from mlx.get_data_addr.
        sl:      Stride bytes per image row.
        bpp:     Bits per pixel.
        x, y:    Top-left pixel position.
        w, h:    Width and height in pixels.
        col:     Packed ARGB colour integer.
        cw, ch:  Canvas dimensions for clipping.
    """
    bytes_per_pixel = bpp // 8
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(cw, x + w), min(ch, y + h)
    if x0 >= x1 or y0 >= y1:
        return
    row = struct.pack('<I', col) * (x1 - x0)
    for ry in range(y0, y1):
        s = ry * sl + x0 * bytes_per_pixel
        buf[s: s + len(row)] = row


def _rainbow(t: float) -> tuple[int, int, int]:
    """Return a smooth rainbow RGB colour at normalised position t.

    Uses three 120-degree-offset sine waves for a continuous hue cycle.

    Args:
        t: Cycle position (any real; wraps at 1.0).

    Returns:
        (R, G, B) tuple, each component in 0-255.
    """
    r = int(127.5 * (1.0 + math.sin(2.0 * math.pi * t)))
    g = int(127.5 * (1.0 + math.sin(2.0 * math.pi * (t + 1.0 / 3.0))))
    b = int(127.5 * (1.0 + math.sin(2.0 * math.pi * (t + 2.0 / 3.0))))
    return (r, g, b)


def _pink_purple(t: float, i: int) -> tuple[int, int, int]:
    """Return an oscillating pink-to-purple colour for heart-mode text.

    Args:
        t: Current time in seconds.
        i: Character index for per-char phase offset.

    Returns:
        (R, G, B) tuple cycling between hot pink and violet.
    """
    phase = t * COLOR_SPEED + i * COLOR_SPREAD
    mix = 0.5 + 0.5 * math.sin(2.0 * math.pi * phase)
    r = int(200 + 55 * mix)
    g = int(40 * (1.0 - mix))
    b = int(150 + 105 * mix)
    return (r, g, b)


def _prompt_name() -> str:
    """Ask the player to type their name in the terminal.

    Loops until a non-empty name (up to MAX_NAME_LEN characters) is
    entered, then returns it as uppercase.

    Returns:
        Validated, uppercase player name.
    """
    while True:
        try:
            raw = input(
                f"\nEnter your name for the leaderboard"
                f" (max {MAX_NAME_LEN} chars): "
            ).strip()
        except EOFError:
            raw = "PLAYER"
        if raw:
            return raw[:MAX_NAME_LEN].upper()
        print("Name cannot be empty, please try again.")


# display class

class MazeDisplay:
    """Graphical display for the maze using the MLX library.

    Handles maze rendering, player movement, solution-path toggle,
    wall-palette cycling, animated generation, victory animation,
    and a persistent leaderboard (heart mode only).
    """

    def __init__(self, cfg: Config) -> None:
        """Initialise all display state and start generating the first maze.

        Args:
            cfg: Parsed maze configuration dictionary.
        """
        self.W: int = cfg['width']
        self.H: int = cfg['height']
        self.entry: tuple[int, int] = cfg['entry_xy']
        self.exit_: tuple[int, int] = cfg['exit_xy']
        self.perfect: bool = cfg['perfect']
        self.algorithm: str = cfg['algorithm'] or 'dfs'
        self.out_file: str = cfg['output_file']
        self.seed: Optional[int] = cfg.get('seed')

        self.ww: int = self.W * CELL_PX + WALL_PX
        self.wh: int = self.H * CELL_PX + WALL_PX

        self.mlx = mlx.init()
        self.win = mlx.new_window(
            self.mlx, self.ww, self.wh, "A-Maze-ing"
        )
        self.img = mlx.new_image(self.mlx, self.ww, self.wh)
        d = mlx.get_data_addr(self.img)
        self.buf: bytearray = d[0]
        self.bpp: int = d[1]
        self.sl: int = d[2]

        self.pal_idx: int = (
            HEART_PALETTE_IDX if self.is_heart_mode else 0
        )
        self.show_path: bool = False
        self.overlay: str = OVL_NONE
        self.dirty: bool = True

        self.state: str = "PLAYING"
        self.player_pos: tuple[int, int] = self.entry
        self.move_count: int = 0

        self.grid: list[list[int]] = []
        self.path: set[tuple[int, int]] = set()
        self.pattern: set[tuple[int, int]] = set()
        self.heart_cells: set[tuple[int, int]] = set()

        self._gen: Optional[MazeGenerator] = None
        self._anim_iter: Optional[Iterator[list[list[int]]]] = None

        self._play_start: float = 0.0
        self._elapsed_secs: int = 0

        self._score_saved: bool = False
        self._current_entry_id: int = -1
        self._lb_entries: list[dict[str, Any]] = _load_lb()

        self._start_new_maze()

    @property
    def is_heart_mode(self) -> bool:
        """True when seed=42 and perfect=False (heart-shaped playable area)."""
        return self.seed == 42 and not self.perfect

    # maze management

    def _start_new_maze(self) -> None:
        """Begin animated generation of a new maze.

        In heart mode the pattern starts empty so the heart silhouette
        emerges naturally during animation. In standard mode the '42'
        digit block is pre-shown from the first frame.
        """
        self._gen = MazeGenerator(
            self.W, self.H, self.entry, self.exit_,
            self.perfect, self.seed, algorithm=self.algorithm,
        )
        self.pattern = (
            set()
            if self.is_heart_mode
            else MazeGenerator.pattern_cells(self.W, self.H)
        )
        self.heart_cells = set()
        self.grid = [[0xF] * self.W for _ in range(self.H)]
        self.path = set()
        self.show_path = False
        self.overlay = OVL_NONE
        self.state = "GENERATING"
        self.player_pos = self.entry
        self.move_count = 0
        self._play_start = 0.0
        self._elapsed_secs = 0
        self._score_saved = False
        self._current_entry_id = -1
        self.dirty = True
        self._anim_iter = self._gen.generate_steps()

    def _advance_animation(self) -> None:
        """
        Consume up to ANIM_STEPS_PER_TICK steps from the generation iterator.

        When the iterator is exhausted the display transitions to PLAYING
        and the finished maze is written to the output file.
        """
        if self._anim_iter is None or self._gen is None:
            return
        for _ in range(ANIM_STEPS_PER_TICK):
            try:
                self.grid = next(self._anim_iter)
                self.dirty = True
            except StopIteration:
                self.grid = self._gen.get_grid()
                self.pattern = self._gen.get_pattern_cells()
                self.heart_cells = self._gen.get_heart_cells()
                self.path = self._make_path(self._gen.get_solution())
                self.state = "PLAYING"
                self._play_start = time.time()
                self.dirty = True
                self._anim_iter = None
                self._write_output()
                return

    def _write_output(self) -> None:
        """Write the finished maze hex representation to the output file."""
        if self._gen is None:
            return
        try:
            with open(self.out_file, 'w', encoding='utf-8') as fh:
                fh.write(self._gen.get_hex_output())
        except OSError as exc:
            sys.stderr.write(
                f"Warning: could not write output file: {exc}\n"
            )

    def _make_path(self, sol: list[str]) -> set[tuple[int, int]]:
        """Convert a direction-string solution into a set of cell coordinates.

        Args:
            sol: List of 'N'/'E'/'S'/'W' direction characters.

        Returns:
            Set of (x, y) cells on the path, excluding the entry cell.
        """
        cells: set[tuple[int, int]] = set()
        x, y = self.entry
        dm = {'N': NORTH, 'E': EAST, 'S': SOUTH, 'W': WEST}
        for ch in sol:
            dx, dy = DIR_DELTA[dm[ch]]
            x += dx
            y += dy
            cells.add((x, y))
        return cells

    # leaderboard

    def _save_score(self, name: str) -> None:
        """Append the current run to leaderboard.json.

        Args:
            name: Player name (already validated, uppercase, max 10 chars).
        """
        entry_id = int(time.time() * 1000)
        entry: dict[str, Any] = {
            'id': entry_id,
            'name': name,
            'moves': self.move_count,
            'secs': self._elapsed_secs,
            'score': 2000 - (self.move_count * self._elapsed_secs),
        }
        self._lb_entries.append(entry)
        _save_lb(self._lb_entries)
        self._current_entry_id = entry_id

    def _score_in_top(self) -> bool:
        """Return True if the current entry appears in the top-5 leaderboard"""
        if self._current_entry_id == -1:
            return False
        top = _top_entries(self._lb_entries)
        return any(e.get('id') == self._current_entry_id for e in top)

    # drawing primitives

    def _r(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        col: tuple[int, int, int],
    ) -> None:
        """Blit a filled rectangle into the image buffer.

        Args:
            x, y: Top-left pixel position.
            w, h: Dimensions in pixels.
            col:  RGB colour tuple.
        """
        _blit(
            self.buf, self.sl, self.bpp,
            x, y, w, h, _pack(*col), self.ww, self.wh,
        )

    def _text_hud(self, x: int, y: int, col: tuple[int, int, int],
                  s: str) -> None:
        """Draw HUD text via mlx.string_put (gameplay/generating states only).

        This method is safe for states where redraws happen only on user
        input (no per-frame animation), so no flicker occurs.

        Args:
            x, y: Pixel position.
            col:  RGB colour tuple.
            s:    String to draw.
        """
        try:
            mlx.string_put(self.mlx, self.win, x, y, _mlx_col(*col), s)
        except Exception:
            pass

    def _draw_glyph(
        self,
        ch: str,
        px: int,
        py: int,
        col: tuple[int, int, int],
        scale: int,
    ) -> None:
        """Render one bitmap glyph into the image buffer.

        Unknown characters are silently skipped.

        Args:
            ch:    Character to render.
            px:    Left pixel position of the glyph.
            py:    Top pixel position of the glyph.
            col:   RGB fill colour.
            scale: Pixel size of each font bit.
        """
        rows = _FONT.get(ch)
        if rows is None:
            return
        for row_i, bits in enumerate(rows):
            for col_i in range(CHAR_COLS):
                if bits & (1 << (CHAR_COLS - 1 - col_i)):
                    self._r(
                        px + col_i * scale,
                        py + row_i * scale,
                        scale,
                        scale,
                        col,
                    )

    def _draw_str_buf(
        self,
        text: str,
        x: int,
        y: int,
        col: tuple[int, int, int],
        scale: int,
        gap: int = 1,
    ) -> None:
        """Render a string into the image buffer using the bitmap font.

        This avoids mlx.string_put entirely so there is no flicker when
        the image is pushed to the window on every frame.

        Args:
            text:  String to render (uppercase; unknown chars are skipped).
            x:     Left pixel position of the first character.
            y:     Top pixel position of the text.
            col:   RGB fill colour.
            scale: Pixel size of each font bit.
            gap:   Pixel gap between adjacent characters.
        """
        step = CHAR_COLS * scale + gap
        for i, ch in enumerate(text):
            self._draw_glyph(ch, x + i * step, y, col, scale)

    def _str_px_w(self, text: str, scale: int, gap: int = 1) -> int:
        """Return the pixel width of a rendered string.

        Args:
            text:  String to measure.
            scale: Glyph scale factor.
            gap:   Gap between characters in pixels.

        Returns:
            Total width in pixels (0 for empty strings).
        """
        if not text:
            return 0
        return len(text) * (CHAR_COLS * scale + gap) - gap

    def _draw_str_centered(
        self,
        text: str,
        y: int,
        col: tuple[int, int, int],
        scale: int,
        gap: int = 1,
    ) -> None:
        """Render a string centred horizontally in the window buffer.

        Args:
            text:  String to render.
            y:     Top pixel position.
            col:   RGB fill colour.
            scale: Glyph scale factor.
            gap:   Gap between characters in pixels.
        """
        w = self._str_px_w(text, scale, gap)
        x = max(0, (self.ww - w) // 2)
        self._draw_str_buf(text, x, y, col, scale, gap)

    def _draw_line_animated(
        self,
        text: str,
        y_base: int,
        scale: int,
        gap: int,
        amp: int,
        t: float,
        phase_offset: float = 0.0,
        heart_color: bool = False,
    ) -> None:
        """Render a centred animated-bounce text line into the image buffer.

        Each character bounces vertically on a sine wave and is coloured
        with a per-character rainbow or pink-purple hue shift.

        Args:
            text:         String to render.
            y_base:       Vertical baseline in pixels.
            scale:        Glyph scale factor.
            gap:          Pixel gap between glyphs.
            amp:          Vertical bounce amplitude in pixels.
            t:            Current time in seconds.
            phase_offset: Additional hue phase offset.
            heart_color:  If True, use pink-purple instead of full rainbow.
        """
        step = CHAR_COLS * scale + gap
        total_w = len(text) * step - gap
        x0 = max(0, (self.ww - total_w) // 2)
        for i, ch in enumerate(text):
            if heart_color:
                col = _pink_purple(t, i)
            else:
                hue = (
                    t * COLOR_SPEED + i * COLOR_SPREAD + phase_offset
                ) % 1.0
                col = _rainbow(hue)
            dy = int(amp * math.sin(t * BOUNCE_FREQ + i * BOUNCE_PHASE))
            self._draw_glyph(ch, x0 + i * step, y_base + dy, col, scale)

    # cell rendering

    def _draw_cell(self, cx: int, cy: int) -> None:
        """Render one maze cell and its north/west walls into the buffer.

        Args:
            cx: Column index of the cell (0-based).
            cy: Row index of the cell (0-based).
        """
        px, py = cx * CELL_PX, cy * CELL_PX
        cs, wt = CELL_PX, WALL_PX
        wc = PALETTES[self.pal_idx % len(PALETTES)]
        val = self.grid[cy][cx]

        if (cx, cy) in self.pattern and self.is_heart_mode:
            self._r(px, py, cs, cs, COL_BG)
            return

        if (cx, cy) == self.player_pos and self.state == "PLAYING":
            bg = COL_PLAYER
        elif (cx, cy) in self.pattern:
            bg = wc
        elif (cx, cy) == self.entry:
            bg = COL_ENTRY
        elif (cx, cy) == self.exit_:
            bg = COL_EXIT
        elif self.show_path and (cx, cy) in self.path:
            bg = COL_PATH
        elif self.state == "GENERATING" and val == 0xF:
            bg = COL_GEN
        else:
            bg = COL_PASSAGE

        self._r(px + wt, py + wt, cs - wt, cs - wt, bg)
        self._r(px, py, wt, wt, wc)
        self._r(px + wt, py, cs - wt, wt, wc if (val & NORTH) else bg)
        self._r(px, py + wt, wt, cs - wt, wc if (val & WEST) else bg)
        if cy == self.H - 1:
            self._r(px, py + cs, wt, wt, wc)
            self._r(
                px + wt, py + cs, cs - wt, wt,
                wc if (val & SOUTH) else bg,
            )
        if cx == self.W - 1:
            self._r(px + cs, py, wt, wt, wc)
            self._r(
                px + cs, py + wt, wt, cs - wt,
                wc if (val & EAST) else bg,
            )
        if cx == self.W - 1 and cy == self.H - 1:
            self._r(px + cs, py + cs, wt, wt, wc)

    def _draw_heart_boundary(self) -> None:
        """Repaint wall edges on heart cells that border the void."""
        wc = PALETTES[self.pal_idx % len(PALETTES)]
        for (cx, cy) in self.heart_cells:
            px, py = cx * CELL_PX, cy * CELL_PX
            cs, wt = CELL_PX, WALL_PX
            for d, (dx, dy) in DIR_DELTA.items():
                if (cx + dx, cy + dy) not in self.heart_cells:
                    if d == NORTH:
                        self._r(px, py, cs + wt, wt, wc)
                    elif d == SOUTH:
                        self._r(px, py + cs, cs + wt, wt, wc)
                    elif d == WEST:
                        self._r(px, py, wt, cs + wt, wc)
                    elif d == EAST:
                        self._r(px + cs, py, wt, cs + wt, wc)

    # overlay renders

    def _draw_victory_overlay(self, t: float) -> None:
        """Render the animated victory screen into the image buffer."""
        sc1, gap1 = 6, 3
        sc2, gap2 = 3, 2
        glyph_h1 = CHAR_ROWS * sc1
        glyph_h2 = CHAR_ROWS * sc2
        block_h = (
            glyph_h1 + BOUNCE_AMP_WIN
            ) + 24 + (glyph_h2 + BOUNCE_AMP_SUB)
        y1 = (self.wh - block_h) // 2 + BOUNCE_AMP_WIN
        y2 = y1 + glyph_h1 + BOUNCE_AMP_WIN + 24

        self._r(0, 0, self.ww, self.wh, BLACK)
        self._draw_line_animated(
            "YOU WIN", y1, sc1, gap1, BOUNCE_AMP_WIN, t,
            heart_color=self.is_heart_mode,
        )
        self._draw_line_animated(
            "YOU ARE A-MAZE-ING!", y2, sc2, gap2, BOUNCE_AMP_SUB, t,
            phase_offset=0.5, heart_color=self.is_heart_mode,
        )

        stats = (
            f"{self.move_count} STEPS"
            f"   {_fmt_time(self._elapsed_secs)}"
        )
        self._draw_str_centered(
            stats, y2 + glyph_h2 + BOUNCE_AMP_SUB + 20, GOLD, 2
        )

        if self.is_heart_mode:
            hint = "[L] LEADERBOARD   [R] NEW MAZE   [Q] QUIT"
        else:
            hint = "[R] NEW MAZE   [Q] QUIT"
        self._draw_str_centered(hint, self.wh - CHAR_ROWS * 2 - 12, DIM, 2)

    def _draw_leaderboard_overlay(self, t: float) -> None:
        """Render the leaderboard screen into the image buffer."""
        self._r(0, 0, self.ww, self.wh, BLACK)

        title_y = max(BOUNCE_AMP_TITLE + 6, self.wh // 10)
        self._draw_line_animated(
            "LEADERBOARD", title_y, 4, 2, BOUNCE_AMP_TITLE, t,
            heart_color=True,
        )

        sub_y = title_y + CHAR_ROWS * 4 + BOUNCE_AMP_TITLE + 10
        self._draw_str_centered("TOP 5  SCORE  STEPS  TIME", sub_y, DIM, 2)

        sep_y = sub_y + CHAR_ROWS * 2 + 10
        self._r(self.ww // 10, sep_y, 4 * self.ww // 5, 1, SILVER_C)

        sc, gap = 2, 1
        row_h = CHAR_ROWS * sc + 12
        table_y = sep_y + 10
        entries = _top_entries(self._lb_entries)

        if not entries:
            self._draw_str_centered("NO RECORDS YET", table_y + 10, DIM, 2)
        else:
            w_rank = self._str_px_w("#5", sc, gap) + 15
            w_name = self._str_px_w("X" * MAX_NAME_LEN, sc, gap) + 10
            w_score = self._str_px_w("9999 <", sc, gap) + 20
            w_steps = self._str_px_w("999", sc, gap) + 20
            w_time = self._str_px_w("99M 59S", sc, gap)

            total_table_w = w_rank + w_name + w_score + w_steps + w_time
            offset_x = (self.ww - total_table_w) // 2

            col_rank_x = offset_x
            col_name_x = col_rank_x + w_rank
            col_score_x = col_name_x + w_name
            col_steps_x = col_score_x + w_score
            col_time_x = col_steps_x + w_steps

            self._r(offset_x, sep_y, total_table_w, 1, SILVER_C)

            for rank, e in enumerate(entries, 1):
                is_cur = (
                    self._current_entry_id != -1 and e.get(
                        'id'
                        ) == self._current_entry_id
                        )
                name = str(e.get('name', '???'))[:MAX_NAME_LEN]
                score = int(e.get('score', e.get('moves', 0)))
                moves = int(e.get('moves', 0))
                secs = int(e.get('secs', 0))

                row_y = table_y + (rank - 1) * row_h
                entry_col = LB_HIGHLIGHT if is_cur else WHITE
                marker = " <" if is_cur else ""

                self._draw_str_buf(f"#{rank}", col_rank_x, row_y, DIM, sc, gap)
                self._draw_str_buf(name, col_name_x, row_y, entry_col, sc, gap)

                self._draw_str_buf(f"{score}{marker}", col_score_x, row_y,
                                   GOLD if is_cur else entry_col, sc, gap)

                self._draw_str_buf(f"{moves}", col_steps_x, row_y,
                                   DIM, sc, gap)
                self._draw_str_buf(_fmt_time(secs), col_time_x, row_y,
                                   DIM, sc, gap)

        self._draw_str_centered(
            "[L] BACK   [R] NEW MAZE   [Q] QUIT",
            self.wh - CHAR_ROWS * 2 - 12, DIM, 2,
        )

    # draw

    def _draw(self) -> None:
        """Redraw the full window.

        Overlays that animate every frame (VICTORY, LEADERBOARD) render
        everything into the image buffer before the single
        put_image_to_window call, eliminating flicker.

        Static states (GENERATING, PLAYING) may use mlx.string_put for the
        HUD since those screens only redraw on input events.
        """
        t = time.time()

        if self.overlay == OVL_LEADERBOARD:
            self._draw_leaderboard_overlay(t)
            mlx.put_image_to_window(self.mlx, self.win, self.img, 0, 0)
            self.dirty = False
            return

        # maze background
        self._r(0, 0, self.ww, self.wh, COL_BG)
        for cy in range(self.H):
            for cx in range(self.W):
                self._draw_cell(cx, cy)
        if self.is_heart_mode:
            self._draw_heart_boundary()

        if self.overlay == OVL_VICTORY:
            self._draw_victory_overlay(t)
            mlx.put_image_to_window(self.mlx, self.win, self.img, 0, 0)
            self.dirty = False
            return

        mlx.put_image_to_window(self.mlx, self.win, self.img, 0, 0)

        if self.state == "GENERATING":
            self._text_hud(4, 4, COL_GEN, "Generating...  [R] skip  [Q] quit")
        else:
            hud = "[R]egen  [P]ath  [C]olor  [Q]uit  WASD/arrows"
            if self.is_heart_mode:
                hud += "  [L] Leaderboard"
            self._text_hud(4, 4, WHITE, hud)

        self.dirty = False

    # game logic

    def attempt_move(self, dx: int, dy: int, wall_dir: int) -> None:
        """Move the player one cell if the wall in that direction is open.

        Args:
            dx:       Column delta (-1, 0, or 1).
            dy:       Row delta (-1, 0, or 1).
            wall_dir: Wall-bit constant (NORTH, EAST, SOUTH, or WEST).
        """
        if self.state != "PLAYING":
            return
        cx, cy = self.player_pos
        if not (self.grid[cy][cx] & wall_dir):
            self.player_pos = (cx + dx, cy + dy)
            self.move_count += 1
            self.dirty = True
            self._check_victory()

    def _check_victory(self) -> None:
        """Trigger the victory overlay when the player reaches the exit.

        In heart mode and only on the first victory for this maze, pause
        the MLX loop to ask the player's name via the terminal, save the
        score, then resume.
        """
        if self.player_pos != self.exit_:
            return
        self._elapsed_secs = int(time.time() - self._play_start)
        self.state = "VICTORY"
        self.overlay = OVL_VICTORY
        self.dirty = True

        if self.is_heart_mode and not self._score_saved:
            self._score_saved = True
            name = _prompt_name()
            self._save_score(name)
            self._lb_entries = _load_lb()

    def _quit_cleanly(self) -> None:
        """Flush streams and terminate the process.

        MLX hooks run inside ctypes C callbacks, so raising SystemExit
        only produces an ignored warning and does not actually quit.
        Flush Python-managed buffers explicitly first, then call
        os._exit() which terminates immediately at the C level.
        """
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(0)

    # input / event loop

    def on_key(self, key: int, _: object) -> int:
        """Handle a key-press event from the MLX event loop.

        Routing:
        - Q / ESC  : quit from any state.
        - R        : start a new maze (resets score_saved for next run).
        - LEADERBOARD overlay: L closes it; R and Q also active.
        - VICTORY overlay: L (heart mode) opens leaderboard.
        - PLAYING: movement, path toggle, colour, L (browse leaderboard).

        Args:
            key: X11 keysym of the pressed key.
            _:   Unused MLX parameter.

        Returns:
            0 as required by the MLX hook API.
        """
        if key in (KEY_Q, KEY_ESC):
            self._quit_cleanly()

        if key == KEY_R:
            self._start_new_maze()
            return 0

        if self.overlay == OVL_LEADERBOARD:
            if key == KEY_L:
                self.overlay = OVL_VICTORY
                self.dirty = True
            return 0

        if self.overlay == OVL_VICTORY:
            if key == KEY_L and self.is_heart_mode:
                self._lb_entries = _load_lb()
                self.overlay = OVL_LEADERBOARD
                self.dirty = True
            return 0

        if key in (KEY_W, KEY_UP):
            self.attempt_move(0, -1, NORTH)
        elif key in (KEY_S, KEY_DOWN):
            self.attempt_move(0, 1, SOUTH)
        elif key in (KEY_A, KEY_LEFT):
            self.attempt_move(-1, 0, WEST)
        elif key in (KEY_D, KEY_RIGHT):
            self.attempt_move(1, 0, EAST)
        elif key == KEY_P and self.state == "PLAYING":
            self.show_path = not self.show_path
            self.dirty = True
        elif key == KEY_C:
            self.pal_idx += 1
            self.dirty = True
        elif key == KEY_L and self.is_heart_mode:
            self._lb_entries = _load_lb()
            self.overlay = OVL_LEADERBOARD
            self.dirty = True
        return 0

    def on_loop(self, _: object) -> int:
        """Main loop callback: advance animation, animate overlays, redraw.

        - GENERATING  : advances the generator iterator each tick.
        - VICTORY     : animates every frame (dirty=True).
        - LEADERBOARD : animates every frame for title bounce.
        - PLAYING     : redraws only when self.dirty is set by input.

        Args:
            _: Unused MLX parameter.

        Returns:
            0 as required by the MLX hook API.
        """
        if self.state == "GENERATING":
            self._advance_animation()
        if self.overlay in (OVL_VICTORY, OVL_LEADERBOARD):
            self.dirty = True
        if self.dirty:
            self._draw()
        time.sleep(0.016)
        return 0

    def run(self) -> None:
        """Register MLX hooks and enter the event loop."""
        mlx.key_hook(self.win, self.on_key, None)
        mlx.loop_hook(self.mlx, self.on_loop, None)
        try:
            mlx.hook(self.win, 17, 0, lambda _: self._quit_cleanly(), None)
        except Exception:
            pass
        mlx.loop(self.mlx)


def run_display(cfg: Config) -> None:
    """Instantiate and run the maze display from a parsed configuration.

    Args:
        cfg: Parsed maze configuration dictionary produced by config_parse.
    """
    MazeDisplay(cfg).run()
