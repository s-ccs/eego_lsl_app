from __future__ import annotations

import EdigRPC_pb2 as eg
from edi_sdk import DEFAULT_CHANNEL_ADDRESS, EdiSdk


address = DEFAULT_CHANNEL_ADDRESS
sampling_rate = 1000

sdk = EdiSdk(address)
devices = sdk.list_devices()
device = sdk.create_device(devices)

device.SetMode(eg.AmplifierMode_Eeg, sampling_rate, None)
resp = device.GetFrame()

frame = resp.FrameList[0]
matrix = frame.Matrix

print(f"address={address}")
print(f"devices={len(devices)}")
print(f"rows={matrix.Rows}, cols={matrix.Cols}, data_len={len(matrix.Data)}, markers={len(frame.TimeMarkers)}")
print(list(matrix.Data[:8]))

device.SetMode(eg.AmplifierMode_Idle, sampling_rate, None)
