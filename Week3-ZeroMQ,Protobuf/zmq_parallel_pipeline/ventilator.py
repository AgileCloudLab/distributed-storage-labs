import zmq
import random
import time

context = zmq.Context()

# Socket to send messages on
sender = context.socket(zmq.PUSH)
sender.bind("tcp://*:5557")

# Socket with direct access to the sink: used to synchronize start of batch
sink = context.socket(zmq.PUSH)
sink.connect("tcp://localhost:5558")

# Wait for the user to start the workers
print("Press Enter when the workers are ready: ")
_ = input()

print("Sending tasks to workers…")
# The first message to the sink is "0" and signals start of batch
sink.send(b'0')

# Initialize random number generator
random.seed()
# Send 100 tasks
total_msec = 0
for task_nbr in range(100):
   # Random workload from 1 to 100 msecs
   workload = random.randint(1, 100)
   sender.send_string(u'%i' % workload)
   total_msec += workload

print(f"Total expected cost: {total_msec} msec")

# Give 0MQ time to deliver
time.sleep(1)