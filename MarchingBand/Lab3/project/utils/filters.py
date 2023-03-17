"""
Module for list-like filters that generate statistics based on a source list. 
Changes to the source list result in changes in the filters' results.

Author: Ryan Au
"""

import math
import time
from collections import UserList, deque
from statistics import mean, median
import threading


def range_limit(value: float, lower: float, upper: float) -> float:
    """Prevents the value from going beyond the upper or lower values.

    Example:
    range_limit(40,30,50)->40 (within bounds)
    range_limit(60,30,50)->50 (upper limit)
    range_limit(20,30,50)->30 (lower limit)

    >>> range_limit(40,30,50)
    40
    >>> range_limit(60,30,50)
    50
    >>> range_limit(20,30,50)
    30
    """
    return min(max(value, lower), upper)


def _wrap_index(i, l):
    """Changes an index from negative to the wrapped index based on length l.

    >>> _wrap_index(10, 5)
    10
    >>> _wrap_index(-10, 5)
    -5
    >>> _wrap_index(-4, 5)
    1
    """
    if i < 0:
        return l + i
    else:
        return i


class AtomicActor:
    def __init__(self):
        self.__atomic_lock__ = threading.RLock()

    def _atomic(func):
        def inner(*args, **kwargs):
            if len(args) == 0 or not isinstance(args[0], AtomicActor):
                raise RuntimeError(
                    "atomic decorator must be applied to a subclass of itself")
            self = args[0]
            with self.__atomic_lock__:
                return func(*args, **kwargs)
        return inner


class CircularList(AtomicActor):
    class Empty:
        def __eq__(self, __o: object) -> bool:
            return isinstance(__o, CircularList.Empty)

        def __repr__(self):
            return "Empty"

        def __bool__(self):
            return False

    def __init__(self, size: int):
        """Initializes the CircularList with a given size

        >>> c = CircularList(4)
        >>> len(c.data)
        4
        >>> c = CircularList(1)
        >>> len(c.data)
        1
        >>> c = CircularList(0) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ValueError: size must be positive non-zero value
        """
        super(CircularList, self).__init__()
        if type(size) != int:
            raise ValueError("size must be of type int")
        if size <= 0:
            raise ValueError("size must be positive non-zero value")
        self.size = size
        self.head = 0
        self.tail = None
        self.data = [CircularList.Empty() for i in range(size)]

    def __repr__(self):
        """String representation of this CircularList"""
        return repr(self.to_list())

    @AtomicActor._atomic
    def update(self, iterable):
        """Appends each element of the iterable to this list.
        The normal CircularList.append rules apply, and will overwrite
        the oldest added element always.

        >>> c = CircularList(3)
        >>> c.update([1,2,3,4,5])
        >>> c
        [3, 4, 5]
        >>> c.update([6,7,8,9])
        >>> c
        [7, 8, 9]
        >>> c.update([10, 11])
        >>> c
        [9, 10, 11]
        """
        for i in iterable:
            self.append(i)

    @AtomicActor._atomic
    def to_list(self):
        """
        Returns a List form of this CircularList.

        >>> c = CircularList(4)
        >>> c.to_list()
        []
        >>> c.append(1)
        Empty
        >>> c.to_list()
        [1]
        >>> c.update([2, 3, 4, 5])
        >>> c.to_list()
        [2, 3, 4, 5]
        >>> c.data
        [5, 2, 3, 4]
        """
        if self.tail is None:
            return list()
        if self.head <= self.tail:
            return self.data[self.head:self.tail+1]
        if self.tail < self.head:
            return [self.data[i] for i in self._slice(self.head, self.tail)]

    @AtomicActor._atomic
    def append(self, element):
        """
        Append an item to this list. Returns element if overriden,
        CircularList.Empty object if there was no element overriden.
        The first element is removed, if list would exceed its size.

        >>> c = CircularList(2)
        >>> c.append(1)
        Empty
        >>> c.append(2)
        Empty
        >>> c.append(3)
        1
        >>> c
        [2, 3]
        >>> c = CircularList(1)
        >>> c.append(1)
        Empty
        >>> c.append(2)
        1
        >>> c.append(3)
        2
        >>> c
        [3]
        >>> c.pophead()
        3
        >>> c.append(4)
        Empty
        >>> c
        [4]
        """

        if isinstance(element, CircularList.Empty):
            raise ValueError(
                "list element cannot be of the CircularList.Empty class")

        if self.tail is None:
            self.tail = self.head
        else:
            # Increment tail from current last element, to next element
            self.tail = (self.tail + 1) % self.size  # 0 to size-1
            if self.tail == self.head:
                self.head = (self.head + 1) % self.size

        last_item = self.data[self.tail]
        self.data[self.tail] = element
        return last_item

    @AtomicActor._atomic
    def pop(self):
        """Remove last added item and return it.

        >>> c = CircularList(2)
        >>> c.update([1, 2, 3])
        >>> c.pop()
        3
        >>> c.pop()
        2
        >>> c.append(4)
        Empty
        """
        if self.tail is None:
            raise RuntimeError("There are no items in this list")

        item = self.data[self.tail]
        self.data[self.tail] = CircularList.Empty()

        if self.head == self.tail:
            self.tail = None
        else:
            self.tail = (self.tail - 1) % self.size

        return item

    def poptail(self):
        """Remove last added item and return it."""
        return self.pop()

    @AtomicActor._atomic
    def pophead(self):
        """Remove first added item and return it."""
        if self.tail is None:
            raise RuntimeError("There are no items in this list")

        item = self.data[self.head]
        self.data[self.head] = CircularList.Empty()

        if self.head == self.tail:
            self.tail = None
        else:
            self.head = (self.head + 1) % self.size

        return item

    def _convert_index(self, index):
        """Converts any given index, into the corresponding circular index.
        Includes values 0 to size-1.

        Internally, it is only based self.head and self.size
        It ignores the current value of self.tail

        >>> c = CircularList(3)
        >>> c._convert_index(1)
        1
        >>> c.update([1, 2, 3, 4])
        >>> c._convert_index(1)
        2
        >>> c.update([5])
        >>> c._convert_index(1)
        0

        """
        index = index % self.size
        index = (self.head + index) % self.size
        return index

    def _slice(self, start, stop, step=1):
        """Slice for this CircularList, but STOP is inclusive

        Internally, only based on self.size

        >>> c = CircularList(5)
        >>> list(c._slice(0, 2))
        [0, 1, 2]
        >>> list(c._slice(0, 0))
        [0]
        >>> list(c._slice(2, 0))
        [2, 3, 4, 0]
        >>> list(c._slice(2, 1))
        [2, 3, 4, 0, 1]
        >>> list(c._slice(4, 1))
        [4, 0, 1]
        """
        start = start % self.size
        stop = stop % self.size
        if stop >= start:
            for i in range(start, stop+1, step):
                yield i
        elif start > stop:
            n = (self.size - start) + (stop+1)
            for i in range(0, n, step):
                yield (i+start) % self.size

    def _index_within(self, i):
        """Returns True if i is a valid element within the CircularList. False if not present."""
        if self.tail is None:
            return False
        elif self.tail >= self.head:
            return i <= self.tail and i >= self.head
        elif self.head > self.tail:
            return (i >= self.head and i < self.size) or (i >= 0 and i <= self.tail)

    @AtomicActor._atomic
    def __len__(self):
        """Get the length of the added elements

        >>> c = CircularList(5)
        >>> len(c)
        0
        >>> c.update([1,2,3])
        >>> len(c)
        3
        >>> c.update([4,5,6,7])
        >>> len(c)
        5
        >>> c.pophead()
        3
        >>> c.pophead()
        4
        >>> len(c)
        3
        """
        if self.tail is None:
            return 0
        elif self.head <= self.tail:
            return self.tail - self.head + 1
        elif self.head > self.tail:
            return self.size - self.head + (self.tail + 1)

    @AtomicActor._atomic
    def __getitem__(self, i: slice | int):
        """Gets an item from the list. 

        Raises IndexError if index is out of bounds or the list is empty

        >>> c = CircularList(5)
        >>> c.update([1])
        >>> c.update([2, 3, 4, 5, 6])
        >>> c[1:4]
        [3, 4, 5]
        >>> c.update([7, 8, 9, 10])
        >>> c[1:4]
        [7, 8, 9]
        >>> c.update([11, 12, 13])
        >>> c[1:4]
        [10, 11, 12]
        >>> c[2:0]
        []
        """
        if type(i) == int:
            if i >= self.__len__():
                raise IndexError("Index out of bounds")
            i = self._convert_index(i)
            item = self.data[i]
            if isinstance(item, CircularList.Empty):
                raise IndexError("Index is out of bounds")
            return item
        if type(i) == slice:
            start = 0 if i.start is None else i.start
            # Becomes the last index we do want to get. Might match start
            stop = self.size-1 if i.stop is None else i.stop-1

            if start > stop:
                return []

            n = self.__len__()
            start = range_limit(start % self.size, 0, n)
            stop = range_limit(stop % self.size, 0, n)

            start = self._convert_index(start)
            # inclusive stop, the index of the last element to get
            stop = self._convert_index(stop)
            step = 1 if i.step is None else i.step

            return [self.data[i] for i in self._slice(start, stop, step)]

    @AtomicActor._atomic
    def __setitem__(self, i: int, value):
        """Sets an index's position in the circular list.

        >>> c = CircularList(4)
        >>> c.update([1,2])
        >>> c[1] = 0
        >>> c
        [1, 0]
        >>> c[2] = 3 # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        IndexError: Index is out of bounds
        >>> c[1] = CircularList.Empty() # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ValueError: list element cannot be of the CircularList.Empty class
        >>> c.update([4, 5, 6, 7])
        >>> c[2] = 1
        >>> c
        [4, 5, 1, 7]
        """
        i = self._convert_index(i)
        item = self.data[i]
        if isinstance(item, CircularList.Empty):
            raise IndexError("Index is out of bounds")
        if isinstance(value, CircularList.Empty):
            raise ValueError(
                "list element cannot be of the CircularList.Empty class")
        self.data[i] = value

    @AtomicActor._atomic
    def __contains__(self, value):
        if isinstance(value, CircularList.Empty):
            raise ValueError(
                "list element cannot be of the CircularList.Empty class")
        return value in self.data

    @AtomicActor._atomic
    def __reversed__(self):
        c = CircularList(self.size)
        c.update(reversed(self.data))
        return c

    @AtomicActor._atomic
    def clear(self):
        n = self.__len__()
        for i in range(n):
            self.pop()

    @AtomicActor._atomic
    def copy(self):
        c = CircularList(self.size)
        c.update(c.to_list())
        return c

    @AtomicActor._atomic
    def extend(self, iterable):
        self.update(iterable)

    @AtomicActor._atomic
    def count(self, value):
        """"""
        return self.to_list().count(value)  # TODO: Optimize this

    @AtomicActor._atomic
    def index(self, value):
        """"""
        return self.to_list().index(value)  # TODO: Optimize this

    def remove(self, value):
        """"""
        raise Exception("Unimplemented function")

    def reverse(self):
        """"""
        raise Exception("Unimplemented function")

    def sort(self):
        """"""
        raise Exception("Unimplemented function")


class WindowedFilter(AtomicActor):
    def __init__(self, window_size=10):
        if type(window_size) != int or window_size <= 0:
            raise RuntimeError(
                "window_size is an invalid value. Must be a positive integer.")

        self.window_size = window_size
        self.queue = deque()
        self.circ = CircularList(self.window_size)

    def __appender__(self, in_value, out_value):
        """The method to be overriden, when subclassing WindowedFilter.

        in_value - the new value being appended
        out_value - the old value that is removed from window
        """
        return in_value

    def get_inner_list(self):
        return self.circ.to_list()

    def to_list(self):
        return list(self.queue)

    def get_value(self):
        if self.queue:
            return self.queue[-1]
        else:
            return None

    def append(self, value, **kwargs):
        out_value = self.circ.append(value)
        if isinstance(out_value, CircularList.Empty):
            out_value = None
        in_value = self.__appender__(value, out_value, **kwargs)
        self.queue.append(in_value)

    def pop(self):
        try:
            out_value = self.circ.pop()
        except:
            out_value = None
        if isinstance(out_value, CircularList.Empty):
            out_value = None
        _ = self.__appender__(None, out_value)
        try:
            return self.queue.pop()
        except:
            return None

    def clear(self):
        while self.pop() is not None:
            pass
        self.queue.clear()

    def __repr__(self):
        return str(list(self.queue))


class MeanWindow(WindowedFilter):
    def __init__(self, window_size=10):
        super().__init__(window_size)
        self.running_sum = 0
        self.running_n = 0

    def __appender__(self, in_value, out_value):
        if out_value is not None:
            self.running_sum -= out_value

        if in_value is not None:
            self.running_sum += in_value

        self.running_n = min(self.window_size, self.running_n + 1)
        return self.running_sum / self.running_n


class SumWindow(WindowedFilter):
    def __init__(self, window_size=10):
        super().__init__(window_size)
        self.running_sum = 0

    def __appender__(self, in_value, out_value):
        if out_value is not None:
            self.running_sum -= out_value
        if in_value is not None:
            self.running_sum += in_value

        return self.running_sum


class MedianWindow(WindowedFilter):
    def __init__(self, window_size=10):
        super().__init__(window_size)
        self.data = []

    def __appender__(self, in_value, out_value):
        if out_value is not None:
            self.data.remove(out_value)
        if in_value is not None:
            self.data.append(in_value)
        self.data.sort()
        return median(self.data)


class IntegrationTracker(WindowedFilter):
    def __init__(self, default_dx=1):
        super().__init__(window_size=1)
        self.default_dx = default_dx

    def __appender__(self, in_value, out_value, dx=None):
        if dx is None:
            dx = self.default_dx
        old = self.get_value()
        old = 0 if old is None else old

        if out_value is None:
            return old
        elif in_value is None:
            # Popping the value
            return old
        else:
            return (out_value + in_value) / 2 * dx + old


class ValueListWrapper(UserList):
    def __init__(self, iterable=None):
        super().__init__(None)

        if iterable is not None:
            iter(iterable)
            self.data = iterable

    def get_value(self):
        return self[-1]


class SimpleFunctionFilter:
    def __init__(self, value_giver, func=None):
        if not (hasattr(value_giver, 'get_value') and callable(getattr(value_giver, 'get_value'))):
            raise RuntimeError(
                "value_giver does not have a valid get_value function")
        self.src = value_giver
        if func is None:
            self.func = lambda x: x
        else:
            self.func = func
        if not callable(func):
            raise RuntimeError(
                "inner function func is not a callable function")

    def get_value(self):
        value = self.src.get_value()
        if value is not None:
            return self.func(value)
        else:
            return None


class RangeLimitFilter(SimpleFunctionFilter):
    def __init__(self, source, lower, upper):
        super().__init__(source, lambda x: range_limit(x, lower, upper))


class ModulusFilter(SimpleFunctionFilter):
    def __init__(self, source, mod):
        super().__init__(source, lambda x: x % mod)


class MaximumFilter(SimpleFunctionFilter):
    def __init__(self, source, maximum_value):
        super().__init__(source, lambda x: max(x, maximum_value))


class MinimumFilter(SimpleFunctionFilter):
    def __init__(self, source, minimum_value):
        super().__init__(source, lambda x: min(x, minimum_value))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
