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


def test_batching():
    assert list(range(10) | pipe.batch(3)) == [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9,]]


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
