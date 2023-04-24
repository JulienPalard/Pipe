import pipe
import doctest


def test_readme():
    failure_count, test_count = doctest.testfile("../README.md")
    assert test_count
    assert not failure_count


def test_uniq():
    assert list(() | pipe.uniq) == []


def test_empty_iterable():
    assert list([] | pipe.take(999)) == []


def test_aliasing():
    is_even = pipe.where(lambda x: not x % 2)

    assert list(range(10) | is_even) == [0, 2, 4, 6, 8]


def test_netcat():
    data = [
        b"HEAD / HTTP/1.0\r\n",
        b"Host: python.org\r\n",
        b"\r\n",
    ]
    response = ""
    for packet in data | pipe.netcat("python.org", 80):
        response += packet.decode("UTF-8")
    assert "HTTP" in response


def test_enumerate():
    data = [4, "abc", {"key": "value"}]
    expected = [(5, 4), (6, "abc"), (7, {"key": "value"})]
    assert list(data | pipe.enumerate(start=5)) == expected


def test_concatenate_pipes():
    data = range(10)
    is_even = pipe.where(lambda x: x % 2 == 0)
    higher_than_4 = pipe.where(lambda x: x > 4)
    expected = [6,8]
    # standard behavior
    assert list(data | is_even | higher_than_4) == expected
    # concatenated pipes
    is_even_and_higher_than_4 = is_even | higher_than_4
    assert list(data | is_even_and_higher_than_4) == expected
