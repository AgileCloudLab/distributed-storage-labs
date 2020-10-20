import kodo
import math
import random
import copy # for deepcopy
from utils import random_string
import messages_pb2
import json

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

def recode(symbols, symbol_count, output_symbol_count):
    """
    Recode a file using RLNC decoder and the provided coded symbols.
    The symbols are fed into the decoder where output_symbol_count symbols are created
    by generating new linear combinations.
    Examples of different techiques to recode using Kodo can be found here:
    https://github.com/steinwurf/kodo-python/blob/master/examples/pure_recode_symbol_api.py
    https://github.com/steinwurf/kodo-python/blob/master/examples/pure_recode_payload_api.py
    https://github.com/steinwurf/kodo-python/blob/master/examples/encode_recode_decode_simple.py

    :param symbols: coded symbols that contain both the coefficients and symbol data
    :param symbol_count: number of symbols needed to decode the file
    :param output_symbol_count: number of symbols to create
    :return: the recoded symbols
    """

    symbol_size = len(symbols[0]) - symbol_count #subtract the coefficients' size
    recoder = kodo.RLNCPureRecoder(kodo.field.binary8, symbol_count, symbol_size, len(symbols))
   # symbol_storage = bytearray(decoder.block_size())
   # decoder.set_symbols_storage(symbol_storage)

    # Feed the provided symbols to the decoder
    for symbol in symbols:
        # Separate the coefficients from the symbol data
        coefficients = symbol[:symbol_count]
        symbol_data = symbol[symbol_count:]
        # Feed it to the decoder
        recoder.consume_symbol(symbol_data, coefficients)

    # Use recoding to generate new symbols
    output_symbols = []
    for i in range(output_symbol_count):
        recoding_coefficients = recoder.recoder_generate()
        #Note that recoding and recoded_symbol coefficients differ
        recoded_symbol, recoded_symbol_coefficients = \
            recoder.recoder_produce_symbol(recoding_coefficients)
        #Add the coefficients in front of the symbol data
        output_symbols.append(recoded_symbol_coefficients + recoded_symbol)

    return output_symbols
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


def start_repair_process(files, repair_socket, repair_response_socket):
    """
    Implements the repair process for RLNC-based erasure coding. It receives a list
    of files that are to be checked. For each file, it sends queries to the Storage
    nodes to check how many coded fragments are stored safely. If it finds a missing
    fragment, it determines which Storage node was supposed to store it and repairs it.
    Based on how many fragments are missing, it instructs the storage nodes to send over
    a certain number of recoded fragments. It then recodes over these creating as many
    fragments as were missing, sending the appropriate number to each of the nodes.

    :param files: List of files to be checked
    :param repair_socket: A ZMQ PUB socket to send requests to the storage nodes
    :param repair_response_socket: A ZMQ PULL socket on which the storage nodes respond.
    :return: the number of missing fragments, the number of repaired fragments
    """

    number_of_missing_fragments = 0
    number_of_repaired_fragments = 0

    #Check each file for missing fragments to repair
    for file in files:
        print("Checking file with id: %s" % file["id"])
        #We parse the JSON into a python dictionary
        storage_details = json.loads(file["storage_details"])
        max_erasures = storage_details["max_erasures"]
        fragments_per_node = storage_details["fragments_per_node"]
        symbol_count = (STORAGE_NODES_NUM - max_erasures) * fragments_per_node

        #Iterate over each node's coded fragments to check that none are missing
        nodes = set() # list of all storage nodes
        nodes_with_fragment = set() # list of storage nodes with fragments
        coded_fragments = storage_details["coded_fragments"] # list of all coded fragments
        missing_fragments = [] # list of missing coded fragments
        existing_fragments = [] # list of existing coded fragments
        for fragment in coded_fragments:
            fragment_found = False 

            task = messages_pb2.fragment_status_request()
            task.fragment_name = fragment
            header = messages_pb2.header()
            header.request_type = messages_pb2.FRAGMENT_STATUS_REQ

            repair_socket.send_multipart([b"all_nodes",
                                          header.SerializeToString(),
                                          task.SerializeToString()])

            # Wait until we receive a response from each node
            for task_nbr in range(STORAGE_NODES_NUM):
                msg = repair_response_socket.recv()
                response = messages_pb2.fragment_status_response()
                response.ParseFromString(msg)
                
                nodes.add(response.node_id) #Build a set of nodes
                if response.is_present == True:
                    nodes_with_fragment.add(response.node_id)
                    existing_fragments.append(fragment)
                    fragment_found = True
                    # Check that all fragments with this name are present
                    if response.count < fragments_per_node:
                        fragments_lost = fragments_per_node - response.count
                        print("Partial (%s of %s) RLNC fragments lost for %s"
                              % (fragments_lost, fragments_per_node, fragment))
                        number_of_missing_fragments += fragments_lost
                    else:
                        print("Fragment %s OK" % fragment)

            # The case when all fragments on a single node are lost
            if fragment_found == False:
                print("RLNC all fragments of %s lost" % fragment)
                missing_fragments.append(fragment)
                number_of_missing_fragments += fragments_per_node
#TODO:separate counters for each file
        # Perform the actual repair, if necessary
        if number_of_missing_fragments > 0:
            # Check that enough fragments still remain to be able to reconstruct the data
            if number_of_missing_fragments > max_erasures * fragments_per_node:
                print("Too many lost fragments: %s. Unable to repair file. " % number_of_missing_fragments)
                continue

            #Retrieve sufficient fragments and recode
            for fragment in coded_fragments:
                task = messages_pb2.recode_fragments_request()
                task.fragment_name = fragment
                task.symbol_count = symbol_count
                task.output_fragment_count = 2
                #TODO: test what happens if we request more than the storage node cans provide
                header = messages_pb2.header()
                header.request_type = messages_pb2.RECODE_FRAGMENTS_REQ
                
                repair_socket.send_multipart([b"all_nodes",
                                              header.SerializeToString(),
                                              task.SerializeToString()])

            # Wait until we receive a response from each node that has at least one fragment
            recoded_symbols = []
            for task_nbr in range(len(nodes_with_fragment)):
                response = repair_response_socket.recv_multipart()
                for i in range(len(response)):
                    recoded_symbols.append(bytearray(response[i]))

            # Recreate sufficient repair symbols by recoding over the retrieved symbols again
            re_recoded_symbols = recode(recoded_symbols, symbol_count, number_of_missing_fragments)
            print("Retrieved %s recoded symbols from Storage nodes. Created %s new recoded symbols"
                  % (len(recoded_symbols), len(re_recoded_symbols)))
                    
    return number_of_missing_fragments, number_of_repaired_fragments
