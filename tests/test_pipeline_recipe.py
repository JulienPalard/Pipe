"""
Tests related to the "pipeline recipe" idea.

DEFINITION: Pipeline recipe

* A prepared, often complex pipeline that should easily reusable by others

SOLUTION:

* Use ``or-pipes`` expression (support added to: `pipe` module)
* Use pipe-functions with yield-from expression.
  ADVANTAGE: Has parametrization support.

SEE ALSO:

* https://github.com/JulienPalard/Pipe/pull/88

RELATED:

* pyfunctional -- operator chaining instead of pipe-expressions.
* https://github.com/sspipe/sspipe

.. _pipe: https://github.com/JulienPalard/Pipe
"""

from functools import reduce
from pipe import Pipe as as_pipe
import pytest



# -----------------------------------------------------------------------------
# TEST SUPPORT FOR: Pipeline Recipes
# -----------------------------------------------------------------------------
def use_pipe(iterable, the_pipe):
    yield from (iterable | the_pipe)


# -- SIMILAR TO: functools.reduce() -- But better debuggable/explorable
# def reduce2(function, iterable):
#     it = iter(iterable)
#     value = next(it)
#     for element in it:
#         value = function(value, element)
#     return value

# -- HINT: NOT NEEDED when Pipe.__or__() is supported
def chain_pipes(*pipes):
    def pipe_operator(p1, p2):
        return p1 | p2

    this_pipeline = reduce(pipe_operator, pipes)
    @as_pipe
    def _chain_pipes(iterable):
        yield from (iterable | this_pipeline)
    return _chain_pipes


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
    return use_pipe(iterable, select_numbers_modulo(2))


# -----------------------------------------------------------------------------
# TEST SUITE: Pipeline Recipes
# -----------------------------------------------------------------------------
class TestPipelineRecipe(object):
    """A ``pipeline recipe`` is a prepared, often complex chain of pipes.
    It should be easy to use this pipeline recipe without knowing the details.
    """
    def test_recipe_with_one_pipe(self):
        """Check pipeline-recipe that uses "yield from" can be used."""
        @as_pipe
        def select_multiples_of_3(iterable):
            yield from (iterable | select_numbers_modulo(3))

        numbers = range(8)
        results = list(numbers | select_multiples_of_3)
        expected = [0, 3, 6]
        assert results == expected

    def test_recipe_with_many_pipes(self):
        """Check pipeline-recipe that uses "yield from" with many pipes."""
        @as_pipe
        def select_even_numbers_and_multiply_by(iterable, factor):
            yield from (iterable | select_even_numbers | multiply_by(factor))

        numbers = range(8)
        results = list(numbers | select_even_numbers_and_multiply_by(3))
        expected = [0, 6, 12, 18]
        assert results == expected

    def test_recipe_with_or_pipes(self):
        # REQUIRES: https://github.com/JulienPalard/Pipe/pull/88
        # HINT: or-pipes / Pipe.operator-or is provided here.
        select_even_numbers_and_multiply_by_3B = select_even_numbers | multiply_by(3)

        numbers = range(8)
        results = list(numbers | select_even_numbers_and_multiply_by_3B)
        expected = [0, 6, 12, 18]
        assert results == expected

    # -- REJECTED IDEAS:
    #  use_pipe()       -> BETTER USE: "yield from"
    #  chain_pipes()    -> BETTER USE: or-pipes
    def test_recipe__with_chain_pipes(self):
        # -- HINT: pipe-chain with "or-pipes" is simpler.
        select_even_numbers_and_multiply_by_3A = chain_pipes(select_even_numbers, multiply_by(3))

        numbers = range(8)
        results = list(numbers | select_even_numbers_and_multiply_by_3A)
        expected = [0, 6, 12, 18]
        assert results == expected

    def test_use_pipeline_recipe_1(self):
        """Check if a pipeline-recipe that uses "use_pipe()" can be used."""
        numbers = range(8)
        results = list(numbers | select_even_numbers)  # USES: use_pipe() internally
        expected = [0, 2, 4, 6]
        assert results == expected
