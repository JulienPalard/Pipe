import builtins
import functools
import pipe

from collections import deque


class Terminator:
    """
    Terminate a pipeline, performing a final operation or returning a final result.

    Unlike Pipe elements, Terminators do not necessarily return iterables, but rather final results of a pipeline.
    Terminators can also perform final operations such as `foreach` and `reduce`.

    Represent a termination to a Pipe :
    Described as :
        as_list = Terminator(lambda iterable: list(iterable))
    then the following are equivalent :
        list(range(10) | is_even)
        range(10) | is_even > as_list

    Or represent a terminating Function :
        It's a function returning a Terminator
    Described as :
        join = Terminator(lambda iterable, sep: sep.join(iterable))
    and used as :
        range(10) | is_even > join("-")
        # 0-2-4-6-8

    Or represent a terminating operation :
    Described as :
        foreach = Terminator(lambda iterable, f: f(x) for x in iterable)
    and used as :
        range(10) | is_even > foreach(lambda x: print(x))
    """

    def __init__(self, function):
        self.function = function
        functools.update_wrapper(self, function)

    def __lt__(self, other):
        return self.function(other)

    def __call__(self, *args, **kwargs):
        return Terminator(
            lambda iterable, *args2, **kwargs2: self.function(
                iterable, *args, *args2, **kwargs, **kwargs2
            )
        )


#######################
# Collector Terminators
#######################


def _identity(x):
    return x


@Terminator
def as_dict(iterable, key_func=_identity, value_func=_identity):
    if key_func is _identity and value_func is _identity:
        return dict(iterable)

    return dict(iterable | pipe.map(lambda x: (key_func(x), value_func(x))))


@Terminator
def as_list(iterable):
    return list(iterable)


@Terminator
def as_set(iterable, key_func=_identity):
    if key_func is _identity:
        return dict(iterable)

    return set(iterable | pipe.map(lambda x: key_func(x)))


#####################
# General Terminators
#####################


@Terminator
def foreach(iterable, f):
    for item in iterable:
        f(item)


@Terminator
def join(iterable, sep=""):
    return sep.join(iterable)


_initial_missing = object()


@Terminator
def reduce(iterable, accumulator, initial_value=_initial_missing):
    if initial_value is _initial_missing:
        return functools.reduce(accumulator, iterable)
    return functools.reduce(accumulator, iterable, initial_value)


#######################
# Selecting Terminators
#######################


@Terminator
def first(iterable):
    return next(iter(iterable))


@Terminator
def last(iterable):
    return deque(iterable, maxlen=1).pop()


#####################
# Numeric Terminators
#####################


@Terminator
def max(iterable):
    return builtins.max(iterable)


@Terminator
def min(iterable):
    return builtins.min(iterable)


@Terminator
def sum(iterable):
    return builtins.sum(iterable)
