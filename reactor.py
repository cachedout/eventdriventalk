# -*- encoding: utf-8 -*-

import os
import yaml
import zmq
import zmq.eventloop
import zmq.eventloop.zmqstream
import framer

ctx = zmq.Context()
socket = ctx.socket(zmq.PULL)

socket.bind('tcp://127.0.0.1:12345')

loop = zmq.eventloop.IOLoop.instance()
stream = zmq.eventloop.zmqstream.ZMQStream(socket, loop)


def process_config(config_location):
    if not os.path.exists(config_location):
        print('WARNING: No config file was found at {0}'.format(config_location))
        return {}
    else:
        try:
            fh_ = open(config_location)
            config = yaml.load(fh_)
        finally:
            fh_.close()
        return config
        

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
