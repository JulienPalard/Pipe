#!/usr/bin/env python
""" Infix programming toolkit

Module enablig an infix syntax, as an exemple,
resolving the 2nd Euler Project exercise:
"Find the sum of all the even-valued terms in Fibonacci
 which do not exceed four million."

euler2 = fib() | where(lambda x: x % 2 == 0)
               | take_while(lambda x: x < 4000000)
               | add

The basic symtax is to use a Pipe like in a shell :
>>> [1, 2, 3] | add
6

Each FuncPipe is a function acting like a Pipe, for exemple where :
>>> [1, 2, 3] | where(lambda x: x % 2 == 0) #doctest: +ELLIPSIS
<generator object <genexpr> at ...>

A FuncPipe is nothing more than a function returning a specialized Pipe,

You can construct your pipes using Pipe and FuncPipe classes like :

stdout = Pipe(lambda x: sys.stdout.write(str(x)))
select = FuncPipe(lambda iterable, pred: (pred(x) for x in iterable))

Or using decorators :
@Pipe
def stdout(x):
    sys.stdout.write(str(x))


stdout
    Outputs anything to the standard output
    >>> "42" | stdout
    42

lineout
    Outputs anything to the standard output followed by a line break
    >>> 42 | lineout
    42

as_list
    Outputs an iterable as a list
    
as_tuple
    Outputs an iterable as a tuple

concat()
    Aggregates strings using given separator, or ", " by default
    >>> [1, 2, 3, 4] | concat()
    '1, 2, 3, 4'

average
    Returns the average of the given iterable
    >>> [1, 2, 3, 4, 5, 6] | average
    3.5

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
    >>> [[1, 2], [3, 4], [5]] | chain | concat()
    '1, 2, 3, 4, 5'

  Warning : chain only unfold iterable containing ONLY iterables :
      [1, 2, [3]] | chain
          Gives a TypeError: chain argument #1 must support iteration
          Consider using traverse

traverse
    Recursively unfold iterables
    >>> [[1, 2], [[[3], [[4]]], [5]]] | traverse | concat()
    '1, 2, 3, 4, 5'

select()
    Apply a conversion expression given as parameter
    to each element of the given iterable
    >>> [1, 2, 3] | select(lambda x: x * x) | concat()
    '1, 4, 9'

where()
    Only yields the matching items of the given iterable
    >>> [1, 2, 3] | where(lambda x: x % 2 == 0) | concat()
    '2'

take_while()
    Like itertools.takewhile, yields elements of the
    given iterable while the predicat is true
    >>> [1, 2, 3, 4] | take_while(lambda x: x < 3) | concat()
    '1, 2'

skip_while()
    Like itertools.dropwhile, skips elements of the given iterable
    while the predicat is true, then yields others
    >>> [1, 2, 3, 4] | skip_while(lambda x: x < 3) | concat()
    '3, 4'

chain_with()
    Like itertools.chain, yields elements of the given iterable,
    then yields elements of its parameters
    >>> (1, 2, 3) | chain_with([4, 5], [6]) | concat()
    '1, 2, 3, 4, 5, 6'

take()
    Yields the given quantity of elemenets from the given iterable
    >>> (1, 2, 3, 4, 5) | take(2) | concat()
    '1, 2'

skip()
    Skips the given quantity of elements from the given iterable, then yields
    >>> (1, 2, 3, 4, 5) | skip(2) | concat()
    '3, 4, 5'

islice()
    Just the itertools.islice
    >>> (1, 2, 3, 4, 5, 6, 7, 8, 9) | islice(2, 8, 2) | concat()
    '3, 5, 7'

izip()
    Just the itertools.izip
    >>> (1, 2, 3, 4, 5, 6, 7, 8, 9) \
            | izip([9, 8, 7, 6, 5, 4, 3, 2, 1]) \
            | concat()
    '(1, 9), (2, 8), (3, 7), (4, 6), (5, 5), (6, 4), (7, 3), (8, 2), (9, 1)'

aggregate()
    Works as python reduce
    >>> (1, 2, 3, 4, 5, 6, 7, 8, 9) | aggregate(lambda x, y: x * y)
    362880

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
    Returns the biggest element, using the given key function
    >>> ('aa', 'b', 'foo', 'qwerty', 'bar', 'zoog') | max(key=len)
    'qwerty'
    >>> ('aa', 'b', 'foo', 'qwerty', 'bar', 'zoog') | max()
    'zoog'

min()
    Returns the smallest element, using the given key function
    >>> ('aa', 'b', 'foo', 'qwerty', 'bar', 'zoog') | min(key=len)
    'b'
    >>> ('aa', 'b', 'foo', 'qwerty', 'bar', 'zoog') | min()
    'aa'

groupby()
    Like itertools.groupby(sorted(iterable, key = keyfunc), keyfunc)
    (1, 2, 3, 4, 5, 6, 7, 8, 9) \
            | groupby(lambda x: x % 2 and "Even" or "Odd")
            | select(lambda x: "%s : %s" % (x[0], (x[1] | concat(', '))))
            | concat(' / ')
    'Even : 1, 3, 5, 7, 9 / Odd : 2, 4, 6, 8'

sort()
    Like Python's built-in "sorted" primitive.  Allows cmp (Python 2.x
    only), key, and reverse arguments. By default sorts using the
    identity function as the key.

    >>> "python" | sort() | concat("")
    'hnopty'
    >>> [5, -4, 3, -2, 1] | sort(key=abs) | concat()
    '1, -2, 3, -4, 5'

reverse
    Like Python's built-in "reversed" primitive.
    >>> [1, 2, 3] | reverse | concat()
    '3, 2, 1'
    
permutations()
    Returns all possible permutations
    >>> 'ABC' | permutations(2) | concat(' ')
    "('A', 'B') ('A', 'C') ('B', 'A') ('B', 'C') ('C', 'A') ('C', 'B')"

    >>> range(3) | permutations() | concat('-')
    '(0, 1, 2)-(0, 2, 1)-(1, 0, 2)-(1, 2, 0)-(2, 0, 1)-(2, 1, 0)'

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

import itertools
from functools import reduce
import sys

try:
    import __builtin__ as b
except ImportError:
    import builtins as b


__author__ = 'Julien Palard <julien@eeple.fr>'
__credits__ = 'Jerome Schneider, for its Python skillz'
__date__ = '26 Aug 2010'
__version__ = '1.2'

class Pipe:
    """
    Represent a Pipeable Element :
    Described as :
    first = Pipe(lambda iterable: next(iter(iterable)))
    and used as :
    print [1, 2, 3] | first
    printing 1
    """
    def __init__(self, function):
        self.function = function
    def __ror__(self, other):
        return self.function(other)

class FuncPipe:
    """
    Represent a Pipeable Function :
    It's a function returning a Pipe
    Described as :
    select = FuncPipe(lambda iterable, pred: (pred(x) for x in iterable))
    and used as :
    print [1, 2, 3] | select(lambda x: x * 2)
    # 2, 4, 6
    """
    def __init__(self, function):
        self.function = function
    def __call__(self, *value, **kwargs):
        return Pipe(lambda x: self.function(x, *value, **kwargs))

@FuncPipe
def take(iterable, qte):
    "Yield qte of elements in the given iterable."
    for item in iterable:
        if qte > 0:
            qte -= 1
            yield item
        else:
            return

@FuncPipe
def skip(iterable, qte):
    "Skip qte elements in the given iterable, then yield others."
    for item in iterable:
        if qte == 0:
            yield item
        else:
            qte -= 1

@FuncPipe
def all(iterable, pred):
    "Returns True if ALL elements in the given iterable are true for the given pred function"
    for x in iterable:
        if not pred(x):
            return False
    return True

@FuncPipe
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

@FuncPipe
def max(iterable, **kwargs):
    return b.max(iterable, **kwargs)

@FuncPipe
def min(iterable, **kwargs):
    return b.min(iterable, **kwargs)


@FuncPipe
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

@FuncPipe
def netcat(iterable, host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.connect((host, port))
        buffer = ""
        for to_send in iterable:
            s.send(to_send)
        while 1:
            data = s.recv(4096)
            if not data: break
            buffer += data
        return buffer

@Pipe
def traverse(args):
    for arg in args:
        if type(arg) == list:
            for i in arg | traverse:
                yield i
        else:
            yield arg

@FuncPipe
def concat(iterable, separator=", "):
    try:
        return str(iterable | aggregate(lambda x, y: str(x) + separator + str(y)))
    except TypeError:
        #Todo : Checker mieux que ca si la liste est vide avant de faire le aggregate
        return ''

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
def add(x):
    return sum(x)

@Pipe
def first(iterable):
    return next(iter(iterable))

@Pipe
def chain(iterable):
    return itertools.chain(*iterable)

@FuncPipe
def select(iterable, selector):
    return (selector(x) for x in iterable)

@FuncPipe
def where(iterable, predicate):
    return (x for x in iterable if (predicate(x)))

@FuncPipe
def take_while(iterable, predicate):
    return itertools.takewhile(predicate, iterable)

@FuncPipe
def skip_while(iterable, predicate):
    return itertools.dropwhile(predicate, iterable)

@FuncPipe
def aggregate(iterable, function):
    return reduce(function, iterable)

@FuncPipe
def groupby(iterable, keyfunc):
    return itertools.groupby(sorted(iterable, key = keyfunc), keyfunc)

@FuncPipe
def sort(iterable, **kwargs):
    return sorted(iterable, **kwargs)

@Pipe
def reverse(iterable):
    return reversed(iterable)

chain_with = FuncPipe(itertools.chain)
islice = FuncPipe(itertools.islice)

# Python 2 & 3 compatibility
if "izip" in dir(itertools):
    izip = FuncPipe(itertools.izip)
else:
    izip = FuncPipe(zip)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
