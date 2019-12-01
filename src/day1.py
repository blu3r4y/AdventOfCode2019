# Advent of Code 2019, Day 1
# (c) blu3r4y

import numpy as np

from aocd.models import Puzzle
from funcy import print_calls


@print_calls
def part1(masses):
    return np.sum(masses // 3 - 2)


@print_calls
def part2(masses):
    return sum(map(get_fuel, masses))


def get_fuel(mass):
    total, fuel = 0, mass
    while fuel > 0:
        fuel = max(0, fuel // 3 - 2)
        total += fuel
    return total


def load(data):
    return np.fromstring(data, sep="\n", dtype=int)


if __name__ == "__main__":
    puzzle = Puzzle(year=2019, day=1)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
