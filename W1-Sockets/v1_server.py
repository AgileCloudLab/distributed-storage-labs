"""
Aarhus University - Distributed Storage course - Lab 1

Server part of Task 1

Implement a socket server in Python, that listens on TCP port 9000 locally 
for incoming connections. When a connection is established, print the remote 
address to the terminal window and close the socket.

Both the server and client should run indefinitely until the user terminates 
the program manually (Ctrl+C).
"""

import socket

# Open a socket on TCP port 9000 and start accepting 
# incoming connections from the same computer
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 9000
serversocket.bind(("localhost", port)) 
serversocket.listen(5)
print("Server listening on port %s" % port)
print("(you can exit by Ctrl+C)")

while True:
    (clientsocket, address) = serversocket.accept()
    
    # A new incoming connection is received, serve it
    print("Connection from {}" .format(address))
    
    # Close the connection
    clientsocket.close()
#