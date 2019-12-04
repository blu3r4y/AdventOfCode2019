# Advent of Code 2019, Day 4
# (c) blu3r4y

from itertools import groupby

import numpy as np

from aocd.models import Puzzle
from funcy import print_calls


def solve(start, stop, strict):
    return sum([1 for i in range(start, stop + 1) if is_valid(i, strict)])


@print_calls
def part1(start, stop):
    return solve(start, stop, strict=False)


@print_calls
def part2(start, stop):
    return solve(start, stop, strict=True)


def is_valid(num, strict):
    num = str(num)
    diff = np.diff([ord(e) for e in num])  # value differences
    rle = set(runlength(num))  # value run-lengths

    valid_rles = {2} if strict else {2, 3, 4, 5, 6}

    # monotonically increasing series and
    # duplicate (value with run-length 2 or higher exists)
    # (or only run-length 2 for strict duplicates)
    return np.all(diff >= 0) and len(valid_rles.intersection(rle)) > 0


def runlength(values):
    # count the run-length of consecutive values
    # (c) https://stackoverflow.com/a/1066838/927377
    return [len(list(grp)) for bit, grp in groupby(values) if bit]


def load(data):
    return tuple(map(int, data.split("-")))


if __name__ == "__main__":
    puzzle = Puzzle(year=2019, day=4)

    ans1 = part1(*load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(*load(puzzle.input_data))
    # puzzle.answer_b = ans2
