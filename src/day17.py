# Advent of Code 2019, Day 17
# (c) blu3r4y

from collections import namedtuple

from aocd.models import Puzzle
from funcy import print_calls, chunks, partition, pairwise, takewhile, ilen, flatten

from gridtools import text_to_array, array_to_dict, ComplexGrid, complex_to_tuple
from intcode import IntcodeMachine

SCAFFOLD, FREE = ord("#"), ord(".")
UP, DOWN, LEFT, RIGHT = ord("^"), ord("v"), ord("<"), ord(">")

ORIENTATIONS = [UP, RIGHT, DOWN, LEFT]
FACE_MAPPING = {UP: 1j, RIGHT: 1 + 0j, DOWN: -1j, LEFT: -1 + 0j}


def get_complex_grid(robot, flip):
    # ask the robot for the current field structure and return a complex grid
    robot.execute()
    field = "".join(map(chr, robot.get_output(None, pop=True)[:-2]))  # :-2 to remove double line breaks at end
    field = array_to_dict(text_to_array(field, flip=flip), ignore_values=[FREE])
    cg = ComplexGrid(field)
    cg.plot()
    return cg


def get_intersections(cg: ComplexGrid):
    intersections = []
    for pos in cg.grid.keys():
        neighbors = cg.move(pos).neighbors
        if len(neighbors) == 4:
            intersections.append(complex_to_tuple(pos))

    return intersections


def get_turn_command(a, b):
    # return 'R' or 'L' if the orientation change is a right or left turn
    if a == b:
        return None

    # simulate the turn and check where we end up
    if a * 1j == b:
        return "R"
    elif b * 1j == a:
        return "L"
    else:
        raise ValueError("180 degree turns are forbidden")


def get_path(cg: ComplexGrid):
    # find and set starting location
    start, face = [(pos, val) for pos, val in cg.grid.items() if val != SCAFFOLD][0]
    cg.set(start, SCAFFOLD)  # convert marker to standard field
    cg.move(start, FACE_MAPPING[face])

    del face

    path = []

    # initially, turn towards scaffold
    indexes = cg.neighbor_indexes(include_val=[SCAFFOLD])
    assert len(indexes) == 1
    cg.move(face=FACE_MAPPING[ORIENTATIONS[indexes[0]]])

    # save the initial turn (if we are not aligned already)
    turn = get_turn_command(cg.oldface, cg.face)
    if turn is not None:
        path.append(turn)

    # make one move already
    cg.move_in_face()
    steps = 1

    while True:
        vertical = cg.face == 1j or cg.face == -1j
        horizontal = cg.face == 1 or cg.face == -1

        # straight moves
        if (cg.left and cg.right and horizontal) or \
                (cg.up and cg.down and vertical):
            cg.move_in_face()
            steps += 1

        # go around turns
        else:
            candidates = cg.neighbor_indexes(include_val=[SCAFFOLD], exclude_pos=[cg.oldpos])
            assert len(candidates) <= 1

            # append step counter
            path.append(steps)

            # we are at the end if we are out of options
            if len(candidates) == 0:
                break

            # make and store the turn
            cg.move(face=FACE_MAPPING[ORIENTATIONS[candidates[0]]])
            path.append(get_turn_command(cg.oldface, cg.face))

            # next move
            cg.move_in_face()
            steps = 1

    return list(map(tuple, chunks(2, path)))


def compress(path, max_part_length=None, max_parts=None, verbose=False):
    path = path.copy()
    functions, main_routine = [], []

    if max_part_length is None:
        max_part_length = len(path)

    dummy = namedtuple("dummy", "index")

    def _get_matches(w):
        # store the matched indexes and prepare the sublist to be compared
        result, sublist = [], path[:w]
        for i, window in enumerate(partition(w, 1, path)):  # sliding window of length w
            if sublist == window and not any(isinstance(e, dummy) for e in window):
                result.append(i)

        # clear overlaps
        delete = []
        for m1, m2 in pairwise(result):
            if m1 + w > m2:
                delete.append(m2)
        result = [m for m in result if m not in delete]

        return result

    part_index = 0
    while sum([1 for e in path if not isinstance(e, dummy)]) > 0:

        j = -1  # length of substring

        # override the length limit on the last part
        limit = min(len(path), max_part_length + 1)
        if part_index == max_parts - 1:
            limit = len(path)

        # search for substring with most occurrences
        for i in reversed(range(1, limit)):
            matches = _get_matches(i)
            if len(matches) > 1:
                j = i  # store the previous best value
                break

        # if we immediately find no good matching, take the first few values until the dummy appears
        if j == -1:
            j = ilen(takewhile(lambda e: not isinstance(e, dummy), path))

        matches = _get_matches(j)

        # store found substring
        functions.append(path[:j])

        if verbose:
            print("path:", path)
            print("--> found", len(matches), "occurrences of subpath of length", j, "-->", path[:j])

        # remove the substrings from the path and replace them with a dummy tuple
        for i, c in enumerate(matches):
            c -= i * (j - 1)  # decrease index by number of already removed characters
            del path[c:c + j]  # remove substring at position c with length j (found before)
            path.insert(c, dummy(part_index))

        # remove leading dummies since the algorithm will continue to search from the beginning
        while len(path) > 0 and isinstance(path[0], dummy):
            main_routine.append(path.pop(0))

        part_index += 1

    main_routine = [e.index for e in main_routine]

    return functions, main_routine


def get_commands(functions, main_routine):
    commands = []

    main_routine = ",".join([chr(ord("A") + e) for e in main_routine])
    commands.append(main_routine)

    for i in range(3):
        commands.append(",".join(map(str, flatten(functions[i]))))

    # n for disabling interactive mode
    result = list(map(ord, "\n".join(commands) + "\n" + "n\n"))
    return result


@print_calls
def part1(program):
    robot = IntcodeMachine(program)
    cg = get_complex_grid(robot, flip=False)
    intersections = get_intersections(cg)

    # sum of the coordinate values of alignment params
    return sum([x * y for x, y in intersections])


@print_calls
def part2(program):
    robot = IntcodeMachine(program)
    cg = get_complex_grid(robot, flip=True)

    # find a path on the scaffolds
    path = get_path(cg)

    # compress the path and build the command string
    functions, main_routine = compress(path, max_part_length=3, max_parts=3)
    solution = get_commands(functions, main_routine)

    # switch to interactive mode and submit commands
    robot = IntcodeMachine(program)
    robot.memory[0] = 2
    collected_dust = robot.execute(inputs=solution)

    return collected_dust


if __name__ == "__main__":
    puzzle = Puzzle(year=2019, day=17)

    ans1 = part1(puzzle.input_data)
    # puzzle.answer_a = ans1
    ans2 = part2(puzzle.input_data)
    # puzzle.answer_b = ans2
