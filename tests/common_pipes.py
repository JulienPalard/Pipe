from pipe import Pipe as as_pipe

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
