# Advent of Code 2019, Day 6
# (c) blu3r4y

import networkx as nx

from aocd.models import Puzzle
from funcy import print_calls, takewhile, ilen


@print_calls
def part1(graph):
    checksum = 0
    for target in graph.nodes:
        checksum += nx.shortest_path_length(graph, "COM", target)
    return checksum


@print_calls
def part2(graph):
    you = nx.shortest_path(graph, "COM", "YOU")
    san = nx.shortest_path(graph, "COM", "SAN")

    # number of nodes that both paths have in common
    ncommon = ilen(takewhile(lambda tup: tup[0] == tup[1], zip(you, san)))
    # sum of length from YOU & SAN to common node (-2 for excluding YOU and SAN)
    return len(you) - ncommon + len(san) - ncommon - 2


def load(data):
    return nx.DiGraph([line.split(")") for line in data.split()])


if __name__ == "__main__":
    puzzle = Puzzle(year=2019, day=6)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
