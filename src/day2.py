# Advent of Code 2019, Day 2
# (c) blu3r4y

from itertools import product

import numpy as np

from aocd.models import Puzzle
from funcy import print_calls


def intcode(ops, noun=12, verb=2, stop=None):
    ops[1], ops[2] = noun, verb

    for i in range(0, len(ops), 4):
        if ops[i] == 99:  # halt program
            break

        code, a, b, dest = ops[i:i + 4]

        if code == 1:  # addition
            ops[dest] = ops[a] + ops[b]
        elif code == 2:  # multiplication
            ops[dest] = ops[a] * ops[b]

        # early stopping if output equals stopcode
        if stop is not None and ops[0] == stop:
            return ops[0]

    return ops[0]


@print_calls
def part1(ops):
    return intcode(ops, 12, 2)


@print_calls
def part2(ops, stop=19690720):
    for noun, verb in product(range(0, 100), repeat=2):
        if intcode(ops.copy(), noun, verb, stop) == stop:
            return 100 * noun + verb


def load(data):
    return np.fromstring(data, sep=",", dtype=int)


if __name__ == "__main__":
    puzzle = Puzzle(year=2019, day=2)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
