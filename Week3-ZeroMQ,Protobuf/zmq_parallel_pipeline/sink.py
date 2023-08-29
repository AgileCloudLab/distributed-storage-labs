import time
import zmq

context = zmq.Context()

# Socket to receive messages on
receiver = context.socket(zmq.PULL)
receiver.bind("tcp://*:5558")

# Wait for start of batch from the ventilator
s = receiver.recv()
# Start our clock now
tstart = time.time()
print("Sink started measuring time")

# Collect 100 results from the workers
for task_nbr in range(100):
  s = receiver.recv()
  print('.', end='')

# Calculate and report duration of batch
tend = time.time()
print(f"\nTotal elapsed time: {(tend-tstart)*1000} msec")