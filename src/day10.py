# Advent of Code 2019, Day 10
# (c) blu3r4y

import numpy as np

from aocd.models import Puzzle
from funcy import print_calls


def num_reachable(src, others):
    # normalize distance vectors
    dists = others - src
    dists = dists / np.linalg.norm(dists, axis=1)[:, None]

    # determine number of non-overlapping vectors
    _, uniq = np.unique(np.around(dists, 10), axis=0, return_counts=True)
    nuniq = len(uniq == 1) - 1  # -1 because src is in dsts

    return nuniq


def get_targets(station, asteroids):
    # asteroid coordinates
    ax, ay = asteroids[:, 0], asteroids[:, 1]

    # distances to asteroids
    dists = asteroids - station
    dx, dy = dists[:, 0], dists[:, 1]

    # convert distances to polar coordinates
    rho = np.around(np.hypot(dx, dy), 10)
    theta = np.around(np.arctan2(dy, dx) - np.pi, 10)  # offset for north orientation

    # create matrix with cartesian and polar coordinates (+ indexing helper constants)
    IX, IY, IRHO, ITHETA = 0, 1, 2, 3
    mat = np.vstack([ax, ay, rho, theta]).T

    targets = []

    while len(mat) > 0:
        # sort by theta clockwise (-> decreasing), then by rho increasing
        sub = mat[np.lexsort((mat[:, IRHO], -mat[:, ITHETA]))]
        # remove out-of-sight asteroids by only taking the first row if theta is equal
        sub = sub[np.sort(np.unique(sub[:, ITHETA], return_index=True)[1])]

        # append targets (in reverse xy-order for final output)
        targets.extend(list(zip(sub[:, IY].astype(int), sub[:, IX].astype(int))))

        # remove targets from matrix
        drop_indexes = []
        for y, x in targets:
            idx = np.argmax(np.logical_and(mat[:, IX] == x, mat[:, IY] == y))  # search matching row
            drop_indexes.append(idx)
        mat = np.delete(mat, drop_indexes, axis=0)

    return targets


@print_calls
def part1(asteroids):
    return max([num_reachable(a, asteroids) for a in asteroids])


@print_calls
def part2(asteroids, target=200):
    reachable = [num_reachable(a, asteroids) for a in asteroids]
    station = asteroids[reachable.index(max(reachable))]

    targets = get_targets(station, asteroids)

    # get nth target and compute result
    x, y = targets[target - 1]
    return x * 100 + y


def load(data):
    grid = np.array(list(map(list, data.split())))
    asteroids = list(zip(*np.nonzero(grid == '#')))
    return np.array(asteroids)


if __name__ == "__main__":
    puzzle = Puzzle(year=2019, day=10)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
