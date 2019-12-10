# Advent of Code 2019, Day 9
# (c) blu3r4y

from aocd.models import Puzzle
from funcy import print_calls

from intcode import IntcodeMachine


@print_calls
def part1(data):
    return IntcodeMachine(data).execute([1], nopause=True)


@print_calls
def part2(data):
    return IntcodeMachine(data).execute([2], nopause=True)


if __name__ == "__main__":
    puzzle = Puzzle(year=2019, day=9)

    ans1 = part1(puzzle.input_data)
    # puzzle.answer_a = ans1
    ans2 = part2(puzzle.input_data)
    # puzzle.answer_b = ans2
