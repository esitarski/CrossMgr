from . import common_pb2 as _common_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BatteryState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BATTERY_STATE_UNSPECIFIED: _ClassVar[BatteryState]
    BATTERY_STATE_DISCHARGING: _ClassVar[BatteryState]
    BATTERY_STATE_CHARGING: _ClassVar[BatteryState]
    BATTERY_STATE_IDLE: _ClassVar[BatteryState]

class PowerSource(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    POWER_SOURCE_UNSPECIFIED: _ClassVar[PowerSource]
    POWER_SOURCE_NONE: _ClassVar[PowerSource]
    POWER_SOURCE_AC: _ClassVar[PowerSource]
    POWER_SOURCE_DC: _ClassVar[PowerSource]
    POWER_SOURCE_USBPD: _ClassVar[PowerSource]
    POWER_SOURCE_POE: _ClassVar[PowerSource]

class ElementStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ELEMENT_STATUS_UNKNOWN: _ClassVar[ElementStatus]
    ELEMENT_STATUS_OK: _ClassVar[ElementStatus]
    ELEMENT_STATUS_BAD: _ClassVar[ElementStatus]
    ELEMENT_STATUS_MUTE: _ClassVar[ElementStatus]
    ELEMENT_STATUS_UNAVAILABLE: _ClassVar[ElementStatus]

class ActiveStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ACTIVE_STATUS_UNKNOWN: _ClassVar[ActiveStatus]
    ACTIVE_STATUS_INITIALIZING: _ClassVar[ActiveStatus]
    ACTIVE_STATUS_RUNNING: _ClassVar[ActiveStatus]
    ACTIVE_STATUS_UPDATING: _ClassVar[ActiveStatus]
    ACTIVE_STATUS_FAILED: _ClassVar[ActiveStatus]

class UpdateSeverity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UPDATE_SEVERITY_UNKNOWN: _ClassVar[UpdateSeverity]
    UPDATE_SEVERITY_NORMAL: _ClassVar[UpdateSeverity]
    UPDATE_SEVERITY_CRITICAL: _ClassVar[UpdateSeverity]

class TransponderType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TRANSPONDER_TYPE_UNKNOWN: _ClassVar[TransponderType]
    TRANSPONDER_TYPE_BIB: _ClassVar[TransponderType]
    TRANSPONDER_TYPE_TRIATHLON: _ClassVar[TransponderType]
    TRANSPONDER_TYPE_HUTAG: _ClassVar[TransponderType]
    TRANSPONDER_TYPE_SHOE: _ClassVar[TransponderType]

class PassivePower(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PASSIVE_POWER_UNKNOWN: _ClassVar[PassivePower]
    PASSIVE_POWER_MINIMUM: _ClassVar[PassivePower]
    PASSIVE_POWER_LOW: _ClassVar[PassivePower]
    PASSIVE_POWER_MEDIUM: _ClassVar[PassivePower]
    PASSIVE_POWER_AUTO: _ClassVar[PassivePower]
    PASSIVE_POWER_MAXIMUM: _ClassVar[PassivePower]
BATTERY_STATE_UNSPECIFIED: BatteryState
BATTERY_STATE_DISCHARGING: BatteryState
BATTERY_STATE_CHARGING: BatteryState
BATTERY_STATE_IDLE: BatteryState
POWER_SOURCE_UNSPECIFIED: PowerSource
POWER_SOURCE_NONE: PowerSource
POWER_SOURCE_AC: PowerSource
POWER_SOURCE_DC: PowerSource
POWER_SOURCE_USBPD: PowerSource
POWER_SOURCE_POE: PowerSource
ELEMENT_STATUS_UNKNOWN: ElementStatus
ELEMENT_STATUS_OK: ElementStatus
ELEMENT_STATUS_BAD: ElementStatus
ELEMENT_STATUS_MUTE: ElementStatus
ELEMENT_STATUS_UNAVAILABLE: ElementStatus
ACTIVE_STATUS_UNKNOWN: ActiveStatus
ACTIVE_STATUS_INITIALIZING: ActiveStatus
ACTIVE_STATUS_RUNNING: ActiveStatus
ACTIVE_STATUS_UPDATING: ActiveStatus
ACTIVE_STATUS_FAILED: ActiveStatus
UPDATE_SEVERITY_UNKNOWN: UpdateSeverity
UPDATE_SEVERITY_NORMAL: UpdateSeverity
UPDATE_SEVERITY_CRITICAL: UpdateSeverity
TRANSPONDER_TYPE_UNKNOWN: TransponderType
TRANSPONDER_TYPE_BIB: TransponderType
TRANSPONDER_TYPE_TRIATHLON: TransponderType
TRANSPONDER_TYPE_HUTAG: TransponderType
TRANSPONDER_TYPE_SHOE: TransponderType
PASSIVE_POWER_UNKNOWN: PassivePower
PASSIVE_POWER_MINIMUM: PassivePower
PASSIVE_POWER_LOW: PassivePower
PASSIVE_POWER_MEDIUM: PassivePower
PASSIVE_POWER_AUTO: PassivePower
PASSIVE_POWER_MAXIMUM: PassivePower

class Status(_message.Message):
    __slots__ = ("time", "id", "name", "version", "cust_no", "passing_id", "passing_no", "active_internal", "passive", "gps", "battery_slot1", "battery_slot2", "temperature", "power", "update")
    class PassingNo(_message.Message):
        __slots__ = ("file", "no")
        FILE_FIELD_NUMBER: _ClassVar[int]
        NO_FIELD_NUMBER: _ClassVar[int]
        file: int
        no: int
        def __init__(self, file: _Optional[int] = ..., no: _Optional[int] = ...) -> None: ...
    class Active(_message.Message):
        __slots__ = ("status", "self", "others")
        class Beacon(_message.Message):
            __slots__ = ("channel", "loop_id", "power", "loop_status", "last_seen", "mode", "power_con", "power_status", "beacon_index", "ch_noise_avg", "trans_lqi", "trans_energy_detect", "beacon_lqi", "beacon_energy_detect", "mode_box", "temperature")
            CHANNEL_FIELD_NUMBER: _ClassVar[int]
            LOOP_ID_FIELD_NUMBER: _ClassVar[int]
            POWER_FIELD_NUMBER: _ClassVar[int]
            LOOP_STATUS_FIELD_NUMBER: _ClassVar[int]
            LAST_SEEN_FIELD_NUMBER: _ClassVar[int]
            MODE_FIELD_NUMBER: _ClassVar[int]
            POWER_CON_FIELD_NUMBER: _ClassVar[int]
            POWER_STATUS_FIELD_NUMBER: _ClassVar[int]
            BEACON_INDEX_FIELD_NUMBER: _ClassVar[int]
            CH_NOISE_AVG_FIELD_NUMBER: _ClassVar[int]
            TRANS_LQI_FIELD_NUMBER: _ClassVar[int]
            TRANS_ENERGY_DETECT_FIELD_NUMBER: _ClassVar[int]
            BEACON_LQI_FIELD_NUMBER: _ClassVar[int]
            BEACON_ENERGY_DETECT_FIELD_NUMBER: _ClassVar[int]
            MODE_BOX_FIELD_NUMBER: _ClassVar[int]
            TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
            channel: int
            loop_id: int
            power: int
            loop_status: int
            last_seen: _common_pb2.Time
            mode: int
            power_con: int
            power_status: int
            beacon_index: int
            ch_noise_avg: int
            trans_lqi: int
            trans_energy_detect: int
            beacon_lqi: int
            beacon_energy_detect: int
            mode_box: int
            temperature: int
            def __init__(self, channel: _Optional[int] = ..., loop_id: _Optional[int] = ..., power: _Optional[int] = ..., loop_status: _Optional[int] = ..., last_seen: _Optional[_Union[_common_pb2.Time, _Mapping]] = ..., mode: _Optional[int] = ..., power_con: _Optional[int] = ..., power_status: _Optional[int] = ..., beacon_index: _Optional[int] = ..., ch_noise_avg: _Optional[int] = ..., trans_lqi: _Optional[int] = ..., trans_energy_detect: _Optional[int] = ..., beacon_lqi: _Optional[int] = ..., beacon_energy_detect: _Optional[int] = ..., mode_box: _Optional[int] = ..., temperature: _Optional[int] = ...) -> None: ...
        class OptionalBeacon(_message.Message):
            __slots__ = ("beacon",)
            BEACON_FIELD_NUMBER: _ClassVar[int]
            beacon: Status.Active.Beacon
            def __init__(self, beacon: _Optional[_Union[Status.Active.Beacon, _Mapping]] = ...) -> None: ...
        class OthersEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: int
            value: Status.Active.OptionalBeacon
            def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[Status.Active.OptionalBeacon, _Mapping]] = ...) -> None: ...
        STATUS_FIELD_NUMBER: _ClassVar[int]
        SELF_FIELD_NUMBER: _ClassVar[int]
        OTHERS_FIELD_NUMBER: _ClassVar[int]
        status: ActiveStatus
        self: Status.Active.Beacon
        others: _containers.MessageMap[int, Status.Active.OptionalBeacon]
        def __init__(self_, status: _Optional[_Union[ActiveStatus, str]] = ..., self: _Optional[_Union[Status.Active.Beacon, _Mapping]] = ..., others: _Optional[_Mapping[int, Status.Active.OptionalBeacon]] = ...) -> None: ...
    class Passive(_message.Message):
        __slots__ = ("elements", "transponder_type", "power")
        class Element(_message.Message):
            __slots__ = ("position", "string_no", "status")
            POSITION_FIELD_NUMBER: _ClassVar[int]
            STRING_NO_FIELD_NUMBER: _ClassVar[int]
            STATUS_FIELD_NUMBER: _ClassVar[int]
            position: int
            string_no: int
            status: ElementStatus
            def __init__(self, position: _Optional[int] = ..., string_no: _Optional[int] = ..., status: _Optional[_Union[ElementStatus, str]] = ...) -> None: ...
        class OptionalElement(_message.Message):
            __slots__ = ("element",)
            ELEMENT_FIELD_NUMBER: _ClassVar[int]
            element: Status.Passive.Element
            def __init__(self, element: _Optional[_Union[Status.Passive.Element, _Mapping]] = ...) -> None: ...
        class ElementsEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: int
            value: Status.Passive.OptionalElement
            def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[Status.Passive.OptionalElement, _Mapping]] = ...) -> None: ...
        ELEMENTS_FIELD_NUMBER: _ClassVar[int]
        TRANSPONDER_TYPE_FIELD_NUMBER: _ClassVar[int]
        POWER_FIELD_NUMBER: _ClassVar[int]
        elements: _containers.MessageMap[int, Status.Passive.OptionalElement]
        transponder_type: TransponderType
        power: PassivePower
        def __init__(self, elements: _Optional[_Mapping[int, Status.Passive.OptionalElement]] = ..., transponder_type: _Optional[_Union[TransponderType, str]] = ..., power: _Optional[_Union[PassivePower, str]] = ...) -> None: ...
    class GPS(_message.Message):
        __slots__ = ("no_fix", "location")
        NO_FIX_FIELD_NUMBER: _ClassVar[int]
        LOCATION_FIELD_NUMBER: _ClassVar[int]
        no_fix: bool
        location: _common_pb2.Location
        def __init__(self, no_fix: bool = ..., location: _Optional[_Union[_common_pb2.Location, _Mapping]] = ...) -> None: ...
    class BatteryData(_message.Message):
        __slots__ = ("level", "remaining", "state")
        LEVEL_FIELD_NUMBER: _ClassVar[int]
        REMAINING_FIELD_NUMBER: _ClassVar[int]
        STATE_FIELD_NUMBER: _ClassVar[int]
        level: int
        remaining: _duration_pb2.Duration
        state: BatteryState
        def __init__(self, level: _Optional[int] = ..., remaining: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., state: _Optional[_Union[BatteryState, str]] = ...) -> None: ...
    class BatterySlot(_message.Message):
        __slots__ = ("empty", "battery")
        EMPTY_FIELD_NUMBER: _ClassVar[int]
        BATTERY_FIELD_NUMBER: _ClassVar[int]
        empty: bool
        battery: Status.BatteryData
        def __init__(self, empty: bool = ..., battery: _Optional[_Union[Status.BatteryData, _Mapping]] = ...) -> None: ...
    class Power(_message.Message):
        __slots__ = ("source",)
        SOURCE_FIELD_NUMBER: _ClassVar[int]
        source: PowerSource
        def __init__(self, source: _Optional[_Union[PowerSource, str]] = ...) -> None: ...
    class Update(_message.Message):
        __slots__ = ("installed", "severity", "update_version")
        INSTALLED_FIELD_NUMBER: _ClassVar[int]
        SEVERITY_FIELD_NUMBER: _ClassVar[int]
        UPDATE_VERSION_FIELD_NUMBER: _ClassVar[int]
        installed: bool
        severity: UpdateSeverity
        update_version: str
        def __init__(self, installed: bool = ..., severity: _Optional[_Union[UpdateSeverity, str]] = ..., update_version: _Optional[str] = ...) -> None: ...
    TIME_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    CUST_NO_FIELD_NUMBER: _ClassVar[int]
    PASSING_ID_FIELD_NUMBER: _ClassVar[int]
    PASSING_NO_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_INTERNAL_FIELD_NUMBER: _ClassVar[int]
    PASSIVE_FIELD_NUMBER: _ClassVar[int]
    GPS_FIELD_NUMBER: _ClassVar[int]
    BATTERY_SLOT1_FIELD_NUMBER: _ClassVar[int]
    BATTERY_SLOT2_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    POWER_FIELD_NUMBER: _ClassVar[int]
    UPDATE_FIELD_NUMBER: _ClassVar[int]
    time: _common_pb2.Time
    id: str
    name: str
    version: str
    cust_no: int
    passing_id: int
    passing_no: Status.PassingNo
    active_internal: Status.Active
    passive: Status.Passive
    gps: Status.GPS
    battery_slot1: Status.BatterySlot
    battery_slot2: Status.BatterySlot
    temperature: float
    power: Status.Power
    update: Status.Update
    def __init__(self, time: _Optional[_Union[_common_pb2.Time, _Mapping]] = ..., id: _Optional[str] = ..., name: _Optional[str] = ..., version: _Optional[str] = ..., cust_no: _Optional[int] = ..., passing_id: _Optional[int] = ..., passing_no: _Optional[_Union[Status.PassingNo, _Mapping]] = ..., active_internal: _Optional[_Union[Status.Active, _Mapping]] = ..., passive: _Optional[_Union[Status.Passive, _Mapping]] = ..., gps: _Optional[_Union[Status.GPS, _Mapping]] = ..., battery_slot1: _Optional[_Union[Status.BatterySlot, _Mapping]] = ..., battery_slot2: _Optional[_Union[Status.BatterySlot, _Mapping]] = ..., temperature: _Optional[float] = ..., power: _Optional[_Union[Status.Power, _Mapping]] = ..., update: _Optional[_Union[Status.Update, _Mapping]] = ...) -> None: ...

class Shout(_message.Message):
    __slots__ = ("status", "address")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    status: Status
    address: str
    def __init__(self, status: _Optional[_Union[Status, _Mapping]] = ..., address: _Optional[str] = ...) -> None: ...
