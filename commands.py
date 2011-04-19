# -*- coding: utf-8 -*-

"""
Pipe Commands.

"""
from . import Pipe

from contextlib import closing
import socket
import sys
import itertools
from functools import reduce

try:
    import builtins
except ImportError:
    import __builtin__ as builtins

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
    for item in (iterable | as_list)[-qte:]:
        yield item

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
    "Returns True if ALL elements in the given iterable are true for the given pred function"
    for x in iterable:
        if not pred(x):
            return False
    return True

@Pipe
def any(iterable, pred):
    "Returns True if ANY element in the given iterable is True for the given pred function"
    for x in iterable:
        if pred(x):
            return True
    return False

@Pipe
def average(iterable):
    """
    Build the average for the given iterable, starting with 0.0 as seed
    Will try a division by 0 if the iterable is empty...
    """
    total = 0.0
    qte = 0
    for x in iterable:
        total += x
        qte += 1
    return total / qte

@Pipe
def count(iterable):
    "Count the size of the given iterable, walking thrue it."
    count = 0
    for x in iterable:
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
    pool = tuple(iterable)
    n = len(pool)
    r = n if r is None else r
    if r > n:
        return
    indices = list(range(n))
    cycles = list(range(n, n-r, -1))
    yield tuple(pool[i] for i in indices[:r])
    while n:
        for i in reversed(range(r)):
            cycles[i] -= 1
            if cycles[i] == 0:
                indices[i:] = indices[i+1:] + indices[i:i+1]
                cycles[i] = n - i
            else:
                j = cycles[i]
                indices[i], indices[-j] = indices[-j], indices[i]
                yield tuple(pool[i] for i in indices[:r])
                break
        else:
            return

@Pipe
def netcat(to_send, host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.connect((host, port))
        for data in to_send | traverse:
            s.send(data)
        while 1:
            data = s.recv(4096)
            if not data: break
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
    return separator.join(map(str,iterable))

@Pipe
def as_list(iterable):
    return list(iterable)

@Pipe
def as_tuple(iterable):
    return tuple(iterable)

from collections import Iterable

@Pipe
def strout(inp):
    pprint(inp)

@Pipe
def stdout(inp):
    if not isinstance(inp, Iterable):
        inp = str(inp)
    if type(inp) in (str, unicode):
        sys.stdout.write(inp + "\n")
    else:
        for l in inp:
            l | stdout

from pprint import pprint
@Pipe
def ppout(inp):
    if type(inp) in (str, unicode):
        pprint(inp)
    else:
        for l in inp:
            pprint(l)

@Pipe
def tee(iterable):
    for item in iterable:
        sys.stdout.write(str(item) + "\n")
        yield item

@Pipe
def pptee(inp):
    for item in inp:
        pprint(item)
        yield item

@Pipe
def strtee(inp):
    print str(inp)
    return inp

@Pipe
def pull(inp):
    for i in inp:
        del i

#out = pull

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
        return reduce(function, iterable, kwargs['initializer'])
    else:
        return reduce(function, iterable)

@Pipe
def groupby(iterable, keyfunc):
    return itertools.groupby(sorted(iterable, key = keyfunc), keyfunc)

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
    return func(**iterable) if isinstance(iterable, dict) else func(*iterable)

chain_with = Pipe(itertools.chain)
islice = Pipe(itertools.islice)

# Python 2 & 3 compatibility
if "izip" in dir(itertools):
    izip = Pipe(itertools.izip)
else:
    izip = Pipe(zip)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
