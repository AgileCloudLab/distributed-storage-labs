"""
Aarhus University - Distributed Storage course - Lab 9
HDFS Namenode
"""

from flask import Flask, make_response, request
import random
import utils

app = Flask(__name__)
app.teardown_appcontext(utils.close_db)

# Set up DB structure 
utils.init_db()

# Load the datanode IP addresses from datanodes.txt 
DATANODE_ADDRESSES = utils.read_file_by_line('datanodes.txt')
print("Datanodes: %s" % ', '.join(DATANODE_ADDRESSES))


@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Authorization,Content-Type'
    response.headers['access-control-allow-methods'] = 'DELETE, GET, OPTIONS, POST, PUT'
    return response
#

@app.route('/')
def hello():
    return make_response({'message': 'Namenode'})
#

@app.route('/files',  methods=['GET'])
def list_files():
    db = utils.get_db()
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

@app.route('/files', methods=['POST'])
def add_files():
    payload = request.get_json()
    filename = payload.get('filename')
    filetype = payload.get('type')
    size = payload.get('size')

    # Select 2 random datanodes (without repetition) to store the file replicas
    replica_locations = random.sample(DATANODE_ADDRESSES, k=2)

    # Insert the File record in the DB
    db = utils.get_db()
    cursor = db.execute(
        "INSERT INTO `file`(`filename`, `size`, `type`, `replica_locations`) VALUES (?,?,?,?)",
        (filename, size, filetype, ' '.join(replica_locations))
    )
    db.commit()
    file_id = cursor.lastrowid

    # Return the new file ID and the replica locations (datanode addresses)
    result = {
        "id":  file_id, 
        "replica_locations": replica_locations
    }
    
    return make_response(result, 201)
#

# Start the Flask app (must be after the endpoint functions) 
host_local_computer = "localhost" # Listen for connections on the local computer
host_local_network = "0.0.0.0" # Listen for connections on the local network
app.run(host=host_local_network if utils.is_raspberry_pi() else host_local_computer, port=9000)
