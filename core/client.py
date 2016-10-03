# -*- encoding: utf-8 -*-
import os
import zmq
import yaml
import core.framer
import core.loader
import zmq.eventloop
import zmq.eventloop.zmqstream
import multiprocessing

'''
Create a basic Actor that can take requests
from a Publisher and spawn processes to perform
the actions
'''

CONFIG_LOCATION = '/home/mp/devel/eventdrivetalk/conf/demo_actor.yml'

class Actor(object):
    def __init__(self, opts=None):
        if opts is None:
            self.opts = self.process_config(CONFIG_LOCATION)
        else:
            self.opts = opts

        # Start setting up ZeroMQ
        self.ctx = zmq.Context()
        self.socket = self.ctx.socket(zmq.SUB)

        self.socket.connect('tcp://localhost:2000')

        self.loop = zmq.eventloop.IOLoop.instance()
        self.stream = zmq.eventloop.zmqstream.ZMQStream(self.socket, self.loop)
        self.stream.on_recv(act)

        # Load up actions
        self.actions = loader.load_actions(self.opts, '/home/mp/devel/eventdrivetalk/actions')

    def start(self):
        print('Starting Actor')
        try:
            self.loop.start()
        except KeyboardInterrupt:
            self.stream.close()
            self.loop.stop()
            print('Shut down!')

    def process_config(self, config_location):
        if not os.path.exists(config_location):
            print('WARNING: No config file was found at {0}'.format(config_location))
            return {}
        else:
            try:
                fh_ = open(config_location)
                config = yaml.load(fh_)
            finally:
                fh_close()
            return config

    def act(self, msg):
        '''
        Take a received event and act on it
        '''
        event = framer.unpack(msg)
        action = event['tag'].split().pop()

        # Obviously, we'd normally do some sort of host checking
        # and auth so this is ridiculous but this is just for fun!
        #
        # Blind trust ahoy! ;]
        mp = multiprocessing.Process(target=self._act_target, args=(action))

    def _act_target(self,  action):
        # Perform the action!
        self.actions[action]()
