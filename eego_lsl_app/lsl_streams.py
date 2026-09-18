from __future__ import annotations

from typing import Mapping, Sequence


class LslUnavailable(RuntimeError):
    pass


def make_outlet(
    name: str,
    stream_type: str,
    channel_names: Sequence[str],
    sampling_rate: float,
    unit: str,
    source_id: str | None = None,
    serials: Sequence[str] | None = None,
    last_impedance_kohm: Mapping[str, float] | None = None,
):
    try:
        from pylsl import StreamInfo, StreamOutlet
    except Exception as exc:
        raise LslUnavailable("pylsl is not installed. Run: pip install pylsl") from exc

    info = StreamInfo(name, stream_type, len(channel_names), sampling_rate, "float32", source_id or name)
    desc = info.desc()
    channels = desc.append_child("channels")
    for ch_name in channel_names:
        ch = channels.append_child("channel")
        ch.append_child_value("label", str(ch_name))
        ch.append_child_value("unit", unit)
        ch.append_child_value("type", stream_type)
    if serials:
        amp = desc.append_child("amplifier")
        amp.append_child_value("serials", "+".join(serials))
    if last_impedance_kohm:
        # Static snapshot set once at outlet creation -- not resent per sample/package.
        imp = desc.append_child("last_known_impedance_kohm")
        for ch_name, value in last_impedance_kohm.items():
            imp.append_child_value(str(ch_name), f"{value:.1f}")
    return StreamOutlet(info)


def make_marker_outlet(
    name: str,
    stream_type: str = "Markers",
    channel_name: str = "trigger",
    source_id: str | None = None,
    serials: Sequence[str] | None = None,
):
    """Create an irregular-rate LSL marker outlet for trigger/event codes."""
    try:
        from pylsl import StreamInfo, StreamOutlet
    except Exception as exc:
        raise LslUnavailable("pylsl is not installed. Run: pip install pylsl") from exc

    info = StreamInfo(name, stream_type, 1, 0.0, "int32", source_id or name)
    desc = info.desc()
    channels = desc.append_child("channels")
    ch = channels.append_child("channel")
    ch.append_child_value("label", str(channel_name))
    ch.append_child_value("unit", "code")
    ch.append_child_value("type", stream_type)
    if serials:
        amp = desc.append_child("amplifier")
        amp.append_child_value("serials", "+".join(serials))
    return StreamOutlet(info)

