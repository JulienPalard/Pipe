# -*- coding: utf-8 -*-

from threading import Thread
from Queue import Queue

# TODO: make version that preserves order.

def Threaded(f):
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
                f(item, output, *args)
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
