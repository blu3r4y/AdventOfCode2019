# Advent of Code 2019, Day 19
# (c) blu3r4y

from bisect import bisect_left
from collections import defaultdict
from functools import lru_cache
from itertools import product
from math import ceil, log
from typing import Sequence

import matplotlib.pyplot as plt
from aocd.models import Puzzle
from funcy import print_calls, first

from gridtools import dict_to_array, complex_to_tuple, tuple_to_complex
from intcode import IntcodeMachine
from util import init_interactive_plot

FREE, BEAM = 0, 1


class TractorBeam(object):

    def __init__(self, drone: IntcodeMachine, visualize: bool = False):
        self.drone = drone
        self.grid = defaultdict(int)
        self.view = init_interactive_plot() if visualize else None

    def move(self, pos):
        # move the drone to the target position and save and return the observed cell state
        if pos not in self.grid:
            self.drone.reset()
            status = self.drone.execute(inputs=complex_to_tuple(pos), pop=True)
            self.grid[pos] = status

        return self.grid[pos]

    def map(self, size, until_fit=None):
        # efficiently map the entire beam up to a square of the requested size
        for ndia, dia in enumerate(zigzag(size)):
            seq = LazySeq(lambda i: self.move(tuple_to_complex(dia[i])) == BEAM, len(dia))
            bounds = fast_bounds(seq, 0, len(dia))

            # fill entire range
            if bounds is not None:
                for p in dia[slice(*bounds)]:
                    self.grid[tuple_to_complex(p)] = BEAM

            # cancel as soon as we can fit a box
            if until_fit is not None:
                match = self.fit_box(ndia, until_fit)
                if match is not None:
                    break

            if self.view is not None:
                self.plot()

    def fit_box(self, size, box):
        # brute-force all coordinates and check if a box fits within the beam
        for x, y in product(range(size), repeat=2):
            corners = [(x + dx, y + dy) for dx, dy in product([0, box - 1], repeat=2)]
            if all(self.grid.get(tuple_to_complex(corn), FREE) == BEAM for corn in corners):
                return x, y
        return None

    def plot(self):
        self.view.set_data(dict_to_array(self.grid.copy()).T)
        self.view.set_clim(vmin=0, vmax=1)  # reset value range

        plt.draw()
        plt.pause(.001)


class LazySeq(Sequence):

    @lru_cache(maxsize=None)
    def _get(self, i):
        return self.getter(i)

    def _idx(self, i):
        return i if not self.reverse else self.size - 1 - i

    def __getitem__(self, key):
        if isinstance(key, slice):
            return [self._get(self._idx(i)) for i in range(*key.indices(self.size))]
        elif key < 0:
            return self._get(self._idx(self.size + key))
        return self._get(self._idx(key))

    def __len__(self):
        return self.size

    def __reversed__(self):
        self.reverse = not self.reverse
        return self

    def __init__(self, getter, size, reverse=False):
        self.getter = getter
        self.size = size
        self.reverse = reverse


def zigzag(size):
    # return the coordinates of all diagonals within the requested square shape
    for n in range(1, size + 1):
        yield list(zip(range(n), reversed(range(n))))
    for n in range(1, size):
        yield list(zip(range(n, size), reversed(range(n, size))))


def fast_range(low, upr):
    fringe = set()
    for i in range(ceil(log(upr - low)) + 1):

        # cut the (upr - low) range into 2, 4, 8, 16, ... chunks
        inc = (upr - low) // (2 ** (i + 1))
        for number in range(low, upr, max(1, inc)):
            if number not in fringe:
                fringe.add(number)
                yield number


def fast_bounds(arr, low: int = None, upr: int = None):
    size = len(arr)

    low = low or 0
    upr = upr or size

    # find the first index where the function gives a positive result
    ctr = first(i for i in fast_range(low, upr) if arr[i])

    if ctr is None:
        return None  # no boundaries found

    # find the left and right boundaries
    a = bisect_left(arr, 1, lo=low, hi=ctr)
    b = size - bisect_left(reversed(arr), 1, lo=size - upr, hi=size - ctr)

    return a, b


@print_calls
def part1(program, size=50):
    beam = TractorBeam(IntcodeMachine(program))
    beam.map(size)

    return sum(e for e in beam.grid.values() if e == BEAM)


@print_calls
def part2(program, box=100):
    beam = TractorBeam(IntcodeMachine(program))

    beam.map(int(1E5), until_fit=box)
    match = beam.fit_box(int(1E5), box)
    if match is not None:
        x, y = match
        return x * 10000 + y


if __name__ == "__main__":
    puzzle = Puzzle(year=2019, day=19)

    ans1 = part1(puzzle.input_data)
    # puzzle.answer_a = ans1
    ans2 = part2(puzzle.input_data)
    # puzzle.answer_b = ans2
