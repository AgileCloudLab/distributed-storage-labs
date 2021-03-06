# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: messages.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='messages.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x0emessages.proto\"%\n\x11storedata_request\x12\x10\n\x08\x66ilename\x18\x01 \x01(\t\"#\n\x0fgetdata_request\x12\x10\n\x08\x66ilename\x18\x01 \x01(\tb\x06proto3'
)




_STOREDATA_REQUEST = _descriptor.Descriptor(
  name='storedata_request',
  full_name='storedata_request',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='filename', full_name='storedata_request.filename', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=18,
  serialized_end=55,
)


_GETDATA_REQUEST = _descriptor.Descriptor(
  name='getdata_request',
  full_name='getdata_request',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='filename', full_name='getdata_request.filename', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=57,
  serialized_end=92,
)

DESCRIPTOR.message_types_by_name['storedata_request'] = _STOREDATA_REQUEST
DESCRIPTOR.message_types_by_name['getdata_request'] = _GETDATA_REQUEST
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

storedata_request = _reflection.GeneratedProtocolMessageType('storedata_request', (_message.Message,), {
  'DESCRIPTOR' : _STOREDATA_REQUEST,
  '__module__' : 'messages_pb2'
  # @@protoc_insertion_point(class_scope:storedata_request)
  })
_sym_db.RegisterMessage(storedata_request)

getdata_request = _reflection.GeneratedProtocolMessageType('getdata_request', (_message.Message,), {
  'DESCRIPTOR' : _GETDATA_REQUEST,
  '__module__' : 'messages_pb2'
  # @@protoc_insertion_point(class_scope:getdata_request)
  })
_sym_db.RegisterMessage(getdata_request)


# @@protoc_insertion_point(module_scope)
