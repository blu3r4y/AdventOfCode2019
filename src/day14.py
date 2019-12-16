# Advent of Code 2019, Day 14
# (c) blu3r4y

from collections import namedtuple
from math import ceil
from typing import Dict, Iterable

from aocd.models import Puzzle
from funcy import print_calls
from parse import parse

Element = namedtuple("Element", ["num", "item"])
Recipe = namedtuple("Recipe", ["src", "dst"])


def nanofactory(recipes: Dict[str, Recipe], produce: Element,
                bases: Iterable[str], leftovers: Dict[str, int] = None):
    # bucket for elements that need to be reduced
    stack = {produce.item: produce.num}

    # bucket for base elements that can not be reduced further
    bases = {base: 0 for base in bases}

    # leftovers can be used for crafting but don't need to be reduced further
    leftovers = {} if leftovers is None else leftovers

    while len(stack) > 0:
        target, quantity = stack.popitem()
        recipe = recipes[target]

        # determine how often we need to apply the recipe
        factor = ceil(quantity / recipe.dst.num)

        # split off target element into its source elements
        for element in recipe.src:
            bucket = bases if element.item in bases else stack  # but base elements into a separate bucket

            nrequired = bucket.get(element.item, 0) + element.num * factor
            nleftover = leftovers.get(element.item, 0)

            # compute required source elements after subtracting leftovers
            if nrequired - nleftover > 0:
                bucket[element.item] = nrequired - nleftover
            leftovers[element.item] = max(0, nleftover - nrequired)

        # if we crafted too many target elements we can reuse them later
        nleftover = recipe.dst.num * factor - quantity
        if nleftover > 0:
            leftovers[target] = leftovers.get(target, 0) + nleftover

    # only the base quantities should be left now
    return bases


@print_calls
def part1(recipes: Dict[str, Recipe]):
    core = nanofactory(recipes, produce=Element(1, "FUEL"), bases=["ORE"])
    return core["ORE"]


@print_calls
def part2(recipes: Dict[str, Recipe], ncargo: int = int(1E12)):
    # estimate the cost (in "ORE" units) for 1 unit of "FUEL" by requesting a lot of fuel
    fuelcost = nanofactory(recipes, produce=Element(1E12, "FUEL"), bases=["ORE"])["ORE"] / 1E12
    estimate = int(ncargo / fuelcost)

    # start estimating from below (and assume that we still have some cargo left until we reach the true value)
    nfuel = estimate - 100
    assert nanofactory(recipes, produce=Element(nfuel, "FUEL"), bases=["ORE"])["ORE"] < ncargo

    nores = 1
    while nores < ncargo:
        nores = nanofactory(recipes, produce=Element(nfuel, "FUEL"), bases=["ORE"])["ORE"]
        nfuel += 1

    # revert the last +1 and subtract one more to get the last call where nores <= ncargo still held
    return nfuel - 2


def load(data):
    parser = lambda e: Element(**parse("{num:d} {item:l}", e).named)

    recipes = (line.split(" => ") for line in data.split("\n"))  # split recipe lines and src and dst elements
    recipes = ((src.split(", "), dst) for src, dst in recipes)  # split multiple src components
    recipes = [Recipe(list(map(parser, src)), parser(dst)) for src, dst in recipes]  # parse elements
    recipes = {recipe.dst.item: recipe for recipe in recipes}  # use target item as dict key

    return recipes


if __name__ == "__main__":
    puzzle = Puzzle(year=2019, day=14)

    ans1 = part1(load(puzzle.input_data))
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
