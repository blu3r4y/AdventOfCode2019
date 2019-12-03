# Advent of Code 2019, Day 3
# (c) blu3r4y

from operator import itemgetter

from aocd.models import Puzzle
from funcy import print_calls
from parse import parse


def solve(wires):
    touched, steps = set(), dict()  # cells touched by 1st wire & number of steps
    intersections = set()  # crossing points with 2nd wire

    for i, wire in enumerate(wires):
        pos, length = 0, 0  # current cell position and signal length

        # move cell by cell
        for way, num in wire:
            for _ in range(num):
                pos += get_vector(way)
                length += 1

                if i == 0:  # 1st wire
                    touched.add(pos)
                    steps[pos] = length
                elif i == 1 and pos in touched:  # 2nd wire
                    intersections.add((pos, length + steps[pos]))

    return intersections


def get_vector(ch):
    # return complex orientation vector for direction indicator
    if ch == "R":
        return 1  # right
    elif ch == "U":
        return 1j  # up
    elif ch == "L":
        return -1  # left
    elif ch == "D":
        return -1j  # down


@print_calls
def part1(wires):
    intersections = solve(wires)
    return sorted([int(abs(p.real) + abs(p.imag)) for p, _ in intersections])[0]


@print_calls
def part2(wires):
    intersections = solve(wires)
    return sorted(intersections, key=itemgetter(1))[0][1]


def load(data):
    return [[parse("{:l}{:d}", op) for op in line.split(",")] for line in data.split("\n")]


if __name__ == "__main__":
    puzzle = Puzzle(year=2019, day=3)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
