# Advent of Code 2019, Day 7
# (c) blu3r4y

from itertools import permutations

from aocd.models import Puzzle
from funcy import print_calls

from intcode import IntcodeMachine


def execute_series(ops, seq):
    a = IntcodeMachine(ops, [seq[0], 0]).execute(nopause=True)
    b = IntcodeMachine(ops, [seq[1], a]).execute(nopause=True)
    c = IntcodeMachine(ops, [seq[2], b]).execute(nopause=True)
    d = IntcodeMachine(ops, [seq[3], c]).execute(nopause=True)
    e = IntcodeMachine(ops, [seq[4], d]).execute(nopause=True)
    return e


def execute_loop(ops, seq):
    # create vms and initialize them with their sequence number
    vms = [IntcodeMachine(ops) for _ in seq]
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


if __name__ == "__main__":
    puzzle = Puzzle(year=2019, day=7)

    ans1 = part1(puzzle.input_data)
    # puzzle.answer_a = ans1
    ans2 = part2(puzzle.input_data)
    # puzzle.answer_b = ans2
