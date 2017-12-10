import unittest

from datetime import datetime

from pipe import Pipe


def calc(list_):
    return [x * 2 for x in list_]


class callable_calc(object):
    def __call__(self, list_):
        return calc(list_)


decorated_callable = Pipe(callable_calc())


class MyDescriptor(object):
    def __get__(self, instance, owner):
        return lambda list_: calc(list_)


class C(object):
    @Pipe
    def calc(self, list_):
        return calc(list_)

    @Pipe
    @classmethod
    def class_calc(cls, list_):
        return calc(list_)

    @Pipe
    @staticmethod
    def static_calc(list_):
        return calc(list_)

    descr = Pipe(MyDescriptor())


class MyTestCase(unittest.TestCase):
    def test_simple(self):
        self.assertEqual([2, 4, 6],
                         [1, 2, 3] | Pipe(calc))

    def test_access_from_instance(self):
        instance = C()
        self.assertEqual([2, 4, 6],
                         [1, 2, 3] | instance.calc)

    def test_access_from_class(self):
        instance = C()
        self.assertEqual([2, 4, 6],
                         [1, 2, 3] | C.calc.bind(instance))

    def test_access_from_classmethod(self):
        self.assertEqual([2, 4, 6],
                         [1, 2, 3] | C.class_calc)

    def test_access_from_staticmethod(self):
        self.assertEqual([2, 4, 6],
                         [1, 2, 3] | C.static_calc)

    def test_access_from_callable_calc(self):
        self.assertEqual([2, 4, 6],
                         [1, 2, 3] | decorated_callable)

    def test_access_from_descriptor(self):
        instance = C()
        self.assertEqual([2, 4, 6],
                         [1, 2, 3] | instance.descr)
if __name__ == '__main__':
    unittest.main()
