"""gRPC wrapper for the ANT/eego EdigRPC (EDI 2.0) SDK.

Replaces the old ctypes eego-SDK.dll wrapper (eego_sdk.py). The EdigRPC server
(EdigRPCApp / EDX-Service-TinyUI) must be running and reachable, typically at
localhost:3390.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

import EdigRPC_pb2 as eg
import edi_grpc.device_manager

DEFAULT_CHANNEL_ADDRESS = "localhost:3390"


class EdiSdkError(RuntimeError):
    pass


@dataclass(frozen=True)
class Channel:
    index: int
    name: str
    polarity: int  # eg.ChannelPolarity value
    unit: int  # eg.UnitType value
    reference: str

    @property
    def polarity_name(self) -> str:
        return eg.ChannelPolarity.Name(self.polarity)

    @property
    def is_referential(self) -> bool:
        return self.polarity == eg.ChannelPolarity.Referential

    @property
    def is_bipolar(self) -> bool:
        return self.polarity == eg.ChannelPolarity.Bipolar

    @property
    def is_auxiliary(self) -> bool:
        return self.polarity == eg.ChannelPolarity.Auxiliary


class EdiSdk:
    """Connects to an EdigRPC server and lists/creates the cascaded amplifier device."""

    def __init__(self, channel_address: str = DEFAULT_CHANNEL_ADDRESS) -> None:
        self.channel_address = channel_address
        try:
            self.device_manager = edi_grpc.device_manager.DeviceManager(channel_address)
        except Exception as exc:
            raise EdiSdkError(f"Could not connect to EdigRPC server at {channel_address}: {exc}") from exc

    def __enter__(self) -> "EdiSdk":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        pass

    def list_devices(self):
        """Return every DeviceInfo the server currently reports as attached."""
        try:
            return list(self.device_manager.GetDevices())
        except Exception as exc:
            raise EdiSdkError(f"Could not list devices from {self.channel_address}: {exc}") from exc

    def create_device(self, device_info_list):
        """Create one (possibly cascaded) amplifier handle from ALL given devices.

        Per product requirement, this must always be called with every DeviceInfo
        from list_devices(), never a user-selected subset.
        """
        if not device_info_list:
            raise EdiSdkError("No amplifier devices to create. Call list_devices() first and check for empty results.")
        try:
            return self.device_manager.CreateDevice(device_info_list)
        except Exception as exc:
            raise EdiSdkError(f"Could not create amplifier device: {exc}") from exc


def channels_available(device) -> List[Channel]:
    """Query the channel layout (name/polarity/unit) for a created device."""
    resp = device.GetChannelsAvailable()
    return [
        Channel(index=c.ChannelIndex, name=c.Name, polarity=c.ChannelPolarity, unit=c.UnitType, reference=c.Reference)
        for c in resp.ChannelList
    ]


def sampling_rates_available(device) -> List[float]:
    return list(device.GetSamplingRatesAvailable().RateList)


def nearest_rate(requested: float, available: Sequence[float]) -> float:
    if not available:
        return requested
    return min(available, key=lambda x: abs(float(x) - float(requested)))
