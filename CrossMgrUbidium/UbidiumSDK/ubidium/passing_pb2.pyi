from . import common_pb2 as _common_pb2
from . import transponder_pb2 as _transponder_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Passing(_message.Message):
    __slots__ = ("id", "no", "src", "transponder", "time", "received", "hits", "rssi", "location", "active", "passive", "marker")
    class No(_message.Message):
        __slots__ = ("file", "no")
        FILE_FIELD_NUMBER: _ClassVar[int]
        NO_FIELD_NUMBER: _ClassVar[int]
        file: int
        no: int
        def __init__(self, file: _Optional[int] = ..., no: _Optional[int] = ...) -> None: ...
    class Src(_message.Message):
        __slots__ = ("device_id", "device_name", "input", "no")
        DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
        DEVICE_NAME_FIELD_NUMBER: _ClassVar[int]
        INPUT_FIELD_NUMBER: _ClassVar[int]
        NO_FIELD_NUMBER: _ClassVar[int]
        device_id: str
        device_name: str
        input: str
        no: int
        def __init__(self, device_id: _Optional[str] = ..., device_name: _Optional[str] = ..., input: _Optional[str] = ..., no: _Optional[int] = ...) -> None: ...
    class ActiveData(_message.Message):
        __slots__ = ("loop_only", "loop_id", "channel", "flags")
        LOOP_ONLY_FIELD_NUMBER: _ClassVar[int]
        LOOP_ID_FIELD_NUMBER: _ClassVar[int]
        CHANNEL_FIELD_NUMBER: _ClassVar[int]
        FLAGS_FIELD_NUMBER: _ClassVar[int]
        loop_only: bool
        loop_id: int
        channel: int
        flags: int
        def __init__(self, loop_only: bool = ..., loop_id: _Optional[int] = ..., channel: _Optional[int] = ..., flags: _Optional[int] = ...) -> None: ...
    class PassiveData(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class MarkerData(_message.Message):
        __slots__ = ("loop_id", "channel")
        LOOP_ID_FIELD_NUMBER: _ClassVar[int]
        CHANNEL_FIELD_NUMBER: _ClassVar[int]
        loop_id: int
        channel: int
        def __init__(self, loop_id: _Optional[int] = ..., channel: _Optional[int] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    SRC_FIELD_NUMBER: _ClassVar[int]
    TRANSPONDER_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    RECEIVED_FIELD_NUMBER: _ClassVar[int]
    HITS_FIELD_NUMBER: _ClassVar[int]
    RSSI_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    PASSIVE_FIELD_NUMBER: _ClassVar[int]
    MARKER_FIELD_NUMBER: _ClassVar[int]
    id: int
    no: Passing.No
    src: Passing.Src
    transponder: _transponder_pb2.Transponder
    time: _common_pb2.Time
    received: _common_pb2.Time
    hits: int
    rssi: int
    location: _common_pb2.Location
    active: Passing.ActiveData
    passive: Passing.PassiveData
    marker: Passing.MarkerData
    def __init__(self, id: _Optional[int] = ..., no: _Optional[_Union[Passing.No, _Mapping]] = ..., src: _Optional[_Union[Passing.Src, _Mapping]] = ..., transponder: _Optional[_Union[_transponder_pb2.Transponder, _Mapping]] = ..., time: _Optional[_Union[_common_pb2.Time, _Mapping]] = ..., received: _Optional[_Union[_common_pb2.Time, _Mapping]] = ..., hits: _Optional[int] = ..., rssi: _Optional[int] = ..., location: _Optional[_Union[_common_pb2.Location, _Mapping]] = ..., active: _Optional[_Union[Passing.ActiveData, _Mapping]] = ..., passive: _Optional[_Union[Passing.PassiveData, _Mapping]] = ..., marker: _Optional[_Union[Passing.MarkerData, _Mapping]] = ...) -> None: ...
