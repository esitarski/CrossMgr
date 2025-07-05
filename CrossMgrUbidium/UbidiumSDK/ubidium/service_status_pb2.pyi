from google.protobuf import duration_pb2 as _duration_pb2
from . import common_pb2 as _common_pb2
from . import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StatusRequest(_message.Message):
    __slots__ = ("get", "stop")
    GET_FIELD_NUMBER: _ClassVar[int]
    STOP_FIELD_NUMBER: _ClassVar[int]
    get: CmdGetStatus
    stop: CmdStopStatus
    def __init__(self, get: _Optional[_Union[CmdGetStatus, _Mapping]] = ..., stop: _Optional[_Union[CmdStopStatus, _Mapping]] = ...) -> None: ...

class StatusResponse(_message.Message):
    __slots__ = ("error", "status")
    ERROR_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    error: _common_pb2.Error
    status: _status_pb2.Status
    def __init__(self, error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ..., status: _Optional[_Union[_status_pb2.Status, _Mapping]] = ...) -> None: ...

class CmdGetStatus(_message.Message):
    __slots__ = ("continues", "push_time")
    CONTINUES_FIELD_NUMBER: _ClassVar[int]
    PUSH_TIME_FIELD_NUMBER: _ClassVar[int]
    continues: bool
    push_time: _duration_pb2.Duration
    def __init__(self, continues: bool = ..., push_time: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class CmdStopStatus(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
