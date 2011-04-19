#! python

# Is there a better way than the following?
import sys,os; sys.path.append(os.path.split(os.getcwd())[0])

from Piping import Pipe
# Pipe is actually a LinablePipe, which is based on ArgPipe

from Piping.iterpipe import ShellPipe
from Piping.commands import *

def numlines():
    n = 0
    while True:
        n += 1
        yield n

nf = numlines()
def nl():
    global nf
    print ( '\n#%i  ' % nf.next() ) + '-'*30 + '\n'



lineout = concat | strout

nl()#1
print lineout
# pipelines are pipes concatenated, although they can't be called.
# strout prints the string representation of the whole iterable,
nl()#2
(1,2,3,4) | strtee | take(3) | strtee | lineout
# strtee is like strout, but also returns it's input; I'm not sure
# if it's strout is really needed, maybe all the 'tee' commands can
# replace the 'out' commands?



somedict = {'1':lineout, '2':"pipes!pipes!pipes!", '3':(1,3,4)}
nl()#3
(somedict, somedict) | pptee | pull
print ''
(somedict,) | pptee | pull
print ''
somedict | pptee | pull

nl()#4
(somedict,) | pptee
nl()#5
(somedict,) | pptee | strout
# pptee uses pprint, but we need to pull items through the pipeline
# since the 'tee' commands only prints the items as they pass though.



cal = ShellPipe('cal')
sed = ShellPipe("sed 's/2/X/' ")

nl()#6
print(cal)
print(sed)
print(cal | sed)
# ShellPipes concatenate when piped toghether, automatic pieline!



nl()#7
cal | sed | strtee | ppout
# actual pipelines cannot be pulled until you push an iterable through,
# at which point they turn to iterables themselves (like pipes). ShellPipes
# turn to iterables when pulled.

# Also
#
#> cal | sed | strtee | ppout
#
# is the same as
#
#> None | cal | sed | strtee | ppout
#
# as shellpipes are based on iterpipes,
# shell commands can output with no (None)
# input.

nl()#8
print lineout # a pipeline
print lineout | strout # another new pipeline
# note how strout hasn't printed anything

nl()#9
print cal # a shellpipe
print cal | sed # another new shellpipe
cal | sed | strout
# we don't need a print statement this time

nl()#10
cal | sed | strout # doesn't need input
(1,2,3) | take(2) | strout # needs input
# shellpipes have their __or__ defined, which
# makes them behave differently from pipelines
