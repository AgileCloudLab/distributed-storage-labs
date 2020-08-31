"""
Aarhus University - Distributed Storage course - Lab 1

Server part of Task 3

Extend the server to convert the received bytes to string and 
write it to the console, together with the remote IP address. 
The server should respond by “Message: {received message}“. 
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

    # Read the whole message and convert to string
    msg = clientsocket.recv(4096).decode('utf-8')
    print("Message from {}: {}" .format(client_address, msg))

    # Send response
    response_message = "Message received: {}".format(msg)
    clientsocket.send(bytes(response_message, 'utf-8'))
    
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