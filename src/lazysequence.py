from functools import lru_cache
from typing import Sequence


class LazySequence(Sequence):
    """
    A sequence object that is backed by a function for retrieving elements
    """

    @lru_cache(maxsize=None)
    def _get(self, i):
        return self.getter(i)

    def _idx(self, i):
        return i if not self.reverse else self.size - 1 - i

    def __getitem__(self, key):
        if isinstance(key, slice):
            return [self._get(self._idx(i)) for i in range(*key.indices(self.size))]
        elif isinstance(key, tuple):
            raise TypeError("tuple indexing is not supported")
        elif key < 0:
            return self._get(self._idx(self.size + key))
        return self._get(self._idx(key))

    def __len__(self):
        return self.size

    def __reversed__(self):
        self.reverse = not self.reverse
        return self

    def __init__(self, getter, size, reverse=False):
        """
        Initialize a lazy sequence

        @param getter: A function that returns the element at some index
        @param size: The length of the sequence
        @param reverse: Internally reverse the sequence
        """
        self.getter = getter
        self.size = size
        self.reverse = reverse
