'''
An aggregator that has a FIFO queue

It enqueues a given number of integers
and then calculates an average
'''

# Import Python libs
import Queue

QUEUE = Queue.Queue(maxsize=queue_len)
MAX_COUNTER = 0
PERIOD = 0

def register(self, event, rules):
    '''
    Add an item
    '''
    if not isinstance(item, int):
        raise Exception('The aggregator only works with integers')
    QUEUE.put(item)
    PERIOD += 1

def _flush_queue(self):
    '''
    Flush the queue and return it as a list
    '''
    sums = []
    for i in range(0, QUEUE.qsize()): 
        sums.append(QUEUE.get())
    PERIOD = 0
    return sums
   
def avg(self, event, rules):
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

def max(self, event, rules):
    '''
    Return max value in queue.

    Queue resets
    '''
    # Check and see if it's time to return the max
    # We only do this every so often.
    if self.max_counter < rules['period']:
        return

    
    if max(self._flush_queue()) > rules['max']:
        for react in rules['reactions']:
            self.reactions[react](rules['reactions'][react])


def min(self, event, rules):
    '''
    Return min value in queue

    Queue resets
    '''
    return min(self._flush_queue())


