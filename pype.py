#!/usr/bin/env python
"""
Infix programming syntax

Utilities enablig an infix syntax like this :

euler2 = fib() | where(lambda x: x % 2 == 0)
               | take_while(lambda x: x < 4000000)
               | sum

assert euler2 == 4613732

Resolving the 2nd Euler Project exercise :
"Find the sum of all the even-valued terms in Fibonacci
 which do not exceed four million."

Each Pipe is useable as, for exemple sum :
[1, 2, 3] | sum

Each FuncPipe is useable as, for exemple where :
[1, 2, 3] | where(lambda x: x % 2 == 0)
A FuncPipe is nothing more than a Parametrized Pipe,
or a function returning a specific Pipe

You can construct your pipes using Pipe and FuncPipe classes like :

stdout = Pipe(lambda x: sys.stdout.write(str(x)))
select = FuncPipe(lambda iterable, pred: (pred(x) for x in iterable))

Available Pipes are :

stdout : Outputs anything to the standard output
  Usage : "42" | stdout

lineout : Outputs anything to the standard output followed by a line break
  Usage : 42 | lineout

average : Returns the average of the preceding Iterable
  Usage : print [1, 2, 3, 4, 5, 6] | average

count : Returns the length of the preceding Iterable, counting elements one by one

sum : Returns the sum of all elements in the preceding Iterable

first : Returns the first element of the preceding Iterable

chain : Unfold preceding Iterable of Iterables
  Usage : [[1, 2], [3, 4], [5]] | chain
          Gives [1, 2, 3, 4, 5]
  Warning : chain only unfold Iterable containing ONLY Iterables :
          [1, 2, [3]] | chain
		  Gives a TypeError: chain argument #1 must support iteration
		  Consider using traverse

traverse : Recursively unfold Iterables
  Usage : [[1, 2], [[[3], [[4]]], [5]]] | traverse
          Gives 1, 2, 3, 4, 5

Available FuncPipes are :
select : Apply a conversion expression given as parameter to each element of the preceding Iterable
  Usage : [1, 2, 3] | select(lambda x: x * x)

where : Only yields the matching items of the preceding Iterable:
  Usage : [1, 2, 3] | where(lambda x: x % 1 == 0)

take_while : Like itertools.takewhile, yields elements of the preceding iterable while the predicat is true :
  Usage : [1, 2, 3] | take_while(lambda x: x < 3)

skip_while : Like itertools.dropwhile, skips elements of the preceding iterable while the predicat is true, then yields others

chain_with : Like itertools.chain, yields elements of the preceding iterable, then yields elements of its parameters
  Usage : (1, 2, 3) | chain_width([4, 5, 6]) gives (1, 2, 3, 4, 5, 6)

take : Yields the given quantity of elemenets from the preceding iterable :
  Usage : (1, 2, 3, 4, 5) | take(2) gives (1, 2)

skip : Skips the given quantity of elements from the preceding iterable, then yields :
  Usage : (1, 2, 3, 4, 5) | skip(2) gives (3, 4, 5)

islice : like itertools.islice
  Usage : assert((1, 2, 3, 4, 5, 6, 7, 8, 9) | islice(2, 8, 2) | sum == (3 + 5 + 7))

izip : Like itertools.izip
  Usage : assert((1,2,3,4,5,6,7,8,9)
                     | izip([9,8,7,6,5,4,3,2,1])
                     | select(lambda x : x[0] * x[1])
                     | sum
                       == (1*9 + 2*8 + 3*7 + 4*6 + 5*5 + 6*4 + 7*3 + 8*2 + 9*1))

aggregate : Works as python reduce
  Usage : 	assert(one2nine | aggregate(lambda x, y: x * y) == 1*2*3*4*5*6*7*8*9)
            assert(one2nine | aggregate(lambda x, y: str(x) + ', ' + str(y)) == "1, 2, 3, 4, 5, 6, 7, 8, 9")

concat : A utility to aggregate strings using given separator, works like aggregate(lambda x, y: str(x) + separator + str(y))

any : Returns true if any of the elements matches the given predicat

all : Returns true if all elements matches the given predicat

bigger : Returns the biggest element, using the given comparator

groupby : Like itertools.groupby(sorted(iterable, key = keyfunc), keyfunc)
Usage : assert(one2nine | groupby(lambda x: x % 2 and "Even" or "Odd")
                    | select(lambda x: "%s : %s" % (x[0], (x[1] | concat(', '))))
                    | concat(' / ') == "Even : 1, 3, 5, 7, 9 / Odd : 2, 4, 6, 8")

permutations : Returns all possible permutations as :
  'ABCD' | permutations(2) --> AB AC AD BA BC BD CA CB CD DA DB DC
  range(3) | permutations() --> 012 021 102 120 201 210

"""

import itertools
import sys


__author__ = 'Julien Palard <julien@eeple.fr>'
__credits__ = 'Jerome Schneider, for his Python skill'
__date__ = '5 February 2010'
__version__ = '1.1'

class Pipe:
	"""
	Represent a Pipeable Element :
	Described as :
	first = Pipe(lambda iterable: iter(iterable).next())
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
	def __call__(self, *value):
		return Pipe(lambda x: self.function(x, *value))

def _take(iterable, qte):
	"Yield qte of elements in the given iterable."
	for item in iterable:
		if qte > 0:
			qte -= 1
			yield item
		else:
			return

def _skip(iterable, qte):
	"Skip qte elements in the given iterable, then yield others."
	for item in iterable:
		if qte == 0:
			yield item
		else:
			qte -= 1

def _all(iterable, pred):
	"Returns True if ALL elements in the given iterable are true for the given pred function"
	for x in iterable:
		if not pred(x):
			return False
	return True

def _any(iterable, pred):
	"Returns True if ANY element in the given iterable is True for the given pred function"
	for x in iterable:
		if pred(x):
			return True
	return False

def _average(iterable):
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

def _count(iterable):
	"Count the size of the given iterable, walking thrue it."
	count = 0
	for x in iterable:
		count += 1
	return count

def _max(iterable, comparator):
	biggest = None
	for item in iterable:
		if biggest is None:
			biggest = item
		else:
			if comparator(item, biggest) > 0:
				biggest = item
	return biggest

def permutations(iterable, r=None):
    # permutations('ABCD', 2) --> AB AC AD BA BC BD CA CB CD DA DB DC
    # permutations(range(3)) --> 012 021 102 120 201 210
    pool = tuple(iterable)
    n = len(pool)
    r = n if r is None else r
    if r > n:
        return
    indices = range(n)
    cycles = range(n, n-r, -1)
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


def _traverse_list(*args):
	for arg in args:
		if type(arg) == list:
			for i in _traverse_list(*arg):
				yield i
		else:
			yield arg

stdout =  Pipe(lambda x: sys.stdout.write(str(x)))
lineout = Pipe(lambda x: sys.stdout.write(str(x) + "\n"))
average = Pipe(_average)
count =   Pipe(_count)
sum =     Pipe(sum)
first =   Pipe(lambda iterable: iter(iterable).next())
chain =   Pipe(lambda x: itertools.chain(*x))
traverse =	 Pipe(_traverse_list)

select =     FuncPipe(lambda iterable, pred: (pred(x) for x in iterable))
where =      FuncPipe(lambda iterable, pred: (x for x in iterable if pred(x)))
take_while = FuncPipe(lambda iterable, pred: itertools.takewhile(pred, iterable))
skip_while = FuncPipe(lambda iterable, pred: itertools.dropwhile(pred, iterable))
chain_with = FuncPipe(itertools.chain)
take =       FuncPipe(_take)
skip =       FuncPipe(_skip)
islice =     FuncPipe(itertools.islice)
izip =       FuncPipe(itertools.izip)
aggregate =  FuncPipe(lambda iterable, function: reduce(function, iterable))
concat =     FuncPipe(lambda iterable, separator: iterable | aggregate(lambda x, y: str(x) + separator + str(y)))
any =        FuncPipe(_any)
all =        FuncPipe(_all)
bigger =	 FuncPipe(_max)
groupby =    FuncPipe(lambda iterable, keyfunc: itertools.groupby(sorted(iterable, key = keyfunc), keyfunc))
permutations = FuncPipe(permutations)

if __name__ == "__main__":
	import operator
	def fib():
		x = 1
		yield 1
		y = 1
		yield 1
		while True:
			x = x + y
			yield x
			y = x + y
			yield y

	print "Testing Functional Style Python Module v%s" % __version__
	one2nine = (1,2,3,4,5,6,7,8,9)
	assert(one2nine | average == ((1+2+3+4+5+6+7+8+9)/9))
	assert(one2nine | count == len(one2nine))
	assert(one2nine | sum == (1+2+3+4+5+6+7+8+9))
	assert(one2nine | first == 1)
	assert(one2nine | select(lambda x: x * 2) | sum == (2+4+6+8+10+12+14+16+18))
	assert(one2nine | where(lambda x: x % 2 == 0) | sum == (2+4+6+8))
	assert(one2nine | take_while(lambda x: x < 5) | sum == (1+2+3+4))
	assert(one2nine | skip_while(lambda x: x < 5) | sum == (5+6+7+8+9))

	assert(one2nine | chain_with([10, 11, 12]) | sum == (1+2+3+4+5+6+7+8+9+10+11+12))
	assert(one2nine | take(5) | sum == (1+2+3+4+5))
	assert(one2nine | skip(5) | sum == (6+7+8+9))
	assert(one2nine | islice(2, 8, 2) | sum == (3+5+7))
	assert(one2nine | izip([9,8,7,6,5,4,3,2,1]) | select(lambda x : x[0] * x[1]) | sum == (1*9 + 2*8 + 3*7 + 4*6 + 5*5 + 6*4 + 7*3 + 8*2 + 9*1))
	assert(one2nine | aggregate(lambda x, y: x * y) == 1*2*3*4*5*6*7*8*9)
	assert(one2nine | aggregate(lambda x, y: str(x) + ', ' + str(y)) == "1, 2, 3, 4, 5, 6, 7, 8, 9")
	assert(one2nine | any(lambda x: x == 5))
	assert(one2nine | any(lambda x: x == 10) == False)
	assert(one2nine | all(lambda x: x < 10))
	assert(one2nine | all(lambda x: x < 9) == False)

	assert(one2nine | groupby(lambda x: x % 2 and "Even" or "Odd") \
	                | select(lambda x: "%s : %s" % (x[0], (x[1] | concat(', ')))) \
		            | concat(' / ') == "Even : 1, 3, 5, 7, 9 / Odd : 2, 4, 6, 8")

	assert([[1], [2, 3], [4, 5]] | chain | sum == (1 + 2 + 3 + 4 + 5))
	assert([1, [2, 3], [[[4, 5, [6, 7, 8, 9]]]]] | traverse | take(5) | sum == (1+2+3+4+5))

	# Find the sum of all the multiples of 3 or 5 below 1000.
	euler1 = (itertools.count() | select(lambda x: x * 3) | take_while(lambda x: x < 1000) | sum) \
		   + (itertools.count() | select(lambda x: x * 5) | take_while(lambda x: x < 1000) | sum) \
		   - (itertools.count() | select(lambda x: x * 15) | take_while(lambda x: x < 1000) | sum)
	assert euler1 == 233168

	# Find the sum of all the even-valued terms in Fibonacci which do not exceed four million.
	euler2 = fib() | where(lambda x: x % 2 == 0) | take_while(lambda x: x < 4000000) | sum
	assert euler2 == 4613732

	# Find the difference between the sum of the squares of the first one hundred natural numbers and the square of the sum.
	square = lambda x: x * x
	euler6 = square(itertools.count(1) | take(100) | sum) - (itertools.count(1) | take(100) | select(square) | sum)
	assert euler6 == 25164150

	print "Testing Done !"
