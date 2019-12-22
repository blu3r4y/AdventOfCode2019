import matplotlib.pyplot as plt
import numpy as np


def init_interactive_plot():
    plt.ion()
    plt.figure(figsize=(10, 10))
    plt.axis("off")

    view = plt.imshow(np.ones((10, 10)))
    return view
