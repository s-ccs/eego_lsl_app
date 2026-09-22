"""Command-line presets for the eego LSL app.

Parses a small set of startup options so recurring settings can be preset
without touching the GUI:

    uv run app.py --aux --no-bip --layout capfiles/64ch.txt --sampling-rate 500

Only these four settings are supported; everything else stays in the GUI.
A value of ``None`` means "not preset", so the GUI keeps its own default.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CliPresets:
    """Preset values taken from the command line."""

    include_aux: bool | None = None
    include_bipolar: bool | None = None
    layout_path: Path | None = None
    sampling_rate: int | None = None


def parse_presets(argv: list[str] | None = None) -> CliPresets:
    """Parse the preset options from ``argv`` (defaults to ``sys.argv[1:]``)."""
    parser = argparse.ArgumentParser(
        prog="app.py",
        description="eego LSL app (impedance + EEG) with optional CLI presets.",
    )
    parser.add_argument(
        "--aux",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Include Aux channels: --aux.",
    )
    parser.add_argument(
        "--bip",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Include Bipolar channels: --bip.",
    )
    parser.add_argument(
        "--layout",
        type=Path,
        default=None,
        metavar="PATH",
        help="Path to the electrode layout file to load at startup.",
    )
    parser.add_argument(
        "--sampling-rate",
        type=int,
        default=None,
        metavar="HZ",
        help="Sampling rate in Hz (e.g. 500 or 1000).",
    )
    args = parser.parse_args(argv)
    return CliPresets(
        include_aux=args.aux,
        include_bipolar=args.bip,
        layout_path=args.layout,
        sampling_rate=args.sampling_rate,
    )
