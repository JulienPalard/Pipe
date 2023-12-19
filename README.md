# Pipe — Infix programming toolkit

[![PyPI](https://img.shields.io/pypi/v/pipe)
 ![Monthly downloads](https://img.shields.io/pypi/dm/pipe)
 ![Supported Python Version](https://img.shields.io/pypi/pyversions/pipe.svg)
](https://pypi.org/project/pipe)
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/JulienPalard/pipe/Tests/main)](https://github.com/JulienPalard/pipe/actions)

Module enabling a sh like infix syntax (using pipes).


# Introduction

As an example, here is the solution for the 2nd Euler Project exercise:

> Find the sum of all the even-valued terms in Fibonacci which do not
  exceed four million.

Given `fib` a generator of Fibonacci numbers:

```python
sum(fib() | where(lambda x: x % 2 == 0) | take_while(lambda x: x < 4000000))
```

Each pipes is lazy evalatated, can be aliased, and partially
initialized, so it could be rewritten as:

```python
is_even = where(lambda x: x % 2 == 0)
sum(fib() | is_even | take_while(lambda x: x < 4000000)
```


# Installing

To install the library, you can just run the following command:

```shell
# Linux/macOS
python3 -m pip install pipe

# Windows
py -3 -m pip install pipe
```


# Using

The basic syntax is to use a Pipe like in a shell:

```python
>>> from itertools import count
>>> from pipe import select, take
>>> sum(count() | select(lambda x: x ** 2) | take(10))
285

```

Some pipes take an argument:

```python
>>> from pipe import where
>>> sum([1, 2, 3, 4] | where(lambda x: x % 2 == 0))
6

```

Some do not need one:

```python
>>> from pipe import traverse
>>> for i in [1, [2, 3], 4] | traverse:
...     print(i)
1
2
3
4

```

In which case it's allowed to use the calling parenthesis:

```python
>>> from pipe import traverse
>>> for i in [1, [2, 3], 4] | traverse():
...     print(i)
1
2
3
4

```


## Constructing your own

You can construct your pipes using the `Pipe` class like:

```python
from pipe import Pipe
square = Pipe(lambda iterable: (x ** 2 for x in iterable))
map = Pipe(lambda iterable, fct: builtins.map(fct, iterable)

```

As you can see it's often very short to write, and with a bit of luck
the function you're wrapping already takes an iterable as the first
argument, making the wrapping straight forward:

```python
>>> from collections import deque
>>> from pipe import Pipe
>>> end = Pipe(deque)

```

and that's it `itrable | end(3)` is `deque(iterable, 3)`:

```python
>>> list(range(100) | end(3))
[97, 98, 99]

```

In case it gets more complicated one can use `Pipe` as a decorator to
a function taking an iterable as the first argument, and any other
optional arguments after:

```python
>>> from statistics import mean

>>> @Pipe
... def running_average(iterable, width):
...     items = deque(maxlen=width)
...     for item in iterable:
...         items.append(item)
...         yield mean(items)

>>> list(range(20) | running_average(width=2))
[0, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5, 18.5]
>>> list(range(20) | running_average(width=10))
[0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5, 12.5, 13.5, 14.5]

```


## Partial Pipes

A `pipe` can be parametrized without being evaluated:

```python
>>> running_average_of_two = running_average(2)
>>> list(range(20) | running_average_of_two)
[0, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5, 18.5]

```

For multi-argument pipes then can be partially initialized, you can think of curying:

```python
some_iterable | some_pipe(1, 2, 3)
```

is strictly equivalent to:

```python
some_iterable | some_pipe(1)(2)(3)
```

So it can be used to specialize pipes, first a dummy example:

```python
>>> @Pipe
... def addmul(iterable, to_add, to_mul):
...     """Computes (x + to_add) * to_mul to every items of the input."""
...     for i in iterable:
...         yield (i + to_add) * to_mul

>>> mul = addmul(0)  # This partially initialize addmul with to_add=0
>>> list(range(10) | mul(10))
[0, 10, 20, 30, 40, 50, 60, 70, 80, 90]

```

Which also works with keyword arguments:

```python
>>> add = addmul(to_mul=1)  # This partially initialize addmul with `to_mul=1`
>>> list(range(10) | add(10))
[10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

```


But now for something interesting:

```python
>>> import re
>>> @Pipe
... def grep(iterable, pattern, flags=0):
...     for line in iterable:
...         if re.match(pattern, line, flags=flags):
...             yield line
...
>>> lines = ["Hello", "hello", "World", "world"]
>>> for line in lines | grep("H"):
...     print(line)
Hello

```

Now let's reuse it in two ways, first with a pattern:

```python
>>> lowercase_only = grep("[a-z]+$")
>>> for line in lines | lowercase_only:
...     print(line)
hello
world

```

Or now with a flag:

```python
>>> igrep = grep(flags=re.IGNORECASE)
>>> for line in lines | igrep("hello"):
...    print(line)
...
Hello
hello

```


## Pipeline Recipes

A **pipeline recipe** (aka: partial pipe) provides a pipeline without its pipe-source (sequence/stream).
A pipeline may consist of several complex pipeline parts.
It is easier to just use a **pipeline recipe** (without need of knowing the details).
In addition, the use of the **pipeline recipe**:

* is less error-prone and
* the canned **pipeline recipe** can be tested in advance


### SOLUTION 1: Use "yield from" expressions

```python
# -- FILE: example1_pipeline_recipe_with_yield_from.py
from pipe import Pipe as as_pipe
from example_common_pipes import select_even_numbers, multiply_by

# -- PIPELINE RECIPE: Using pipe-function with yield-from
# ADVANTAGE: Pipeline parametrization can be done late.
@as_pipe
def select_even_numbers_and_multiply_by(iterable, factor):
    yield from (iterable | select_even_numbers | multiply_by(factor))

numbers = range(8)
results = list(numbers | select_even_numbers_and_multiply_by(3))
expected = [0, 6, 12, 18]
assert results == expected
```

### SOLUTION 2: Use or-pipe expressions

```python
# -- FILE: example2_pipeline_recipe_with_or_pipes.py
# REQUIRES: or-pipe expressions
from example_common_pipes import select_even_numbers, multiply_by

# -- PIPELINE RECIPE: Using or-pipe expressions
# NOTE: Pipeline parametrization must be done early (when pipeline is defined).
select_even_numbers_and_multiply_by_3 = select_even_numbers | multiply_by(3)

numbers = range(8)
results = list(numbers | select_even_numbers_and_multiply_by_3)
expected = [0, 6, 12, 18]
assert results == expected
```

### SOLUTION 3: Use make-pipe idiom with or-pipe expressions

```python
# -- FILE: example3_pipeline_recipe_with_make_pipe_using_or_pipes.py
# REQUIRES: or-pipe expressions
from example_common_pipes import select_even_numbers, multiply_by

# -- PIPELINE RECIPE: Using make_pipe4<PIPE_RECIPE> as factory function
# ADVANTAGE: Pipeline parametrization can be done late.
def make_pipe4select_even_numbers_and_multiply_by(factor):
    # -- USES: or-pipe expressions
    return select_even_numbers | multiply_by(factor)

select_even_numbers_and_multiply_by_3 = make_pipe4select_even_numbers_and_multiply_by(3)

numbers = range(8)
results = list(numbers | select_even_numbers_and_multiply_by_3)
expected = [0, 6, 12, 18]
assert results == expected
```

```python
# -- FILE: example_common_pipes.py
from pipe import Pipe as as_pipe

@as_pipe
def select_numbers_modulo(iterable, modulus):
    for number in iterable:
        if (number % modulus) == 0:
            yield number

@as_pipe
def multiply_by(iterable, factor):
    for number in iterable:
        yield number * factor

@as_pipe
def select_even_numbers(iterable):
    yield from (iterable | select_numbers_modulo(2))
```


# Deprecations of pipe 1.x

In pipe 1.x a lot of functions were returning iterables and a lot
other functions were returning non-iterables, causing confusion. The
one returning non-iterables could only be used as the last function of
a pipe expression, so they are in fact useless:

```python
range(100) | where(lambda x: x % 2 == 0) | add
```

can be rewritten with no less readability as:

```python
sum(range(100) | where(lambda x: x % 2 == 0))
```

so all pipes returning non-iterables are now deprecated and were
removed in pipe 2.0.


## What should I do?

Oh, you just upgraded pipe, got an exception, and landed here? You
have three solutions:


1) Stop using closing-pipes, replace `...|...|...|...|as_list` to
   `list(...|...|...|)`, that's it, it's even shorter.

2) If "closing pipes" are not an issue for you, and you really like
   them, just reimplement the few you really need, it often take a very
   few lines of code, or copy them from
   [here](https://github.com/JulienPalard/Pipe/blob/dd179c8ff0aa28ee0524f3247e5cb1c51347cba6/pipe.py).

3) If you still rely on a lot of them and are in a hurry, just `pip install pipe<2`.


And start testing your project using the [Python Development
Mode](https://docs.python.org/3/library/devmode.html) so you catch
those warnings before they bite you.


## But I like them, pleassssse, reintroduce them!

This has already been discussed in [#74](https://github.com/JulienPalard/Pipe/issues/74).

An `@Pipe` is often easily implemented in a 1 to 3 lines of code
function, and the `pipe` module does not aim at giving all
possibilities, it aims at giving the `Pipe` decorator.

So if you need more pipes, closing pipes, weird pipes, you-name-it,
feel free to implement them on your project, and consider the
already-implemented ones as examples on how to do it.

See the `Constructing your own` paragraph below.


# Existing Pipes in this module

Alphabetical list of available pipes; when several names are listed for a given pipe, these are aliases.

## `batched`

Like Python 3.12 `itertool.batched`:

```python
>>> from pipe import batched
>>> list("ABCDEFG" | batched(3))
[('A', 'B', 'C'), ('D', 'E', 'F'), ('G',)]

```

## `chain`

Chain a sequence of iterables:

```python
>>> from pipe import chain
>>> list([[1, 2], [3, 4], [5]] | chain)
[1, 2, 3, 4, 5]

```

Warning : chain only unfold iterable containing ONLY iterables:

```python
[1, 2, [3]] | chain
```
Gives a `TypeError: chain argument #1 must support iteration`
Consider using traverse.


## `chain_with(other)`

Like itertools.chain, yields elements of the given iterable,
hen yields elements of its parameters

```python
>>> from pipe import chain_with
>>> list((1, 2, 3) | chain_with([4, 5], [6]))
[1, 2, 3, 4, 5, 6]

```

## `dedup(key=None)`

Deduplicate values, using the given `key` function if provided.

```python
>>> from pipe import dedup
>>> list([-1, 0, 0, 0, 1, 2, 3] | dedup)
[-1, 0, 1, 2, 3]
>>> list([-1, 0, 0, 0, 1, 2, 3] | dedup(key=abs))
[-1, 0, 2, 3]

```


## `enumerate(start=0)`

The builtin `enumerate()` as a Pipe:

```python
>>> from pipe import enumerate
>>> list(['apple', 'banana', 'citron'] | enumerate)
[(0, 'apple'), (1, 'banana'), (2, 'citron')]
>>> list(['car', 'truck', 'motorcycle', 'bus', 'train'] | enumerate(start=6))
[(6, 'car'), (7, 'truck'), (8, 'motorcycle'), (9, 'bus'), (10, 'train')]

```


## `filter(predicate)`

Alias for `where(predicate)`, see `where(predicate)`.


## `groupby(key=None)`

Like `itertools.groupby(sorted(iterable, key = keyfunc), keyfunc)`

```python
>>> from pipe import groupby, map
>>> items = range(10)
>>> ' / '.join(items | groupby(lambda x: "Odd" if x % 2 else "Even")
...                  | select(lambda x: "{}: {}".format(x[0], ', '.join(x[1] | map(str)))))
'Even: 0, 2, 4, 6, 8 / Odd: 1, 3, 5, 7, 9'

```


## `islice()`

Just the `itertools.islice` function as a Pipe:

```python
>>> from pipe import islice
>>> list((1, 2, 3, 4, 5, 6, 7, 8, 9) | islice(2, 8, 2))
[3, 5, 7]

```

## `izip()`

Just the `itertools.izip` function as a Pipe:

```python
>>> from pipe import izip
>>> list(range(0, 10) | izip(range(1, 11)))
[(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (9, 10)]

```

## `map()`, `select()`

Apply a conversion expression given as parameter
to each element of the given iterable

```python
>>> list([1, 2, 3] | map(lambda x: x * x))
[1, 4, 9]

>>> list([1, 2, 3] | select(lambda x: x * x))
[1, 4, 9]

```

## `netcat`

The netcat Pipe sends and receive bytes over TCP:

```python
data = [
    b"HEAD / HTTP/1.0\r\n",
    b"Host: python.org\r\n",
    b"\r\n",
]
for packet in data | netcat("python.org", 80):
    print(packet.decode("UTF-8"))
```

Gives:

```
HTTP/1.1 301 Moved Permanently
Content-length: 0
Location: https://python.org/
Connection: close
```

## ```permutations(r=None)```

Returns all possible permutations:

```python
>>> from pipe import permutations
>>> for item in 'ABC' | permutations(2):
...     print(item)
('A', 'B')
('A', 'C')
('B', 'A')
('B', 'C')
('C', 'A')
('C', 'B')

```

```python
>>> for item in range(3) | permutations:
...     print(item)
(0, 1, 2)
(0, 2, 1)
(1, 0, 2)
(1, 2, 0)
(2, 0, 1)
(2, 1, 0)

```

## `reverse`

Like Python's built-in `reversed` function.

```python
>>> from pipe import reverse
>>> list([1, 2, 3] | reverse)
[3, 2, 1]

```

## `select(fct)`

Alias for `map(fct)`, see `map(fct)`.


## `skip()`

Skips the given quantity of elements from the given iterable, then yields

```python
>>> from pipe import skip
>>> list((1, 2, 3, 4, 5) | skip(2))
[3, 4, 5]

```


## `skip_while(predicate)`

Like itertools.dropwhile, skips elements of the given iterable
while the predicate is true, then yields others:

```python
>>> from pipe import skip_while
>>> list([1, 2, 3, 4] | skip_while(lambda x: x < 3))
[3, 4]

```

## `sort(key=None, reverse=False)`

Like Python's built-in "sorted" primitive.

```python
>>> from pipe import sort
>>> ''.join("python" | sort)
'hnopty'
>>> [5, -4, 3, -2, 1] | sort(key=abs)
[1, -2, 3, -4, 5]

```

## `t`

Like Haskell's operator ":":

```python
>>> from pipe import t
>>> for i in 0 | t(1) | t(2):
...     print(i)
0
1
2

```

## `tail(n)`

Yields the given quantity of the last elements of the given iterable.

```python
>>> from pipe import tail
>>> for i in (1, 2, 3, 4, 5) | tail(3):
...     print(i)
3
4
5

```

## `take(n)`

Yields the given quantity of elements from the given iterable, like `head`
in shell script.

```python
>>> from pipe import take
>>> for i in count() | take(5):
...     print(i)
0
1
2
3
4

```

## `take_while(predicate)`

Like `itertools.takewhile`, yields elements of the
given iterable while the predicate is true:

```python
>>> from pipe import take_while
>>> for i in count() | take_while(lambda x: x ** 2 < 100):
...     print(i)
0
1
2
3
4
5
6
7
8
9

```

## `tee`

tee outputs to the standard output and yield unchanged items, useful for
debugging a pipe stage by stage:

```python
>>> from pipe import tee
>>> sum(["1", "2", "3", "4", "5"] | tee | map(int) | tee)
'1'
1
'2'
2
'3'
3
'4'
4
'5'
5
15

```

The `15` at the end is the `sum` returning.


## `transpose()`

Transposes the rows and columns of a matrix.

```python
>>> from pipe import transpose
>>> [[1, 2, 3], [4, 5, 6], [7, 8, 9]] | transpose
[(1, 4, 7), (2, 5, 8), (3, 6, 9)]

```

## `traverse`

Recursively unfold iterables:

```python
>>> list([[1, 2], [[[3], [[4]]], [5]]] | traverse)
[1, 2, 3, 4, 5]
>>> squares = (i * i for i in range(3))
>>> list([[0, 1, 2], squares] | traverse)
[0, 1, 2, 0, 1, 4]

```

## `uniq(key=None)`


Like dedup() but only deduplicate consecutive values, using the given
`key` function if provided (or else the identity).

```python
>>> from pipe import uniq
>>> list([1, 1, 2, 2, 3, 3, 1, 2, 3] | uniq)
[1, 2, 3, 1, 2, 3]
>>> list([1, -1, 1, 2, -2, 2, 3, 3, 1, 2, 3] | uniq(key=abs))
[1, 2, 3, 1, 2, 3]

```

## `where(predicate)`, `filter(predicate)`

Only yields the matching items of the given iterable:

```python
>>> list([1, 2, 3] | where(lambda x: x % 2 == 0))
[2]

```

Don't forget they can be aliased:

```python
>>> positive = where(lambda x: x > 0)
>>> negative = where(lambda x: x < 0)
>>> sum([-10, -5, 0, 5, 10] | positive)
15
>>> sum([-10, -5, 0, 5, 10] | negative)
-15

```

# Euler project samples

> Find the sum of all the multiples of 3 or 5 below 1000.

```python
>>> euler1 = sum(count() | where(lambda x: x % 3 == 0 or x % 5 == 0) | take_while(lambda x: x < 1000))
>>> assert euler1 == 233168

```

> Find the sum of all the even-valued terms in Fibonacci which do not exceed four million.

```python
euler2 = sum(fib() | where(lambda x: x % 2 == 0) | take_while(lambda x: x < 4000000))
```

> Find the difference between the sum of the squares of the first one hundred natural numbers and the square of the sum.

```python
>>> square = map(lambda x: x ** 2)
>>> euler6 = sum(range(101)) ** 2 - sum(range(101) | square)
>>> assert euler6 == 25164150

```

# Lazy evaluation

Using this module, you get lazy evaluation at two levels:
- the object obtained by piping is a generator and will be evaluated only if needed,
- within a series of pipe commands, only the elements that are actually needed will be evaluated.

To illustrate:

```python
from itertools import count
from pipe import select, where, take


def dummy_func(x):
    print(f"processing at value {x}")
    return x


print("----- test using a generator as input -----")

print(f"we are feeding in a: {type(count(100))}")

res_with_count = (count(100) | select(dummy_func)
                             | where(lambda x: x % 2 == 0)
                             | take(2))

print(f"the resulting object is: {res_with_count}")
print(f"when we force evaluation we get:")
print(f"{list(res_with_count)}")

print("----- test using a list as input -----")

list_to_100 = list(range(100))
print(f"we are feeding in a: {type(list_to_100)} which has length {len(list_to_100)}")

res_with_list = (list_to_100 | select(dummy_func)
                             | where(lambda x: x % 2 == 0)
                             | take(2))

print(f"the resulting object is: {res_with_list}")
print(f"when we force evaluation we get:")
print(f"{list(res_with_list)}")
```

Which prints:

```
----- test using a generator as input -----
we are feeding in a: <class 'itertools.count'>
the resulting object is: <generator object take at 0x7fefb5e70c10>
when we force evaluation we get:
processing at value 100
processing at value 101
processing at value 102
processing at value 103
processing at value 104
[100, 102]
----- test using a list as input -----
we are feeding in a: <class 'list'> which has length 100
the resulting object is: <generator object take at 0x7fefb5e70dd0>
when we force evaluation we get:
processing at value 0
processing at value 1
processing at value 2
processing at value 3
processing at value 4
[0, 2]
```
