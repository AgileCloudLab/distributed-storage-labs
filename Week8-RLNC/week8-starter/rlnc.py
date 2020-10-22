import kodo
import math
import random
import copy # for deepcopy
from utils import random_string
import messages_pb2
import json

STORAGE_NODES_NUM = 4

# TO BE DONE: placeholder for store_file


# TO BE DONE: placeholder for __decode_file



def recode(symbols, symbol_count, output_symbol_count):
    """
    Recode a file using an RLNC recoder and the provided coded symbols.
    The symbols are fed into the recoder where output_symbol_count symbols are created
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
    recoder = kodo.RLNCPureRecoder(kodo.field.binary8, symbol_count, symbol_size, symbol_count)

    # Feed the provided symbols to the decoder
    for symbol in symbols:
        # Separate the coefficients from the symbol data
        coefficients = symbol[:symbol_count]
        symbol_data = symbol[symbol_count:]
        # Feed it to the recoder
        recoder.consume_symbol(symbol_data, coefficients)

    # Use recoding to generate new symbols
    output_symbols = []
    for i in range(output_symbol_count):
        # Recoding coefficients are used during the recoding process
        recoding_coefficients = recoder.recoder_generate()
        # Recoded coefficients can be used when decoding
        recoded_symbol, recoded_symbol_coefficients = \
            recoder.recoder_produce_symbol(recoding_coefficients)
        #Add the recoded coefficients in front of the symbol data
        output_symbols.append(recoded_symbol_coefficients + recoded_symbol)

    return output_symbols
#


# TO BE DONE: placeholder for get_file


def __store_repair_fragments(missing_fragments, partially_missing_fragments,
                             repair_symbols, subfragments_per_node,
                             repair_socket, repair_response_socket):
    '''
    Sends the repaired fragments/subfragments to the appropriate storage nodes

    :param missing fragments: Fragments that are completely missing
    :param partially_missing fragments: Fragments with missing subfragments
    :param repair_symbols: the symbols(subfragments) to store
    :param subfragments_per_node: number of subfragments per fragment
    :param repair_socket: A ZMQ PUB socket to send requests to the storage nodes
    :param repair_response_socket: A ZMQ PULL socket on which the storage nodes respond.
    :return: the number of repaired subfragments
    '''

    number_of_repaired_subfragments = 0

    # 1. Full missing fragments (arbitrary choice to have this first as all repair packets
    # are functionally equivalent)
    for fragment in missing_fragments:
        task = messages_pb2.storedata_request()
        task.filename = fragment["name"]

        header = messages_pb2.header()
        header.request_type = messages_pb2.STORE_FRAGMENT_DATA_REQ

        frames = [fragment["node_id"].encode('UTF-8'), #Use the node_id as the topic
                  header.SerializeToString(),
                  task.SerializeToString()]

        for i in range(number_of_repaired_subfragments,
                       number_of_repaired_subfragments + subfragments_per_node):
            frames.append(bytearray(repair_symbols[i]))

        number_of_repaired_subfragments += subfragments_per_node
        repair_socket.send_multipart(frames)

        # Wait until we receive a response for every fragment
        for task_nbr in range(len(missing_fragments)):
            resp = repair_response_socket.recv_string()
            print('Repaired fully missing fragment: %s' % resp)

        # 2. Partially missing fragments
        for fragment in partially_missing_fragments:
            task = messages_pb2.storedata_request()
            task.filename = fragment["name"]

            header = messages_pb2.header()
            header.request_type = messages_pb2.STORE_FRAGMENT_DATA_REQ

            frames = [fragment["node_id"].encode('UTF-8'), #Use the node_id as the topic
                      header.SerializeToString(),
                      task.SerializeToString()]

            for i in range(number_of_repaired_subfragments,
                           number_of_repaired_subfragments + fragment["subfragments_lost"]):
                frames.append(bytearray(repair_symbols[i]))

            number_of_repaired_subfragments += fragment["subfragments_lost"]
            repair_socket.send_multipart(frames)

        # Wait until we receive a response for every fragment
        for task_nbr in range(len(partially_missing_fragments)):
            resp = repair_response_socket.recv_string()
            print('Repaired partially missing fragment: %s' % resp)

    return number_of_repaired_subfragments
#


def start_repair_process(files, repair_socket, repair_response_socket):
    """
    Implements the repair process for RLNC-based erasure coding. It receives a list
    of files that are to be checked. For each file, it sends queries to the Storage
    nodes to check how many coded subfragments are stored safely. If it finds a missing
    subfragment, it determines which Storage node was supposed to store it and repairs it.
    Based on how many subfragments are missing, it instructs the storage nodes to send over
    a certain number of recoded subfragments. It then recodes over these creating as many
    subfragments as were missing, sending the appropriate number to each of the nodes.

    :param files: List of files to be checked
    :param repair_socket: A ZMQ PUB socket to send requests to the storage nodes
    :param repair_response_socket: A ZMQ PULL socket on which the storage nodes respond.
    :return: the number of missing subfragments, the number of repaired subfragments
    """

    total_missing_subfragment_count = 0
    total_repaired_subfragment_count = 0

    #Check each file for missing fragments to repair
    for file in files:
        print("Checking file with id: %s" % file["id"])
        #We parse the JSON into a python dictionary
        storage_details = json.loads(file["storage_details"])
        max_erasures = storage_details["max_erasures"]
        subfragments_per_node = storage_details["subfragments_per_node"]
        symbol_count = (STORAGE_NODES_NUM - max_erasures) * subfragments_per_node

        '''
        Iterate over each node's coded subfragments to check what is missing.
        Because this is a distributed system where the central Controller has no knowledge
        of what is stored on each Strorage node, we build several lists and sets to get an
        accurate picture. Through these lists and sets we determine:
        - which nodes respond to our queries
        - which nodes have a partially missing fragment (and how many subfragments are missing)
        - which nodes have fully lost their fragment
        This information will be key in determining where and how many repaired subfragments
        to send later.
        '''
        nodes = set() # list of all storage nodes
        nodes_with_fragment = set() # list of storage nodes with at least partial fragments
        coded_fragments = storage_details["coded_fragments"] # list of all coded fragments
        missing_fragments = [] # list of coded fragments that are fully missing
        partially_missing_fragments = [] # list of coded fragments that are partially missing
        existing_fragments = [] # list of coded fragments that are at least in part intact
        missing_subfragment_count = 0

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
                
                nodes.add(response.node_id) # Build a set of nodes
                if response.is_present == True:
                    nodes_with_fragment.add(response.node_id)
                    existing_fragments.append(fragment)
                    fragment_found = True

                    # Check for partially missing fragments
                    if response.count < subfragments_per_node:
                        subfragments_lost = subfragments_per_node - response.count
                        print("Partial (%s of %s) RLNC fragments lost for %s from node %s"
                              % (subfragments_lost, subfragments_per_node, fragment, response.node_id))
                        #Register it as a partial fragment loss
                        partially_missing_fragments.append({"name": fragment,
                                                            "subfragments_lost": subfragments_lost,
                                                            "node_id": response.node_id})
                        missing_subfragment_count += subfragments_lost
                    else:
                        print("Fragment %s OK" % fragment)

            # If neither node responded with a positive message, the fragment is fully missing
            if fragment_found == False:
                print("RLNC all parts of fragment %s missing" % fragment)
                #Register it as a full lost fragment, we cannot yet determine which node had it
                missing_fragments.append({"name": fragment,
                                          "node_id": "?"})
                missing_subfragment_count += subfragments_per_node

        # We can now determine which nodes had a full missing fragment by subtracting the two
        # sets from eachother.
        nodes_without_fragment = list(nodes.difference(nodes_with_fragment))
        assert(len(nodes_without_fragment) == len(missing_fragments))

        # Assign each full missing fragment to a node that has not fragments stored on it
        i = 0
        for node in nodes_without_fragment:
            missing_fragments[i]["node_id"] = node
            i += 1


        # Perform the actual repair, if necessary
        if missing_subfragment_count > 0:
            # Check that enough fragments still remain to be able to reconstruct the data
            if missing_subfragment_count > max_erasures * subfragments_per_node:
                print("Too many lost fragments: %s. Unable to repair file. " % missing_subfragment_count)
                continue # Move onto the next file

            #Retrieve sufficient fragments and recode
            for fragment in coded_fragments:
                task = messages_pb2.recode_fragments_request()
                task.fragment_name = fragment
                task.symbol_count = symbol_count
                # Request as many fragments as the node originally had stored.
                # Quite wasteful, surely we can do better
                task.output_fragment_count = subfragments_per_node

                header = messages_pb2.header()
                header.request_type = messages_pb2.RECODE_FRAGMENTS_REQ
                
                repair_socket.send_multipart([b"all_nodes",
                                              header.SerializeToString(),
                                              task.SerializeToString()])

            # Wait until we receive a response from each node that has at least one subfragment
            recoded_symbols = []
            for task_nbr in range(len(nodes_with_fragment)):
                response = repair_response_socket.recv_multipart()
                for i in range(len(response)):
                    recoded_symbols.append(bytearray(response[i]))


            # Recreate sufficient repair symbols by recoding over the retrieved symbols again
            repair_symbols = recode(recoded_symbols, symbol_count, missing_subfragment_count)
            print("Retrieved %s recoded symbols from Storage nodes. Created %s new recoded symbols"
                  % (len(recoded_symbols), len(repair_symbols)))

            # Send the repair symbols to the storage nodes based on the lists we previously built
            repaired_subfragment_count = __store_repair_fragments(missing_fragments, partially_missing_fragments,
                                                                  repair_symbols, subfragments_per_node,
                                                                  repair_socket, repair_response_socket)

        # Add the per-file counters to the total tally
        total_missing_subfragment_count += missing_subfragment_count
        total_repaired_subfragment_count += repaired_subfragment_count

    return total_repaired_subfragment_count, total_repaired_subfragment_count
