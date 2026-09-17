import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DeviceConnection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Usb: _ClassVar[DeviceConnection]
    RIO: _ClassVar[DeviceConnection]
    File: _ClassVar[DeviceConnection]
    gRPC: _ClassVar[DeviceConnection]

class EegDeviceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN: _ClassVar[EegDeviceType]

class UnitType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Volt: _ClassVar[UnitType]
    MicroVolt: _ClassVar[UnitType]

class AmplifierMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AmplifierMode_Disconnect: _ClassVar[AmplifierMode]
    AmplifierMode_PowerOff: _ClassVar[AmplifierMode]
    AmplifierMode_Eeg: _ClassVar[AmplifierMode]
    AmplifierMode_Impedance: _ClassVar[AmplifierMode]
    AmplifierMode_OpenLine: _ClassVar[AmplifierMode]
    AmplifierMode_Idle: _ClassVar[AmplifierMode]

class AmplifierFrameType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AmplifierFrameType_EEG: _ClassVar[AmplifierFrameType]
    AmplifierFrameType_ImpedanceVoltages: _ClassVar[AmplifierFrameType]
    AmplifierFrameType_OpenLine: _ClassVar[AmplifierFrameType]
    AmplifierFrameType_Stimulation: _ClassVar[AmplifierFrameType]

class OutputChannelType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OutputChannelType_TriggerOutput: _ClassVar[OutputChannelType]
    OutputChannelType_Stimulation: _ClassVar[OutputChannelType]

class AmplifierNotifyType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    None: _ClassVar[AmplifierNotifyType]
    ModeChange: _ClassVar[AmplifierNotifyType]
    PowerChange: _ClassVar[AmplifierNotifyType]

class ChannelPolarity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Referential: _ClassVar[ChannelPolarity]
    Bipolar: _ClassVar[ChannelPolarity]
    Auxiliary: _ClassVar[ChannelPolarity]
    Receiver: _ClassVar[ChannelPolarity]
    Transmitter: _ClassVar[ChannelPolarity]
    Disabled: _ClassVar[ChannelPolarity]
Usb: DeviceConnection
RIO: DeviceConnection
File: DeviceConnection
gRPC: DeviceConnection
UNKNOWN: EegDeviceType
Volt: UnitType
MicroVolt: UnitType
AmplifierMode_Disconnect: AmplifierMode
AmplifierMode_PowerOff: AmplifierMode
AmplifierMode_Eeg: AmplifierMode
AmplifierMode_Impedance: AmplifierMode
AmplifierMode_OpenLine: AmplifierMode
AmplifierMode_Idle: AmplifierMode
AmplifierFrameType_EEG: AmplifierFrameType
AmplifierFrameType_ImpedanceVoltages: AmplifierFrameType
AmplifierFrameType_OpenLine: AmplifierFrameType
AmplifierFrameType_Stimulation: AmplifierFrameType
OutputChannelType_TriggerOutput: OutputChannelType
OutputChannelType_Stimulation: OutputChannelType
None: AmplifierNotifyType
ModeChange: AmplifierNotifyType
PowerChange: AmplifierNotifyType
Referential: ChannelPolarity
Bipolar: ChannelPolarity
Auxiliary: ChannelPolarity
Receiver: ChannelPolarity
Transmitter: ChannelPolarity
Disabled: ChannelPolarity

class DoubleList(_message.Message):
    __slots__ = ("Values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    Values: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, Values: _Optional[_Iterable[float]] = ...) -> None: ...

class DeviceInfo(_message.Message):
    __slots__ = ("AmplifierType", "Key", "Serial")
    AMPLIFIERTYPE_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    SERIAL_FIELD_NUMBER: _ClassVar[int]
    AmplifierType: EegDeviceType
    Key: str
    Serial: str
    def __init__(self, AmplifierType: _Optional[_Union[EegDeviceType, str]] = ..., Key: _Optional[str] = ..., Serial: _Optional[str] = ...) -> None: ...

class DeviceParameters(_message.Message):
    __slots__ = ("HasBattery",)
    HASBATTERY_FIELD_NUMBER: _ClassVar[int]
    HasBattery: bool
    def __init__(self, HasBattery: _Optional[bool] = ...) -> None: ...

class PowerInfo(_message.Message):
    __slots__ = ("BatteryLevel", "isBatteryCharging", "isPowerOn")
    BATTERYLEVEL_FIELD_NUMBER: _ClassVar[int]
    ISBATTERYCHARGING_FIELD_NUMBER: _ClassVar[int]
    ISPOWERON_FIELD_NUMBER: _ClassVar[int]
    BatteryLevel: int
    isBatteryCharging: bool
    isPowerOn: bool
    def __init__(self, BatteryLevel: _Optional[int] = ..., isBatteryCharging: _Optional[bool] = ..., isPowerOn: _Optional[bool] = ...) -> None: ...

class ChannelType(_message.Message):
    __slots__ = ("ChannelIndex", "ChannelPolarity", "UnitType", "Name", "Reference")
    CHANNELINDEX_FIELD_NUMBER: _ClassVar[int]
    CHANNELPOLARITY_FIELD_NUMBER: _ClassVar[int]
    UNITTYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_FIELD_NUMBER: _ClassVar[int]
    ChannelIndex: int
    ChannelPolarity: ChannelPolarity
    UnitType: UnitType
    Name: str
    Reference: str
    def __init__(self, ChannelIndex: _Optional[int] = ..., ChannelPolarity: _Optional[_Union[ChannelPolarity, str]] = ..., UnitType: _Optional[_Union[UnitType, str]] = ..., Name: _Optional[str] = ..., Reference: _Optional[str] = ...) -> None: ...

class StreamParams(_message.Message):
    __slots__ = ("ActiveChannels", "Ranges", "SamplingRate", "BufferSize", "DataReadyPercentage")
    class RangesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: float
        def __init__(self, key: _Optional[int] = ..., value: _Optional[float] = ...) -> None: ...
    ACTIVECHANNELS_FIELD_NUMBER: _ClassVar[int]
    RANGES_FIELD_NUMBER: _ClassVar[int]
    SAMPLINGRATE_FIELD_NUMBER: _ClassVar[int]
    BUFFERSIZE_FIELD_NUMBER: _ClassVar[int]
    DATAREADYPERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    ActiveChannels: _containers.RepeatedScalarFieldContainer[int]
    Ranges: _containers.ScalarMap[int, float]
    SamplingRate: float
    BufferSize: int
    DataReadyPercentage: int
    def __init__(self, ActiveChannels: _Optional[_Iterable[int]] = ..., Ranges: _Optional[_Mapping[int, float]] = ..., SamplingRate: _Optional[float] = ..., BufferSize: _Optional[int] = ..., DataReadyPercentage: _Optional[int] = ...) -> None: ...

class DoubleMatrix(_message.Message):
    __slots__ = ("Cols", "Rows", "Data")
    COLS_FIELD_NUMBER: _ClassVar[int]
    ROWS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    Cols: int
    Rows: int
    Data: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, Cols: _Optional[int] = ..., Rows: _Optional[int] = ..., Data: _Optional[_Iterable[float]] = ...) -> None: ...

class Impedances(_message.Message):
    __slots__ = ("Channels", "Reference", "Ground")
    CHANNELS_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_FIELD_NUMBER: _ClassVar[int]
    GROUND_FIELD_NUMBER: _ClassVar[int]
    Channels: _containers.RepeatedScalarFieldContainer[int]
    Reference: _containers.RepeatedScalarFieldContainer[int]
    Ground: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, Channels: _Optional[_Iterable[int]] = ..., Reference: _Optional[_Iterable[int]] = ..., Ground: _Optional[_Iterable[int]] = ...) -> None: ...

class TimeMarker(_message.Message):
    __slots__ = ("Start", "TimeMarkerCode")
    START_FIELD_NUMBER: _ClassVar[int]
    TIMEMARKERCODE_FIELD_NUMBER: _ClassVar[int]
    Start: _timestamp_pb2.Timestamp
    TimeMarkerCode: int
    def __init__(self, Start: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., TimeMarkerCode: _Optional[int] = ...) -> None: ...

class AmplifierFrame(_message.Message):
    __slots__ = ("BufferLoadCapacity", "FrameType", "Impedance", "Start", "StartPcTime", "Matrix", "TimeMarkers")
    BUFFERLOADCAPACITY_FIELD_NUMBER: _ClassVar[int]
    FRAMETYPE_FIELD_NUMBER: _ClassVar[int]
    IMPEDANCE_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    STARTPCTIME_FIELD_NUMBER: _ClassVar[int]
    MATRIX_FIELD_NUMBER: _ClassVar[int]
    TIMEMARKERS_FIELD_NUMBER: _ClassVar[int]
    BufferLoadCapacity: int
    FrameType: AmplifierFrameType
    Impedance: Impedances
    Start: _timestamp_pb2.Timestamp
    StartPcTime: _timestamp_pb2.Timestamp
    Matrix: DoubleMatrix
    TimeMarkers: _containers.RepeatedCompositeFieldContainer[TimeMarker]
    def __init__(self, BufferLoadCapacity: _Optional[int] = ..., FrameType: _Optional[_Union[AmplifierFrameType, str]] = ..., Impedance: _Optional[_Union[Impedances, _Mapping]] = ..., Start: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., StartPcTime: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., Matrix: _Optional[_Union[DoubleMatrix, _Mapping]] = ..., TimeMarkers: _Optional[_Iterable[_Union[TimeMarker, _Mapping]]] = ...) -> None: ...

class OutputTriggerChannelInfo(_message.Message):
    __slots__ = ("ChannelIndex", "ChannelType", "Parameters")
    class ParametersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(self, key: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...
    CHANNELINDEX_FIELD_NUMBER: _ClassVar[int]
    CHANNELTYPE_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    ChannelIndex: int
    ChannelType: OutputChannelType
    Parameters: _containers.ScalarMap[str, float]
    def __init__(self, ChannelIndex: _Optional[int] = ..., ChannelType: _Optional[_Union[OutputChannelType, str]] = ..., Parameters: _Optional[_Mapping[str, float]] = ...) -> None: ...

class Controller_CreateDeviceRequest(_message.Message):
    __slots__ = ("DeviceInfoList",)
    DEVICEINFOLIST_FIELD_NUMBER: _ClassVar[int]
    DeviceInfoList: _containers.RepeatedCompositeFieldContainer[DeviceInfo]
    def __init__(self, DeviceInfoList: _Optional[_Iterable[_Union[DeviceInfo, _Mapping]]] = ...) -> None: ...

class Controller_CreateDeviceResponse(_message.Message):
    __slots__ = ("AmplifierHandle",)
    AMPLIFIERHANDLE_FIELD_NUMBER: _ClassVar[int]
    AmplifierHandle: int
    def __init__(self, AmplifierHandle: _Optional[int] = ...) -> None: ...

class DeviceManager_GetDevicesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DeviceManager_GetDevicesResponse(_message.Message):
    __slots__ = ("DeviceInfoList",)
    DEVICEINFOLIST_FIELD_NUMBER: _ClassVar[int]
    DeviceInfoList: _containers.RepeatedCompositeFieldContainer[DeviceInfo]
    def __init__(self, DeviceInfoList: _Optional[_Iterable[_Union[DeviceInfo, _Mapping]]] = ...) -> None: ...

class DeviceManager_DeviceAttachRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DeviceManager_DeviceAttachResponse(_message.Message):
    __slots__ = ("DeviceInfo",)
    DEVICEINFO_FIELD_NUMBER: _ClassVar[int]
    DeviceInfo: DeviceInfo
    def __init__(self, DeviceInfo: _Optional[_Union[DeviceInfo, _Mapping]] = ...) -> None: ...

class DeviceManager_DeviceDetachRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DeviceManager_DeviceDetachResponse(_message.Message):
    __slots__ = ("DeviceInfo",)
    DEVICEINFO_FIELD_NUMBER: _ClassVar[int]
    DeviceInfo: DeviceInfo
    def __init__(self, DeviceInfo: _Optional[_Union[DeviceInfo, _Mapping]] = ...) -> None: ...

class Amplifier_DisposeRequest(_message.Message):
    __slots__ = ("AmplifierHandle",)
    AMPLIFIERHANDLE_FIELD_NUMBER: _ClassVar[int]
    AmplifierHandle: int
    def __init__(self, AmplifierHandle: _Optional[int] = ...) -> None: ...

class Amplifier_DisposeResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Amplifier_GetDeviceInformationRequest(_message.Message):
    __slots__ = ("AmplifierHandle",)
    AMPLIFIERHANDLE_FIELD_NUMBER: _ClassVar[int]
    AmplifierHandle: int
    def __init__(self, AmplifierHandle: _Optional[int] = ...) -> None: ...

class Amplifier_GetDeviceInformationResponse(_message.Message):
    __slots__ = ("DeviceInformation",)
    DEVICEINFORMATION_FIELD_NUMBER: _ClassVar[int]
    DeviceInformation: _containers.RepeatedCompositeFieldContainer[DeviceInfo]
    def __init__(self, DeviceInformation: _Optional[_Iterable[_Union[DeviceInfo, _Mapping]]] = ...) -> None: ...

class Amplifier_GetDeviceParametersRequest(_message.Message):
    __slots__ = ("AmplifierHandle",)
    AMPLIFIERHANDLE_FIELD_NUMBER: _ClassVar[int]
    AmplifierHandle: int
    def __init__(self, AmplifierHandle: _Optional[int] = ...) -> None: ...

class Amplifier_GetDeviceParametersResponse(_message.Message):
    __slots__ = ("DeviceParameters",)
    DEVICEPARAMETERS_FIELD_NUMBER: _ClassVar[int]
    DeviceParameters: _containers.RepeatedCompositeFieldContainer[DeviceParameters]
    def __init__(self, DeviceParameters: _Optional[_Iterable[_Union[DeviceParameters, _Mapping]]] = ...) -> None: ...

class Amplifier_GetChannelsAvailableRequest(_message.Message):
    __slots__ = ("AmplifierHandle",)
    AMPLIFIERHANDLE_FIELD_NUMBER: _ClassVar[int]
    AmplifierHandle: int
    def __init__(self, AmplifierHandle: _Optional[int] = ...) -> None: ...

class Amplifier_GetChannelsAvailableResponse(_message.Message):
    __slots__ = ("ChannelList",)
    CHANNELLIST_FIELD_NUMBER: _ClassVar[int]
    ChannelList: _containers.RepeatedCompositeFieldContainer[ChannelType]
    def __init__(self, ChannelList: _Optional[_Iterable[_Union[ChannelType, _Mapping]]] = ...) -> None: ...

class Amplifier_GetSamplingRatesAvailableRequest(_message.Message):
    __slots__ = ("AmplifierHandle",)
    AMPLIFIERHANDLE_FIELD_NUMBER: _ClassVar[int]
    AmplifierHandle: int
    def __init__(self, AmplifierHandle: _Optional[int] = ...) -> None: ...

class Amplifier_GetSamplingRatesAvailableResponse(_message.Message):
    __slots__ = ("RateList",)
    RATELIST_FIELD_NUMBER: _ClassVar[int]
    RateList: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, RateList: _Optional[_Iterable[float]] = ...) -> None: ...

class Amplifier_GetModesAvailableRequest(_message.Message):
    __slots__ = ("AmplifierHandle",)
    AMPLIFIERHANDLE_FIELD_NUMBER: _ClassVar[int]
    AmplifierHandle: int
    def __init__(self, AmplifierHandle: _Optional[int] = ...) -> None: ...

class Amplifier_GetModesAvailableResponse(_message.Message):
    __slots__ = ("ModeList",)
    MODELIST_FIELD_NUMBER: _ClassVar[int]
    ModeList: _containers.RepeatedScalarFieldContainer[AmplifierMode]
    def __init__(self, ModeList: _Optional[_Iterable[_Union[AmplifierMode, str]]] = ...) -> None: ...

class Amplifier_GetRangesAvailableRequest(_message.Message):
    __slots__ = ("AmplifierHandle",)
    AMPLIFIERHANDLE_FIELD_NUMBER: _ClassVar[int]
    AmplifierHandle: int
    def __init__(self, AmplifierHandle: _Optional[int] = ...) -> None: ...

class Amplifier_GetRangesAvailableResponse(_message.Message):
    __slots__ = ("RangeMap",)
    class RangeMapEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: DoubleList
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[DoubleList, _Mapping]] = ...) -> None: ...
    RANGEMAP_FIELD_NUMBER: _ClassVar[int]
    RangeMap: _containers.MessageMap[int, DoubleList]
    def __init__(self, RangeMap: _Optional[_Mapping[int, DoubleList]] = ...) -> None: ...

class Amplifier_GetModeRequest(_message.Message):
    __slots__ = ("AmplifierHandle",)
    AMPLIFIERHANDLE_FIELD_NUMBER: _ClassVar[int]
    AmplifierHandle: int
    def __init__(self, AmplifierHandle: _Optional[int] = ...) -> None: ...

class Amplifier_GetModeResponse(_message.Message):
    __slots__ = ("ModeList",)
    MODELIST_FIELD_NUMBER: _ClassVar[int]
    ModeList: _containers.RepeatedScalarFieldContainer[AmplifierMode]
    def __init__(self, ModeList: _Optional[_Iterable[_Union[AmplifierMode, str]]] = ...) -> None: ...

class Amplifier_SetModeRequest(_message.Message):
    __slots__ = ("AmplifierHandle", "Mode", "StreamParams")
    AMPLIFIERHANDLE_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    STREAMPARAMS_FIELD_NUMBER: _ClassVar[int]
    AmplifierHandle: int
    Mode: AmplifierMode
    StreamParams: StreamParams
    def __init__(self, AmplifierHandle: _Optional[int] = ..., Mode: _Optional[_Union[AmplifierMode, str]] = ..., StreamParams: _Optional[_Union[StreamParams, _Mapping]] = ...) -> None: ...

class Amplifier_SetModeResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Amplifier_GetFrameRequest(_message.Message):
    __slots__ = ("AmplifierHandle",)
    AMPLIFIERHANDLE_FIELD_NUMBER: _ClassVar[int]
    AmplifierHandle: int
    def __init__(self, AmplifierHandle: _Optional[int] = ...) -> None: ...

class Amplifier_GetFrameResponse(_message.Message):
    __slots__ = ("FrameList",)
    FRAMELIST_FIELD_NUMBER: _ClassVar[int]
    FrameList: _containers.RepeatedCompositeFieldContainer[AmplifierFrame]
    def __init__(self, FrameList: _Optional[_Iterable[_Union[AmplifierFrame, _Mapping]]] = ...) -> None: ...

class Amplifier_GetPowerRequest(_message.Message):
    __slots__ = ("AmplifierHandle",)
    AMPLIFIERHANDLE_FIELD_NUMBER: _ClassVar[int]
    AmplifierHandle: int
    def __init__(self, AmplifierHandle: _Optional[int] = ...) -> None: ...

class Amplifier_GetPowerResponse(_message.Message):
    __slots__ = ("PowerList",)
    POWERLIST_FIELD_NUMBER: _ClassVar[int]
    PowerList: _containers.RepeatedCompositeFieldContainer[PowerInfo]
    def __init__(self, PowerList: _Optional[_Iterable[_Union[PowerInfo, _Mapping]]] = ...) -> None: ...

class Amplifier_NotifyEventRequest(_message.Message):
    __slots__ = ("AmplifierHandle",)
    AMPLIFIERHANDLE_FIELD_NUMBER: _ClassVar[int]
    AmplifierHandle: int
    def __init__(self, AmplifierHandle: _Optional[int] = ...) -> None: ...

class Amplifier_NotifyEventResponse(_message.Message):
    __slots__ = ("NotifyType",)
    NOTIFYTYPE_FIELD_NUMBER: _ClassVar[int]
    NotifyType: AmplifierNotifyType
    def __init__(self, NotifyType: _Optional[_Union[AmplifierNotifyType, str]] = ...) -> None: ...

class Amplifier_SetOutputTriggerChannelsRequest(_message.Message):
    __slots__ = ("AmplifierHandle", "infos")
    AMPLIFIERHANDLE_FIELD_NUMBER: _ClassVar[int]
    INFOS_FIELD_NUMBER: _ClassVar[int]
    AmplifierHandle: int
    infos: _containers.RepeatedCompositeFieldContainer[OutputTriggerChannelInfo]
    def __init__(self, AmplifierHandle: _Optional[int] = ..., infos: _Optional[_Iterable[_Union[OutputTriggerChannelInfo, _Mapping]]] = ...) -> None: ...

class Amplifier_SetOutputTriggerChannelsResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Amplifier_SetStimulationParametersRequest(_message.Message):
    __slots__ = ("AmplifierHandle", "StimlationParams")
    AMPLIFIERHANDLE_FIELD_NUMBER: _ClassVar[int]
    STIMLATIONPARAMS_FIELD_NUMBER: _ClassVar[int]
    AmplifierHandle: int
    StimlationParams: str
    def __init__(self, AmplifierHandle: _Optional[int] = ..., StimlationParams: _Optional[str] = ...) -> None: ...

class Amplifier_SetStimulationParametersResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Amplifier_StartOutputTriggerRequest(_message.Message):
    __slots__ = ("AmplifierHandle", "Channels")
    AMPLIFIERHANDLE_FIELD_NUMBER: _ClassVar[int]
    CHANNELS_FIELD_NUMBER: _ClassVar[int]
    AmplifierHandle: int
    Channels: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, AmplifierHandle: _Optional[int] = ..., Channels: _Optional[_Iterable[int]] = ...) -> None: ...

class Amplifier_StartOutputTriggerResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Amplifier_StopOutputTriggerRequest(_message.Message):
    __slots__ = ("AmplifierHandle", "Channels")
    AMPLIFIERHANDLE_FIELD_NUMBER: _ClassVar[int]
    CHANNELS_FIELD_NUMBER: _ClassVar[int]
    AmplifierHandle: int
    Channels: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, AmplifierHandle: _Optional[int] = ..., Channels: _Optional[_Iterable[int]] = ...) -> None: ...

class Amplifier_StopOutputTriggerResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Amplifier_StartStimulationRequest(_message.Message):
    __slots__ = ("AmplifierHandle", "Channels")
    AMPLIFIERHANDLE_FIELD_NUMBER: _ClassVar[int]
    CHANNELS_FIELD_NUMBER: _ClassVar[int]
    AmplifierHandle: int
    Channels: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, AmplifierHandle: _Optional[int] = ..., Channels: _Optional[_Iterable[int]] = ...) -> None: ...

class Amplifier_StartStimulationResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Amplifier_StopStimulationRequest(_message.Message):
    __slots__ = ("AmplifierHandle", "Channels")
    AMPLIFIERHANDLE_FIELD_NUMBER: _ClassVar[int]
    CHANNELS_FIELD_NUMBER: _ClassVar[int]
    AmplifierHandle: int
    Channels: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, AmplifierHandle: _Optional[int] = ..., Channels: _Optional[_Iterable[int]] = ...) -> None: ...

class Amplifier_StopStimulationResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetStateRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetStateResponse(_message.Message):
    __slots__ = ("Id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    Id: str
    def __init__(self, Id: _Optional[str] = ...) -> None: ...
