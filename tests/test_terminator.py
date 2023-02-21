import pipe
import pipe.terminator as term


def test_as_dict():
    data = ["banana", "grapefruit", "guava"]
    expected = {"BANANA": 6, "GRAPEFRUIT": 10, "GUAVA": 5}
    actual = data > term.as_dict(
        key_func=lambda e: e.upper(),
        value_func=lambda e: len(e),
    )
    assert isinstance(actual, dict)
    assert actual == expected


def test_as_list():
    expected = ["abc", 6, {"key": "value"}]
    actual = expected | pipe.take(3) > term.as_list
    assert isinstance(actual, list)
    assert actual == expected


def test_as_set():
    data = ["banana", "grapefruit", "guava"]
    expected = {"BANANA", "GRAPEFRUIT", "GUAVA"}
    actual = data > term.as_set(
        key_func=lambda e: e.upper(),
    )
    assert isinstance(actual, set)
    assert actual == expected


def test_join():
    actual = range(10) | pipe.filter(lambda x: x % 2 == 0) | pipe.map(str) > term.join("-")
    assert actual == "0-2-4-6-8"


def _foreach_func(actual, e):
    actual[e.upper()] = len(e)


def test_foreach():
    data = ["banana", "grapefruit", "guava"]
    expected = {"BANANA": 6, "GRAPEFRUIT": 10, "GUAVA": 5}
    actual = {}
    data > term.foreach(lambda e: _foreach_func(actual, e))
    assert actual == expected


def test_reduce():
    actual = range(10) | pipe.filter(lambda e: e % 2 == 0) > term.reduce(lambda a, b: a + b)
    assert actual == 20


def test_reduce_with_initial():
    data = ["banana", "grapefruit", "guava"]
    actual = data > term.reduce(lambda acc, e: acc + len(e), 0)
    assert actual == 21


def test_first():
    actual = ["a", "b", "c"] > term.first
    assert actual == "a"


def test_last():
    actual = ["a", "b", "c"] > term.last
    assert actual == "c"


def test_max():
    actual = [3, 7, -4, 0] > term.max
    assert actual == 7


def test_min():
    actual = [3, 7, -4, 0] > term.min
    assert actual == -4


def test_sum():
    actual = [3, 7, -4, 0] > term.sum
    assert actual == 6
