# -*- coding: utf-8 -*-

# Copyright (c) 2009-2010 Andrey Vlasovskikh
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import with_statement

from . import Pipe
from contextlib import contextmanager
import re, errno, locale, sys
from subprocess import Popen, PIPE, CalledProcessError
from threading import Thread
from codecs import iterdecode

@contextmanager
def _popen(*args, **kwargs):
    '... -> ContextManager(Popen)'
    def write(fd, xs):
        try:
            for x in xs:
                fd.write(x)
        except IOError, e:
            if e.errno != errno.EPIPE:
                write_excpts.append(e)
        except Exception, e:
            write_excpts.append(e)
        finally:
            fd.close()

    write_excpts = []
    stdin = kwargs.get('stdin')
    if _is_iterable(stdin):
        kwargs = kwargs.copy()
        kwargs['stdin'] = PIPE

    p = Popen(*args, **kwargs)
    try:
        if _is_iterable(stdin):
            writer = Thread(target=write, args=(p.stdin, iter(stdin)))
            writer.start()
            try:
                yield p
            finally:
                writer.join()
                if len(write_excpts) > 0:
                    raise write_excpts.pop()
        else:
            yield p
    except Exception, e:
        if hasattr(p, 'terminate'):
            p.terminate()
        raise
    else:
        ret = p.wait()
        if ret != 0:
            raise CalledProcessError(ret, *args)


def _run_pipeline(command, input, **opts):
    if not (_is_iterable(input) or input is None):
        raise TypeError('input must be iterable or None, got %r' %
                        type(input).__name__)

    if isinstance(input, (str, unicode)):
        input = [input]

    opts = opts.copy()
    opts.update(dict(shell=True, stdin=input))

    with _popen(command, **opts) as p:
        if p.stdout is None:
            return
        xs = p.stdout
        for x in p.stdout:
            yield x[:-1]

def bincmd(command, *args, **kwargs):
    kwargs = kwargs.copy()
    kwargs.setdefault('stdout', PIPE)
    command = format(command, args)
    return lambda input: _run_pipeline(command, input, **kwargs)


def cmd(command, *args, **kwargs):
    def decode(xs):
        return iterdecode(xs, encoding)

    def encode(xs):
        if isinstance(input, (str, unicode)):
            return [xs.encode(encoding)]
        elif xs is None:
            return xs
        else:
            return (x.encode(encoding) for x in xs)

    kwargs = kwargs.copy()
    encoding = kwargs.setdefault('encoding', locale.getpreferredencoding())
    kwargs.pop('encoding')
    return compose(decode, bincmd(command, *args, **kwargs), encode)


class ShellPipe():
    def __init__(self, funcstring, *args, **kwargs):
        self.funcstring = funcstring
        self.pargs = tuple(args)
        self.pkwargs = dict(kwargs)

    def __or__(self, other):
        if isinstance(other, ShellPipe):
            return ShellPipe(
                self.funcstring +'|'+ other.funcstring,
                *(self.pargs + other.pargs),
                **dict(self.pkwargs, **(other.pkwargs)) )
        return bincmd(self.funcstring, *(self.pargs), **(self.pkwargs))(None) | other

    def __ror__(self, other):
        if isinstance(other, ShellPipe):
            return ShellPipe(
                other.funcstring +'|'+ self.funcstring,
                *(other.pargs + self.args),
                **dict(other.pkwargs, **(self.pkwargs)) )
        return bincmd(self.funcstring, *(self.pargs), **(self.pkwargs))(other)


    def __call__(self, *args, **kwargs):
        cpargs = self.pargs + args
        cpkwargs = dict(self.pkwargs, **kwargs)
        return ShellPipe(self.funcstring, *cpargs, **cpkwargs)




def run(cmd, input=None):
    return cmd(input)

def call(cmd, input=None):
    return _retcode(run(cmd, input))

def check_call(cmd, input=None):
    _consume(run(cmd, input))

def format(command, args):
    if command.count('{}') != len(args):
        raise TypeError('arguments do not match the format string %r: %r',
                        (command, args))
    fmt = command.replace('%', '%%').replace('{}', '%s')
    return fmt % tuple(map(_shell_escape, args))

def compose(*fs):
    f = lambda x: reduce(lambda x, f: f(x), reversed(fs), x)
    f.__name__ = ', '.join(f.__name__ for f in fs)
    return f

def _consume(xs):
    for x in xs:
        pass

def _retcode(xs):
    try:
        _consume(xs)
    except CalledProcessError, e:
        return e.returncode
    else:
        return 0

def _shell_escape(str):
    return re.sub(r'''([ \t'"\$])''', r'\\\1', str)

def _is_iterable(x):
    'object -> bool'
    return hasattr(x, '__iter__')
