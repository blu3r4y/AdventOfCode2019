# Advent of Code 2019, Day 6
# (c) blu3r4y

import networkx as nx

from aocd.models import Puzzle
from funcy import print_calls


@print_calls
def part1(graph):
    checksum = 0
    for target in graph.nodes:
        checksum += nx.shortest_path_length(graph, "COM", target)
    return checksum


@print_calls
def part2(graph):
    return nx.shortest_path_length(graph.to_undirected(), "YOU", "SAN") - 2


def load(data):
    return nx.DiGraph([line.split(")") for line in data.split()])


if __name__ == "__main__":
    puzzle = Puzzle(year=2019, day=6)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
