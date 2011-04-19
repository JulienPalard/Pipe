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


class OldPipe:
    def __init__(self, function):
        self.function = function

    def __ror__(self, other):
        return self.function(other)

    def __call__(self, *args, **kwargs):
        return Pipe(lambda x: self.function(x, *args, **kwargs))

# This version of pipe stores arguments, allowing for them to be
# changed/updated AND prevents nested lambdas (which I think might
# be an issue, although I'm not sure)
class ArgPipe:
    def __init__(self, function, *args, **kwargs):
        self.function = function
        self.pargs = tuple(args)
        self.pkwargs = dict(kwargs)

    def __ror__(self, other):
        return self.function(other, *self.pargs, **self.pkwargs)

    def __call__(self, *args, **kwargs):
        cpargs = self.pargs + args
        cpkwargs = dict(self.pkwargs, **kwargs)
        return Pipe(self.function, *cpargs, **cpkwargs)

# Pipelines let you store multiple pipes, then use them as if they where pipes.
class PipeLine():
    def __init__(self, *pipes):
        self.pipes = pipes

    def __or__(self, other):
        if isinstance(other, PipeLine):
            return PipeLine(*(self.pipes + other.pipes))
        if isinstance(other, LinablePipe):
            return PipeLine(*(self.pipes + (other,)))

    def __ror__(self, other):
        if isinstance(other, PipeLine):
            return PipeLine(*(other.pipes + self.pipes))
        if isinstance(other, LinablePipe):
            return PipeLine(other, *(self.pipes))
        retval = other
        for p in self.pipes:
            retval = retval | p
        return retval

class LinablePipe(ArgPipe):
    def __init__(self, *args, **kwargs):
        ArgPipe.__init__(self, *args, **kwargs)
        
    def __ror__(self, other):
        if isinstance(other, LinablePipe):
            return PipeLine(other, self)
        return ArgPipe.__ror__(self, other)

class Pipe(LinablePipe): # use LinablePipe
    pass

if __name__ == "__main__":
    import doctest
    doctest.testmod()
