from collections import defaultdict
from copy import copy
from enum import IntEnum
from typing import Dict, Tuple, Union, Any, Iterable, Sequence

import matplotlib.pyplot as plt
import numpy as np


class ComplexGrid(object):
    class Direction(IntEnum):
        UP = 0
        RIGHT = 1
        DOWN = 2
        LEFT = 3

    class DirectionDiagonal(IntEnum):
        UP = 0
        UPRIGHT = 1
        RIGHT = 2
        DOWNRIGHT = 3
        DOWN = 4
        DOWNLEFT = 5
        LEFT = 6
        UPLEFT = 7

    def __init__(self, grid: Dict[complex, Any], bounds: Tuple[int, int] = None,
                 direction_order: Sequence[int] = None, diagonal_mode: bool = False):
        self.grid = grid
        self.bounds = bounds
        self.direction_order = direction_order if direction_order is not None else range(4)

        self.pos = 0
        self.face = 1j

        self.oldface = None
        self.oldpos = None

        if not diagonal_mode:
            self._offsets = np.array(
                [1j, 1 + 0j, -1j, -1 + 0j])[np.array(self.direction_order)]
        else:
            self._offsets = np.array(
                [1j, 1 + 1j, 1 + 0j, 1 - 1j, -1j, -1 - 1j, -1 + 0j, -1 + 1j])[np.array(self.direction_order)]

    def at(self, pos: complex):
        if isinstance(self.grid, defaultdict):
            return self.grid[pos]
        return self.grid.get(pos, None)

    def set(self, pos: complex, value: Any):
        self.grid[pos] = value
        return self

    def move(self, pos: complex = None, face: complex = None):
        if pos is not None:
            self.oldpos = copy(self.pos)
            self.pos = pos
        if face is not None:
            self.oldface = copy(self.face)
            self.face = face
        return self

    def offset(self, by: complex, face: complex = None):
        return self.move(self.pos + by, face=face)

    def move_in_face(self):
        return self.offset(self.face)

    def move_left(self):
        return self.offset(-1)

    def move_right(self):
        return self.offset(1)

    def move_up(self):
        return self.offset(1j)

    def move_down(self):
        return self.offset(-1j)

    def move_upleft(self):
        return self.move_up().move_left()

    def move_upright(self):
        return self.move_up().move_right()

    def move_downleft(self):
        return self.move_down().move_left()

    def move_downright(self):
        return self.move_down().move_right()

    @property
    def left(self):
        return self.at(self.pos - 1)

    @property
    def right(self):
        return self.at(self.pos + 1)

    @property
    def up(self):
        return self.at(self.pos + 1j)

    @property
    def down(self):
        return self.at(self.pos - 1j)

    @property
    def neighbors(self):
        return self.neighbor_values(remove_none=True)

    def neighbor_positions(self, exclude_pos: Iterable[complex] = None):
        if self.bounds is not None:
            return [self.pos + dxy for dxy in self._offsets if
                    (0 <= self.pos + dxy < self.bounds[0]) and
                    (0 <= self.pos + dxy < self.bounds[1]) and
                    (exclude_pos is None or self.pos + dxy not in exclude_pos)]
        else:
            return [self.pos + dxy for dxy in self._offsets if
                    (exclude_pos is None or self.pos + dxy not in exclude_pos)]

    def neighbor_values(self, exclude_pos: Iterable[complex] = None, exclude_val: Iterable[Any] = None,
                        remove_none: bool = False):
        neighbors = [self.at(pos) for pos in self.neighbor_positions(exclude_pos) if
                     (exclude_val is None or self.at(pos) not in exclude_val)]
        return neighbors if not remove_none else list(filter(lambda e: e is not None, neighbors))

    def neighbor_items(self, exclude_pos: Iterable[complex] = None, exclude_val: Iterable[Any] = None,
                       remove_none: bool = False):
        neighbors = [(pos, self.at(pos)) for pos in self.neighbor_positions(exclude_pos) if
                     (exclude_val is None or self.at(pos) not in exclude_val)]
        return neighbors if not remove_none else list(filter(lambda e: e[1] is not None, neighbors))

    def neighbor_indexes(self, exclude_pos: Iterable[complex] = None, exclude_val: Iterable[Any] = None,
                         include_val: Iterable[Any] = None):
        # note: exclusion has precedence over inclusion
        return [i for i, pos in enumerate(self.neighbor_positions()) if
                (include_val is None or self.at(pos) in include_val) and
                (exclude_val is None or self.at(pos) not in exclude_val) and
                (exclude_pos is None or pos not in exclude_pos) and
                self.at(pos) is not None]

    def plot(self):
        arr = dict_to_array(self.grid)
        plt.imshow(np.flip(arr.T))
        plt.show()


def dict_to_array(grid: Union[Dict[Tuple[int, int], Any], Dict[complex, Any]],
                  fill_value: Any = 0, origin: str = "upper left") -> np.ndarray:
    # map complex numbers to int tuples
    if not all(isinstance(key, tuple) for key in grid.keys()):
        grid = dict_complex_to_tuples(grid)

    # retrieve bounds and initialize a new empty grid
    keys = np.array(list(grid.keys()))
    (xmin, ymin), (xmax, ymax) = np.amin(keys, axis=0), np.amax(keys, axis=0)

    # fill grid cells
    result = np.full((xmax - xmin + 1, ymax - ymin + 1), fill_value=fill_value)
    for (x, y), value in grid.items():
        result[x - xmin, y - ymin] = value

    return rotate_array(result, origin)


def array_to_dict(grid: np.ndarray, use_tuples: bool = False, ignore_values: Iterable[Any] = None,
                  origin: str = "upper left") -> Union[Dict[Tuple[int, int], Any], Dict[complex, Any]]:
    ignore_values = ignore_values if ignore_values is not None else [0]

    # fill dictionary
    result = {}
    for (x, y), value in np.ndenumerate(rotate_array(grid, origin, inverse=True)):
        if value not in ignore_values:
            key = (x, y) if use_tuples else x + 1j * y
            result[key] = value

    return result


def text_to_array(text: Union[str, Iterable[str], Iterable[Iterable[str]]], use_ints: bool = True,
                  origin: str = "upper left", transpose: bool = True, flip: bool = True) -> np.ndarray:
    if isinstance(text, str):  # we got one large string
        text = [list(lines) for lines in text.split("\n")]
    else:  # we got a list of strings, or a list of list of individual characters
        text = [list(line) if isinstance(line, str) else line for line in list(text)]

    # check for equal line lengths
    lengths = np.array(list(map(len, text)))
    assert np.all(lengths == lengths[0]), "line lengths are not equal"

    if use_ints:
        text = [list(map(ord, line)) for line in text]

    result = np.array(text)
    result = rotate_array(result, origin)

    # transposing the axis system ensures that you can use (x, y) indexing order
    if transpose:
        result = result.T

    # flipping the axis system ensures that up and down is correctly assigned
    if flip:
        result = np.flip(result)

    return result


def dict_complex_to_tuples(grid: Dict[complex, Any]) -> Dict[Tuple[int, int], Any]:
    return {complex_to_tuple(key): val for key, val in grid.items()}


def dict_tuples_to_complex(grid: Dict[Tuple[int, int], Any]) -> Dict[complex, Any]:
    return {tuple_to_complex(key): val for key, val in grid.items()}


def complex_to_tuple(val: complex) -> Tuple[int, int]:
    return int(val.real), int(val.imag)


def tuple_to_complex(val: Tuple[int, int]) -> complex:
    return val[0] + 1j * val[1]


def rotate_array(grid: np.ndarray, origin: str = "lower left", inverse: bool = False) -> np.ndarray:
    origin = origin.replace("bot", "lower").replace("top", "upper")

    assert ("lower" in origin or "upper" in origin) and \
           ("left" in origin or "right" in origin), \
        "Specify the origin with 'lower' / 'upper' and 'left' / 'right' phrases"

    # align origin point
    if "upper" in origin:
        k = 0 if "left" in origin else 3
    elif "lower" in origin:
        k = 1 if "left" in origin else 2

    return np.rot90(grid, k=k if not inverse else -k)
