"""Quick gRPC smoke test: list devices and print channel/rate info for the cascaded device."""
import sys

from edi_sdk import DEFAULT_CHANNEL_ADDRESS, EdiSdk, channels_available, sampling_rates_available

address = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CHANNEL_ADDRESS
sdk = EdiSdk(address)
devices = sdk.list_devices()
print("Devices:", devices)
if not devices:
    raise SystemExit("No amplifier found")

# Always cascade every reported device into one handle, per product requirement.
device = sdk.create_device(devices)
print("Channels:", channels_available(device))
print("Sampling rates:", sampling_rates_available(device))
