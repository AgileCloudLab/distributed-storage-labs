"""
Aarhus University - Distributed Storage course - Lab 4

Storage Node
"""
import zmq
import messages_pb2

import sys
import os
import random
import string

from utils import random_string, write_file, is_raspberry_pi


# Read the folder name where chunks should be stored from the first program argument
# (or use the current folder if none was given)
data_folder = sys.argv[1] if len(sys.argv) > 1 else "./"
if data_folder != "./":
    # Try to create the folder  
    try:
        os.mkdir('./'+data_folder)
    except FileExistsError as _:
        # OK, the folder exists 
        pass
print("Data folder: %s" % data_folder)

if is_raspberry_pi():
    # On the Raspberry Pi: ask the user to input the last segment of the server IP address
    server_address = input("Server address: 192.168.0.___ ")
    pull_address = "tcp://192.168.0."+server_address+":5557"
    sender_address = "tcp://192.168.0."+server_address+":5558"
    subscriber_address = "tcp://192.168.0."+server_address+":5559"
else:
    # On the local computer: use localhost
    pull_address = "tcp://localhost:5557"
    push_address = "tcp://localhost:5558"
    subscriber_address = "tcp://localhost:5559"
    

context = zmq.Context()
# Socket to receive Store Chunk messages from the controller
receiver = context.socket(zmq.PULL)
receiver.connect(pull_address)
print("Listening on "+ pull_address)
# Socket to send results to the controller
sender = context.socket(zmq.PUSH)
sender.connect(push_address)
# Socket to receive Get Chunk messages from the controller
subscriber = context.socket(zmq.SUB)
subscriber.connect(subscriber_address)
# Receive every message (empty subscription)
subscriber.setsockopt(zmq.SUBSCRIBE, b'')


# Use a Poller to monitor two sockets at the same time
poller = zmq.Poller()
poller.register(receiver, zmq.POLLIN)
poller.register(subscriber, zmq.POLLIN)

while True:
    try:
        # Poll all sockets
        socks = dict(poller.poll())
    except KeyboardInterrupt:
        break
    pass

    # At this point one or multiple sockets may have received a message

    if receiver in socks:
        # Incoming message on the 'receiver' socket where we get tasks to store a chunk
        msg = receiver.recv_multipart()
        # Parse the Protobuf message from the first frame
        task = messages_pb2.storedata_request()
        task.ParseFromString(msg[0])

        # The data is the second frame
        data = msg[1]

        print('Chunk to save: %s, size: %d bytes' % (task.filename, len(data)))

        # Store the chunk with the given filename
        chunk_local_path = data_folder+'/'+task.filename
        write_file(data, chunk_local_path)
        print("Chunk saved to %s" % chunk_local_path)

        # Send response (just the file name)
        sender.send_string(task.filename)
        

    if subscriber in socks:
        # Incoming message on the 'subscriber' socket where we get retrieve requests
        msg = subscriber.recv()
        
        # Parse the Protobuf message from the first frame
        task = messages_pb2.getdata_request()
        task.ParseFromString(msg)

        filename = task.filename
        print("Data chunk request: %s" % filename)

        # Try to load the requested file from the local file system,
        # send response only if found
        try:
            with open(data_folder+'/'+filename, "rb") as in_file:
                print("Found chunk %s, sending it back" % filename)

                sender.send_multipart([
                    bytes(filename, 'utf-8'),
                    in_file.read()
                ])
        except FileNotFoundError:
            # This is OK here
            pass
#