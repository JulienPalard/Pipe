#!/usr/bin/env python
""" Infix programming toolkit

Module enabling a sh like infix syntax (using pipes).

= Introduction =
As an exemple, here is the solution for the 2nd Euler Project exercise :

"Find the sum of all the even-valued terms in Fibonacci
 which do not exceed four million."

Given fib a generator of fibonacci numbers :

euler2 = Pipe(fib()).where(lambda x: x % 2 == 0)
                    .take_while(lambda x: x < 4000000)
                    .add().data


= Vocabulary =
 * a Pipe: a Pipe is a 'pipeable' function, somthing that you can pipe to,
           In the code 'Pipe([1, 2, 3]).add' add is a Pipe
 * a Pipe function: A standard function returning a Pipe so it can be used like
           a normal Pipe but called like in : Pipe([1, 2, 3]).concat("#")


= Syntax =
The basic symtax is to use a Pipe like in a shell :
>>> Pipe([1, 2, 3]).add().data
6

A Pipe can be a function call, for exemple the Pipe function 'where' :
>>> Pipe([1, 2, 3]).where(lambda x: x % 2 == 0).data #doctest: +ELLIPSIS
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
    >>> Pipe("42").stdout().data
    42

lineout
    Outputs anything to the standard output followed by a line break
    >>> Pipe(42).lineout().data
    42

tee
    tee outputs to the standard output and yield unchanged items, usefull for
    debugging
    >>> Pipe([1, 2, 3, 4, 5]).tee().add().data
    1
    2
    3
    4
    5
    15

as_list
    Outputs an iterable as a list
    >>> Pipe((0, 1, 2)).as_list().data
    [0, 1, 2]

as_tuple
    Outputs an iterable as a tuple
    >>> Pipe([1, 2, 3]).as_tuple().data
    (1, 2, 3)

as_dict
    Outputs an iterable of tuples as a dictionary
    Pipe([('a', 1), ('b', 2), ('c', 3)]).as_dict().data
    {'a': 1, 'b': 2, 'c': 3}

concat()
    Aggregates strings using given separator, or ", " by default
    >>> Pipe([1, 2, 3, 4]).concat().data
    '1, 2, 3, 4'
    >>> Pipe([1, 2, 3, 4]).concat("#").data
    '1#2#3#4'

average
    Returns the average of the given iterable
    >>> Pipe([1, 2, 3, 4, 5, 6]).average().data
    3.5

netcat
    Open a socket on the given host and port, and send data to it,
    Yields host reponse as it come.
    netcat apply traverse to its input so it can take a string or
    any iterable.

    "GET / HTTP/1.0\r\nHost: google.fr\r\n\r\n" \
       .netcat('google.fr', 80)               \
       .concat                                \
       .stdout()

netwrite
    Like netcat but don't read the socket after sending data

count
    Returns the length of the given iterable, counting elements one by one
    >>> Pipe([1, 2, 3, 4, 5, 6]).count().data
    6

    >>> Pipe(i for i in range(10)).count().data
    10

add
    Returns the sum of all elements in the preceding iterable
    >>> Pipe((1, 2, 3, 4, 5, 6)).add().data
    21

first
    Returns the first element of the given iterable
    >>> Pipe((1, 2, 3, 4, 5, 6)).first().data
    1

chain
    Unfold preceding Iterable of Iterables
    >>> Pipe([[1, 2], [3, 4], [5]]).chain().concat().data
    '1, 2, 3, 4, 5'

    Warning : chain only unfold iterable containing ONLY iterables :
      Pipe([1, 2, [3]]).chain
          Gives a TypeError: chain argument #1 must support iteration
          Consider using traverse

traverse
    Recursively unfold iterables
    >>> Pipe([[1, 2], [[[3], [[4]]], [5]]]).traverse().concat().data
    '1, 2, 3, 4, 5'
    >>> squares = (i * i for i in range(3))
    >>> Pipe([[0, 1, 2], squares]).traverse().as_list().data
    [0, 1, 2, 0, 1, 4]

select()
    Apply a conversion expression given as parameter
    to each element of the given iterable
    >>> Pipe([1, 2, 3]).select(lambda x: x * x).concat().data
    '1, 4, 9'

where()
    Only yields the matching items of the given iterable
    >>> Pipe([1, 2, 3]).where(lambda x: x % 2 == 0).concat().data
    '2'

take_while()
    Like itertools.takewhile, yields elements of the
    given iterable while the predicat is true
    >>> Pipe([1, 2, 3, 4]).take_while(lambda x: x < 3).concat().data
    '1, 2'

skip_while()
    Like itertools.dropwhile, skips elements of the given iterable
    while the predicat is true, then yields others
    >>> Pipe([1, 2, 3, 4]).skip_while(lambda x: x < 3).concat().data
    '3, 4'

chain_with()
    Like itertools.chain, yields elements of the given iterable,
    then yields elements of its parameters
    >>> Pipe((1, 2, 3)).chain_with([4, 5], [6]).concat().data
    '1, 2, 3, 4, 5, 6'

take()
    Yields the given quantity of elemenets from the given iterable, like head
    in shell script.
    >>> Pipe((1, 2, 3, 4, 5)).take(2).concat().data
    '1, 2'

tail()
    Yiels the given quantity of the last elements of the given iterable.
    >>> Pipe((1, 2, 3, 4, 5)).tail(3).concat().data
    '3, 4, 5'

skip()
    Skips the given quantity of elements from the given iterable, then yields
    >>> Pipe((1, 2, 3, 4, 5)).skip(2).concat().data
    '3, 4, 5'

islice()
    Just the itertools.islice
    >>> Pipe((1, 2, 3, 4, 5, 6, 7, 8, 9)).islice(2, 8, 2).concat().data
    '3, 5, 7'

izip()
    Just the itertools.izip
    >>> Pipe((1, 2, 3, 4, 5, 6, 7, 8, 9)) \
           .izip([9, 8, 7, 6, 5, 4, 3, 2, 1]) \
           .concat().data
    '(1, 9), (2, 8), (3, 7), (4, 6), (5, 5), (6, 4), (7, 3), (8, 2), (9, 1)'

aggregate()
    Works as python reduce, the optional initializer must be passed as a
    keyword argument
    >>> Pipe((1, 2, 3, 4, 5, 6, 7, 8, 9)).aggregate(lambda x, y: x * y).data
    362880

    >>> Pipe(()).aggregate(lambda x, y: x + y, initializer=0).data
    0

    Simulate concat :
    >>> Pipe((1, 2, 3, 4, 5, 6, 7, 8, 9)) \
           .aggregate(lambda x, y: str(x) + ', ' + str(y)).data
    '1, 2, 3, 4, 5, 6, 7, 8, 9'

any()
    Returns True if any element of the given iterable satisfies the predicate
    >>> Pipe((1, 3, 5, 6, 7)).any(lambda x: x >= 7).data
    True

    >>> Pipe((1, 3, 5, 6, 7)).any(lambda x: x > 7).data
    False

all()
    Returns True if all elements of the given iterable
    satisfies the given predicate
    >>> Pipe((1, 3, 5, 6, 7)).all(lambda x: x < 7).data
    False

    >>> Pipe((1, 3, 5, 6, 7)).all(lambda x: x <= 7).data
    True

max()
    Returns the biggest element, using the given key function if
    provided (or else the identity)

    >>> Pipe(('aa', 'b', 'foo', 'qwerty', 'bar', 'zoog')).max(key=len).data
    'qwerty'
    >>> Pipe(('aa', 'b', 'foo', 'qwerty', 'bar', 'zoog')).max().data
    'zoog'
    >>> Pipe(('aa', 'b', 'foo', 'qwerty', 'bar', 'zoog')).max().data
    'zoog'

min()
    Returns the smallest element, using the key function if provided
    (or else the identity)

    >>> Pipe(('aa', 'b', 'foo', 'qwerty', 'bar', 'zoog')).min(key=len).data
    'b'
    >>> Pipe(('aa', 'b', 'foo', 'qwerty', 'bar', 'zoog')).min().data
    'aa'

groupby()
    Like itertools.groupby(sorted(iterable, key = keyfunc), keyfunc)
    (1, 2, 3, 4, 5, 6, 7, 8, 9) \
           .groupby(lambda x: x % 2 and "Even" or "Odd")
           .select(lambda x: "%s : %s" % (xPipe([0], (x[1]).concat(', '))))
           .concat(' / ').data
    'Even : 1, 3, 5, 7, 9 / Odd : 2, 4, 6, 8'

sort()
    Like Python's built-in "sorted" primitive. Allows cmp (Python 2.x
    only), key, and reverse arguments. By default sorts using the
    identity function as the key.

    >>> Pipe("python").sort().concat("").data
    'hnopty'
    >>> Pipe([5, -4, 3, -2, 1]).sort(key=abs).concat().data
    '1, -2, 3, -4, 5'

reverse
    Like Python's built-in "reversed" primitive.
    >>> Pipe([1, 2, 3]).reverse().concat().data
    '3, 2, 1'

passed
    Like Python's pass.
    >>> Pipe("something").passed().data

index
    Returns index of value in iterable
    >>> Pipe([1,2,3,2,1]).index(2).data
    1
    >>> Pipe([1,2,3,2,1]).index(1,1).data
    4

strip
    Like Python's strip-method for str.
    >>> '  abc   '.strip()
    'abc'
    >>> '.,[abc] ] '.strip('.,[] ')
    'abc'

rstrip
    Like Python's rstrip-method for str.
    >>> '  abc   '.rstrip()
    '  abc'
    >>> '.,[abc] ] '.rstrip('.,[] ')
    '.,[abc'

lstrip
    Like Python's lstrip-method for str.
    >>> 'abc   '.lstrip()
    'abc   '
    >>> '.,[abc] ] '.lstrip('.,[] ')
    'abc] ] '

run_with
    >>> Pipe((1,10,2)).run_with(range).as_list().data
    [1, 3, 5, 7, 9]

    Like Haskell's operator ":"
    >>> Pipe(0).t(1).t(2).data == Pipe(range(3)).as_list().data
    True

to_type
    Typecast
    >>> Pipe(range(5)).add().to_type(str).t(' is summ!').concat('').data
    '10 is summ!'

permutations()
    Returns all possible permutations
    >>> Pipe('ABC').permutations(2).concat(' ').data
    "('A', 'B') ('A', 'C') ('B', 'A') ('B', 'C') ('C', 'A') ('C', 'B')"

    >>> Pipe(range(3)).permutations().concat('-').data
    '(0, 1, 2)-(0, 2, 1)-(1, 0, 2)-(1, 2, 0)-(2, 0, 1)-(2, 1, 0)'

windowed
    Returns iterable which yields sliding windows of containing
    elements drawn from given iterable.
    >>> Pipe((1, 2, 3, 4, 5, 6, 7, 8)).windowed(2).as_list().data
    [[1, 2], [3, 4], [5, 6], [7, 8]]

    >>> Pipe((1, 2, 3, 4, 5, 6, 7, 8)).windowed(3).as_list().data
    [[1, 2, 3], [4, 5, 6], [7, 8]]

Euler project samples :

    # Find the sum of all the multiples of 3 or 5 below 1000.
    euler1 = (itertools.count().select(lambda x: x * 3).take_while(lambda x: x < 1000).add) \
           + (itertools.count().select(lambda x: x * 5).take_while(lambda x: x < 1000).add) \
           - (itertools.count().select(lambda x: x * 15).take_while(lambda x: x < 1000).add)
    assert euler1 == 233168

    # Find the sum of all the even-valued terms in Fibonacci which do not exceed four million.
    euler2 = fib().where(lambda x: x % 2 == 0).take_while(lambda x: x < 4000000).add()
    assert euler2 == 4613732

    # Find the difference between the sum of the squares of the first one hundred natural numbers and the square of the sum.
    square = lambda x: x * x
    euler6 = square(itertools.count(1).take(100).add) - (itertools.count(1).take(100).select(square).add)
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
    'lstrip', 'rstrip', 'run_with', 't', 'to_type',
]


class Pipe(object):
    def __init__(self, data):
        self.data = data

    @staticmethod
    def register(f, name=None):
        def _(self, *args, **kwargs):
            return Pipe(f(self.data, *args, **kwargs))
        setattr(Pipe, f.__name__ if name is None else name, _)
        return f

@Pipe.register
def take(iterable, qte):
    "Yield qte of elements in the given iterable."
    for item in iterable:
        if qte > 0:
            qte -= 1
            yield item
        else:
            return

@Pipe.register
def tail(iterable, qte):
    "Yield qte of elements in the given iterable."
    out = []
    for item in iterable:
        out.append(item)
        if len(out) > qte:
            out.pop(0)
    return out

@Pipe.register
def skip(iterable, qte):
    "Skip qte elements in the given iterable, then yield others."
    for item in iterable:
        if qte == 0:
            yield item
        else:
            qte -= 1

@Pipe.register
def all(iterable, pred):
    "Returns True if ALL elements in the given iterable are true for the given pred function"
    return builtins.all(pred(x) for x in iterable)

@Pipe.register
def any(iterable, pred):
    "Returns True if ANY element in the given iterable is True for the given pred function"
    return builtins.any(pred(x) for x in iterable)

@Pipe.register
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

@Pipe.register
def count(iterable):
    "Count the size of the given iterable, walking thrue it."
    count = 0
    for x in iterable:
        count += 1
    return count

@Pipe.register
def max(iterable, **kwargs):
    return builtins.max(iterable, **kwargs)

@Pipe.register
def min(iterable, **kwargs):
    return builtins.min(iterable, **kwargs)

@Pipe.register
def as_dict(iterable):
    return dict(iterable)

@Pipe.register
def permutations(iterable, r=None):
    # permutations('ABCD', 2) --> AB AC AD BA BC BD CA CB CD DA DB DC
    # permutations(range(3)) --> 012 021 102 120 201 210
    for x in itertools.permutations(iterable, r):
        yield x

@Pipe.register
def netcat(to_send, host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.connect((host, port))
        for data in to_send.traverse:
            s.send(data)
        while 1:
            data = s.recv(4096)
            if not data: break
            yield data

@Pipe.register
def netwrite(to_send, host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.connect((host, port))
        for data in to_send.traverse:
            s.send(data)

@Pipe.register
def traverse(args):
    for arg in args:
        try:
            if isinstance(arg, str):
                yield arg
            else:
                for i in traverse(arg):
                    yield i
        except TypeError:
            # not iterable --- output leaf
            yield arg

@Pipe.register
def concat(iterable, separator=", "):
    try:
        return separator.join(map(str, iterable))
    except UnicodeEncodeError:
        # in case it's unicode no mapping is required.
        return separator.join(iterable)

@Pipe.register
def as_list(iterable):
    return list(iterable)

@Pipe.register
def as_tuple(iterable):
    return tuple(iterable)

@Pipe.register
def stdout(x):
    sys.stdout.write(str(x))

@Pipe.register
def lineout(x):
    sys.stdout.write(str(x) + "\n")

@Pipe.register
def tee(iterable):
    for item in iterable:
        sys.stdout.write(str(item) + "\n")
        yield item

@Pipe.register
def add(x):
    return sum(x)

@Pipe.register
def first(iterable):
    return next(iter(iterable))

@Pipe.register
def chain(iterable):
    return itertools.chain(*iterable)

@Pipe.register
def select(iterable, selector):
    return (selector(x) for x in iterable)

@Pipe.register
def where(iterable, predicate):
    return (x for x in iterable if (predicate(x)))

@Pipe.register
def take_while(iterable, predicate):
    return itertools.takewhile(predicate, iterable)

@Pipe.register
def skip_while(iterable, predicate):
    return itertools.dropwhile(predicate, iterable)

@Pipe.register
def aggregate(iterable, function, **kwargs):
    if 'initializer' in kwargs:
        return reduce(function, iterable, kwargs['initializer'])
    else:
        return reduce(function, iterable)
@Pipe.register
def groupby(iterable, keyfunc):
    return itertools.groupby(sorted(iterable, key = keyfunc), keyfunc)

@Pipe.register
def sort(iterable, **kwargs):
    return sorted(iterable, **kwargs)

@Pipe.register
def reverse(iterable):
    return reversed(iterable)

@Pipe.register
def passed(x):
    pass

@Pipe.register
def index(iterable, value, start=0, stop=None):
    return iterable.index(value, start, stop or len(iterable))

@Pipe.register
def strip(iterable, chars=None):
    return iterable.strip(chars)

@Pipe.register
def rstrip(iterable, chars=None):
    return iterable.rstrip(chars)

@Pipe.register
def lstrip(iterable, chars=None):
    return iterable.lstrip(chars)

@Pipe.register
def run_with(iterable, func):
    return  func(**iterable) if isinstance(iterable, dict) else \
            func( *iterable) if hasattr(iterable,'__iter__') else \
            func(  iterable)

@Pipe.register
def t(iterable, y):
    if hasattr(iterable,'__iter__') and not isinstance(iterable, str):
        return iterable + type(iterable)([y])
    else:
        return [iterable, y]

@Pipe.register
def to_type(x, t):
    return t(x)

@Pipe.register
def windowed(iterable, window_size):
    if window_size <= 0:
        raise ValueError('window_size must be positive')
    iterator = iter(iterable)
    i = 0
    window = []
    while True:
        try:
            current = next(iterator)
        except StopIteration:
            if len(window) > 0:
                yield window
            break
        window.append(current)
        i = (i + 1) % window_size
        if i == 0:
            yield window
            window = []


chain_with = Pipe.register(itertools.chain, 'chain_with')
islice = Pipe.register(itertools.islice)

# Python 2 & 3 compatibility
if "izip" in dir(itertools):
    izip = Pipe.register(itertools.izip)
else:
    izip = Pipe.register(zip, 'izip')

if __name__ == "__main__":
    import doctest
    doctest.testmod()
