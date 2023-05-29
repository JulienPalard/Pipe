"""
Tests related to the "pipeline recipe" idea.

DEFINITION: Pipeline recipe

* A prepared, often complex pipeline that should easily reusable by others

SOLUTIONS:

* Use pipe-functions with ``yield-from`` expression.
* Use ``or-pipe expressions`` (support added to: `pipe` module)
* Use make-idiom with ``or-pipe expressions``.

SEE ALSO:

* https://github.com/JulienPalard/Pipe/pull/88

RELATED:

* pyfunctional -- operator chaining instead of pipe-expressions.
* https://github.com/sspipe/sspipe

.. _pipe: https://github.com/JulienPalard/Pipe
"""

from pipe import Pipe as as_pipe
import pytest



# -----------------------------------------------------------------------------
# TEST SUPPORT FOR: Pipeline Recipes -- Common pipes
# -----------------------------------------------------------------------------
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


# -----------------------------------------------------------------------------
# TEST SUITE: Pipeline Recipes
# -----------------------------------------------------------------------------
class TestPipelineRecipe(object):
    """A ``pipeline recipe`` is a prepared, often complex chain of pipes.
    It should be easy to use this pipeline recipe without knowing the details.
    """
    def test_recipe_with_yield_from_using_one_pipe(self):
        """Check pipeline-recipe that uses "yield from" can be used."""
        @as_pipe
        def select_multiples_of_3(iterable):
            yield from (iterable | select_numbers_modulo(3))

        numbers = range(8)
        results = list(numbers | select_multiples_of_3)
        expected = [0, 3, 6]
        assert results == expected

    def test_recipe_with_yield_from_using_many_pipes(self):
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
        # REQUIRES: or-pipe expressions
        select_even_numbers_and_multiply_by_3B = select_even_numbers | multiply_by(3)

        numbers = range(8)
        results = list(numbers | select_even_numbers_and_multiply_by_3B)
        expected = [0, 6, 12, 18]
        assert results == expected

    def test_recipe_with_make_pipe_using_or_pipes(self):
        # REQUIRES: https://github.com/JulienPalard/Pipe/pull/88
        # REQUIRES: or-pipe expressions
        def make_pipe4select_even_numbers_and_multiply_by(factor):
            # -- USES: or-pipe expressions
            return select_even_numbers | multiply_by(factor)

        select_even_numbers_and_multiply_by_3C = make_pipe4select_even_numbers_and_multiply_by(3)

        numbers = range(8)
        results = list(numbers | select_even_numbers_and_multiply_by_3C)
        expected = [0, 6, 12, 18]
        assert results == expected
