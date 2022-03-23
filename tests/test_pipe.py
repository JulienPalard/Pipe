import pipe
import doctest


def test_readme():
    doctest.testfile("../README.md")


def test_uniq():
    assert list(() | pipe.uniq) == []
