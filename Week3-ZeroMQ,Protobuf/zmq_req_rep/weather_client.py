# Weather update client that receives Protobuf messages on tcp://localhost:5556
import sys
import zmq
import weather_pb2

#  Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5556")

# Zipcode filter, default is NYC, 10001
zip_filter = sys.argv[1] if len(sys.argv) > 1 else "10001"

# Subscribe to all messages
socket.setsockopt_string(zmq.SUBSCRIBE, "")

print("Collecting updates from weather server of zip code %s" % zip_filter)

# Collect 5 updates 
updates = []
while len(updates) < 5:
    # Receive the raw message (not recv_string!)
    message = socket.recv()
    # Parse the protobuf-serialized message
    update = weather_pb2.weatherupdate()
    update.ParseFromString(message)

    # Filter messages manually for the matching zipcode
    if update.zipcode == int(zip_filter):
        print("Update for %s zipcode received\n%s" % (zip_filter, update))
        updates.append(update)

# Calculate average
total_temp = sum([u.temperature for u in updates])

print("Average temperature for zipcode '%s' was %f" % (
     zip_filter, total_temp/(len(updates)))
)
