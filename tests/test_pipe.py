import pipe


def test_uniq():
    assert list(() | pipe.uniq) == []


def test_take_zero():
    assert list([1, 2, 3] | pipe.take(0)) == []


def test_take_one():
    assert list([1, 2, 3] | pipe.take(1)) == [1]


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
