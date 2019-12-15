# Advent of Code 2019, Day 15
# (c) blu3r4y

from collections import defaultdict
from random import choice

import matplotlib.pyplot as plt
import numpy as np
from aocd.models import Puzzle
from funcy import print_calls

from intcode import IntcodeMachine
from util import coordinates_to_grid

NORTH, SOUTH, WEST, EAST = 1, 2, 3, 4
WALL, EMPTY, GOAL, OXYGEN = 0, 1, 2, 2

# map directions to robot commands
COMMANDS = {1: EAST, 1j: NORTH, -1: WEST, -1j: SOUTH}


class TremauxMethod(object):

    def __init__(self, robot: IntcodeMachine, start: complex = 0, visualize: bool = False):
        self.robot = robot

        self.grid = defaultdict(int)
        self.marks = defaultdict(int)

        self.start = start
        self.pos = start
        self.face = 1j
        self.goal = None

        self.view = None
        if visualize:
            plt.ion()
            plt.figure()
            plt.axis("off")
            self.view = plt.imshow(np.ones((50, 50, 3)))

    def escape(self, scanmode=False):
        # the starting point needs to be valid
        self.grid[self.pos] = EMPTY

        self.peek_neighbors()

        # initially face towards the first path option
        self.face = self.get_options(self.pos)[0] - self.pos

        # implementation of trémaux’ method
        # https://en.wikipedia.org/wiki/Maze_solving_algorithm#Tr%C3%A9maux's_algorithm

        # default: search until we found the goal
        # scanmode: map entire maze until we are back at the beginning
        first = True
        while (not scanmode and self.goal is None) \
                or (scanmode and (self.pos != self.start or first)):
            first = False
            self.peek_neighbors()

            origin = self.pos - self.face

            # possible paths
            options = self.get_options(self.pos)
            assert len(options) > 0
            if origin in options:  # going back is not an option
                options.remove(origin)

            # we hit a wall ...
            if len(options) == 0:
                target = origin  # -> go back

            # simply follow the path ...
            elif len(options) == 1:
                target = options[0]

            # we are at a crossing point ...
            else:

                # mark the cell at which we entered the crossing point
                self.marks[origin] += 1

                marks = [self.marks[opt] for opt in options]

                # no marks at all ... ?
                if sum(marks) == 0:
                    target = choice(options)  # -> choose random

                # no marks from origin ... ?
                elif self.marks[origin] == 0:
                    target = origin  # -> go back

                # otherwise, take path with least marks ...
                else:
                    options_marks = sorted(zip(options, marks), key=lambda e: e[1])
                    target = options_marks[0][0]

                # mark the chosen cell
                self.marks[target] += 1

            # make move in new facing direction
            self.face = target - self.pos
            self.move(self.pos + self.face, force=True)

            if self.view:
                self.plot()

        return self.goal

    def move(self, target, backtrack=False, force=False):
        vec = target - self.pos
        assert (abs(int(vec.imag)) == 1) ^ (abs(int(vec.real)) == 1), "can only move 1 cell at a time"

        # carry out the move
        status = self.robot.execute([COMMANDS[vec]])
        self.grid[target] = status

        # ensure the move was valid
        if force and status == WALL:
            raise ValueError(f"can not force a move to {target} because there is a wall")

        if status == GOAL:
            self.goal = target

        if status != WALL:
            if backtrack:
                self.robot.execute([COMMANDS[-vec]])  # go back!
            else:
                self.pos = target  # set new position

    def peek_neighbors(self):
        # just visit neighbors for observing what cells are there
        neighbors = self.get_neighbors(self.pos)
        for neighbor in neighbors:
            if neighbor not in self.grid:
                self.move(neighbor, backtrack=True)

    def get_options(self, pos):
        # get all movable cells adjacent to pos
        return [p for p in self.get_neighbors(pos) if self.grid[p] != WALL]

    @staticmethod
    def get_neighbors(pos):
        return [pos + (1j ** p) for p in range(4)]

    def shortest_path_length(self, start, goal) -> int:
        queue, distances = [start], {start: 0}
        while queue:
            node = queue.pop(0)
            if node == goal:
                return distances[node]
            for neighbor in self.get_options(node):
                if neighbor not in distances:
                    queue.append(neighbor)
                    distances[neighbor] = distances[node] + 1  # distance to parent plus one step

        return -1  # no path found

    def fill_oxygen(self):
        oxygen = {self.goal}  # already filled areas
        silhouette = {self.goal}  # area that was filled in the last timestep

        t = 0
        while len(silhouette) > 0:

            new_silhouette = set()

            for pos in silhouette:
                for adj in self.get_options(pos):

                    # fill each adjacent cell in the silhouette that is not already filled
                    if adj not in oxygen:
                        new_silhouette.add(adj)
                        self.grid[adj] = OXYGEN

            # prepare next iteration
            oxygen.update(new_silhouette)
            silhouette = new_silhouette

            if self.view:
                self.plot()

            t += 1

        return t - 1  # remove 1 step because the last step doesn't count anymore

    def plot(self):
        grid = self.grid.copy()
        grid[self.pos] = 4
        grid[self.start] = 5
        grid = coordinates_to_grid(grid)

        self.view.set_data(grid.T)  # reset grid content
        self.view.set_clim(vmin=0, vmax=5)  # reset value range

        plt.draw()
        plt.pause(.001)


@print_calls
def part1(program):
    robot = IntcodeMachine(program)
    solver = TremauxMethod(robot, visualize=False)

    oxygen = solver.escape()
    return solver.shortest_path_length(0, oxygen)


@print_calls
def part2(program):
    robot = IntcodeMachine(program)
    solver = TremauxMethod(robot, visualize=False)

    solver.escape(scanmode=True)
    return solver.fill_oxygen()


if __name__ == "__main__":
    puzzle = Puzzle(year=2019, day=15)

    ans1 = part1(puzzle.input_data)
    # puzzle.answer_a = ans1
    ans2 = part2(puzzle.input_data)
    # puzzle.answer_b = ans2
