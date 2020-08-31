"""
Aarhus University - Distributed Storage course - Lab 1

Server part of Task 2

Modify the server code to start a new background thread 
for each new incoming connection, and handle it there.
"""

import socket
import threading

def handle_connection(clientsocket, client_address):
    """
    Serve an incoming connection and close the client socket.

    :param clientsocket: The socket where client connection is established
    :param client_address: IP address of the client
    :return: Nothing
    """

    print("Connection from {}" .format(client_address))
    
    # Close the connection
    clientsocket.close()
#

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
    
    # Run handle_connection() on a new thread, 
    # pass the client socket and address
    client_thread = threading.Thread(
        target=handle_connection, 
        args=(clientsocket, address)
    )
    client_thread.start()
#