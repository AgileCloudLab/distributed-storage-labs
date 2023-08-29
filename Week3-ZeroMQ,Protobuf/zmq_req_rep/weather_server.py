#   Weather update server that sends Protobuf messages
import zmq
from random import randrange
import weather_pb2

context = zmq.Context()

socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5556")

while True:
   # Create the random weather update
   update = weather_pb2.weatherupdate()
   update.zipcode = randrange(1, 100000)
   update.temperature = randrange(-80, 135)
   update.humidity = randrange(10, 60)
   
   # Serialize and send
   update_string = update.SerializeToString()
   socket.send(update_string)