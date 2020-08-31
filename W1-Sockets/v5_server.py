"""
Aarhus University - Distributed Storage course - Lab 1

Server part of Task 5

Extend message type #2 to include the data size before sending 
the data itself. You can choose a number of bytes to encode this 
information, and make sure the client never tries to send data 
more than what can be encoded on this many bytes.

Alternatively, you can introduce different message types that 
define the data size bytes.

The server should verify that every byte was received before 
saving the file.
"""

import socket
import threading
import sys
import random, string

# Define 1-byte constants for the message types
MESSAGE_TYPE_STRING = 1
MESSAGE_DATA_1B = 2
MESSAGE_DATA_2B = 3
MESSAGE_DATA_3B = 4
MESSAGE_DATA_4B = 5

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

def sizeof_fmt(num, suffix='B'):
    for unit in ['','K','M','G','T']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

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
    
    elif message_type in [MESSAGE_DATA_1B, MESSAGE_DATA_2B, MESSAGE_DATA_3B, MESSAGE_DATA_4B]:
        # Data message, parse the data length 
        
        bytes_num = 0
        if message_type == MESSAGE_DATA_1B:
            bytes_num = 1
        elif message_type == MESSAGE_DATA_2B:
            bytes_num = 2
        elif message_type == MESSAGE_DATA_3B:
            bytes_num = 3
        elif message_type == MESSAGE_DATA_4B:
            bytes_num = 4
        else:
            raise ValueError("Unexpected message type: {}".format(message_type))
        
        # Read the data length bytes from the buffer
        data_length_bytes = clientsocket.recv(bytes_num)
        # Make sure we received the same number of bytes we expect
        assert(len(data_length_bytes) == bytes_num)
        # Convert to int
        data_length = int.from_bytes(data_length_bytes, byteorder=sys.byteorder)
        print("Data message, expected data size: {} ".format(sizeof_fmt(data_length)))

        # Read the data until the socket is closed
        data_msg = b""
        part = clientsocket.recv(4096)
        while(len(part) > 0):
            data_msg += part
            part = clientsocket.recv(4096)
        
        # Make sure we received every byte
        if not len(data_msg) == data_length:
            raise ValueError("Error! Expected %d bytes, received %d bytes.", data_length, len(data_msg))
        
        print("Data message from {}: {} " .format(client_address, sizeof_fmt(len(data_msg))))
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