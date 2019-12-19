from typing import Dict, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np


def coordinates_to_grid(coordinates: Union[Dict[Tuple[int, int], int], Dict[complex, int]],
                        plot: int = False, rotate: int = 0) -> np.ndarray:
    """
    Given a dictionary with coordinates as keys, return a grid that is filled with those values

    @param coordinates: An (x, y) tuple or a complex number
    @param plot: Plot the result
    @param rotate: The number of times the final grid is rotated by 90 degrees
    @return: The filled numpy grid
    """

    if any(isinstance(k, complex) for k in coordinates.keys()):
        # map complex numbers to int tuples
        # noinspection PyUnresolvedReferences
        coordinates = {(int(key.real), int(key.imag)): val for key, val in coordinates.items()}

    # retrieve bounds and initialize a new empty grid
    arr = np.array(list(coordinates.keys()))
    (xmin, ymin), (xmax, ymax) = np.amin(arr, axis=0), np.amax(arr, axis=0)
    grid = np.zeros((xmax - xmin + 1, ymax - ymin + 1))

    # paint grid cells
    for (x, y), color in coordinates.items():
        grid[x - xmin, y - ymin] = color

    if plot:
        plt.imshow(np.rot90(grid, k=rotate))
        plt.show()

    return grid


def init_interactive_plot():
    plt.ion()
    plt.figure(figsize=(10, 10))
    plt.axis("off")

    view = plt.imshow(np.ones((10, 10)))
    return view
