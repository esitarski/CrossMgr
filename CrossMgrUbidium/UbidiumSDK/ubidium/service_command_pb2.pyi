from google.protobuf import duration_pb2 as _duration_pb2
from . import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Key(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    KEY_UNSPECIFIED: _ClassVar[Key]
    KEY_OK: _ClassVar[Key]
    KEY_BACK: _ClassVar[Key]
    KEY_UP: _ClassVar[Key]
    KEY_DOWN: _ClassVar[Key]
    KEY_LEFT: _ClassVar[Key]
    KEY_RIGHT: _ClassVar[Key]
    KEY_SCREEN_1: _ClassVar[Key]
    KEY_SCREEN_2: _ClassVar[Key]
    KEY_SCREEN_3: _ClassVar[Key]
    KEY_SCREEN_4: _ClassVar[Key]
    KEY_START: _ClassVar[Key]
KEY_UNSPECIFIED: Key
KEY_OK: Key
KEY_BACK: Key
KEY_UP: Key
KEY_DOWN: Key
KEY_LEFT: Key
KEY_RIGHT: Key
KEY_SCREEN_1: Key
KEY_SCREEN_2: Key
KEY_SCREEN_3: Key
KEY_SCREEN_4: Key
KEY_START: Key

class CommandRequest(_message.Message):
    __slots__ = ("id", "new_file", "set_time", "get_screen", "press_key", "get_settings", "set_settings", "reboot")
    ID_FIELD_NUMBER: _ClassVar[int]
    NEW_FILE_FIELD_NUMBER: _ClassVar[int]
    SET_TIME_FIELD_NUMBER: _ClassVar[int]
    GET_SCREEN_FIELD_NUMBER: _ClassVar[int]
    PRESS_KEY_FIELD_NUMBER: _ClassVar[int]
    GET_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    SET_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    REBOOT_FIELD_NUMBER: _ClassVar[int]
    id: int
    new_file: CmdNewFile
    set_time: CmdSetTime
    get_screen: CmdGetScreen
    press_key: CmdPressKey
    get_settings: CmdGetSettings
    set_settings: CmdSetSettings
    reboot: CmdReboot
    def __init__(self, id: _Optional[int] = ..., new_file: _Optional[_Union[CmdNewFile, _Mapping]] = ..., set_time: _Optional[_Union[CmdSetTime, _Mapping]] = ..., get_screen: _Optional[_Union[CmdGetScreen, _Mapping]] = ..., press_key: _Optional[_Union[CmdPressKey, _Mapping]] = ..., get_settings: _Optional[_Union[CmdGetSettings, _Mapping]] = ..., set_settings: _Optional[_Union[CmdSetSettings, _Mapping]] = ..., reboot: _Optional[_Union[CmdReboot, _Mapping]] = ...) -> None: ...

class CommandResponse(_message.Message):
    __slots__ = ("request_id", "error", "new_file_response", "set_time_response", "get_screen_response", "press_key_response", "get_settings_response", "set_settings_response", "reboot_response")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    NEW_FILE_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    SET_TIME_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    GET_SCREEN_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    PRESS_KEY_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    GET_SETTINGS_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    SET_SETTINGS_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    REBOOT_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    request_id: int
    error: _common_pb2.Error
    new_file_response: CmdNewFileResponse
    set_time_response: CmdSetTimeResponse
    get_screen_response: CmdGetScreenResponse
    press_key_response: CmdPressKeyResponse
    get_settings_response: CmdGetSettingsResponse
    set_settings_response: CmdSetSettingsResponse
    reboot_response: CmdRebootResponse
    def __init__(self, request_id: _Optional[int] = ..., error: _Optional[_Union[_common_pb2.Error, _Mapping]] = ..., new_file_response: _Optional[_Union[CmdNewFileResponse, _Mapping]] = ..., set_time_response: _Optional[_Union[CmdSetTimeResponse, _Mapping]] = ..., get_screen_response: _Optional[_Union[CmdGetScreenResponse, _Mapping]] = ..., press_key_response: _Optional[_Union[CmdPressKeyResponse, _Mapping]] = ..., get_settings_response: _Optional[_Union[CmdGetSettingsResponse, _Mapping]] = ..., set_settings_response: _Optional[_Union[CmdSetSettingsResponse, _Mapping]] = ..., reboot_response: _Optional[_Union[CmdRebootResponse, _Mapping]] = ...) -> None: ...

class CmdNewFile(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CmdNewFileResponse(_message.Message):
    __slots__ = ("file_no",)
    FILE_NO_FIELD_NUMBER: _ClassVar[int]
    file_no: int
    def __init__(self, file_no: _Optional[int] = ...) -> None: ...

class CmdSetTime(_message.Message):
    __slots__ = ("automatic", "manual")
    class Source(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SOURCE_UNSPECIFIED: _ClassVar[CmdSetTime.Source]
        SOURCE_GPS_OR_NTP: _ClassVar[CmdSetTime.Source]
        SOURCE_GPS: _ClassVar[CmdSetTime.Source]
        SOURCE_NTP: _ClassVar[CmdSetTime.Source]
    SOURCE_UNSPECIFIED: CmdSetTime.Source
    SOURCE_GPS_OR_NTP: CmdSetTime.Source
    SOURCE_GPS: CmdSetTime.Source
    SOURCE_NTP: CmdSetTime.Source
    AUTOMATIC_FIELD_NUMBER: _ClassVar[int]
    MANUAL_FIELD_NUMBER: _ClassVar[int]
    automatic: CmdSetTime.Source
    manual: _common_pb2.Time
    def __init__(self, automatic: _Optional[_Union[CmdSetTime.Source, str]] = ..., manual: _Optional[_Union[_common_pb2.Time, _Mapping]] = ...) -> None: ...

class CmdSetTimeResponse(_message.Message):
    __slots__ = ("time", "source")
    class Source(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SOURCE_UNSPECIFIED: _ClassVar[CmdSetTimeResponse.Source]
        SOURCE_MANUAL: _ClassVar[CmdSetTimeResponse.Source]
        SOURCE_GPS: _ClassVar[CmdSetTimeResponse.Source]
        SOURCE_NTP: _ClassVar[CmdSetTimeResponse.Source]
    SOURCE_UNSPECIFIED: CmdSetTimeResponse.Source
    SOURCE_MANUAL: CmdSetTimeResponse.Source
    SOURCE_GPS: CmdSetTimeResponse.Source
    SOURCE_NTP: CmdSetTimeResponse.Source
    TIME_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    time: _common_pb2.Time
    source: CmdSetTimeResponse.Source
    def __init__(self, time: _Optional[_Union[_common_pb2.Time, _Mapping]] = ..., source: _Optional[_Union[CmdSetTimeResponse.Source, str]] = ...) -> None: ...

class CmdGetScreen(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CmdGetScreenResponse(_message.Message):
    __slots__ = ("image",)
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    image: bytes
    def __init__(self, image: _Optional[bytes] = ...) -> None: ...

class CmdPressKey(_message.Message):
    __slots__ = ("key",)
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: Key
    def __init__(self, key: _Optional[_Union[Key, str]] = ...) -> None: ...

class CmdPressKeyResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CmdGetSettings(_message.Message):
    __slots__ = ("keys",)
    KEYS_FIELD_NUMBER: _ClassVar[int]
    keys: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, keys: _Optional[_Iterable[str]] = ...) -> None: ...

class CmdGetSettingsResponse(_message.Message):
    __slots__ = ("settings",)
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    settings: _containers.RepeatedCompositeFieldContainer[Setting]
    def __init__(self, settings: _Optional[_Iterable[_Union[Setting, _Mapping]]] = ...) -> None: ...

class CmdSetSettings(_message.Message):
    __slots__ = ("settings",)
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    settings: _containers.RepeatedCompositeFieldContainer[Setting]
    def __init__(self, settings: _Optional[_Iterable[_Union[Setting, _Mapping]]] = ...) -> None: ...

class CmdSetSettingsResponse(_message.Message):
    __slots__ = ("settings",)
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    settings: _containers.RepeatedCompositeFieldContainer[Setting]
    def __init__(self, settings: _Optional[_Iterable[_Union[Setting, _Mapping]]] = ...) -> None: ...

class CmdReboot(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CmdRebootResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Setting(_message.Message):
    __slots__ = ("key", "int_val", "string_val", "bool_val", "duration_val")
    KEY_FIELD_NUMBER: _ClassVar[int]
    INT_VAL_FIELD_NUMBER: _ClassVar[int]
    STRING_VAL_FIELD_NUMBER: _ClassVar[int]
    BOOL_VAL_FIELD_NUMBER: _ClassVar[int]
    DURATION_VAL_FIELD_NUMBER: _ClassVar[int]
    key: str
    int_val: int
    string_val: str
    bool_val: bool
    duration_val: _duration_pb2.Duration
    def __init__(self, key: _Optional[str] = ..., int_val: _Optional[int] = ..., string_val: _Optional[str] = ..., bool_val: bool = ..., duration_val: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...
