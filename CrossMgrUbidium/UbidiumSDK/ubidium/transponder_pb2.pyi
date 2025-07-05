from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Transponder(_message.Message):
    __slots__ = ("id", "active", "passive", "marker")
    class ActiveData(_message.Message):
        __slots__ = ("wakeup_counter", "battery", "temperature")
        WAKEUP_COUNTER_FIELD_NUMBER: _ClassVar[int]
        BATTERY_FIELD_NUMBER: _ClassVar[int]
        TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
        wakeup_counter: int
        battery: int
        temperature: int
        def __init__(self, wakeup_counter: _Optional[int] = ..., battery: _Optional[int] = ..., temperature: _Optional[int] = ...) -> None: ...
    class PassiveData(_message.Message):
        __slots__ = ("order_id",)
        ORDER_ID_FIELD_NUMBER: _ClassVar[int]
        order_id: int
        def __init__(self, order_id: _Optional[int] = ...) -> None: ...
    class MarkerData(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    PASSIVE_FIELD_NUMBER: _ClassVar[int]
    MARKER_FIELD_NUMBER: _ClassVar[int]
    id: str
    active: Transponder.ActiveData
    passive: Transponder.PassiveData
    marker: Transponder.MarkerData
    def __init__(self, id: _Optional[str] = ..., active: _Optional[_Union[Transponder.ActiveData, _Mapping]] = ..., passive: _Optional[_Union[Transponder.PassiveData, _Mapping]] = ..., marker: _Optional[_Union[Transponder.MarkerData, _Mapping]] = ...) -> None: ...
