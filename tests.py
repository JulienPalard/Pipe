import unittest

from pipe import Pipe


class C(object):
    @Pipe
    def calc(self, list_):
        return [x * 2 for x in list_]


class MyTestCase(unittest.TestCase):

    def test_access_from_instance(self):
        instance = C()
        self.assertEqual([2, 4, 6],
                         [1, 2, 3] | instance.calc)

    def test_access_from_class(self):
        instance = C()
        self.assertEqual([2, 4, 6],
                         [1, 2, 3] | C.calc.bind(instance))


if __name__ == '__main__':
    unittest.main()
