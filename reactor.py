# -*- encoding: utf-8 -*-

import zmq
import zmq.eventloop
import zmq.eventloop.zmqstream
import framer

ctx = zmq.Context()
socket = ctx.socket(zmq.PULL)

socket.bind('tcp://127.0.0.1:12345')

loop = zmq.eventloop.IOLoop.instance()
stream = zmq.eventloop.zmqstream.ZMQStream(socket, loop)

def process_reaction(raw):
    print('Fetched {0} messages'.format(len(raw)))
    for msg in raw:
        event = framer.unpack(msg)
        print(event)

stream.on_recv(process_reaction)

print('Starting loop')
try:
    loop.start()
except KeyboardInterrupt:
    print('\nShutting down')
