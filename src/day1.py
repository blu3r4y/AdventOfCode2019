# Advent of Code 2019, Day 1
# (c) blu3r4y

import numpy as np


def part1(masses):
    return np.sum(masses // 3 - 2)


def part2(masses):
    return sum(map(get_fuel, masses))


def get_fuel(mass):
    total, fuel = 0, mass
    while fuel > 0:
        fuel = max(0, fuel // 3 - 2)
        total += fuel
    return total


def load(path):
    return np.loadtxt(path, dtype=int)


if __name__ == "__main__":
    print(part1(load(r"../assets/day1.txt")))
    print(part2(load(r"../assets/day1.txt")))
