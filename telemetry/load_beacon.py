#/usr/bin/env python2.7
import zmq
import os
import socket
import time
import random
import core.framer

# Create a context
ctx = zmq.Context()

# Our tag
tag = '/client/load/silver'
while True:
    # Frame it up
    event = framer.pack(tag, {'cur_load': os.getloadavg()})
    socket = ctx.socket(zmq.PUSH)
    print('Socket connected at localhost on 2001')
    socket.connect('tcp://localhost:2001')
    print('Sending')
    socket.send(event)
    socket.close()
    time.sleep(1)
