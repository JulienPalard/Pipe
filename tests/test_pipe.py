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


def test_class_support():
    class Factory:
        n = 10

        @pipe.Pipe
        def mul(self, iterable):
            return (x * self.n for x in iterable)

    assert list([1, 2, 3] | Factory().mul) == [10, 20, 30]


def test_pipe_repr():
    @pipe.Pipe
    def sample_pipe(iterable):
        return (x * 2 for x in iterable)

    assert repr(sample_pipe) == "piped::<sample_pipe>(*(), **{})"

    @pipe.Pipe
    def sample_pipe_with_args(iterable, factor):
        return (x * factor for x in iterable)

    pipe_instance = sample_pipe_with_args(3)
    real_repr = repr(pipe_instance)
    assert "piped::<sample_pipe_with_args>(" in real_repr
    assert "3" in real_repr
