"""
Aarhus University - Distributed Storage course - Lab 1

Client part of Task 5

Extend message type #2 to include the data size before sending 
the data itself. You can choose a number of bytes to encode this 
information, and make sure the client never tries to send data 
more than what can be encoded on this many bytes.

Alternatively, you can introduce different message types that 
define the data size bytes.
"""

import socket
import random
import sys

# Define 1-byte constants for the message types
MESSAGE_TYPE_STRING = 1
MESSAGE_DATA_1B = 2
MESSAGE_DATA_2B = 3
MESSAGE_DATA_3B = 4
MESSAGE_DATA_4B = 5


def connect():
    # Connect to the server on localhost:9000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 9002
    sock.connect(("localhost", port))
    # When connect() returns we have a connection
    return sock

def sizeof_fmt(num, suffix='B'):
    for unit in ['','K','M','G','T']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


# Read a string from the console
msg_type = input("String (1) or Data (2) message? ")
while msg_type:
    
    if msg_type == '1':
        msg = input("What is the message? ")
        sock = connect()
        
        # Trim the message to 4kB
        msg = msg[:4096]
        
        # Send message type and the message itself
        message_type_bytes = MESSAGE_TYPE_STRING.to_bytes(length=1, byteorder=sys.byteorder)
        sock.send(message_type_bytes)
        sock.send(bytes(msg, 'utf-8'))
        
        # Not expecting an answer, close the socket
        sock.close()
        print("String message sent.")
    
    elif msg_type == '2':
        print("Data message selected")
        sock = connect()

        # Generate random data size between 1 byte - 20 megabytes
        data_length = random.randint(1, 20 * 1e6)
        print("Generating {} data".format(sizeof_fmt(data_length)))
        data = bytearray(data_length)
        for i in range(data_length):
            data[i] = random.randint(0, 255)
        

        message_type = None
        bytes_num = 0
        if data_length <= pow(2, 8):
            message_type = MESSAGE_DATA_1B
            bytes_num = 1

        elif data_length <= pow(2, 2*8):
            message_type = MESSAGE_DATA_2B
            bytes_num = 2

        elif data_length <= pow(2, 3*8):
            message_type = MESSAGE_DATA_3B
            bytes_num = 3

        elif data_length <= pow(2, 4*8):
            message_type = MESSAGE_DATA_4B
            bytes_num = 4
        else:
            sock.close()
            raise ValueError("Data size too large!")
            
        print("Message type: {}".format(message_type))
        
        # Send message type
        message_type_bytes = message_type.to_bytes(length=1, byteorder=sys.byteorder)
        sock.send(message_type_bytes)

        # Send the data length using 'bytes_num' bytes
        data_length_bytes = data_length.to_bytes(length=bytes_num, byteorder=sys.byteorder)
        sock.send(data_length_bytes)
        
        # Send the data
        totalsent = 0
        while totalsent < data_length:
            sent = sock.send(data[totalsent:])
            if sent == 0:
                raise RuntimeError("Socket connection broken")
            totalsent = totalsent + sent
        
        # Make sure we sent the whole data
        assert(totalsent == data_length)

        sock.close()
        print("Data message of {} bytes sent.".format(data_length))

    # Ask again
    msg_type = input("String (1) or Data (2) message? ")
#