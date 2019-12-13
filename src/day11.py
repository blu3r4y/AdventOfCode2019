# Advent of Code 2019, Day 11
# (c) blu3r4y

from aocd.models import Puzzle
from funcy import print_calls

from intcode import IntcodeMachine
from util import coordinates_to_grid

BLACK, WHITE = 0, 1


def painting_robot(program, start=BLACK):
    robot = IntcodeMachine(program)
    pos, face = 0, 1j
    panels = {pos: start}

    while not robot.done:
        sensor = panels.get(pos, BLACK)
        robot.execute(inputs=[sensor])
        paint, turn = robot.get_output(n=2)

        # paint current cell
        panels[pos] = paint

        # move one cell left or right
        face *= 1j if turn == 0 else -1j
        pos += face

    return panels


@print_calls
def part1(program):
    return len(painting_robot(program))


@print_calls
def part2(program):
    panels = painting_robot(program, start=WHITE)
    coordinates_to_grid(panels, plot=True, rotate=1)


if __name__ == "__main__":
    puzzle = Puzzle(year=2019, day=11)

    ans1 = part1(puzzle.input_data)
    # puzzle.answer_a = ans1
    ans2 = part2(puzzle.input_data)
    # puzzle.answer_b = ans2
