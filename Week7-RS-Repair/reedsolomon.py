import kodo
import math
import random
import copy # for deepcopy
from utils import random_string
import messages_pb2
import json

STORAGE_NODES_NUM = 4

RS_CAUCHY_COEFFS = [
    bytearray([253, 126, 255, 127]),
    bytearray([126, 253, 127, 255]),
    bytearray([255, 127, 253, 126]),
    bytearray([127, 255, 126, 253])
]

def store_file(file_data, max_erasures, send_task_socket, response_socket):
    """
    Store a file using Reed Solomon erasure coding, protecting it against 'max_erasures' 
    unavailable storage nodes. 
    The erasure coding part codes are the customized version of the 'encode_decode_using_coefficients'
    example of kodo-python, where you can find a detailed description of each step.

    :param file_data: The file contents to be stored as a Python bytearray 
    :param max_erasures: How many storage node failures should the data survive
    :param send_task_socket: A ZMQ PUSH socket to the storage nodes
    :param response_socket: A ZMQ PULL socket where the storage nodes respond
    :return: A list of the coded fragment names, e.g. (c1,c2,c3,c4)
    """

    # Make sure we can realize max_erasures with 4 storage nodes
    assert(max_erasures >= 0)
    assert(max_erasures < STORAGE_NODES_NUM)

    # How many coded fragments (=symbols) will be required to reconstruct the encoded data. 
    symbols = STORAGE_NODES_NUM - max_erasures
    # The size of one coded fragment (total size/number of symbols, rounded up)
    symbol_size = math.ceil(len(file_data)/symbols)
    # Kodo RLNC encoder using 2^8 finite field
    encoder = kodo.RLNCEncoder(kodo.field.binary8, symbols, symbol_size)
    encoder.set_symbols_storage(file_data)

    fragment_names = []

    # Generate one coded fragment for each Storage Node
    for i in range(STORAGE_NODES_NUM):
        # Select the next Reed Solomon coefficient vector 
        coefficients = RS_CAUCHY_COEFFS[i]
        # Generate a coded fragment with these coefficients 
        # (trim the coeffs to the actual length we need)
        symbol = encoder.produce_symbol(coefficients[:symbols])
        # Generate a random name for it and save
        name = random_string(8)
        fragment_names.append(name)
        
        # Send a Protobuf STORE DATA request to the Storage Nodes
        task = messages_pb2.storedata_request()
        task.filename = name

        send_task_socket.send_multipart([
            task.SerializeToString(),
            bytearray(symbol)
        ])
    
    # Wait until we receive a response for every fragment
    for task_nbr in range(STORAGE_NODES_NUM):
        resp = response_socket.recv_string()
        print('Received: %s' % resp)

    return fragment_names
#

def get_file(coded_fragments, max_erasures, file_size, data_req_socket, response_socket):
    """
    Implements retrieving a file that is stored with Reed Solomon erasure coding

    :param coded_fragments: Names of the coded fragments
    :param max_erasures: Max erasures setting that was used when storing the file
    :param file_size: The original data size. 
    :param data_req_socket: A ZMQ SUB socket to request chunks from the storage nodes
    :param response_socket: A ZMQ PULL socket where the storage nodes respond.
    :return: A list of the random generated chunk names, e.g. (c1,c2), (c3,c4)
    """
    
    # We need 4-max_erasures fragments to reconstruct the file, select this many 
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

    # Receive both chunks and insert them to 
    symbols = []
    for _ in range(len(fragnames)):
        result = response_socket.recv_multipart()
        # In this case we don't care about the received name, just use the 
        # data from the second frame
        symbols.append({
            "chunkname": result[0].decode('utf-8'), 
            "data": bytearray(result[1])
        })
    print("All coded fragments received successfully")

    # Reconstruct the original data with a decoder
    symbols_num = len(symbols)
    symbol_size = len(symbols[0]['data'])
    decoder = kodo.RLNCDecoder(kodo.field.binary8, symbols_num, symbol_size)
    data_out = bytearray(decoder.block_size())
    decoder.set_symbols_storage(data_out)

    for symbol in symbols:
        # Figure out the which coefficient vector produced this fragment
        # by checking the fragment name index 
        coeff_idx = coded_fragments.index(symbol['chunkname'])
        coefficients = RS_CAUCHY_COEFFS[coeff_idx]
        # Use the same coefficients for decoding (trim the coefficients to 
        # symbols_num to avoid nasty bugs)
        decoder.consume_symbol(symbol['data'], coefficients[:symbols_num])

    
    # Make sure the decoder successfully reconstructed the file
    assert(decoder.is_complete())

    return data_out[:file_size]
#


def start_repair_process(files, repair_socket, repair_response_socket):
    number_of_missing_fragments = 0
    number_of_repaired_fragments = 0

    #Check that each file is actually stored on the storage nodes
    for file in files:
        #We parse the JSON into a python dictionary
        storage_details = json.loads(file["storage_details"])

        #Iterate over each coded fragment to check that it is not missing
        nodes = set() # list of all storage nodes
        nodes_with_fragment = set() # list of storage nodes with fragment
        coded_fragments = storage_details["coded_fragments"]
        lost_fragments = []
        existing_fragments = []
        for fragment in coded_fragments:
            task = messages_pb2.fragment_status_request()
            task.fragment_name = fragment
            repair_socket.send(
                task.SerializeToString()
            )

            fragment_found = False
            # Wait until we receive a response from each node
            for task_nbr in range(STORAGE_NODES_NUM):
                msg = repair_response_socket.recv()
                response = messages_pb2.fragment_status_response()
                response.ParseFromString(msg)

                #Build a set of nodes
                nodes.add(response.node_id)
                if response.is_present == True:
                    nodes_with_fragment.add(response.node_id)
                    existing_fragments.append(fragment)
                    fragment_found = True

            if fragment_found == False:
                print("Fragment %s lost" % fragment)
                lost_fragments.append(fragment)
                number_of_missing_fragments += 1
            else:
                print("Fragment %s OK" % fragment)

        # If we have lost fragments, we figure out where they were stored
        # we assume that each node stored exactly 1 or 0 fragments
        nodes_without_fragment = list(nodes.difference(nodes_with_fragment))
        if len(lost_fragments) > 0:

            # Check that enough fragments still remain to be able to repair
            if len(lost_fragments) > storage_details["max_erasures"]:
                print("Too many lost fragments: %s. Unable to repair. " % len(lost_fragments))
                continue

            # Retrieve sufficient fragments to decode
            # TODO

            # Re-encode each missing fragment: foreach loop
            for lost_fragment in lost_fragments:
                number_of_repaired_fragments += 1
                # TODO

    return number_of_missing_fragments, number_of_repaired_fragments
