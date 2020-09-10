import messages_pb2

# Instantiate the 'file' message class and fill it
pb_file = messages_pb2.file()
pb_file.id = 1
pb_file.name = "test.pdf"
pb_file.type = "application/pdf"
pb_file.size = 123
# You don't have to set all fields, unless they are marked 'required' in the proto 

# Serialize the file message to a string, 
# which can be transported over any protocol
encoded_pb_file = pb_file.SerializeToString()
print("Message:\n%s" % pb_file)
print("Encoded message:\n%s (%d bytes)" % (encoded_pb_file, len(encoded_pb_file)))


# -- Transport the serialized string to the receiver --


# On the receiver end, instantiate the same file message class
# and call ParseFromString to reconstruct it from the serialized message
pb_file2 = messages_pb2.file()
pb_file2.ParseFromString(encoded_pb_file)

# The parsed file has the same attributes as the original did
assert(pb_file2.id == pb_file.id)
assert(pb_file2.name == pb_file.name)
assert(pb_file2.type == pb_file.type)
assert(pb_file2.size == pb_file.size)