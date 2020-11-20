import messages_pb2
import hashlib
import zlib
import utils

# Deduplication block size (bytes)
BLOCK_SIZE = 4096

def store_file(file_data, send_task_socket, response_socket):
    """
    Compress a file using deduplication and Gzip, and distribute the unique blocks 
    randomly across the Storage Nodes

    :param file_data: A bytearray that holds the file contents
    :param send_task_socket: A ZMQ PUSH socket to the storage nodes
    :param response_socket: A ZMQ PULL socket where the storage nodes respond.
    :return: List of hash IDs and a string that indicates deduplication rate
    """
    
    hash_ids = []

    # Cut the file to 4kB blocks and calculate the MD5 hashes
    blocks = []
    hashes = []
    for block in utils.chunks(file_data, BLOCK_SIZE):
        h = hashlib.md5()
        h.update(block)
        hash_string = h.digest().hex() # Convert the bytes to hex string
        hashes.append(hash_string)
        blocks.append(block)
    #

    # Figure out which hashes are already stored
    db = utils.get_db()
    # Construct a parameterized query that looks like this: 
    # SELECT hash FROM block_hash WHERE hash IN (?,?,?,?) 
    query = "SELECT * FROM `block_hash` WHERE `hash` IN ({placeholders})".format(
        placeholders=','.join(['?']*len(hashes))
    )
    cursor = db.execute(query, hashes)
    existing_hashes = cursor.fetchall()
    # Convert to dictionaries
    existing_hashes = [dict(h) for h in existing_hashes]

    # Iterate the blocks and hashes again to construct the list of BlockHash IDs. 
    # New blocks are Gzipped and sent to the Storage Nodes
    new_blocks_num = 0
    for i in range(len(blocks)):
        block = blocks[i]
        hash_string = hashes[i]

        # Check if the hash is already known
        existing_hash = next((h for h in existing_hashes if h['hash'] == hash_string), None)
        if existing_hash:
            # Yes, this hash is already known and stored, use its ID 
            hash_ids.append(existing_hash['id'])
            # Move on to the next block
            continue
        
        # This is a new block, previously unknown to the system.
        new_blocks_num += 1
        
        # Compress the block and send to a random Storage Node
        compressed_block = zlib.compress(block)
        compression_rate = 100*(1-(len(compressed_block)/len(block)))
        print("New block {} compressed by {:.2f}% with Gzip".format(hash_string, compression_rate))
        task = messages_pb2.storedata_request()
        task.filename = hash_string
        send_task_socket.send_multipart([
            task.SerializeToString(),
            compressed_block
        ])
        
        #  Store the new block hash in the DB.
        cursor = db.execute("INSERT INTO `block_hash`(`hash`) VALUES (?)", [hash_string])
        new_hash_id = cursor.lastrowid

        # Also, add it to 'existing_hashes' so if it's repeating within 
        # the file we can deduplicate it
        existing_hashes.append({
            "id": new_hash_id,
            "hash": hash_string
        })

        hash_ids.append(new_hash_id)
    # 

    new_blocks = "{}/{}".format(new_blocks_num, len(blocks))
    return hash_ids, new_blocks
#

def get_file(hash_ids, data_req_socket, response_socket):
    """
    Implements retrieving a file that is stored with RAID 1 using 4 storage nodes.

    :param hash_ids: List of hash IDs that identify blocks of the file
    :param data_req_socket: A ZMQ SUB socket to request chunks from the storage nodes
    :param response_socket: A ZMQ PULL socket where the storage nodes respond.
    :return: The original file contents
    """

    file_contents = bytearray()

    # Load the block hashes from DB
    db = utils.get_db()
    query = "SELECT * FROM `block_hash` WHERE `id` IN ({placeholders})".format(
        placeholders=','.join(['?']*len(hash_ids))
    )
    cursor = db.execute(query, hash_ids)
    block_hashes  = [dict(h) for h in cursor.fetchall()]

    # Load each block
    for hash_id in hash_ids:
        # Find the block hash record
        block_hash = next((h for h in block_hashes if h['id'] == hash_id), None)
        if not block_hash:
            raise ValueError("Hash %d not found in DB!", hash_id)

        hash_string = block_hash['hash']
        # Load the block from the Storage Node 
        task = messages_pb2.getdata_request()
        task.filename = hash_string
        data_req_socket.send(
            task.SerializeToString()
        )
        result = response_socket.recv_multipart()
        # First frame: file name (string)
        filename_received = result[0].decode('utf-8')
        assert(filename_received == hash_string)
        # Second frame: data
        compressed_block = result[1]
        # Decompress and append to the file contents
        file_contents += zlib.decompress(compressed_block)

    return file_contents
#