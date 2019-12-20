# Advent of Code 2019, Day 13
# (c) blu3r4y
from typing import Tuple, Dict

import matplotlib.pyplot as plt
from aocd.models import Puzzle
from funcy import print_calls, chunks

from intcode import IntcodeMachine
from util import coordinates_to_grid, init_interactive_plot

EMPTY, WALL, BLOCK, PADDLE, BALL = 0, 1, 2, 3, 4


def plot_tiles(tiles, view):
    grid = coordinates_to_grid(tiles)

    view.set_data(grid.T)  # reset grid content
    view.set_clim(vmin=0, vmax=4)  # reset value range

    plt.draw()
    plt.pause(.02)


def read_tiles(robot, tiles=None) -> Tuple[Dict[Tuple[int, int], int], int]:
    tiles, score = {} if not tiles else tiles, 0
    for x, y, tile in chunks(3, robot.get_output(None, pop=True)):
        if x == -1 and y == 0:
            score = tile  # special score tile
        else:
            assert tile <= 4
            tiles[(x, y)] = tile

    return tiles, score


def compute_move(tiles):
    px, py = next(pos for pos, val in tiles.items() if val == PADDLE)
    bx, by = next(pos for pos, val in tiles.items() if val == BALL)
    return max(min(bx - px, 1), -1)  # simply follow the ball


@print_calls
def part1(program):
    robot = IntcodeMachine(program)
    robot.execute(nopause=True)

    tiles, _ = read_tiles(robot)

    # count number of block tiles
    return sum(1 for t in tiles.values() if t == BLOCK)


@print_calls
def part2(program, visualize=False):
    robot = IntcodeMachine(program)
    robot.memory[0] = 2  # free game mode

    # render board
    robot.execute()
    tiles, score = read_tiles(robot)

    if visualize:
        view = init_interactive_plot()
        plot_tiles(tiles, view)

    while not robot.done:
        direction = compute_move(tiles)

        # apply move and re-render board
        robot.execute(inputs=[direction])
        tiles, score = read_tiles(robot, tiles)

        if visualize:
            plot_tiles(tiles, view)

    return score


if __name__ == "__main__":
    puzzle = Puzzle(year=2019, day=13)

    ans1 = part1(puzzle.input_data)
    # puzzle.answer_a = ans1
    ans2 = part2(puzzle.input_data)
    # puzzle.answer_b = ans2
