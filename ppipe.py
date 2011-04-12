#!/usr/bin/env python

from threading import Thread, Lock
from Queue import Queue
import time
from pipe import *
from datetime import datetime

def Threaded(todo):
    def result(iterator, *args, **kwargs):
        qte_of_workers = kwargs.get('qte_of_workers', 1)
        end_sentinel = ()
        input = Queue()
        output = Queue()
        workers = []
        working_threads = 0
        def worker():
            while True:
                item = input.get()
                if item is end_sentinel:
                    input.task_done()
                    output.put(item)
                    return
                todo(item, output, *args)
                input.task_done()
        def feeder():
            for item in iterator:
                input.put(item)
            for i in xrange(qte_of_workers):
                input.put(end_sentinel)
        for i in xrange(qte_of_workers):
            thread = Thread(target=worker)
            thread.start()
            workers.append(thread)
            working_threads += 1
        thread = Thread(target=feeder).start()
        while True:
            item = output.get()
            if item != end_sentinel:
                yield item
                output.task_done()
            else:
                output.task_done()
                working_threads -= 1
                if working_threads == 0:
                    return
    return result

@Pipe
@Threaded
def parallel_where(item, output, condition):
    if condition(item):
        output.put(item)

@Pipe
@Threaded
def parallel_select(item, output, todo):
    output.put(todo(item))

stdoutlock = Lock()
def log(column, text):
    stdoutlock.acquire()
    print ' ' * column * 10,
    print str(datetime.now().time().strftime("%S")),
    print text
    stdoutlock.release()

def fat_big_condition1(x):
    log(1, "Working...")
    time.sleep(2)
    log(1, "Done !")
    return 1

def fat_big_condition2(x):
    log(2, "Working...")
    time.sleep(2)
    log(2, "Done !")
    return 1

print "Normal execution :"
xrange(4) | where(fat_big_condition1) \
          | where(fat_big_condition2) \
          | add | lineout

print "Parallel with 1 worker"
xrange(4) | parallel_where(fat_big_condition1) \
          | where(fat_big_condition2) \
          | add | lineout

print "Parallel with 2 workers"
xrange(4) | parallel_where(fat_big_condition1, qte_of_workers=2) \
          | parallel_where(fat_big_condition2, qte_of_workers=2) | add | stdout

print "Parallel with 4 workers"
xrange(4) | parallel_where(fat_big_condition1, qte_of_workers=4) \
          | parallel_where(fat_big_condition2, qte_of_workers=4) | add | stdout
