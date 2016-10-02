# -*- encoding: utf-8 -*-

import os
import yaml
import framer
import loader
import fnmatch
import threading
import zmq
import zmq.eventloop
import zmq.eventloop.zmqstream
import tornado.ioloop


CONFIG_LOCATION='/home/mp/devel/eventdriventalk/example_conf/demo.yml'


class Publisher(object):
    '''
    A PUB/SUB relationahip that can publish events based on rules
    '''
    def __init__(self, opts=None):
        if opts is None:
            self.opts = self.process_config(CONFIG_LOCATION)
        else:
            self.opts = opts

        self.ctx = zmq.Context()
        self.pub_socket = self.ctx.socket(zmq.PUB)

        self.pub_socket.bind('tcp://127.0.0.1:2000')

        self.loop = zmq.eventloop.IOLoop.instance()
        self.pub_stream = zmq.eventloop.zmqstream.ZMQStream(self.pub_socket, self.loop)

        # Now create PULL socket over IPC to listen to reactor

        self.pull_socket = self.ctx.socket(zmq.PULL)
        self.pull_socket.bind('ipc:///tmp/reactor.ipc')
        self.pull_stream = zmq.eventloop.zmqstream.ZMQStream(self.pull_socket, self.loop)

        # Test bridge
        self.pull_stream.on_recv(self.ping)


    def process_config(self, config_location):
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

    def start(self):
        print('Starting publisher!')
        try:
            self.loop.start()
        except KeyboardInterrupt:
            print('Shutting down!')
            self.stream.close()
            self.loop.stop()

    def ping(self, *args, **kwargs):
        print('Ping called')
        self.pub_socket.send_string('Pong!')


class Reactor(object):
    '''
    A PUSH/PULL relationship that takes events streamed from one or more
    machines and reacts to them using a trivial rules engine.
    '''
    def __init__(self, opts=None):
        if opts is None:
            self.opts = self.process_config(CONFIG_LOCATION)
        else:
            self.opts = opts

        # General setup of ZeroMQ
        self.ctx = zmq.Context()
        self.loop = zmq.eventloop.IOLoop.instance()

        # Begin setup of PULL socket
        self.pull_socket = self.ctx.socket(zmq.PULL)
        self.pull_socket.bind('tcp://127.0.0.1:2001')

        self.pull_stream = zmq.eventloop.zmqstream.ZMQStream(self.pull_socket, self.loop)
        self.pull_stream.on_recv(self.stream_decode)

        # Begin setup of PUSH socket for IPC to publisher
        self.push_socket = self.ctx.socket(zmq.PUSH)
        self.push_socket.connect('ipc:///tmp/reactor.ipc')

        self.push_stream = zmq.eventloop.zmqstream.ZMQStream(self.push_socket, self.loop)

        self.reactions = loader.load_reactions(self.opts, '/home/mp/devel/eventdriventalk/reactions')

    def start(self):
        print('Starting reactor!')
        try:
            self.loop.start()
        except KeyboardInterrupt:
            self.stream.close()
            self.loop.stop()
            print('\nShutting down')

    def process_config(self, config_location):
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

    def process_event(self, event):
        '''
        Take an event and attempt to match it
        in the list of keys.

        If found, schedule the requested action.
        '''
        if not self.opts:
            return
        ## TESTING
        self.push_socket.send_string('Saw something!')
        for reaction in self.opts:
            if fnmatch.fnmatch(event['tag'], reaction):
                for action in self.opts[reaction]:
                    # Super-simple non-blocking appraoch
                    # Threading won't scale as much as a true event loop
                    # would. It will, however, handle cases where single-threaded
                    # loop would be blocked. Do you trust your reactions to be co-op?!
                    t = threading.Thread(target=self.react, args=(action, event))
                    t.start()
                    
    def react(self, action, event):
        self.reactions[action](event)

    def stream_decode(self, raw):
        for msg in raw:
            event = framer.unpack(msg)
            print('Decoded', event)
            self.process_event(event)


