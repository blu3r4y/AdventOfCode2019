# Advent of Code 2019, Day 12
# (c) blu3r4y

import itertools
import math
from collections import namedtuple
from typing import List, Tuple

import numpy as np
from aocd.models import Puzzle
from funcy import print_calls
from parse import parse

Moon = namedtuple("Moon", ["x", "y", "z"])


def gravity(moons: List[Moon], velocities: List[np.ndarray]) -> Tuple[List[Moon], List[np.ndarray]]:
    indexes = range(len(moons))

    # iterate over pairs and change velocities
    for i, j in itertools.combinations(indexes, r=2):
        change = offset(moons[i], moons[j])
        velocities[i] += change
        velocities[j] -= change

    # apply velocity changes
    for i, (dx, dy, dz) in zip(indexes, velocities):
        moon = moons[i]
        moons[i] = Moon(moon.x + dx, moon.y + dy, moon.z + dz)

    return moons, velocities


def offset(a: Moon, b: Moon) -> np.ndarray:
    # compute velocity offsets (-1 if a > b, 1 if a < b, 0 else)
    dx = -1 if a.x > b.x else (1 if a.x < b.x else 0)
    dy = -1 if a.y > b.y else (1 if a.y < b.y else 0)
    dz = -1 if a.z > b.z else (1 if a.z < b.z else 0)
    return np.array([dx, dy, dz], dtype=int)


def energy(moons: List[Moon], velocities: List[np.ndarray]) -> int:
    potential = [abs(m.x) + abs(m.y) + abs(m.z) for m in moons]
    kinetic = [abs(vx) + abs(vy) + abs(vz) for vx, vy, vz in velocities]
    return sum([p * k for p, k in zip(potential, kinetic)])


def fingerprint(moons: List[Moon], velocities: List[np.ndarray]) -> Tuple[int, int, int]:
    # compute a uniuqe fingerprint of the universe per each axis
    hx = hash(tuple([(m.x, v[0]) for m, v in zip(moons, velocities)]))
    hy = hash(tuple([(m.y, v[1]) for m, v in zip(moons, velocities)]))
    hz = hash(tuple([(m.z, v[2]) for m, v in zip(moons, velocities)]))
    return hx, hy, hz


def lcm(a: int, b: int) -> int:
    # compute the least common multiple between two values
    return abs(a * b) // math.gcd(a, b)


@print_calls
def part1(moons, steps=1000):
    velocities = [np.zeros(3, dtype=int) for _ in range(len(moons))]
    for t in range(steps):
        moons, velocities = gravity(moons, velocities)
    return energy(moons, velocities)


@print_calls
def part2(moons):
    velocities = [np.zeros(3, dtype=int) for _ in range(len(moons))]

    hashsets = [set(), set(), set()]  # hash stores per axes
    times = [None, None, None]  # store the times that each axis repeats itself

    for t in itertools.count():
        moons, velocities = gravity(moons, velocities)

        # check if this state existed before (per axis)
        fps = fingerprint(moons, velocities)
        for i in range(3):
            if fps[i] in hashsets[i] and times[i] is None:
                times[i] = t
            hashsets[i].add(fps[i])

        # break if we found reoccurring timestamps for all axes
        if all(times):
            break

    # the universe repeats itself at the least common multiple of the three axes repeats
    result = lcm(lcm(times[0], times[1]), times[2])
    return result


def load(data):
    return [Moon(**parse("<x={x:d}, y={y:d}, z={z:d}>", line).named)
            for line in data.split('\n') if len(line) > 0]


if __name__ == "__main__":
    puzzle = Puzzle(year=2019, day=12)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
