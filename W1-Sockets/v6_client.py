"""
Aarhus University - Distributed Storage course - Lab 1

Client part of Task 6

Copy a few test files to the directory where the client is. 
The client reads a filename string  (e.g. “test.pdf”) from the 
user in each iteration of the main while loop. When it’s given, 
the client tries to read the file from its local folder into 
the memory. If the file exists, the client first sends the file 
name to the server as a #1 type message, and waits for a response. 
If the response is the string “OK”, the client sends the file 
contents as a #2 type message, and closes the connection. 

Both the client and server must handle files over 4kB correctly (send and receive multiple chunks).
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


# Read a filename from the console
filename = input("File to send: ")
while filename:
    
    # Stage 1: Read the file into memory
    file_contents = b""
    try:
        with open('./'+filename, 'rb') as f:
            # Read file contents
            print("Reading file {} to memory...".format(filename))
            while True:
                chunk = f.read(4000000)
                if len(chunk) > 0:
                    file_contents += chunk
                else:
                    break
    except Exception as e:
        print("Error reading file {}: {}".format(filename, e))
        filename = input("File to send: ")
        continue

    print("File {} read successfully, size: {}".format(filename, sizeof_fmt(len(file_contents))))
    
    # Stage 2: Send file name and read response

    # Open socket connection
    sock = connect()
    # Send message type and the message itself
    message_type_bytes = MESSAGE_TYPE_STRING.to_bytes(length=1, byteorder=sys.byteorder)
    sock.send(message_type_bytes)
    # Send filename
    sock.send(bytes(filename, 'utf-8'))

    # Read response from the same socket
    response = sock.recv(4096).decode('utf-8')
    if not response == "OK":
        raise ValueError("Error! Server response: {}".format(response))

    print("Server responded OK, sending file contents...")


    # Stage 3: Send the file contents as a data message
    
    data_length = len(file_contents)

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
        sent = sock.send(file_contents[totalsent:])
        if sent == 0:
            raise RuntimeError("Socket connection broken")
        totalsent = totalsent + sent
    
    # Make sure we sent the whole data
    assert(totalsent == data_length)

    sock.close()
    print("Data message of {} bytes sent.".format(data_length))

    # Ask again
    filename = input("File to send: ")
#