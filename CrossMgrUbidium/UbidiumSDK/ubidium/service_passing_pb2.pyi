from . import common_pb2 as _common_pb2
from . import passing_pb2 as _passing_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PassingRequest(_message.Message):
    __slots__ = ("get", "stop", "ack")
    GET_FIELD_NUMBER: _ClassVar[int]
    STOP_FIELD_NUMBER: _ClassVar[int]
    ACK_FIELD_NUMBER: _ClassVar[int]
    get: CmdGetPassings
    stop: CmdStopPassings
    ack: CmdAckPassing
    def __init__(self, get: _Optional[_Union[CmdGetPassings, _Mapping]] = ..., stop: _Optional[_Union[CmdStopPassings, _Mapping]] = ..., ack: _Optional[_Union[CmdAckPassing, _Mapping]] = ...) -> None: ...

class PassingResponse(_message.Message):
    __slots__ = ("error", "passing", "welcome")
    ERROR_FIELD_NUMBER: _ClassVar[int]
    PASSING_FIELD_NUMBER: _ClassVar[int]
    WELCOME_FIELD_NUMBER: _ClassVar[int]
    error: _common_pb2.Error
    passing: _passing_pb2.Passing
    welcome: Welcome
    def __init__(self, error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ..., passing: _Optional[_Union[_passing_pb2.Passing, _Mapping]] = ..., welcome: _Optional[_Union[Welcome, _Mapping]] = ...) -> None: ...

class CmdGetPassings(_message.Message):
    __slots__ = ("start_ref", "no", "id", "end_ref", "count")
    class StartReference(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        START_REFERENCE_UNSPECIFIED: _ClassVar[CmdGetPassings.StartReference]
        START_REFERENCE_NOW: _ClassVar[CmdGetPassings.StartReference]
        START_REFERENCE_BEGINNING_OF_CURRENT_FILE: _ClassVar[CmdGetPassings.StartReference]
        START_REFERENCE_BEGINNING_OF_FIRST_FILE: _ClassVar[CmdGetPassings.StartReference]
    START_REFERENCE_UNSPECIFIED: CmdGetPassings.StartReference
    START_REFERENCE_NOW: CmdGetPassings.StartReference
    START_REFERENCE_BEGINNING_OF_CURRENT_FILE: CmdGetPassings.StartReference
    START_REFERENCE_BEGINNING_OF_FIRST_FILE: CmdGetPassings.StartReference
    class EndReference(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        END_REFERENCE_UNSPECIFIED: _ClassVar[CmdGetPassings.EndReference]
        END_REFERENCE_UNTIL_STOPPED: _ClassVar[CmdGetPassings.EndReference]
        END_REFERENCE_CURRENTLY_EXISTING: _ClassVar[CmdGetPassings.EndReference]
        END_REFERENCE_END_OF_FILE: _ClassVar[CmdGetPassings.EndReference]
    END_REFERENCE_UNSPECIFIED: CmdGetPassings.EndReference
    END_REFERENCE_UNTIL_STOPPED: CmdGetPassings.EndReference
    END_REFERENCE_CURRENTLY_EXISTING: CmdGetPassings.EndReference
    END_REFERENCE_END_OF_FILE: CmdGetPassings.EndReference
    START_REF_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    END_REF_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    start_ref: CmdGetPassings.StartReference
    no: _passing_pb2.Passing.No
    id: int
    end_ref: CmdGetPassings.EndReference
    count: int
    def __init__(self, start_ref: _Optional[_Union[CmdGetPassings.StartReference, str]] = ..., no: _Optional[_Union[_passing_pb2.Passing.No, _Mapping]] = ..., id: _Optional[int] = ..., end_ref: _Optional[_Union[CmdGetPassings.EndReference, str]] = ..., count: _Optional[int] = ...) -> None: ...

class CmdStopPassings(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CmdAckPassing(_message.Message):
    __slots__ = ("id", "no")
    ID_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    id: int
    no: _passing_pb2.Passing.No
    def __init__(self, id: _Optional[int] = ..., no: _Optional[_Union[_passing_pb2.Passing.No, _Mapping]] = ...) -> None: ...

class Welcome(_message.Message):
    __slots__ = ("current_id", "current_no", "cust_no")
    CURRENT_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENT_NO_FIELD_NUMBER: _ClassVar[int]
    CUST_NO_FIELD_NUMBER: _ClassVar[int]
    current_id: int
    current_no: _passing_pb2.Passing.No
    cust_no: int
    def __init__(self, current_id: _Optional[int] = ..., current_no: _Optional[_Union[_passing_pb2.Passing.No, _Mapping]] = ..., cust_no: _Optional[int] = ...) -> None: ...
