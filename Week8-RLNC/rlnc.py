import kodo
import math
import random
import copy # for deepcopy
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


def decode_file(symbols):
    """
    Decode a file using RLNC decoder and the provided coded symbols.
    The number of symbols must be the same as (STORAGE_NODES_NUM - max_erasures) *
    fragments_per_node.

    :param symbols: coded symbols that contain both the coefficients and symbol data
    :return: the decoded file data
    """

    # Reconstruct the original data with a decoder
    symbols_num = len(symbols)
    symbol_size = len(symbols[0]['data']) - symbols_num #subtract the coefficients' size
    decoder = kodo.RLNCDecoder(kodo.field.binary8, symbols_num, symbol_size)
    data_out = bytearray(decoder.block_size())
    decoder.set_symbols_storage(data_out)

    for symbol in symbols:
        # Separate the coefficients from the symbol data
        coefficients = symbol['data'][:symbols_num]
        symbol_data = symbol['data'][symbols_num:]
        # Feed it to the decoder
        decoder.consume_symbol(symbol_data, coefficients)

    # Make sure the decoder successfully reconstructed the file
    assert(decoder.is_complete())
    print("File decoded successfully")

    return data_out
#


def get_file(coded_fragments, max_erasures, file_size,
             data_req_socket, response_socket):
    """
    Implements retrieving a file that is stored with Reed Solomon erasure coding

    :param coded_fragments: Names of the coded fragments
    :param max_erasures: Max erasures setting that was used when storing the file
    :param file_size: The original data size.
    :param data_req_socket: A ZMQ SUB socket to request chunks from the storage nodes
    :param response_socket: A ZMQ PULL socket where the storage nodes respond.
    :return: A list of the random generated chunk names, e.g. (c1,c2), (c3,c4)
    """

    # We need fragments from 4-max_erasures nodes to reconstruct the file, select this many
    # by randomly removing 'max_erasures' elements from the given chunk names.
    fragnames = copy.deepcopy(coded_fragments)
    for i in range(max_erasures):
        fragnames.remove(random.choice(fragnames))

    # Request the coded fragments in parallel
    for name in fragnames:
        task = messages_pb2.getdata_request()
        task.filename = name
        data_req_socket.send(
            task.SerializeToString()
            )

    # Receive all chunks and insert them into the symbols array
    symbols = []
    for _ in range(len(fragnames)):
        result = response_socket.recv_multipart()
        for i in range(1, len(result)):
            symbols.append({
                "data": bytearray(result[i])
            })
    print("All coded fragments received successfully")

    #Reconstruct the original file data
    file_data = decode_file(symbols)

    return file_data[:file_size]
#
