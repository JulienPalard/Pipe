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


def test_class_support_on_methods():
    class Factory:
        n = 10

        @pipe.Pipe
        def mul(self, iterable):
            return (x * self.n for x in iterable)

    assert list([1, 2, 3] | Factory().mul) == [10, 20, 30]


def test_class_support_on_static_methods():
    class TenFactory:
        @pipe.Pipe
        @staticmethod
        def mul(iterable):
            return (x * 10 for x in iterable)

    assert list([1, 2, 3] | TenFactory.mul) == [10, 20, 30]


def test_class_support_on_class_methods():
    class Factory:
        n = 10

        @pipe.Pipe
        @classmethod
        def mul(cls, iterable):
            return (x * cls.n for x in iterable)

    assert list([1, 2, 3] | Factory.mul) == [10, 20, 30]

    Factory.n = 2
    assert list([1, 2, 3] | Factory.mul) == [2, 4, 6]

    obj = Factory()
    assert list([1, 2, 3] | obj.mul) == [2, 4, 6]


def test_class_support_with_named_parameter():
    class Factory:
        @pipe.Pipe
        @staticmethod
        def mul(iterable, factor=None):
            return (x * factor for x in iterable)

    assert list([1, 2, 3] | Factory.mul(factor=5)) == [5, 10, 15]


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


def test_chained_pipes():
    pipeline = ... | pipe.skip(2) | pipe.take(3)

    assert list(range(10) | pipeline) == [2, 3, 4]

    @pipe.Pipe
    def double(iterable):
        return (x * 2 for x in iterable)

    extended_pipeline = pipeline | double
    assert list(range(10) | extended_pipeline) == [4, 6, 8]
    assert list(range(10) | pipeline | double) == [4, 6, 8]


def test_chained_pipes_on_bad_constructor():
    assert pipe.ChainedPipes.chain_with(None, None) is None


def test_chained_pipes_reps():
    pipeline = ... | pipe.skip(2) | pipe.take(3)

    repr_pipeline = repr(pipeline)
    assert repr(pipe.skip(2)) in repr_pipeline
    assert repr(pipe.take(3)) in repr_pipeline
