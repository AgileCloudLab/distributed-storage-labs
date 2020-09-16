"""
Aarhus University - Distributed Storage course - Lab 4

REST API server for RAID on Raspberry PI Stack
"""
from flask import Flask, make_response, g, request, send_file
import sqlite3
import base64
import random, string
import logging
import os

import time
import zmq
import math
import messages_pb2
import io


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            'files.db',
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()



# Initiate ZMQ sockets
context = zmq.Context()

# Socket to send tasks to Storage Nodes
send_task_socket = context.socket(zmq.PUSH)
send_task_socket.bind("tcp://*:5557")

# Socket to receive messages from Storage Nodes
response_socket = context.socket(zmq.PULL)
response_socket.bind("tcp://*:5558")
# Wait for all workers to start and connect. 
time.sleep(1)
print("Listening to ZMQ messages on tcp://*:5558")

app = Flask(__name__)
app.teardown_appcontext(close_db)




@app.route('/')
def hello():
    return make_response({'message': 'Hello World!'})

@app.route('/files',  methods=['GET'])
def list_files():
    db = get_db()
    cursor = db.execute("SELECT * FROM `file`")
    if not cursor: 
        return make_response({"message": "Error connecting to the database"}, 500)
    
    files = cursor.fetchall()
    # Convert files from sqlite3.Row object (which is not JSON-encodable) to 
    # a standard Python dictionary simply by casting
    files = [dict(file) for file in files]
    #print("Files from DB: {}".format(files))
    return make_response({"files": files})
#

@app.route('/files/<int:file_id>',  methods=['GET'])
def download_file(file_id):

    db = get_db()
    cursor = db.execute("SELECT * FROM `file` WHERE `id`=?", [file_id])
    if not cursor: 
        return make_response({"message": "Error connecting to the database"}, 500)
    
    
    f = cursor.fetchone()
    # Convert to a Python dictionary
    f = dict(f)

    print("File requested: {}".format(f['filename']))

    # Select one chunk of each half
    part1_filenames = f['part1_filenames'].split(',')
    part2_filenames = f['part2_filenames'].split(',')

    part1_filename = part1_filenames[random.randint(0, len(part1_filenames)-1)]
    part2_filename = part2_filenames[random.randint(0, len(part2_filenames)-1)]

    # Reqest the random selected replica of both chunks in parallel
    task1 = messages_pb2.getdata_request()
    task1.filename = part1_filename
    send_task_socket.send_multipart([
        bytes('GET_DATA', 'utf-8'),
        task1.SerializeToString()
    ])
    task2 = messages_pb2.getdata_request()
    task2.filename = part2_filename
    send_task_socket.send_multipart([
        bytes('GET_DATA', 'utf-8'),
        task2.SerializeToString()
    ])

    # Receive both chunks and insert them to 
    file_data_parts = [None, None]
    for _ in range(2):
        result = response_socket.recv_multipart()
        # First frame: file name (string)
        filename_received = result[0].decode('utf-8')
        # Second frame: data
        chunk_data = result[1]

        print("Received %s" % filename_received)

        if filename_received == part1_filename:
            # The first part was received
            file_data_parts[0] = chunk_data
        else:
            # The second part was received
            file_data_parts[1] = chunk_data

    print("Both chunks received successfully")

    # Combine the parts and serve the file
    file_data = file_data_parts[0] + file_data_parts[1]
    return send_file(io.BytesIO(file_data), mimetype=f['content_type'])
#

# HTTP HEAD requests are served by the GET endpoint of the same URL,
# so we'll introduce a new endpoint URL for requesting file metadata.
@app.route('/files/<int:file_id>/info',  methods=['GET'])
def get_file_metadata(file_id):

    db = get_db()
    cursor = db.execute("SELECT * FROM `file` WHERE `id`=?", [file_id])
    if not cursor: 
        return make_response({"message": "Error connecting to the database"}, 500)
    
    f = cursor.fetchone()
    # Convert to a Python dictionary
    f = dict(f)

    print("File: %s" % f)

    return make_response(f)
#


@app.route('/files/<int:file_id>',  methods=['DELETE'])
def delete_file(file_id):

    db = get_db()
    cursor = db.execute("SELECT * FROM `file` WHERE `id`=?", [file_id])
    if not cursor: 
        return make_response({"message": "Error connecting to the database"}, 500)
    
    f = cursor.fetchone()
    if not f:
        return make_response({"message": "File {} not found".format(file_id)}, 404)

    # Convert to a Python dictionary
    f = dict(f)
    print("File to delete: %s" % f)

    # Delete the file contents with os.remove()
    os.remove(f['blob_name'])

    # Delete the file record from the DB
    db.execute("DELETE FROM `file` WHERE `id`=?", [file_id])
    db.commit()

    # Return empty 200 Ok response
    return make_response('')
#

def random_string(length=8):
    return ''.join([random.SystemRandom().choice(string.ascii_letters + string.digits) for n in range(length)])


@app.route('/files', methods=['POST'])
def add_files():
    payload = request.get_json()
    filename = payload.get('filename')
    content_type = payload.get('content_type')
    file_data = base64.b64decode(payload.get('contents_b64'))
    size = len(file_data)

    # RAID 1: cut the file in half and store both halves 2x
    file_data_1 = file_data[:math.ceil(size/2.0)]
    file_data_2 = file_data[math.ceil(size/2.0):]
    #print("First half: %s" % file_data_1)
    #print("Second half: %s" % file_data_2)

    # We'll keep assign a random generated filename for all 4 data chunks, and store which one belongs to which half
    file_data_1_names = [random_string(8), random_string(8)]
    file_data_2_names = [random_string(8), random_string(8)]
    print("Filenames for part 1: %s" % file_data_1_names)
    print("Filenames for part 2: %s" % file_data_2_names)
    
    # 
    for name in file_data_1_names:
        task = messages_pb2.storedata_request()
        task.filename = name
        send_task_socket.send_multipart([
            bytes('STORE_DATA', 'utf-8'),
            task.SerializeToString(),
            file_data_1
        ])

    for name in file_data_2_names:
        task = messages_pb2.storedata_request()
        task.filename = name
        send_task_socket.send_multipart([
            bytes('STORE_DATA', 'utf-8'),
            task.SerializeToString(),
            file_data_2
        ])
    
    # Wait until we recieve 4 responses from the workers
    for task_nbr in range(4):
        resp = response_socket.recv_string()
        print('Received: %s' % resp)
    
    # All chunks are stored, insert the File record in the DB

    # Insert the File record in the DB
    db = get_db()
    cursor = db.execute(
        "INSERT INTO `file`(`filename`, `size`, `content_type`, `part1_filenames`, `part2_filenames`) VALUES (?,?,?,?,?)",
        (filename, size, content_type, ','.join(file_data_1_names), ','.join(file_data_2_names))
    )
    db.commit()

    # Return the ID of the new file record with HTTP 201 (Created) status code
    return make_response({"id": cursor.lastrowid }, 201)
#



import logging
@app.errorhandler(500)
def server_error(e):
    logging.exception("Internal error: %s", e)
    return make_response({"error": str(e)}, 500)


# Start the Flask app and listen on the whole local network
app.run(host="localhost", port=9000)