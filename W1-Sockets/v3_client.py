"""
Aarhus University - Distributed Storage course - Lab 1

Client part of Task 3

Extend the client to read a string from the standard input, 
and send that to the server. Limit the string size to 4kB 
(just drop the rest).
"""

import socket

# Read a string from the console
msg = input("Enter message to send: ")
while len(msg):
    
    # Connect to the server on localhost:9000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 9000
    sock.connect(("localhost", port))
    # When connect() returns we have a connection
    print("Socket connection established to the server, sending message '{}'".format(msg))
    
    # Trim the message to 4kB and send it
    msg = msg[:4096]
    bytes_sent = sock.send(bytes(msg, 'utf-8'))
    
    # Not expecting an answer, close the socket immediately
    sock.close()
    
    # Read a new message
    msg = input("Enter message to send: ")
#