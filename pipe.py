"""Library allowing a sh like infix syntax using pipes."""

__author__ = "Julien Palard <julien@python.org>"
__version__ = "2.2"
__credits__ = """Jérôme Schneider for teaching me the Python datamodel,
and all contributors."""

import builtins
import functools
import itertools
import socket
import sys
from collections import deque
from contextlib import closing


class Pipe:
    """
    Pipe class enable a sh like infix syntax.

    This class allows you to create a pipeline of operations by chaining functions
    together using the `|` operator. It wraps a function and its arguments, enabling
    you to apply the function to an input in a clean and readable manner.

    Examples
    --------
    Create a new Pipe operation:

        >>> from pipe import Pipe
        >>> @Pipe
        ... def double(iterable):
        ...     return (x * 2 for x in iterable)

    Use the Pipe operation:

        >>> result = [1, 2, 3] | double
        >>> list(result)
        [2, 4, 6]

    Notes
    -----
    ...

    """

    def __init__(self, function, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.function = function
        self.instance = None
        functools.update_wrapper(self, function)

    def __ror__(self, other):
        """
        Implement the reverse pipe operator (`|`) for the object.

        Parameters
        ----------
        other : Any
            The left-hand operand of the `|` operator.

        Returns
        -------
        Any
            The result of applying the stored function to `other` with the
            provided arguments and keyword arguments.

        """
        return self.function(other, *self.args, **self.kwargs)

    def __call__(self, *args, **kwargs):
        return Pipe(
            self.function,
            *self.args,
            *args,
            **self.kwargs,
            **kwargs,
        )

    def __repr__(self) -> str:
        return "piped::<%s>(*%s, **%s)" % (
            self.function.__name__,
            self.args,
            self.kwargs,
        )

    def __get__(self, instance, owner=None):
        return Pipe(
            function=self.function.__get__(instance, owner),
            *self.args,
            *self.kwargs,
        )


@Pipe
def take(iterable, qte):
    """Yield qte of elements in the given iterable."""
    if not qte:
        return
    for item in iterable:
        yield item
        qte -= 1
        if qte == 0:
            break


@Pipe
def tail(iterable, qte):
    """Yield qte of elements in the given iterable."""
    return deque(iterable, maxlen=qte)


@Pipe
def skip(iterable, qte):
    """Skip qte elements in the given iterable, then yield others."""
    for item in iterable:
        if qte == 0:
            yield item
        else:
            qte -= 1


@Pipe
def dedup(iterable, key=lambda x: x):
    """Only yield unique items. Use a set to keep track of duplicate data."""
    seen = set()
    for item in iterable:
        dupkey = key(item)
        if dupkey not in seen:
            seen.add(dupkey)
            yield item


@Pipe
def uniq(iterable, key=lambda x: x):
    """Deduplicate consecutive duplicate values."""
    iterator = iter(iterable)
    try:
        prev = next(iterator)
    except StopIteration:
        return
    yield prev
    prevkey = key(prev)
    for item in iterator:
        itemkey = key(item)
        if itemkey != prevkey:
            yield item
        prevkey = itemkey


enumerate = Pipe(builtins.enumerate)


@Pipe
def permutations(iterable, r=None):
    # permutations('ABCD', 2) --> AB AC AD BA BC BD CA CB CD DA DB DC
    # permutations(range(3)) --> 012 021 102 120 201 210
    yield from itertools.permutations(iterable, r)


@Pipe
def netcat(to_send, host, port):
    """Send and receive bytes over TCP."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.connect((host, port))
        for data in to_send | traverse:
            s.send(data)
        while 1:
            data = s.recv(4096)
            if not data:
                break
            yield data


@Pipe
def traverse(args):
    if isinstance(args, (str, bytes)):
        yield args
        return
    for arg in args:
        try:
            yield from arg | traverse
        except TypeError:
            # not iterable --- output leaf
            yield arg


@Pipe
def tee(iterable):
    for item in iterable:
        sys.stdout.write(repr(item) + "\n")
        yield item


@Pipe
def select(iterable, selector):
    return builtins.map(selector, iterable)


map = select


@Pipe
def where(iterable, predicate):
    return (x for x in iterable if predicate(x))


filter = where


@Pipe
def take_while(iterable, predicate):
    return itertools.takewhile(predicate, iterable)


@Pipe
def skip_while(iterable, predicate):
    return itertools.dropwhile(predicate, iterable)


@Pipe
def groupby(iterable, keyfunc):
    return itertools.groupby(sorted(iterable, key=keyfunc), keyfunc)


@Pipe
def sort(iterable, key=None, reverse=False):  # pylint: disable=redefined-outer-name
    return sorted(iterable, key=key, reverse=reverse)


@Pipe
def reverse(iterable):
    return reversed(iterable)


@Pipe
def t(iterable, y):
    if hasattr(iterable, "__iter__") and not isinstance(iterable, str):
        return iterable + type(iterable)([y])
    return [iterable, y]


@Pipe
def transpose(iterable):
    return list(zip(*iterable))


@Pipe
def batched(iterable, n):
    iterator = iter(iterable)
    while batch := tuple(itertools.islice(iterator, n)):
        yield batch


chain = Pipe(itertools.chain.from_iterable)
chain_with = Pipe(itertools.chain)
islice = Pipe(itertools.islice)
izip = Pipe(zip)
