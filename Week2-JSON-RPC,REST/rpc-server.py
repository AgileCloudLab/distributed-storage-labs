"""
Aarhus University - Distributed Storage course - Lab 2

JSON-RPC Server

Original source: https://tinyrpc.readthedocs.io/en/latest/examples.html
"""

import gevent
import gevent.pywsgi
import gevent.queue
from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from tinyrpc.transports.wsgi import WsgiServerTransport
from tinyrpc.server.gevent import RPCServerGreenlets
from tinyrpc.dispatch import RPCDispatcher
import base64

dispatcher = RPCDispatcher()
transport = WsgiServerTransport(queue_class=gevent.queue.Queue)

# start wsgi server as a background-greenlet
wsgi_server = gevent.pywsgi.WSGIServer(('127.0.0.1', 5000), transport.handle)
gevent.spawn(wsgi_server.serve_forever)

rpc_server = RPCServerGreenlets(transport, JSONRPCProtocol(), dispatcher)

def write_file(data, filename=None):
    """
    Write the given data to a local file with the given filename

    :param data: A bytes object that stores the file contents
    :param filename: The file name. If not given, a random string is generated
    :return: The file name of the newly written file, or None if there was an error
    """
    if not filename:
        # Generate random filename
        filename_length = 8
        filename = ''.join([random.SystemRandom().choice(string.ascii_letters + string.digits) for n in range(filename_length)])
        # Add '.bin' extension
        filename += ".bin"
    
    try:
        # Open filename for writing binary content ('wb')
        # note: when a file is opened using the 'with' statment, 
        # it is closed automatically when the scope ends
        with open('./'+filename, 'wb') as f:
            f.write(data)
    except EnvironmentError as e:
        print("Error writing file: {}".format(e))
        return None
    
    return filename
#

@dispatcher.public
def reverse_string(s):
    return s[::-1]

"""
Task 5: Extend rpc-server.py with a new remote callable 
function that accepts a file name (string) and contents 
(base64 string), and stores the file in the local file system. 
"""
@dispatcher.public
def upload_file(filename, contents_b64):
    file_data = base64.b64decode(contents_b64)
    write_file(file_data, filename)
    return "File {} ({} bytes) saved successfully".format(filename, len(file_data)) 

# in the main greenlet, run our rpc_server
rpc_server.serve_forever()
