import zmq
import zmq.eventloop
import framer
EVENT_SOCKET = None

def _make_eventer():
   ctx = zmq.Context()
   push_socket = self.ctx.socket(zmq.PUSH)
   push_socket.connect('ipc:///tmp/reactor.ipc')
   EVENT_SOCKET = push_socket

def fire_event(event_data):
    if not EVENT_SOCKET:
        _make_eventer()
    print('Using event socket: {0}'.format(EVENT_SOCKET))  # FIXME debugging
    framed_event = framer.pack(event_data)
    push_socket.send(framed_event)



