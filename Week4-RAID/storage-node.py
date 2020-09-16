import zmq
import time
import messages_pb2


def random_string(length=8):
    return ''.join([random.SystemRandom().choice(string.ascii_letters + string.digits) for n in range(length)])

def write_file(data, filename=None):
    """
    Write the given data to a local file with the given filename

    :param data: A bytes object that stores the file contents
    :param filename: The file name. If not given, a random string is generated
    :return: The file name of the newly written file, or None if there was an error
    """
    if not filename:
        # Generate random filename
        filename = random_string(8)
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

context = zmq.Context()

# Socket to receive tasks from the ventilator
pull_address = "tcp://localhost:5557"
receiver = context.socket(zmq.PULL)
receiver.connect(pull_address)
print("Listening on %s" % pull_address)

# Socket to send results to the sink
sender = context.socket(zmq.PUSH)
sender.connect("tcp://localhost:5558")

# Process tasks forever
while True:
    msg = receiver.recv_multipart()

    command = msg[0].decode('utf-8')

    if command == 'STORE_DATA':
        
        # Parse the Protobuf message from the second frame
        task = messages_pb2.storedata_request()
        task.ParseFromString(msg[1])
        
        # The data to store is the third frame
        data = msg[2]

        print('File to save: %s' % task.filename)
        print("File size: %d" % len(data))

        # Store the file with the 
        write_file(data, task.filename)
    
        # Send response (just the file name)
        sender.send_string(task.filename)
    
    else:
        print("Unknown command: %s" % command)
