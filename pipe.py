#!/usr/bin/env python
import functools

""" Infix programming toolkit

Module enabling a sh like infix syntax (using pipes).

= Introduction =
As an exemple, here is the solution for the 2nd Euler Project exercise :

"Find the sum of all the even-valued terms in Fibonacci
 which do not exceed four million."

Given fib a generator of fibonacci numbers :

euler2 = fib() | where(lambda x: x % 2 == 0)
               | take_while(lambda x: x < 4000000)
               | add


= Vocabulary =
 * a Pipe: a Pipe is a 'pipeable' function, somthing that you can pipe to,
           In the code '[1, 2, 3] | add' add is a Pipe
 * a Pipe function: A standard function returning a Pipe so it can be used like
           a normal Pipe but called like in : [1, 2, 3] | concat("#")


= Syntax =
The basic symtax is to use a Pipe like in a shell :
>>> [1, 2, 3] | add
6

A Pipe can be a function call, for exemple the Pipe function 'where' :
>>> [1, 2, 3] | where(lambda x: x % 2 == 0) #doctest: +ELLIPSIS
<generator object <genexpr> at ...>

A Pipe as a function is nothing more than a function returning
a specialized Pipe.


= Constructing your own =
You can construct your pipes using Pipe classe initialized with lambdas like :

stdout = Pipe(lambda x: sys.stdout.write(str(x)))
select = Pipe(lambda iterable, pred: (pred(x) for x in iterable))

Or using decorators :
@Pipe
def stdout(x):
    sys.stdout.write(str(x))

= Existing Pipes in this module =

stdout
    Outputs anything to the standard output
    >>> "42" | stdout
    42

lineout
    Outputs anything to the standard output followed by a line break
    >>> 42 | lineout
    42

tee
    tee outputs to the standard output and yield unchanged items, usefull for
    debugging
    >>> [1, 2, 3, 4, 5] | tee | add
    1
    2
    3
    4
    5
    15

as_list
    Outputs an iterable as a list
    >>> (0, 1, 2) | as_list
    [0, 1, 2]

as_tuple
    Outputs an iterable as a tuple
    >>> [1, 2, 3] | as_tuple
    (1, 2, 3)

as_dict
    Outputs an iterable of tuples as a dictionary
    [('a', 1), ('b', 2), ('c', 3)] | as_dict
    {'a': 1, 'b': 2, 'c': 3}

concat()
    Aggregates strings using given separator, or ", " by default
    >>> [1, 2, 3, 4] | concat
    '1, 2, 3, 4'
    >>> [1, 2, 3, 4] | concat("#")
    '1#2#3#4'

average
    Returns the average of the given iterable
    >>> [1, 2, 3, 4, 5, 6] | average
    3.5

netcat
    Open a socket on the given host and port, and send data to it,
    Yields host reponse as it come.
    netcat apply traverse to its input so it can take a string or
    any iterable.

    "GET / HTTP/1.0\r\nHost: google.fr\r\n\r\n" \
        | netcat('google.fr', 80)               \
        | concat                                \
        | stdout

netwrite
    Like netcat but don't read the socket after sending data

count
    Returns the length of the given iterable, counting elements one by one
    >>> [1, 2, 3, 4, 5, 6] | count
    6

add
    Returns the sum of all elements in the preceding iterable
    >>> (1, 2, 3, 4, 5, 6) | add
    21

first
    Returns the first element of the given iterable
    >>> (1, 2, 3, 4, 5, 6) | first
    1

chain
    Unfold preceding Iterable of Iterables
    >>> [[1, 2], [3, 4], [5]] | chain | concat
    '1, 2, 3, 4, 5'

    Warning : chain only unfold iterable containing ONLY iterables :
      [1, 2, [3]] | chain
          Gives a TypeError: chain argument #1 must support iteration
          Consider using traverse

traverse
    Recursively unfold iterables
    >>> [[1, 2], [[[3], [[4]]], [5]]] | traverse | concat
    '1, 2, 3, 4, 5'
    >>> squares = (i * i for i in range(3))
    >>> [[0, 1, 2], squares] | traverse | as_list
    [0, 1, 2, 0, 1, 4]

select()
    Apply a conversion expression given as parameter
    to each element of the given iterable
    >>> [1, 2, 3] | select(lambda x: x * x) | concat
    '1, 4, 9'

where()
    Only yields the matching items of the given iterable
    >>> [1, 2, 3] | where(lambda x: x % 2 == 0) | concat
    '2'

take_while()
    Like itertools.takewhile, yields elements of the
    given iterable while the predicat is true
    >>> [1, 2, 3, 4] | take_while(lambda x: x < 3) | concat
    '1, 2'

skip_while()
    Like itertools.dropwhile, skips elements of the given iterable
    while the predicat is true, then yields others
    >>> [1, 2, 3, 4] | skip_while(lambda x: x < 3) | concat
    '3, 4'

chain_with()
    Like itertools.chain, yields elements of the given iterable,
    then yields elements of its parameters
    >>> (1, 2, 3) | chain_with([4, 5], [6]) | concat
    '1, 2, 3, 4, 5, 6'

take()
    Yields the given quantity of elemenets from the given iterable, like head
    in shell script.
    >>> (1, 2, 3, 4, 5) | take(2) | concat
    '1, 2'

tail()
    Yiels the given quantity of the last elements of the given iterable.
    >>> (1, 2, 3, 4, 5) | tail(3) | concat
    '3, 4, 5'

skip()
    Skips the given quantity of elements from the given iterable, then yields
    >>> (1, 2, 3, 4, 5) | skip(2) | concat
    '3, 4, 5'

islice()
    Just the itertools.islice
    >>> (1, 2, 3, 4, 5, 6, 7, 8, 9) | islice(2, 8, 2) | concat
    '3, 5, 7'

izip()
    Just the itertools.izip
    >>> (1, 2, 3, 4, 5, 6, 7, 8, 9) \
            | izip([9, 8, 7, 6, 5, 4, 3, 2, 1]) \
            | concat
    '(1, 9), (2, 8), (3, 7), (4, 6), (5, 5), (6, 4), (7, 3), (8, 2), (9, 1)'

aggregate()
    Works as python reduce, the optional initializer must be passed as a
    keyword argument
    >>> (1, 2, 3, 4, 5, 6, 7, 8, 9) | aggregate(lambda x, y: x * y)
    362880

    >>> () | aggregate(lambda x, y: x + y, initializer=0)
    0

    Simulate concat :
    >>> (1, 2, 3, 4, 5, 6, 7, 8, 9) \
            | aggregate(lambda x, y: str(x) + ', ' + str(y))
    '1, 2, 3, 4, 5, 6, 7, 8, 9'

any()
    Returns True if any element of the given iterable satisfies the predicate
    >>> (1, 3, 5, 6, 7) | any(lambda x: x >= 7)
    True

    >>> (1, 3, 5, 6, 7) | any(lambda x: x > 7)
    False

all()
    Returns True if all elements of the given iterable
    satisfies the given predicate
    >>> (1, 3, 5, 6, 7) | all(lambda x: x < 7)
    False

    >>> (1, 3, 5, 6, 7) | all(lambda x: x <= 7)
    True

max()
    Returns the biggest element, using the given key function if
    provided (or else the identity)

    >>> ('aa', 'b', 'foo', 'qwerty', 'bar', 'zoog') | max(key=len)
    'qwerty'
    >>> ('aa', 'b', 'foo', 'qwerty', 'bar', 'zoog') | max()
    'zoog'
    >>> ('aa', 'b', 'foo', 'qwerty', 'bar', 'zoog') | max
    'zoog'

min()
    Returns the smallest element, using the key function if provided
    (or else the identity)

    >>> ('aa', 'b', 'foo', 'qwerty', 'bar', 'zoog') | min(key=len)
    'b'
    >>> ('aa', 'b', 'foo', 'qwerty', 'bar', 'zoog') | min
    'aa'

groupby()
    Like itertools.groupby(sorted(iterable, key = keyfunc), keyfunc)
    (1, 2, 3, 4, 5, 6, 7, 8, 9) \
            | groupby(lambda x: x % 2 and "Even" or "Odd")
            | select(lambda x: "%s : %s" % (x[0], (x[1] | concat(', '))))
            | concat(' / ')
    'Even : 1, 3, 5, 7, 9 / Odd : 2, 4, 6, 8'

sort()
    Like Python's built-in "sorted" primitive. Allows cmp (Python 2.x
    only), key, and reverse arguments. By default sorts using the
    identity function as the key.

    >>> "python" | sort | concat("")
    'hnopty'
    >>> [5, -4, 3, -2, 1] | sort(key=abs) | concat
    '1, -2, 3, -4, 5'

reverse
    Like Python's built-in "reversed" primitive.
    >>> [1, 2, 3] | reverse | concat
    '3, 2, 1'

passed
    Like Python's pass.
    >>> "something" | passed


index
    Returns index of value in iterable
    >>> [1,2,3,2,1] | index(2)
    1
    >>> [1,2,3,2,1] | index(1,1)
    4

strip
    Like Python's strip-method for str.
    >>> '  abc   ' | strip
    'abc'
    >>> '.,[abc] ] ' | strip('.,[] ')
    'abc'

rstrip
    Like Python's rstrip-method for str.
    >>> '  abc   ' | rstrip
    '  abc'
    >>> '.,[abc] ] ' | rstrip('.,[] ')
    '.,[abc'

lstrip
    Like Python's lstrip-method for str.
    >>> 'abc   ' | lstrip
    'abc   '
    >>> '.,[abc] ] ' | lstrip('.,[] ')
    'abc] ] '

run_with
    >>> (1,10,2) | run_with(range) | as_list
    [1, 3, 5, 7, 9]

t
    Like Haskell's operator ":"
    >>> 0 | t(1) | t(2) == range(3) | as_list
    True

to_type
    Typecast
    >>> range(5) | add | to_type(str) | t(' is summ!') | concat('')
    '10 is summ!'

permutations()
    Returns all possible permutations
    >>> 'ABC' | permutations(2) | concat(' ')
    "('A', 'B') ('A', 'C') ('B', 'A') ('B', 'C') ('C', 'A') ('C', 'B')"

    >>> range(3) | permutations | concat('-')
    '(0, 1, 2)-(0, 2, 1)-(1, 0, 2)-(1, 2, 0)-(2, 0, 1)-(2, 1, 0)'

transpose()
    Transposes the rows and columns of a matrix
    >>> [[1, 2, 3], [4, 5, 6], [7, 8, 9]] | transpose
    [(1, 4, 7), (2, 5, 8), (3, 6, 9)]

Euler project samples :

    # Find the sum of all the multiples of 3 or 5 below 1000.
    euler1 = (itertools.count() | select(lambda x: x * 3) | take_while(lambda x: x < 1000) | add) \
           + (itertools.count() | select(lambda x: x * 5) | take_while(lambda x: x < 1000) | add) \
           - (itertools.count() | select(lambda x: x * 15) | take_while(lambda x: x < 1000) | add)
    assert euler1 == 233168

    # Find the sum of all the even-valued terms in Fibonacci which do not exceed four million.
    euler2 = fib() | where(lambda x: x % 2 == 0) | take_while(lambda x: x < 4000000) | add
    assert euler2 == 4613732

    # Find the difference between the sum of the squares of the first one hundred natural numbers and the square of the sum.
    square = lambda x: x * x
    euler6 = square(itertools.count(1) | take(100) | add) - (itertools.count(1) | take(100) | select(square) | add)
    assert euler6 == 25164150


"""
from contextlib import closing
import socket
import itertools
from functools import reduce
import sys

try:
    import builtins
except ImportError:
    import __builtin__ as builtins


__author__ = 'Julien Palard <julien@eeple.fr>'
__credits__ = """Jerome Schneider, for its Python skillz,
and dalexander for contributing"""
__date__ = '10 Nov 2010'
__version__ = '1.4'
__all__ = [
    'Pipe', 'take', 'tail', 'skip', 'all', 'any', 'average', 'count',
    'max', 'min', 'as_dict', 'permutations', 'netcat', 'netwrite',
    'traverse', 'concat', 'as_list', 'as_tuple', 'stdout', 'lineout',
    'tee', 'add', 'first', 'chain', 'select', 'where', 'take_while',
    'skip_while', 'aggregate', 'groupby', 'sort', 'reverse',
    'chain_with', 'islice', 'izip', 'passed', 'index', 'strip',
    'lstrip', 'rstrip', 'run_with', 't', 'to_type', 'transpose'
]

class Pipe(object):
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
    def __init__(self, decorated):
        if hasattr(decorated, '__func__'):
            # For static- and classmethods
            functools.wraps(decorated.__func__)(self)
        elif hasattr(decorated, '__name__'):
            functools.wraps(decorated)(self)
        else:
            # For callable objects
            functools.wraps(type(decorated))(self)

        self.decorated = decorated


    def __ror__(self, other):
        return self.decorated(other)

    def __call__(self, *args, **kwargs):
        return type(self)(lambda x: self.decorated(x, *args, **kwargs))

    def __get__(self, instance, owner):
        # For any decorated which is also a descriptor
        if hasattr(self.decorated, '__get__'):
            function_to_pipe = self.decorated.__get__(instance, owner)
        else:
            function_to_pipe = self.decorated

        return type(self)(function_to_pipe)

    def bind(self, instance_or_class):
        return type(self)(lambda x: self.decorated(instance_or_class, x))

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
    "Returns True if ALL elements in the given iterable are true for the given pred function"
    return builtins.all(pred(x) for x in iterable)

@Pipe
def any(iterable, pred):
    "Returns True if ANY element in the given iterable is True for the given pred function"
    return builtins.any(pred(x) for x in iterable)

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
    return  func(**iterable) if isinstance(iterable, dict) else \
            func( *iterable) if hasattr(iterable,'__iter__') else \
            func(  iterable)

@Pipe
def t(iterable, y):
    if hasattr(iterable,'__iter__') and not isinstance(iterable, str):
        return iterable + type(iterable)([y])
    else:
        return [iterable, y]

@Pipe
def to_type(x, t):
    return t(x)

@Pipe
def transpose(iterable):
    return zip(*iterable)

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
