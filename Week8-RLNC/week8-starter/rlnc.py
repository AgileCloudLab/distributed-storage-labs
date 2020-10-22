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

# TO BE DONE: placeholder for recode

# TO BE DONE: placeholder for get_file

# TO BE DONE: placeholder for __store_repair_fragments



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
        # TO BE DONE: placeholder for status requests


        # TO BE DONE: placeholder for the recode on the Controller


        
        # Add the per-file counters to the total tally
        #total_repaired_subfragment_count += repaired_subfragment_count
        #total_missing_subfragment_count += missing_subfragment_count
        

    return total_repaired_subfragment_count, total_repaired_subfragment_count
