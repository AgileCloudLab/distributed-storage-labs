import time
import zmq

context = zmq.Context()

# Socket to receive tasks from the ventilator
receiver = context.socket(zmq.PULL)
receiver.connect("tcp://localhost:5557")

# Socket to send results to the sink
sender = context.socket(zmq.PUSH)
sender.connect("tcp://localhost:5558")
print("Worker is listening")

tasks_served = 0
# Process tasks forever
while True:
   s = receiver.recv()
   tasks_served += 1
   
   # Simulate do the work by waiting the received amount of time
   time.sleep(int(s)*0.001)
   # Send results to sink (just an empty message now)
   sender.send(b'')
   print(f"Sent result #{tasks_served} to sink.")