"""
Explore the `pipe`_ module with some tests.

SEE ALSO:

* https://github.com/JulienPalard/Pipe

RELATED:

* pyfunctional -- operator chaining instead of pipe-expressions.
* https://github.com/sspipe/sspipe

.. _pipe: https://github.com/JulienPalard/Pipe
"""

from pipe import Pipe as as_pipe, where, take_while
import pytest


# -----------------------------------------------------------------------------
# EXPLORATION: PIPE-ADAPTER(s)
# -----------------------------------------------------------------------------
@as_pipe
def inspect_pipe(iterable, func=None, predicate=None):
    """Inspect what items pass through this pipe."""
    if func is None:
        func = print
    if predicate is None:
        predicate = lambda _x: True

    for item in iterable | take_while(predicate):
        func(item)
        yield item

@as_pipe
def to_list(iterable):
    """Pipe adapter that converts the output of this pipe-segment into a list.

    .. code-block::

        outputs = range(5) | ... | to_list
        assert isinstance(outputs, list)
    """
    return list(iterable)



# -----------------------------------------------------------------------------
# TEST SUITE
# -----------------------------------------------------------------------------
def test_pipe_basics():
    """
    IDEA::
        is_even = where(lambda x: x % 2)
        result = list(range(4)) | is_even | to_list
    """
    inputs = list(range(6))
    is_odd = where(lambda x: x % 2 == 1)
    outputs = list(inputs | is_odd)     # OTHERWISE: result is a generator

    expected = [1, 3, 5]
    assert outputs == expected
    assert isinstance(outputs, list)

def test_to_list__as_pipe_adapter():
    """
    IDEA::
        is_even = where(lambda x: x % 2)
        result = list(range(4)) | is_even | to_list
    """
    inputs = list(range(5))
    is_even = where(lambda x: x % 2 == 0)
    outputs = inputs | is_even | to_list

    expected = [0, 2, 4]
    assert outputs == expected
    assert isinstance(outputs, list)

def test_pipe_sink():
    """Test how a pipe-sink can be provided.

    IDEA::

        is_even = where(lambda x: x % 2)
        result = list(range(4)) | is_even | collector

    """
    class Collector(object):
        def __init__(self, data=None):
            self.data = data or []

        def append(self, item):
            self.data.append(item)

    @as_pipe
    def collect_to(iterable, container):
        for item in iterable:
            container.append(item)
        return container

    inputs = list(range(5))
    is_even = where(lambda x: x % 2 == 0)
    collector = Collector()
    output = inputs | is_even | collect_to(collector)

    expected = [0, 2, 4]
    assert output.data == expected
    assert output is collector
    assert isinstance(output, Collector)
