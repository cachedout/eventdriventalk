import zmq
import socket
import time
import random
import framer

# Create a context
ctx = zmq.Context()

# Our tag
tag = '/client_load/silver'

while True:
    # Choose a random number
    randint = random.randint(1, 100)
    # Frame it up
    event = framer.pack(tag, {'cur_load': randint})
    socket = ctx.socket(zmq.PUSH)
    print('Socket connected at localhost on 12345')
    socket.connect('tcp://localhost:12345')
    print('Sending')
    socket.send(event)
    socket.close()
    time.sleep(0.1)
