from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Prewarn(_message.Message):
    __slots__ = ("src", "transponder_id")
    class Src(_message.Message):
        __slots__ = ("input",)
        INPUT_FIELD_NUMBER: _ClassVar[int]
        input: str
        def __init__(self, input: _Optional[str] = ...) -> None: ...
    SRC_FIELD_NUMBER: _ClassVar[int]
    TRANSPONDER_ID_FIELD_NUMBER: _ClassVar[int]
    src: Prewarn.Src
    transponder_id: str
    def __init__(self, src: _Optional[_Union[Prewarn.Src, _Mapping]] = ..., transponder_id: _Optional[str] = ...) -> None: ...
