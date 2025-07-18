# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: status.proto
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
    'status.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import common_pb2 as common__pb2
from google.protobuf import duration_pb2 as google_dot_protobuf_dot_duration__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0cstatus.proto\x12\x12raceresult.ubidium\x1a\x0c\x63ommon.proto\x1a\x1egoogle/protobuf/duration.proto\"\xe9\x18\n\x06Status\x12&\n\x04time\x18\x01 \x01(\x0b\x32\x18.raceresult.ubidium.Time\x12\x0f\n\x02id\x18\x02 \x01(\tH\x00\x88\x01\x01\x12\x11\n\x04name\x18\x03 \x01(\tH\x01\x88\x01\x01\x12\x14\n\x07version\x18\x04 \x01(\tH\x02\x88\x01\x01\x12\x14\n\x07\x63ust_no\x18\x05 \x01(\rH\x03\x88\x01\x01\x12\x17\n\npassing_id\x18\x06 \x01(\x04H\x04\x88\x01\x01\x12=\n\npassing_no\x18\x07 \x01(\x0b\x32$.raceresult.ubidium.Status.PassingNoH\x05\x88\x01\x01\x12?\n\x0f\x61\x63tive_internal\x18\x08 \x01(\x0b\x32!.raceresult.ubidium.Status.ActiveH\x06\x88\x01\x01\x12\x38\n\x07passive\x18\t \x01(\x0b\x32\".raceresult.ubidium.Status.PassiveH\x07\x88\x01\x01\x12\x30\n\x03gps\x18\n \x01(\x0b\x32\x1e.raceresult.ubidium.Status.GPSH\x08\x88\x01\x01\x12\x42\n\rbattery_slot1\x18\x0b \x01(\x0b\x32&.raceresult.ubidium.Status.BatterySlotH\t\x88\x01\x01\x12\x42\n\rbattery_slot2\x18\x0c \x01(\x0b\x32&.raceresult.ubidium.Status.BatterySlotH\n\x88\x01\x01\x12\x18\n\x0btemperature\x18\r \x01(\x01H\x0b\x88\x01\x01\x12\x34\n\x05power\x18\x0e \x01(\x0b\x32 .raceresult.ubidium.Status.PowerH\x0c\x88\x01\x01\x12\x36\n\x06update\x18\x0f \x01(\x0b\x32!.raceresult.ubidium.Status.UpdateH\r\x88\x01\x01\x1a?\n\tPassingNo\x12\x11\n\x04\x66ile\x18\x01 \x01(\rH\x00\x88\x01\x01\x12\x0f\n\x02no\x18\x02 \x01(\rH\x01\x88\x01\x01\x42\x07\n\x05_fileB\x05\n\x03_no\x1a\xb3\x08\n\x06\x41\x63tive\x12\x35\n\x06status\x18\x03 \x01(\x0e\x32 .raceresult.ubidium.ActiveStatusH\x00\x88\x01\x01\x12\x36\n\x04self\x18\x01 \x01(\x0b\x32(.raceresult.ubidium.Status.Active.Beacon\x12=\n\x06others\x18\x02 \x03(\x0b\x32-.raceresult.ubidium.Status.Active.OthersEntry\x1a\xb2\x05\n\x06\x42\x65\x61\x63on\x12\x14\n\x07\x63hannel\x18\x02 \x01(\rH\x00\x88\x01\x01\x12\x14\n\x07loop_id\x18\x03 \x01(\rH\x01\x88\x01\x01\x12\x12\n\x05power\x18\x04 \x01(\rH\x02\x88\x01\x01\x12\x18\n\x0bloop_status\x18\x05 \x01(\rH\x03\x88\x01\x01\x12\x30\n\tlast_seen\x18\x06 \x01(\x0b\x32\x18.raceresult.ubidium.TimeH\x04\x88\x01\x01\x12\x11\n\x04mode\x18\x07 \x01(\rH\x05\x88\x01\x01\x12\x16\n\tpower_con\x18\x08 \x01(\rH\x06\x88\x01\x01\x12\x19\n\x0cpower_status\x18\t \x01(\rH\x07\x88\x01\x01\x12\x19\n\x0c\x62\x65\x61\x63on_index\x18\n \x01(\rH\x08\x88\x01\x01\x12\x19\n\x0c\x63h_noise_avg\x18\x0b \x01(\rH\t\x88\x01\x01\x12\x16\n\ttrans_lqi\x18\x0c \x01(\rH\n\x88\x01\x01\x12 \n\x13trans_energy_detect\x18\r \x01(\rH\x0b\x88\x01\x01\x12\x17\n\nbeacon_lqi\x18\x0e \x01(\rH\x0c\x88\x01\x01\x12!\n\x14\x62\x65\x61\x63on_energy_detect\x18\x0f \x01(\rH\r\x88\x01\x01\x12\x15\n\x08mode_box\x18\x13 \x01(\rH\x0e\x88\x01\x01\x12\x18\n\x0btemperature\x18\x14 \x01(\x05H\x0f\x88\x01\x01\x42\n\n\x08_channelB\n\n\x08_loop_idB\x08\n\x06_powerB\x0e\n\x0c_loop_statusB\x0c\n\n_last_seenB\x07\n\x05_modeB\x0c\n\n_power_conB\x0f\n\r_power_statusB\x0f\n\r_beacon_indexB\x0f\n\r_ch_noise_avgB\x0c\n\n_trans_lqiB\x16\n\x14_trans_energy_detectB\r\n\x0b_beacon_lqiB\x17\n\x15_beacon_energy_detectB\x0b\n\t_mode_boxB\x0e\n\x0c_temperatureJ\x04\x08\x01\x10\x02\x1aZ\n\x0eOptionalBeacon\x12=\n\x06\x62\x65\x61\x63on\x18\x01 \x01(\x0b\x32(.raceresult.ubidium.Status.Active.BeaconH\x00\x88\x01\x01\x42\t\n\x07_beacon\x1a_\n\x0bOthersEntry\x12\x0b\n\x03key\x18\x01 \x01(\r\x12?\n\x05value\x18\x02 \x01(\x0b\x32\x30.raceresult.ubidium.Status.Active.OptionalBeacon:\x02\x38\x01\x42\t\n\x07_status\x1a\xcb\x04\n\x07Passive\x12\x42\n\x08\x65lements\x18\x02 \x03(\x0b\x32\x30.raceresult.ubidium.Status.Passive.ElementsEntry\x12\x42\n\x10transponder_type\x18\x03 \x01(\x0e\x32#.raceresult.ubidium.TransponderTypeH\x00\x88\x01\x01\x12\x34\n\x05power\x18\x04 \x01(\x0e\x32 .raceresult.ubidium.PassivePowerH\x01\x88\x01\x01\x1a\x96\x01\n\x07\x45lement\x12\x15\n\x08position\x18\x02 \x01(\rH\x00\x88\x01\x01\x12\x16\n\tstring_no\x18\x03 \x01(\rH\x01\x88\x01\x01\x12\x36\n\x06status\x18\x04 \x01(\x0e\x32!.raceresult.ubidium.ElementStatusH\x02\x88\x01\x01\x42\x0b\n\t_positionB\x0c\n\n_string_noB\t\n\x07_status\x1a_\n\x0fOptionalElement\x12@\n\x07\x65lement\x18\x01 \x01(\x0b\x32*.raceresult.ubidium.Status.Passive.ElementH\x00\x88\x01\x01\x42\n\n\x08_element\x1a\x63\n\rElementsEntry\x12\x0b\n\x03key\x18\x01 \x01(\r\x12\x41\n\x05value\x18\x02 \x01(\x0b\x32\x32.raceresult.ubidium.Status.Passive.OptionalElement:\x02\x38\x01\x42\x13\n\x11_transponder_typeB\x08\n\x06_powerJ\x04\x08\x01\x10\x02\x1aQ\n\x03GPS\x12\x10\n\x06no_fix\x18\x01 \x01(\x08H\x00\x12\x30\n\x08location\x18\x02 \x01(\x0b\x32\x1c.raceresult.ubidium.LocationH\x00\x42\x06\n\x04\x64\x61ta\x1a\xac\x01\n\x0b\x42\x61tteryData\x12\x12\n\x05level\x18\x01 \x01(\rH\x00\x88\x01\x01\x12\x31\n\tremaining\x18\x02 \x01(\x0b\x32\x19.google.protobuf.DurationH\x01\x88\x01\x01\x12\x34\n\x05state\x18\x03 \x01(\x0e\x32 .raceresult.ubidium.BatteryStateH\x02\x88\x01\x01\x42\x08\n\x06_levelB\x0c\n\n_remainingB\x08\n\x06_state\x1a\x61\n\x0b\x42\x61tterySlot\x12\x0f\n\x05\x65mpty\x18\x01 \x01(\x08H\x00\x12\x39\n\x07\x62\x61ttery\x18\x02 \x01(\x0b\x32&.raceresult.ubidium.Status.BatteryDataH\x00\x42\x06\n\x04\x64\x61ta\x1aH\n\x05Power\x12\x34\n\x06source\x18\x01 \x01(\x0e\x32\x1f.raceresult.ubidium.PowerSourceH\x00\x88\x01\x01\x42\t\n\x07_source\x1a\xa6\x01\n\x06Update\x12\x16\n\tinstalled\x18\x01 \x01(\x08H\x00\x88\x01\x01\x12\x39\n\x08severity\x18\x02 \x01(\x0e\x32\".raceresult.ubidium.UpdateSeverityH\x01\x88\x01\x01\x12\x1b\n\x0eupdate_version\x18\x03 \x01(\tH\x02\x88\x01\x01\x42\x0c\n\n_installedB\x0b\n\t_severityB\x11\n\x0f_update_versionB\x05\n\x03_idB\x07\n\x05_nameB\n\n\x08_versionB\n\n\x08_cust_noB\r\n\x0b_passing_idB\r\n\x0b_passing_noB\x12\n\x10_active_internalB\n\n\x08_passiveB\x06\n\x04_gpsB\x10\n\x0e_battery_slot1B\x10\n\x0e_battery_slot2B\x0e\n\x0c_temperatureB\x08\n\x06_powerB\t\n\x07_update\"D\n\x05Shout\x12*\n\x06status\x18\x01 \x01(\x0b\x32\x1a.raceresult.ubidium.Status\x12\x0f\n\x07\x61\x64\x64ress\x18\x02 \x01(\t*\x80\x01\n\x0c\x42\x61tteryState\x12\x1d\n\x19\x42\x41TTERY_STATE_UNSPECIFIED\x10\x00\x12\x1d\n\x19\x42\x41TTERY_STATE_DISCHARGING\x10\x01\x12\x1a\n\x16\x42\x41TTERY_STATE_CHARGING\x10\x02\x12\x16\n\x12\x42\x41TTERY_STATE_IDLE\x10\x03*\x9a\x01\n\x0bPowerSource\x12\x1c\n\x18POWER_SOURCE_UNSPECIFIED\x10\x00\x12\x15\n\x11POWER_SOURCE_NONE\x10\x01\x12\x13\n\x0fPOWER_SOURCE_AC\x10\x02\x12\x13\n\x0fPOWER_SOURCE_DC\x10\x03\x12\x16\n\x12POWER_SOURCE_USBPD\x10\x04\x12\x14\n\x10POWER_SOURCE_POE\x10\x05*\x93\x01\n\rElementStatus\x12\x1a\n\x16\x45LEMENT_STATUS_UNKNOWN\x10\x00\x12\x15\n\x11\x45LEMENT_STATUS_OK\x10\x01\x12\x16\n\x12\x45LEMENT_STATUS_BAD\x10\x02\x12\x17\n\x13\x45LEMENT_STATUS_MUTE\x10\x03\x12\x1e\n\x1a\x45LEMENT_STATUS_UNAVAILABLE\x10\x04*\x9a\x01\n\x0c\x41\x63tiveStatus\x12\x19\n\x15\x41\x43TIVE_STATUS_UNKNOWN\x10\x00\x12\x1e\n\x1a\x41\x43TIVE_STATUS_INITIALIZING\x10\x01\x12\x19\n\x15\x41\x43TIVE_STATUS_RUNNING\x10\x02\x12\x1a\n\x16\x41\x43TIVE_STATUS_UPDATING\x10\x03\x12\x18\n\x14\x41\x43TIVE_STATUS_FAILED\x10\x04*g\n\x0eUpdateSeverity\x12\x1b\n\x17UPDATE_SEVERITY_UNKNOWN\x10\x00\x12\x1a\n\x16UPDATE_SEVERITY_NORMAL\x10\x01\x12\x1c\n\x18UPDATE_SEVERITY_CRITICAL\x10\x02*\xa0\x01\n\x0fTransponderType\x12\x1c\n\x18TRANSPONDER_TYPE_UNKNOWN\x10\x00\x12\x18\n\x14TRANSPONDER_TYPE_BIB\x10\x01\x12\x1e\n\x1aTRANSPONDER_TYPE_TRIATHLON\x10\x02\x12\x1a\n\x16TRANSPONDER_TYPE_HUTAG\x10\x03\x12\x19\n\x15TRANSPONDER_TYPE_SHOE\x10\x04*\xa8\x01\n\x0cPassivePower\x12\x19\n\x15PASSIVE_POWER_UNKNOWN\x10\x00\x12\x19\n\x15PASSIVE_POWER_MINIMUM\x10\x01\x12\x15\n\x11PASSIVE_POWER_LOW\x10\x02\x12\x18\n\x14PASSIVE_POWER_MEDIUM\x10\x03\x12\x16\n\x12PASSIVE_POWER_AUTO\x10\x04\x12\x19\n\x15PASSIVE_POWER_MAXIMUM\x10\x05\x42)Z\x12raceresult/ubidium\xaa\x02\x12RaceResult.Ubidiumb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'status_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'Z\022raceresult/ubidium\252\002\022RaceResult.Ubidium'
  _globals['_STATUS_ACTIVE_OTHERSENTRY']._loaded_options = None
  _globals['_STATUS_ACTIVE_OTHERSENTRY']._serialized_options = b'8\001'
  _globals['_STATUS_PASSIVE_ELEMENTSENTRY']._loaded_options = None
  _globals['_STATUS_PASSIVE_ELEMENTSENTRY']._serialized_options = b'8\001'
  _globals['_BATTERYSTATE']._serialized_start=3333
  _globals['_BATTERYSTATE']._serialized_end=3461
  _globals['_POWERSOURCE']._serialized_start=3464
  _globals['_POWERSOURCE']._serialized_end=3618
  _globals['_ELEMENTSTATUS']._serialized_start=3621
  _globals['_ELEMENTSTATUS']._serialized_end=3768
  _globals['_ACTIVESTATUS']._serialized_start=3771
  _globals['_ACTIVESTATUS']._serialized_end=3925
  _globals['_UPDATESEVERITY']._serialized_start=3927
  _globals['_UPDATESEVERITY']._serialized_end=4030
  _globals['_TRANSPONDERTYPE']._serialized_start=4033
  _globals['_TRANSPONDERTYPE']._serialized_end=4193
  _globals['_PASSIVEPOWER']._serialized_start=4196
  _globals['_PASSIVEPOWER']._serialized_end=4364
  _globals['_STATUS']._serialized_start=83
  _globals['_STATUS']._serialized_end=3260
  _globals['_STATUS_PASSINGNO']._serialized_start=746
  _globals['_STATUS_PASSINGNO']._serialized_end=809
  _globals['_STATUS_ACTIVE']._serialized_start=812
  _globals['_STATUS_ACTIVE']._serialized_end=1887
  _globals['_STATUS_ACTIVE_BEACON']._serialized_start=997
  _globals['_STATUS_ACTIVE_BEACON']._serialized_end=1687
  _globals['_STATUS_ACTIVE_OPTIONALBEACON']._serialized_start=1689
  _globals['_STATUS_ACTIVE_OPTIONALBEACON']._serialized_end=1779
  _globals['_STATUS_ACTIVE_OTHERSENTRY']._serialized_start=1781
  _globals['_STATUS_ACTIVE_OTHERSENTRY']._serialized_end=1876
  _globals['_STATUS_PASSIVE']._serialized_start=1890
  _globals['_STATUS_PASSIVE']._serialized_end=2477
  _globals['_STATUS_PASSIVE_ELEMENT']._serialized_start=2092
  _globals['_STATUS_PASSIVE_ELEMENT']._serialized_end=2242
  _globals['_STATUS_PASSIVE_OPTIONALELEMENT']._serialized_start=2244
  _globals['_STATUS_PASSIVE_OPTIONALELEMENT']._serialized_end=2339
  _globals['_STATUS_PASSIVE_ELEMENTSENTRY']._serialized_start=2341
  _globals['_STATUS_PASSIVE_ELEMENTSENTRY']._serialized_end=2440
  _globals['_STATUS_GPS']._serialized_start=2479
  _globals['_STATUS_GPS']._serialized_end=2560
  _globals['_STATUS_BATTERYDATA']._serialized_start=2563
  _globals['_STATUS_BATTERYDATA']._serialized_end=2735
  _globals['_STATUS_BATTERYSLOT']._serialized_start=2737
  _globals['_STATUS_BATTERYSLOT']._serialized_end=2834
  _globals['_STATUS_POWER']._serialized_start=2836
  _globals['_STATUS_POWER']._serialized_end=2908
  _globals['_STATUS_UPDATE']._serialized_start=2911
  _globals['_STATUS_UPDATE']._serialized_end=3077
  _globals['_SHOUT']._serialized_start=3262
  _globals['_SHOUT']._serialized_end=3330
# @@protoc_insertion_point(module_scope)
