# -*- coding: utf-8 -*-

"""
Infix programming toolkit

Module enabling a sh like infix syntax (using pipes).

"""
__author__ = 'Julien Palard <julien@eeple.fr>'
__credits__ = """Jerome Schneider, for its Python skillz,
and dalexander for contributing"""
__date__ = '10 Nov 2010'
__version__ = '1.4'

class Pipe:
    
    def __init__(self, function):
        self.function = function

    def __ror__(self, other):
        return self.function(other)

    def __call__(self, *args, **kwargs):
        return Pipe(lambda x: self.function(x, *args, **kwargs))

if __name__ == "__main__":
    import doctest
    doctest.testmod()
