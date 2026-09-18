from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass

import grpc

import EdigRPC_pb2 as eg
from edi_sdk import EdiSdk, EdiSdkError, channels_available, nearest_rate, sampling_rates_available
from lsl_streams import make_marker_outlet, make_outlet


@dataclass
class WorkerConfig:
    channel_address: str
    serial: str
    channel_names: list[str]
    sampling_rate: int = 512
    stream_lsl: bool = True
    # Number of referential channels to stream, capped by what the layout/amplifier(s) report.
    selected_reference_count: int = 64
    # Extra non-referential channels to include (server-reported names), for both EEG and Impedance.
    include_bipolar: bool = False
    include_aux: bool = False
    # Static snapshot of the last known impedance, attached once as EEG outlet metadata only.
    last_impedance: dict[str, float] | None = None


class StreamWorker(threading.Thread):
    def __init__(self, mode: str, config: WorkerConfig, out_queue: queue.Queue):
        super().__init__(daemon=True)
        if mode not in {"impedance", "eeg"}:
            raise ValueError("mode must be 'impedance' or 'eeg'")
        self.mode = mode
        self.config = config
        self.out_queue = out_queue
        self.stop_event = threading.Event()
        self.sdk: EdiSdk | None = None
        self.device = None
        self._close_lock = threading.Lock()
        self._stream_closed = False

    def stop(self) -> None:
        self.stop_event.set()

    def _close_stream_safely(self) -> None:
        with self._close_lock:
            if self._stream_closed or self.device is None:
                return
            try:
                self.device.SetMode(eg.AmplifierMode_Idle, self.config.sampling_rate, None)
            except Exception:
                pass
            finally:
                self._stream_closed = True

    def run(self) -> None:
        try:
            self.sdk = EdiSdk(self.config.channel_address)
            devices = self.sdk.list_devices()
            if not devices:
                raise EdiSdkError(f"No amplifier devices reported by the EdigRPC server at {self.config.channel_address}.")
            # Per product requirement: always cascade every reported device into one handle.
            self.device = self.sdk.create_device(devices)
            self._stream_closed = False
            if self.mode == "impedance":
                self._run_impedance()
            else:
                self._run_eeg()
        except Exception as exc:
            self.out_queue.put({"type": "error", "message": str(exc)})
        finally:
            self._close_stream_safely()
            self.device = None
            self.sdk = None
            self.out_queue.put({"type": "stopped", "mode": self.mode})

    def _selected_channels(self):
        """Return (indices, names, unit_multipliers) for referential channels, plus any
        optionally-enabled Bipolar/Auxiliary channels appended after them.

        Indices are the server's ChannelIndex values, which double as column numbers
        into Matrix/Impedance arrays because Device.SetMode() always activates every
        channel in order (see edi_grpc/device.py).
        """
        channels = channels_available(self.device)
        referential = [c for c in channels if c.is_referential]
        if not referential:
            raise EdiSdkError("The amplifier reported no referential channels.")
        n = max(0, min(len(referential), int(self.config.selected_reference_count or len(self.config.channel_names))))
        referential = referential[:n]
        layout_names = list(self.config.channel_names)[:n]
        names = layout_names if len(layout_names) == len(referential) else [c.name or f"REF{i + 1}" for i, c in enumerate(referential)]
        unit_multipliers = [1_000_000.0 if c.unit == eg.UnitType.Volt else 1.0 for c in referential]
        indices = [c.index for c in referential]

        extra = []
        if self.config.include_bipolar:
            extra.extend(c for c in channels if c.is_bipolar)
        if self.config.include_aux:
            extra.extend(c for c in channels if c.is_auxiliary)
        for c in extra:
            indices.append(c.index)
            names.append(c.name or f"CH{c.index}")
            unit_multipliers.append(1_000_000.0 if c.unit == eg.UnitType.Volt else 1.0)

        return indices, names, unit_multipliers

    def _get_frame(self):
        """Call GetFrame(), tolerating buffer-overflow (sample-loss) errors per the EDI manual.

        The manual states GetFrame() throws if internal buffers overflow -- meaning
        samples were lost -- from polling too slowly, but the stream itself continues
        afterward. Only a gRPC transport error is treated as fatal (raised to stop
        the worker).
        """
        try:
            return self.device.GetFrame()
        except grpc.RpcError as exc:
            raise EdiSdkError(f"gRPC connection error: {exc}") from exc
        except Exception as exc:
            self.out_queue.put({"type": "info", "message": f"GetFrame recovered from an error: {exc}"})
            return None

    def _run_impedance(self) -> None:
        # SamplingRate is ignored by EDI in impedance mode per the manual.
        self.device.SetMode(eg.AmplifierMode_Impedance, self.config.sampling_rate, None)
        indices, electrode_names, _ = self._selected_channels()
        self.out_queue.put({
            "type": "info",
            "message": (
                f"Impedance mode: streaming {len(electrode_names)} channel(s). "
                "The amplifier computes impedance roughly every 1-2s; the app keeps the last "
                "known value between updates, per the EDI manual."
            ),
        })
        outlet = None
        started = False
        try:
            while not self.stop_event.is_set():
                resp = self._get_frame()
                if resp is None:
                    continue
                for frame in resp.FrameList:
                    if not frame.HasField("Impedance"):
                        continue
                    imp = frame.Impedance
                    channel_ohm = list(imp.Channels)
                    if not channel_ohm:
                        continue
                    electrode_ohm = [channel_ohm[i] for i in indices if i < len(channel_ohm)]
                    if len(electrode_ohm) != len(electrode_names):
                        continue
                    ref_ohm = list(imp.Reference)
                    gnd_ohm = list(imp.Ground)
                    ref_names = ["REF"] if len(ref_ohm) <= 1 else [f"REF{i + 1}" for i in range(len(ref_ohm))]
                    gnd_names = ["GND"] if len(gnd_ohm) <= 1 else [f"GND{i + 1}" for i in range(len(gnd_ohm))]
                    names = electrode_names + ref_names + gnd_names
                    raw_ohm = electrode_ohm + ref_ohm + gnd_ohm
                    kohm = [v / 1000.0 for v in raw_ohm]
                    if not started:
                        if self.config.stream_lsl:
                            outlet = make_outlet(
                                "eegosport_impedance", "Impedance", names, 0.0, "kOhm",
                                source_id=f"eegosport_impedance-{self.config.serial}",
                                serials=[self.config.serial],
                            )
                        self.out_queue.put({"type": "started", "mode": "impedance", "channels": names})
                        started = True
                    if outlet:
                        outlet.push_sample(kohm)
                    self.out_queue.put({"type": "impedance", "names": names, "values": kohm, "raw_ohm": raw_ohm})
        finally:
            self._close_stream_safely()

    def _run_eeg(self) -> None:
        available_rates = sampling_rates_available(self.device)
        sampling_rate = nearest_rate(self.config.sampling_rate, available_rates)
        if sampling_rate != self.config.sampling_rate:
            self.out_queue.put({
                "type": "info",
                "message": f"Adjusted EEG sampling rate {self.config.sampling_rate} \u2192 {sampling_rate:g} Hz (nearest supported).",
            })
        self.device.SetMode(eg.AmplifierMode_Eeg, sampling_rate, None)
        indices, names, unit_multipliers = self._selected_channels()
        n_channels = len(names)

        outlet = None
        trigger_outlet = None
        if self.config.stream_lsl:
            outlet = make_outlet(
                "eegosport", "EEG", names, sampling_rate, "microvolts",
                source_id=f"eegosport-{self.config.serial}",
                serials=[self.config.serial],
                last_impedance_kohm=self.config.last_impedance,
            )
            trigger_outlet = make_marker_outlet(
                "eegosport_marker", "Markers", "trigger",
                source_id=f"eegosport_marker-{self.config.serial}",
                serials=[self.config.serial],
            )
        self.out_queue.put({"type": "started", "mode": "eeg", "channels": names})

        # Amplifier-clock-based gap detection: independent of the GetFrame() exception path.
        expected_next_amp_time: float | None = None
        try:
            while not self.stop_event.is_set():
                resp = self._get_frame()
                if resp is None:
                    continue
                for frame in resp.FrameList:
                    # Marker/trigger events now come from the frame directly, not a data channel.
                    for marker in frame.TimeMarkers:
                        if trigger_outlet:
                            trigger_outlet.push_sample([marker.TimeMarkerCode])
                        self.out_queue.put({"type": "trigger", "code": marker.TimeMarkerCode})

                    m = frame.Matrix
                    if not m.Data or m.Cols <= 0 or m.Rows <= 0:
                        continue

                    amp_start = frame.Start.seconds + frame.Start.nanos / 1e9
                    if expected_next_amp_time is not None:
                        gap = amp_start - expected_next_amp_time
                        if gap > 1.5 / sampling_rate:
                            lost = round(gap * sampling_rate)
                            self.out_queue.put({
                                "type": "error",
                                "message": f"Sample loss detected: ~{lost} sample(s) missing (gap {gap * 1000:.1f} ms) based on the amplifier clock.",
                            })
                    expected_next_amp_time = amp_start + m.Rows / sampling_rate

                    rows_uv = []
                    for s in range(m.Rows):
                        base = s * m.Cols
                        row = []
                        for ci, ch_idx in enumerate(indices):
                            if ch_idx >= m.Cols:
                                continue
                            row.append(m.Data[base + ch_idx] * unit_multipliers[ci])
                        if len(row) == n_channels:
                            rows_uv.append(row)
                    if not rows_uv:
                        continue
                    if outlet:
                        # push_chunk's single timestamp is the LAST sample's capture time;
                        # LSL derives the rest backward from the nominal sampling rate.
                        last_sample_time = amp_start + (len(rows_uv) - 1) / sampling_rate
                        outlet.push_chunk(rows_uv, last_sample_time)
                time.sleep(0.005)
        finally:
            self._close_stream_safely()

