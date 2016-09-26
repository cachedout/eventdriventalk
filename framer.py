# -*- encoding: utf-8 -*-

import msgpack

def pack(tag, msg):
    '''
    tags look like '/namespace/type'

    msg is a dictionary containing the message to be processed
    '''
    return msgpack.dumps({'tag': tag, 'data': msg})

def unpack(msg):
    return msgpack.loads(msg)
