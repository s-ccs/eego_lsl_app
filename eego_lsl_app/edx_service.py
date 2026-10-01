from __future__ import annotations

import socket
import subprocess
import threading
import time
from pathlib import Path

DEFAULT_EDX_SERVICE_ADDRESS = "localhost:3390"
DEFAULT_EDX_SERVICE_PORT = 3390


def locate_edx_service_binary() -> Path:
    """Return the bundled local EdigRPCApp.dll runtime binary."""
    local_runtime = Path(__file__).resolve().parent / "edi_grpc" / "runtime" / "EdigRPCApp.dll"
    if not local_runtime.exists():
        raise FileNotFoundError(f"Could not find EdigRPCApp.dll at {local_runtime}")
    return local_runtime


def is_edx_service_running(address: str = DEFAULT_EDX_SERVICE_ADDRESS) -> bool:
    host, _, port_text = address.partition(":")
    port = DEFAULT_EDX_SERVICE_PORT if not port_text else int(port_text)
    try:
        with socket.create_connection((host or "localhost", port), timeout=0.75):
            return True
    except (OSError, ValueError):
        return False


def wait_for_edx_service(address: str = DEFAULT_EDX_SERVICE_ADDRESS, timeout: float = 10.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if is_edx_service_running(address):
            return True
        time.sleep(0.25)
    return False


def _pump_service_output(process: subprocess.Popen, log_callback) -> None:
    if process.stdout is None:
        return
    try:
        for line in process.stdout:
            text = line.rstrip("\r\n")
            if text and log_callback is not None:
                log_callback(text)
    except Exception:
        pass


def start_edx_service(log_callback=None) -> subprocess.Popen | None:
    """Start the .NET EdigRPC service if it is not already running."""
    if is_edx_service_running():
        if log_callback is not None:
            log_callback("INFO: EDX service already running on localhost:3390.")
        return None

    dll_path = locate_edx_service_binary()
    cmd = [
        "dotnet",
        str(dll_path),
        "--port",
        str(DEFAULT_EDX_SERVICE_PORT),
    ]
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=str(dll_path.parent),
    )
    if log_callback is not None:
        thread = threading.Thread(target=_pump_service_output, args=(process, log_callback), daemon=True)
        thread.start()
    return process


def stop_edx_service(process: subprocess.Popen | None) -> None:
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)
