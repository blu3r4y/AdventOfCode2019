# Advent of Code 2019, Day 16
# (c) blu3r4y

import numpy as np

from aocd.models import Puzzle
from funcy import print_calls

BASE = np.array([0, 1, 0, -1], dtype=int)


def pattern(level, length):
    # repeat the values in the base pattern and broadcast (tile) the entire pattern to the desired length
    return np.tile(np.repeat(BASE, level), length // (BASE.shape[0] * level) + 1)[1:length + 1]


def multiply(signal, mask):
    # compute the line and return the one-digit only
    return np.abs(np.dot(signal, mask)) % 10


def fft(signal):
    # compute an entire phase, consisting of as much lines as the input is long
    result = np.zeros_like(signal)
    for i in range(len(signal)):
        result[i] = multiply(signal, pattern(i + 1, len(signal)))
    return result


@print_calls
def part1(signal, nphases=100):
    signal = np.array(list(map(int, signal)))

    for i in range(nphases):
        signal = fft(signal)

    return "".join(map(str, signal[:8]))


@print_calls
def part2(signal, nphases=100, nrepeat=10000):
    signal = signal * nrepeat
    offset = int(signal[:7])

    # this method can only compute offsets in the second half of the result
    # with a fixed base pattern of [0, 1, 0, -1]
    assert offset > len(signal) / 2

    # only care about the desired region and reverse for more efficient np.cumsum
    signal = np.array(list(map(int, signal[offset:])))[::-1]

    for phase in range(nphases):
        signal = np.cumsum(signal) % 10

    # undo reverse and select first 8 values
    return "".join(map(str, signal[::-1][:8]))


if __name__ == "__main__":
    puzzle = Puzzle(year=2019, day=16)

    ans1 = part1(puzzle.input_data)
    # puzzle.answer_a = ans1
    ans2 = part2(puzzle.input_data)
    # puzzle.answer_b = ans2
