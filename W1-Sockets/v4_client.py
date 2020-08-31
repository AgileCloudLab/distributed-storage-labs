"""
Aarhus University - Distributed Storage course - Lab 1

Client part of Task 4

Define a message format where you have 2 message types:

    1) Send a short variable length string, up to 4 kB. 
        Send the string length on an appropriate number of 
        bytes in the beginning of the message.

    2) Send arbitrary size binary data (e.g. file contents)

The client should first ask the user which type of message 
they want to send. If string type was selected, read the string 
from the input and send it to the server. If binary type was 
selected, generate a random byte array and send that to the server. 
The client should write what happened to the console. Keep doing 
this until the user exits the program (e.g. after sending the 
message, the client should again ask the user what message type to 
send). Close the connection after a single message has been sent.
"""

import socket
import random
import sys

# Define 1-byte constants for the message types
MESSAGE_TYPE_STRING = 1
MESSAGE_TYPE_DATA = 2

def connect():
    # Connect to the server on localhost:9000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 9002
    sock.connect(("localhost", port))
    # When connect() returns we have a connection
    return sock

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
        
        # Send message type
        message_type_bytes = MESSAGE_TYPE_DATA.to_bytes(1, byteorder=sys.byteorder)
        sock.send(message_type_bytes)
        
        # Generate random data size between 1 byte - 1 megabytes
        data_length = random.randint(1, 1e6)
        data = bytearray()
        for i in range(data_length):
            data.append(random.randint(0, 255))
        
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