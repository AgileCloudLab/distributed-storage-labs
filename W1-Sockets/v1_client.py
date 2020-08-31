"""
Aarhus University - Distributed Storage course - Lab 1

Client part of Task 1

Write a simple client program that connects to the server and print a 
status message to the terminal every time when the user hits the Enter key. 

Both the server and client should run indefinitely until the user terminates 
the program manually (Ctrl+C).
"""

import socket

# Start a loop until the user input is a single Enter (which evaluates to False)
while not input("Hit Enter to connect to the server!"):
    
    # Connect to the server on localhost:9000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 9000
    sock.connect(("localhost", port))
    # When connect() returns we have a connection
    print("Socket connection established to the server, sending dummy message...")
    
    # Send a dummy message (the string 'hello' converted to bytes)
    sock.send(b'hello')
    
    # Not expecting an answer, close the socket immediately
    sock.close()
    print("Socket closed.")
#