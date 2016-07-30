Help on module pipe:

NAME
    pipe - Infix programming toolkit

FILE
    /home/mandark/doc/code/python/pipe/pipe.py

DESCRIPTION
    Module enablig a sh like infix syntax (using pipes).
    
    = Introduction =
    As an example, here is the solution for the 2nd Euler Project exercise :
    
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
    The basic syntax is to use a Pipe like in a shell :
    >>> [1, 2, 3] | add
    6
    
    A Pipe can be a function call, for example the Pipe function 'where' :
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
    
    as_list
        Outputs an iterable as a list
        >>> (0, 1, 2) | as_list
        [0, 1, 2]
    
    as_tuple
        Outputs an iterable as a tuple
        >>> [1, 2, 3] | as_tuple
        (1, 2, 3)
    
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
    
        "GET / HTTP/1.0
    Host: google.fr
    
    "         | netcat('google.fr', 80)                       | concat                                        | stdout
    
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
        >>> (1, 2, 3, 4, 5, 6, 7, 8, 9)             | izip([9, 8, 7, 6, 5, 4, 3, 2, 1])             | concat
        '(1, 9), (2, 8), (3, 7), (4, 6), (5, 5), (6, 4), (7, 3), (8, 2), (9, 1)'
    
    aggregate()
        Works as python reduce
        >>> (1, 2, 3, 4, 5, 6, 7, 8, 9) | aggregate(lambda x, y: x * y)
        362880
    
        Simulate concat :
        >>> (1, 2, 3, 4, 5, 6, 7, 8, 9)             | aggregate(lambda x, y: str(x) + ', ' + str(y))
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
        (1, 2, 3, 4, 5, 6, 7, 8, 9)             | groupby(lambda x: x % 2 and "Even" or "Odd")
                | select(lambda x: "%s : %s" % (x[0], (x[1] | concat(', '))))
                | concat(' / ')
        'Even : 1, 3, 5, 7, 9 / Odd : 2, 4, 6, 8'
    
    sort()
        Like Python's built-in "sorted" primitive.  Allows cmp (Python 2.x
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
    
    permutations()
        Returns all possible permutations
        >>> 'ABC' | permutations(2) | concat(' ')
        "('A', 'B') ('A', 'C') ('B', 'A') ('B', 'C') ('C', 'A') ('C', 'B')"
    
        >>> range(3) | permutations | concat('-')
        '(0, 1, 2)-(0, 2, 1)-(1, 0, 2)-(1, 2, 0)-(2, 0, 1)-(2, 1, 0)'
    
    Euler project samples :
    
        # Find the sum of all the multiples of 3 or 5 below 1000.
        euler1 = (itertools.count() | select(lambda x: x * 3) | take_while(lambda x: x < 1000) | add)            + (itertools.count() | select(lambda x: x * 5) | take_while(lambda x: x < 1000) | add)            - (itertools.count() | select(lambda x: x * 15) | take_while(lambda x: x < 1000) | add)
        assert euler1 == 233168
    
        # Find the sum of all the even-valued terms in Fibonacci which do not exceed four million.
        euler2 = fib() | where(lambda x: x % 2 == 0) | take_while(lambda x: x < 4000000) | add
        assert euler2 == 4613732
    
        # Find the difference between the sum of the squares of the first one hundred natural numbers and the square of the sum.
        square = lambda x: x * x
        euler6 = square(itertools.count(1) | take(100) | add) - (itertools.count(1) | take(100) | select(square) | add)
        assert euler6 == 25164150

CLASSES
    Pipe
    
    class Pipe
     |  Represent a Pipeable Element :
     |  Described as :
     |  first = Pipe(lambda iterable: next(iter(iterable)))
     |  and used as :
     |  print [1, 2, 3] | first
     |  printing 1
     |  
     |  Or represent a Pipeable Function :
     |  It's a function returning a Pipe
     |  Described as :
     |  select = Pipe(lambda iterable, pred: (pred(x) for x in iterable))
     |  and used as :
     |  print [1, 2, 3] | select(lambda x: x * 2)
     |  # 2, 4, 6
     |  
     |  Methods defined here:
     |  
     |  __call__(self, *args, **kwargs)
     |  
     |  __init__(self, function)
     |  
     |  __ror__(self, other)

FUNCTIONS
    reduce(...)
        reduce(function, sequence[, initial]) -> value
        
        Apply a function of two arguments cumulatively to the items of a sequence,
        from left to right, so as to reduce the sequence to a single value.
        For example, reduce(lambda x, y: x+y, [1, 2, 3, 4, 5]) calculates
        ((((1+2)+3)+4)+5).  If initial is present, it is placed before the items
        of the sequence in the calculation, and serves as a default when the
        sequence is empty.

DATA
    __author__ = 'Julien Palard <julien@eeple.fr>'
    __credits__ = 'Jerome Schneider, for its Python skillz,\nand dalexande...
    __date__ = '10 Nov 2010'
    __version__ = '1.3'
    add = <pipe.Pipe instance>
    aggregate = <pipe.Pipe instance>
    all = <pipe.Pipe instance>
    any = <pipe.Pipe instance>
    as_list = <pipe.Pipe instance>
    as_tuple = <pipe.Pipe instance>
    average = <pipe.Pipe instance>
    chain = <pipe.Pipe instance>
    chain_with = <pipe.Pipe instance>
    concat = <pipe.Pipe instance>
    count = <pipe.Pipe instance>
    first = <pipe.Pipe instance>
    groupby = <pipe.Pipe instance>
    islice = <pipe.Pipe instance>
    izip = <pipe.Pipe instance>
    lineout = <pipe.Pipe instance>
    max = <pipe.Pipe instance>
    min = <pipe.Pipe instance>
    netcat = <pipe.Pipe instance>
    netwrite = <pipe.Pipe instance>
    permutations = <pipe.Pipe instance>
    reverse = <pipe.Pipe instance>
    select = <pipe.Pipe instance>
    skip = <pipe.Pipe instance>
    skip_while = <pipe.Pipe instance>
    sort = <pipe.Pipe instance>
    stdout = <pipe.Pipe instance>
    take = <pipe.Pipe instance>
    take_while = <pipe.Pipe instance>
    traverse = <pipe.Pipe instance>
    where = <pipe.Pipe instance>

VERSION
    1.3

DATE
    10 Nov 2010

AUTHOR
    Julien Palard <julien@eeple.fr>

CREDITS
    Jerome Schneider, for its Python skillz,
    and dalexander for contributing


