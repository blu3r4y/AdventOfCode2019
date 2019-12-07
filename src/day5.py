# Advent of Code 2019, Day 5
# (c) blu3r4y

from intcode import IntcodeMachine

import numpy as np
from aocd.models import Puzzle
from funcy import print_calls


@print_calls
def part1(ops):
    return IntcodeMachine(ops, [1]).execute()


@print_calls
def part2(ops):
    return IntcodeMachine(ops, [5]).execute()


def load(data):
    return np.fromstring(data, sep=",", dtype=int)


if __name__ == "__main__":
    puzzle = Puzzle(year=2019, day=5)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
