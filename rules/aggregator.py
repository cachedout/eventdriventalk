'''
An aggregator that has a FIFO queue

It enqueues a given number of integers
and then calculates an average
'''

# Import Python libs
import Queue

class Aggregator(object):
    def __init__(self, queue_len):
        self.queue = Queue.Queue(maxsize=queue_len)

    def put(self, item):
        '''
        Add an item
        '''
        if not isinstance(item, int):
            raise Exception('The aggregator only works with integers')
        self.queue.put(item)

    def _flush_queue(self):
        '''
        Flush the queue and return it as a list
        '''
        sums = []
        for i in range(0, self.queue.qsize()): 
            sums.append(self.queue.get())
        return sums
       
    def avg(self):
        '''
        Pull all the items out of the queue
        and calculate an average as a float.

        Queue will be reset.
        '''
        sums = self._flush_queue()
        if not sums:
            return 0

        total_sum = float(reduce(lambda x, y: x+y, sums))
        return total_sum / len(sums)

    def max(self):
        '''
        Return max value in queue.

        Queue resets
        '''
        return max(self._flush_queue())


    def min(self):
        '''
        Return min value in queue

        Queue resets
        '''
        return min(self._flush_queue())
