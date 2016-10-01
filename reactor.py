# -*- encoding: utf-8 -*-

import os
import yaml
import zmq
import zmq.eventloop
import zmq.eventloop.zmqstream
import framer


CONFIG_LOCATION='/home/mp/devel/eventdriventalk/example_conf/demo.yml'

class Reactor(object):

    def __init__(self, opts=None):
        if opts is None:
            self.opts = self.process_config()
        else:
            self.opts = opts

        self.ctx = zmq.Context()
        self.socket = ctx.socket(zmq.PULL)

        self.socket.bind('tcp://127.0.0.1:12345')

        self.loop = zmq.eventloop.IOLoop.instance()
        self.stream = zmq.eventloop.zmqstream.ZMQStream(socket, loop)

        self.stream.on_recv(self.stream_decode)

    def start(self):
        print('Starting loop')
        try:
            loop.start()
        except KeyboardInterrupt:
            print('\nShutting down')


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

    def process_event(event):
        '''
        Take an event and attempt to match it
        in the list of keys.

        If found, schedule the requested action.
        '''
        pass
            

    def stream_decode(raw):
        print('Fetched {0} messages'.format(len(raw)))
        for msg in raw:
            event = framer.unpack(msg)
            print(event)
            process_event(event)


