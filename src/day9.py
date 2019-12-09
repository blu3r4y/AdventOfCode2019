# Advent of Code 2019, Day 9
# (c) blu3r4y

from intcode import IntcodeMachine

import numpy as np

from aocd.models import Puzzle
from funcy import print_calls


@print_calls
def part1(data):
    return IntcodeMachine(data).execute([1])


@print_calls
def part2(data):
    return IntcodeMachine(data).execute([2])


def load(data):
    return np.array(list(map(int, data.split(","))), dtype=np.int64)


if __name__ == "__main__":
    puzzle = Puzzle(year=2019, day=9)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
