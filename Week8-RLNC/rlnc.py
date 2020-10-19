import kodo
import math
import random
from utils import random_string
import messages_pb2

STORAGE_NODES_NUM = 4

def store_file(file_data, max_erasures, fragments_per_node,
               send_task_socket, response_socket):
    """
    Store a file using RLNC, protecting it against 'max_erasures' unavailable storage nodes. 

    :param file_data: The file contents to be stored as a Python bytearray 
    :param max_erasures: How many storage node failures should the data survive
    :param fragments_per_node: How many fragments are stored per node
    :param send_task_socket: A ZMQ PUSH socket to the storage nodes
    :param response_socket: A ZMQ PULL socket where the storage nodes respond
    :return: A list of the coded fragment names, e.g. (c1,c2,c3,c4)
    """

    # Make sure we can realize max_erasures with 4 storage nodes
    assert(max_erasures >= 0)
    assert(max_erasures < STORAGE_NODES_NUM)

    # At least one fragment per node
    assert(fragments_per_node > 0)

    # How many coded fragments (=symbols) will be required to reconstruct the encoded data. 
    symbols = (STORAGE_NODES_NUM - max_erasures) * fragments_per_node
    # The size of one coded fragment (total size/number of symbols, rounded up)
    symbol_size = math.ceil(len(file_data)/symbols)
    # Kodo RLNC encoder using 2^8 finite field
    encoder = kodo.RLNCEncoder(kodo.field.binary8, symbols, symbol_size)
    encoder.set_symbols_storage(file_data)

    fragment_names = []

    # Generate several coded fragments for each Storage Node
    for i in range(STORAGE_NODES_NUM):

        # Generate a random name for them and save
        name = random_string(8)
        fragment_names.append(name)
        
        # Send a Protobuf STORE DATA request to the Storage Nodes
        task = messages_pb2.storedata_request()
        task.filename = name
        
        # Stores all fragments that go to one Storage node
        # First frame contains the task
        frames = [task.SerializeToString()] 

        for j in range(fragments_per_node):
            # Create a random coefficient vector
            coefficients = bytearray()
            for k in range(symbols):
                coefficients.append(random.randint(0,255))

            # Generate a coded fragment with these coefficients 
            symbol = encoder.produce_symbol(coefficients)
            frames.append(coefficients + bytearray(symbol))

        # Send all frames as a single multipart message
        send_task_socket.send_multipart(frames)
 
    # Wait until we receive a response for every message
    for task_nbr in range(STORAGE_NODES_NUM):
        resp = response_socket.recv_string()
        print('Received: %s' % resp)

    return fragment_names
#
