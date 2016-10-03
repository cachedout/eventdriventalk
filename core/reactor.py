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


CONFIG_LOCATION='/home/mp/devel/eventdriventalk/conf/demo.yml'


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

        self.pull_stream.on_recv(self.republish)


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

    def republish(self, msg):
        self.pub_socket.send_string(msg)

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
        return
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

        self.actions = loader.load_actions(self.opts, '/home/mp/devel/eventdriventalk/actions')
        self.registers = loader.load_registers(self.opts, '/home/mp/devel/eventdriventalk/registers')
        self.rules = loader.load_registers(self.opts, '/home/mp/devel/eventdriventalk/rules')

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
        for tag in self.opts:
            if fnmatch.fnmatch(event['tag'], tag):
                for action in self.opts[tag]['reactions']:
                    # Super-simple non-blocking appraoch
                    # Threading won't scale as much as a true event loop
                    # would. It will, however, handle cases where single-threaded
                    # loop would be blocked. Do you trust your reactions to be co-op?!
                    # Of course, the other side of this is thread-safety. Either way, be smart!
                    t = threading.Thread(target=self.react, args=(action, event))
                    t.start()
                if 'rules' in self.opts[tag]:
                    rule_actions = []
                for rule in self.opts[tag]['rules']:
                    rule_actions = process_rule(rule, event, tracking_id)
                    if rule_actions:
                        for action in rule_actions:
                            self.react(action.keys()[0], action.values())
                    else:
                        # Rule chaining ends when a rule does not match
                        break


    def process_rule(self, rule, event, tracking_id):
        reactions = []
        for rule_name in rule:
            #register = rule[rule_name]['register']
            # Bail out if the period has expired in the register.
            rule_register = rule[rule_name]['register']
            if self.registers[rule_register].period < rule[rule_name]['period']:
                return
            else:
                registered_val = self.registers[rule_register](event['data'])  # FIXME normalize :]
                # Now process the rule
                if self.rules[rule_name](registered_val, rule[rule_name][threshold]):

                    # If the rule rule matches, start processing reactions
                    for react in rule[rule_name]['reactions']:
                        reactions.append(react)
                    return reactions

                    
    def react(self, action, event):
         self.actions[action](event)

    def stream_decode(self, raw):
        for msg in raw:
            event = framer.unpack(msg)
            print('Decoded', event)
            self.process_event(event)


