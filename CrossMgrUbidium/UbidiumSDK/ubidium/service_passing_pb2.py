# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: service_passing.proto
# Protobuf Python Version: 6.31.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    6,
    31,
    0,
    '',
    'service_passing.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import common_pb2 as common__pb2
from . import passing_pb2 as passing__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15service_passing.proto\x12\x12raceresult.ubidium\x1a\x0c\x63ommon.proto\x1a\rpassing.proto\"\xb1\x01\n\x0ePassingRequest\x12\x31\n\x03get\x18\x01 \x01(\x0b\x32\".raceresult.ubidium.CmdGetPassingsH\x00\x12\x33\n\x04stop\x18\x02 \x01(\x0b\x32#.raceresult.ubidium.CmdStopPassingsH\x00\x12\x30\n\x03\x61\x63k\x18\x03 \x01(\x0b\x32!.raceresult.ubidium.CmdAckPassingH\x00\x42\x05\n\x03\x63md\"\xa9\x01\n\x0fPassingResponse\x12*\n\x05\x65rror\x18\x01 \x01(\x0b\x32\x19.raceresult.ubidium.ErrorH\x00\x12.\n\x07passing\x18\x02 \x01(\x0b\x32\x1b.raceresult.ubidium.PassingH\x00\x12.\n\x07welcome\x18\x03 \x01(\x0b\x32\x1b.raceresult.ubidium.WelcomeH\x00\x42\n\n\x08response\"\xb8\x04\n\x0e\x43mdGetPassings\x12\x46\n\tstart_ref\x18\x01 \x01(\x0e\x32\x31.raceresult.ubidium.CmdGetPassings.StartReferenceH\x00\x12,\n\x02no\x18\x02 \x01(\x0b\x32\x1e.raceresult.ubidium.Passing.NoH\x00\x12\x0c\n\x02id\x18\x03 \x01(\x04H\x00\x12\x42\n\x07\x65nd_ref\x18\x04 \x01(\x0e\x32/.raceresult.ubidium.CmdGetPassings.EndReferenceH\x01\x12\x0f\n\x05\x63ount\x18\x05 \x01(\rH\x01\"\xa6\x01\n\x0eStartReference\x12\x1f\n\x1bSTART_REFERENCE_UNSPECIFIED\x10\x00\x12\x17\n\x13START_REFERENCE_NOW\x10\x01\x12-\n)START_REFERENCE_BEGINNING_OF_CURRENT_FILE\x10\x02\x12+\n\'START_REFERENCE_BEGINNING_OF_FIRST_FILE\x10\x03\"\x93\x01\n\x0c\x45ndReference\x12\x1d\n\x19\x45ND_REFERENCE_UNSPECIFIED\x10\x00\x12\x1f\n\x1b\x45ND_REFERENCE_UNTIL_STOPPED\x10\x01\x12$\n END_REFERENCE_CURRENTLY_EXISTING\x10\x02\x12\x1d\n\x19\x45ND_REFERENCE_END_OF_FILE\x10\x03\x42\x07\n\x05startB\x05\n\x03\x65nd\"\x11\n\x0f\x43mdStopPassings\"U\n\rCmdAckPassing\x12\x0c\n\x02id\x18\x01 \x01(\x04H\x00\x12,\n\x02no\x18\x02 \x01(\x0b\x32\x1e.raceresult.ubidium.Passing.NoH\x00\x42\x08\n\x06latest\"b\n\x07Welcome\x12\x12\n\ncurrent_id\x18\x01 \x01(\x04\x12\x32\n\ncurrent_no\x18\x02 \x01(\x0b\x32\x1e.raceresult.ubidium.Passing.No\x12\x0f\n\x07\x63ust_no\x18\x03 \x01(\rB)Z\x12raceresult/ubidium\xaa\x02\x12RaceResult.Ubidiumb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'service_passing_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'Z\022raceresult/ubidium\252\002\022RaceResult.Ubidium'
  _globals['_PASSINGREQUEST']._serialized_start=75
  _globals['_PASSINGREQUEST']._serialized_end=252
  _globals['_PASSINGRESPONSE']._serialized_start=255
  _globals['_PASSINGRESPONSE']._serialized_end=424
  _globals['_CMDGETPASSINGS']._serialized_start=427
  _globals['_CMDGETPASSINGS']._serialized_end=995
  _globals['_CMDGETPASSINGS_STARTREFERENCE']._serialized_start=663
  _globals['_CMDGETPASSINGS_STARTREFERENCE']._serialized_end=829
  _globals['_CMDGETPASSINGS_ENDREFERENCE']._serialized_start=832
  _globals['_CMDGETPASSINGS_ENDREFERENCE']._serialized_end=979
  _globals['_CMDSTOPPASSINGS']._serialized_start=997
  _globals['_CMDSTOPPASSINGS']._serialized_end=1014
  _globals['_CMDACKPASSING']._serialized_start=1016
  _globals['_CMDACKPASSING']._serialized_end=1101
  _globals['_WELCOME']._serialized_start=1103
  _globals['_WELCOME']._serialized_end=1201
# @@protoc_insertion_point(module_scope)
