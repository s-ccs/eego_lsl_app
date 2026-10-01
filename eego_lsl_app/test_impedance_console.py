"""Quick gRPC smoke test: stream impedance mode to the console for the cascaded device."""
import sys
import time

import EdigRPC_pb2 as eg
from edi_sdk import DEFAULT_CHANNEL_ADDRESS, EdiSdk, channels_available

address = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CHANNEL_ADDRESS
sdk = EdiSdk(address)
devices = sdk.list_devices()
if not devices:
    raise SystemExit("No amplifier found")

# Always cascade every reported device into one handle, per product requirement.
device = sdk.create_device(devices)
referential = [c for c in channels_available(device) if c.is_referential]
print(f"Streaming impedance for {len(referential)} referential channel(s) from {[d.Serial for d in devices]}")

device.SetMode(eg.AmplifierMode_Impedance, 1000, None)



try:
    while True:
        for frame in device.GetFrame().FrameList:
            if frame.HasField("Impedance"):
                # Per the EDI manual, this only arrives roughly once every 1-2s.
                print("Impedance (ohm):", list(frame.Impedance.Channels)[0:10], "...")
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    device.SetMode(eg.AmplifierMode_Idle,1000, None)
