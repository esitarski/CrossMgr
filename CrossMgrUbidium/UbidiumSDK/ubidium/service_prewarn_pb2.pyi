from . import common_pb2 as _common_pb2
from . import prewarn_pb2 as _prewarn_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PrewarnRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PrewarnResponse(_message.Message):
    __slots__ = ("error", "prewarn")
    ERROR_FIELD_NUMBER: _ClassVar[int]
    PREWARN_FIELD_NUMBER: _ClassVar[int]
    error: _common_pb2.Error
    prewarn: _prewarn_pb2.Prewarn
    def __init__(self, error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ..., prewarn: _Optional[_Union[_prewarn_pb2.Prewarn, _Mapping]] = ...) -> None: ...
