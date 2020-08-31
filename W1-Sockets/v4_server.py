"""
Aarhus University - Distributed Storage course - Lab 1

Server part of Task 4

Define a message format where you have 2 message types:

    1) Send a short variable length string, up to 4 kB. 
        Send the string length on an appropriate number of 
        bytes in the beginning of the message.

    2) Send arbitrary size binary data (e.g. file contents)

Messages from the client start with the message type byte, 
followed by the string or binary data.

Extend the server to parse the single-byte message type, and 
handle the rest of the message accordingly. If a string was 
received, print it to the console. If binary data was sent by 
the client, store it as a file with a random generated filename
"""

import socket
import threading
import sys
import random
import string

# Define 1-byte constants for the message types
MESSAGE_TYPE_STRING = 1
MESSAGE_TYPE_DATA = 2

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

def handle_connection(clientsocket, client_address):
    """
    Serve an incoming connection and close the client socket.

    :param clientsocket: The socket where client connection is established
    :param client_address: IP address of the client
    :return: Nothing
    """

    # Read first byte of the buffer (message type)
    message_type = clientsocket.recv(1)
    
    # Convert the 'bytes' object to integer
    message_type = int.from_bytes(message_type, byteorder=sys.byteorder)
    
    if message_type == MESSAGE_TYPE_STRING:
        # String message
        msg = clientsocket.recv(4096).decode('utf-8')
        print("String received from {}: {}" .format(client_address, msg))
    
    
    elif message_type == MESSAGE_TYPE_DATA:
        # Data message, read until there is something in the buffer
        data_msg = b""
        part = clientsocket.recv(4096)
        while(len(part) > 0):
            data_msg += part
            part = clientsocket.recv(4096)
        
        print("Data message from {}: {} bytes" .format(client_address, len(data_msg)))
        filename = write_file(data_msg)
        if filename:
            print("Saved as file: {}".format(filename))
        else:
            print("Error saving file.")
    
    else:
        print("Unexpected message type: {}".format(message_type))

    # Close the connection
    clientsocket.close()
#

# Open a socket on TCP port 9000 and start accepting 
# incoming connections from the same computer
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 9002
serversocket.bind(("localhost", port)) 
serversocket.listen(5)
print("Server listening on port %s" % port)
print("(you can exit by Ctrl+C)")

while True:
    (clientsocket, address) = serversocket.accept()
    
    # Run handle_connection() on a new thread, 
    # pass the client socket and address
    client_thread = threading.Thread(
        target=handle_connection, 
        args=(clientsocket, address)
    )
    client_thread.start()
#