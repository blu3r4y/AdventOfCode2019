# Advent of Code 2019, Day 8
# (c) blu3r4y

import numpy as np
import matplotlib.pyplot as plt

from aocd.models import Puzzle
from funcy import print_calls


@print_calls
def part1(data, width=25, height=6):
    img = data.reshape([-1, width * height]).tolist()  # decode layers
    fewest = sorted(img, key=lambda l: l.count(0))[0]  # layer with fewest zeros
    return fewest.count(1) * fewest.count(2)


@print_calls
def part2(data, width=25, height=6):
    img = data.reshape([-1, height, width])  # decode layers
    mask = np.argmax(img != 2, axis=0)  # first nonzero per pixel slice

    # per pixel, select masked layer
    out = np.zeros((height, width), dtype=int)
    for (i, j), _ in np.ndenumerate(out):
        out[i, j] = img[mask[i, j], i, j]

    # plot the message visually
    plt.imshow(out)
    plt.show()


def load(data):
    return np.array(list(map(int, data)))


if __name__ == "__main__":
    puzzle = Puzzle(year=2019, day=8)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
