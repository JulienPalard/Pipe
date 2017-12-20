#!/usr/bin/env python

"""Module enabling a sh like infix syntax (using pipes).
"""

import functools
import itertools
import socket
import sys
import inspect
from contextlib import closing

try:
    import builtins
except ImportError:
    import __builtin__ as builtins

__author__ = 'Julien Palard <julien@eeple.fr>'
__credits__ = """Jerome Schneider, for its Python skillz,
and dalexander for contributing"""
__date__ = '10 Nov 2010'
__version__ = '1.4.2'
__all__ = [
    'Pipe', 'take', 'tail', 'skip', 'all', 'any', 'average', 'count',
    'max', 'min', 'as_dict', 'permutations', 'netcat', 'netwrite',
    'traverse', 'concat', 'as_list', 'as_tuple', 'stdout', 'lineout',
    'tee', 'add', 'first', 'chain', 'select', 'where', 'take_while',
    'skip_while', 'aggregate', 'groupby', 'sort', 'reverse',
    'chain_with', 'islice', 'izip', 'passed', 'index', 'strip',
    'lstrip', 'rstrip', 'run_with', 't', 'to_type', 'transpose'
]

__lambda_name__ = '<lambda>'


def is_lambda(f):
    return f.__name__ == __lambda_name__


def is_to_destruct(f):
    if not callable(f):
        raise TypeError('Not callable argument!')
    try:
        if getattr(f, '__code__', None) is None:
            return False
            # We cannot make sure that if we should destruct params when this callable object doesn't have '__code__' attribute.
        arg_info = inspect.getfullargspec(f)
    except TypeError:
        # As for builtin callable objects which cannot be inpected, We take them as single-parameter functions by default.
        return False

    if not is_lambda(f):
        # If it's not a `lambda`, we should handle default arguments, keyword argument and star argument.
        # There is a safe way to destruct parameters:
        # We should ensure that, if we couldn't judge whether we should destruct the parameter,
        #    take it as a single-parameter function.
        # And if there are at least two non-default formal arguments, the only actual parameter should be destructed.
        if arg_info.varargs or arg_info.kwonlyargs or arg_info.defaults:
            return False
        n = len(arg_info.args)
    else:
        # When it's a `lambda`, the judgement could be easier:
        # If `varargs` has any `varargs`, the parameter should be destructed.
        # If there are at least two formal arguments(normal arguments and default ones),
        #    the only actual parameter should be destructed.
        if arg_info.varargs:
            return True
        n = len(arg_info.args) + len(arg_info.kwonlyargs)

    if n is 0:
        raise TypeError('Function can not be with zero parameter.')
    return n is not 1


def destruct_func(f):
    # An example:
    # (1, 2) | Pipe(lambda x, y: x+y)
    # => 3
    def destruct(e):
        return f(*e)

    return destruct


class Pipe:
    """
    Represent a Pipeable Element :
    Described as :
    first = Pipe(lambda iterable: next(iter(iterable)))
    and used as :
    print [1, 2, 3] | first
    printing 1

    Or represent a Pipeable Function :
    It's a function returning a Pipe
    Described as :
    select = Pipe(lambda iterable, pred: (pred(x) for x in iterable))
    and used as :
    print [1, 2, 3] | select(lambda x: x * 2)
    # 2, 4, 6
    """

    def __init__(self, function):
        self.function = destruct_func(function) if is_to_destruct(function) else function
        functools.update_wrapper(self, function)

    def __ror__(self, other):
        return self.function(other)

    def __call__(self, *args, **kwargs):
        return Pipe(lambda x: self.function(x, *args, **kwargs))


@Pipe
def take(iterable, qte):
    "Yield qte of elements in the given iterable."
    for item in iterable:
        if qte > 0:
            qte -= 1
            yield item
        else:
            return


@Pipe
def tail(iterable, qte):
    "Yield qte of elements in the given iterable."
    out = []
    for item in iterable:
        out.append(item)
        if len(out) > qte:
            out.pop(0)
    return out


@Pipe
def skip(iterable, qte):
    "Skip qte elements in the given iterable, then yield others."
    for item in iterable:
        if qte == 0:
            yield item
        else:
            qte -= 1


@Pipe
def all(iterable, pred):
    """Returns True if ALL elements in the given iterable are true for the
    given pred function"""
    return builtins.all(pred(x) for x in iterable)


@Pipe
def any(iterable, pred):
    """Returns True if ANY element in the given iterable is True for the
    given pred function"""
    return builtins.any(pred(x) for x in iterable)


@Pipe
def average(iterable):
    """Build the average for the given iterable, starting with 0.0 as seed
    Will try a division by 0 if the iterable is empty...
    """
    total = 0.0
    qte = 0
    for element in iterable:
        total += element
        qte += 1
    return total / qte


@Pipe
def count(iterable):
    "Count the size of the given iterable, walking thrue it."
    count = 0
    for element in iterable:
        count += 1
    return count


@Pipe
def max(iterable, **kwargs):
    return builtins.max(iterable, **kwargs)


@Pipe
def min(iterable, **kwargs):
    return builtins.min(iterable, **kwargs)


@Pipe
def as_dict(iterable):
    return dict(iterable)


@Pipe
def permutations(iterable, r=None):
    # permutations('ABCD', 2) --> AB AC AD BA BC BD CA CB CD DA DB DC
    # permutations(range(3)) --> 012 021 102 120 201 210
    for x in itertools.permutations(iterable, r):
        yield x


@Pipe
def netcat(to_send, host, port):
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
def netwrite(to_send, host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.connect((host, port))
        for data in to_send | traverse:
            s.send(data)


@Pipe
def traverse(args):
    for arg in args:
        try:
            if isinstance(arg, str):
                yield arg
            else:
                for i in arg | traverse:
                    yield i
        except TypeError:
            # not iterable --- output leaf
            yield arg


@Pipe
def concat(iterable, separator=", "):
    return separator.join(map(str, iterable))


@Pipe
def as_list(iterable):
    return list(iterable)


@Pipe
def as_tuple(iterable):
    return tuple(iterable)


@Pipe
def stdout(x):
    sys.stdout.write(str(x))


@Pipe
def lineout(x):
    sys.stdout.write(str(x) + "\n")


@Pipe
def tee(iterable):
    for item in iterable:
        sys.stdout.write(str(item) + "\n")
        yield item


@Pipe
def write(iterable, fname, glue='\n'):
    with open(fname, 'w') as f:
        for item in iterable:
            f.write(str(item) + glue)


@Pipe
def add(x):
    return sum(x)


@Pipe
def first(iterable):
    return next(iter(iterable))


@Pipe
def chain(iterable):
    return itertools.chain(*iterable)


@Pipe
def select(iterable, selector):
    return (selector(x) for x in iterable)


@Pipe
def where(iterable, predicate):
    return (x for x in iterable if (predicate(x)))


@Pipe
def take_while(iterable, predicate):
    return itertools.takewhile(predicate, iterable)


@Pipe
def skip_while(iterable, predicate):
    return itertools.dropwhile(predicate, iterable)


@Pipe
def aggregate(iterable, function, **kwargs):
    if 'initializer' in kwargs:
        return functools.reduce(function, iterable, kwargs['initializer'])
    return functools.reduce(function, iterable)


@Pipe
def groupby(iterable, keyfunc):
    return itertools.groupby(sorted(iterable, key=keyfunc), keyfunc)


@Pipe
def sort(iterable, **kwargs):
    return sorted(iterable, **kwargs)


@Pipe
def reverse(iterable):
    return reversed(iterable)


@Pipe
def passed(x):
    pass


@Pipe
def index(iterable, value, start=0, stop=None):
    return iterable.index(value, start, stop or len(iterable))


@Pipe
def strip(iterable, chars=None):
    return iterable.strip(chars)


@Pipe
def rstrip(iterable, chars=None):
    return iterable.rstrip(chars)


@Pipe
def lstrip(iterable, chars=None):
    return iterable.lstrip(chars)


@Pipe
def run_with(iterable, func):
    return (func(**iterable) if isinstance(iterable, dict) else
            func(*iterable) if hasattr(iterable, '__iter__') else
            func(iterable))


@Pipe
def t(iterable, y):
    if hasattr(iterable, '__iter__') and not isinstance(iterable, str):
        return iterable + type(iterable)([y])
    return [iterable, y]


@Pipe
def to_type(x, t):
    return t(x)


@Pipe
def transpose(iterable):
    return list(zip(*iterable))


chain_with = Pipe(itertools.chain)
islice = Pipe(itertools.islice)

# Python 2 & 3 compatibility
if "izip" in dir(itertools):
    izip = Pipe(itertools.izip)
else:
    izip = Pipe(zip)

if __name__ == "__main__":
    import doctest

    doctest.testfile('README.md')
