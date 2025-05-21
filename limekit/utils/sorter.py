from random import randrange
from limekit.engine.parts import EnginePart


class Sort(EnginePart):
    name = "__sorter"

    @classmethod
    def quick_sort(cls, collection):
        """A pure Python implementation of quick sort algorithm

        :param collection: a mutable collection of comparable items
        :return: the same collection ordered by ascending

        Examples:
        >>> quick_sort([0, 5, 3, 2, 2])
        [0, 2, 2, 3, 5]
        >>> quick_sort([])
        []
        >>> quick_sort([-2, 5, 0, -45])
        [-45, -2, 0, 5]
        """
        collection = list(collection)

        if len(collection) < 2:
            return collection
        pivot_index = randrange(len(collection))  # Use random element as pivot
        pivot = collection[pivot_index]
        greater: list[int] = []  # All elements greater than pivot
        lesser: list[int] = []  # All elements less than or equal to pivot

        for element in collection[:pivot_index]:
            (greater if element > pivot else lesser).append(element)

        for element in collection[pivot_index + 1 :]:
            (greater if element > pivot else lesser).append(element)

        return [*cls.quick_sort(lesser), pivot, *cls.quick_sort(greater)]
