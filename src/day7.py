# Advent of Code 2019, Day 7
# (c) blu3r4y

from intcode import IntcodeMachine

from itertools import permutations

import numpy as np

from aocd.models import Puzzle
from funcy import print_calls


def execute_series(ops, seq):
    a = IntcodeMachine(ops.copy(), [seq[0], 0]).execute()
    b = IntcodeMachine(ops.copy(), [seq[1], a]).execute()
    c = IntcodeMachine(ops.copy(), [seq[2], b]).execute()
    d = IntcodeMachine(ops.copy(), [seq[3], c]).execute()
    e = IntcodeMachine(ops.copy(), [seq[4], d]).execute()
    return e


def execute_loop(ops, seq):
    # create vms and initialize them with their sequence number
    vms = [IntcodeMachine(ops.copy()) for _ in seq]
    for vm, sid in zip(vms, seq):
        assert vm.execute([sid]) is None

    # run until all vms are done
    output = 0
    while not all([vm.done for vm in vms]):
        for vm in vms:
            output = vm.execute([output])  # set input to previous output

    return vms[-1].get_output()


@print_calls
def part1(ops):
    return max([execute_series(ops, seq) for seq in permutations([0, 1, 2, 3, 4])])


@print_calls
def part2(ops):
    return max([execute_loop(ops, seq) for seq in permutations([5, 6, 7, 8, 9])])


def load(data):
    return np.array(list(map(int, data.split(","))), dtype=int)


if __name__ == "__main__":
    puzzle = Puzzle(year=2019, day=7)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
