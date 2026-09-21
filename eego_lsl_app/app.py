from __future__ import annotations

import queue
import statistics
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from edi_sdk import DEFAULT_CHANNEL_ADDRESS, EdiSdk, EdiSdkError, channels_available, sampling_rates_available
from layout import Electrode, auxiliary_contacts, impedance_contacts, load_layout, normalize_to_canvas, reference_electrodes
from workers import StreamWorker, WorkerConfig
from firewall import add_firewall_rules, ensure_firewall_rule_interactive

GREEN = "#35c46f"
YELLOW = "#f4c542"
RED = "#e85d5d"
GRAY = "#a8b3b8"
DARK = "#24323a"
CANVAS_BG = "#f7f9fb"
HEAD_OUTLINE = "#d8dee4"
ELECTRODE_OUTLINE = "#4f5b62"


class EegoLslApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("eego LSL: Impedance + EEG v25")
        self.geometry("1160x780")
        self.minsize(1020, 680)

        self.layout_path: Path | None = None
        self.electrodes: list[Electrode] = []
        self.electrode_items: dict[str, int] = {}
        self.electrode_text_items: dict[str, int] = {}
        # Separate canvas item IDs for auxiliary duplicate icons (EOG/REF/GND).
        # EOG is also Ref 32 in the main layout, so it needs its own aux item.
        self.aux_icon_items: dict[str, int] = {}
        self.aux_icon_text_items: dict[str, int] = {}
        # Auxiliary contacts shown in the upper-left of the topomap for 64-channel caps.
        # These are not part of the 64 EEG reference channels; they are display/status contacts.
        self.aux_channel_names = ["EOG", "REF", "GND"]
        self.devices = []  # all DeviceInfo currently reported by the EdigRPC server
        self.last_values: dict[str, float] = {}
        # Topomap colours are based only on impedance values. EEG voltage is never used for colouring.
        self.last_impedance_values: dict[str, float] = {}
        self.last_unit: str = "kΩ"
        self.worker: StreamWorker | None = None
        self.queue: queue.Queue = queue.Queue()
        self.battery_var = tk.StringVar(value="Battery: unavailable")
        self.battery_note = "Battery percentage is not exposed by the bundled eego SDK C wrapper."
        self.mode_var = tk.StringVar(value="impedance")
        self._mode_default_bg: str | None = None
        self._mode_default_active_bg: str | None = None

        self._build_ui()
        self.after(250, self._ask_layout_on_start)
        self.after(700, self._ensure_firewall_on_startup)
        self.after(100, self._poll_worker_queue)

    def _ensure_firewall_on_startup(self):
        ensure_firewall_rule_interactive(self)

    def configure_firewall(self):
        ensure_firewall_rule_interactive(self, force_prompt=True)

    def _build_ui(self):
        root = ttk.Frame(self, padding=10)
        root.pack(fill=tk.BOTH, expand=True)

        top = ttk.Frame(root)
        top.pack(fill=tk.X)

        ttk.Button(top, text="Load electrode layout", command=self.load_layout_dialog).pack(side=tk.LEFT)
        ttk.Button(top, text="Configure firewall", command=self.configure_firewall).pack(side=tk.LEFT, padx=(8, 0))
        self.layout_label = ttk.Label(top, text="No layout loaded")
        self.layout_label.pack(side=tk.LEFT, padx=8)
        ttk.Label(top, textvariable=self.battery_var, foreground="#7a858c").pack(side=tk.RIGHT, padx=(8, 0))

        ttk.Separator(root).pack(fill=tk.X, pady=8)

        controls = ttk.Frame(root)
        controls.pack(fill=tk.X)

        ttk.Label(controls, text="Server address").grid(row=0, column=0, padx=4, pady=4, sticky=tk.E)
        self.server_address_var = tk.StringVar(value=DEFAULT_CHANNEL_ADDRESS)
        ttk.Entry(controls, textvariable=self.server_address_var, width=20).grid(row=0, column=1, padx=4, pady=4, sticky=tk.W)
        ttk.Button(controls, text="Detect amplifier", command=self.detect_amplifiers).grid(row=0, column=2, padx=4, pady=4)
        self.amp_label_var = tk.StringVar(value="No amplifier detected")
        # Own row + wraplength so a long/concatenated serial list can never push later rows' columns.
        ttk.Label(controls, textvariable=self.amp_label_var, wraplength=420).grid(row=0, column=3, columnspan=3, padx=4, pady=4, sticky=tk.W)

        ttk.Label(controls, text="Display / stream").grid(row=1, column=0, padx=(0, 4), pady=4, sticky=tk.E)
        mode_buttons = ttk.Frame(controls)
        mode_buttons.grid(row=1, column=1, padx=4, pady=4, sticky=tk.W)
        self.mode_impedance_btn = tk.Button(
            mode_buttons,
            text="Impedance",
            width=12,
            command=lambda: self._select_mode("impedance"),
        )
        self.mode_impedance_btn.pack(side=tk.LEFT, padx=(0, 6))
        self.mode_eeg_btn = tk.Button(
            mode_buttons,
            text="Activity",
            width=10,
            command=lambda: self._select_mode("eeg"),
        )
        self.mode_eeg_btn.pack(side=tk.LEFT)
        self._mode_default_bg = self.mode_impedance_btn.cget("bg")
        self._mode_default_active_bg = self.mode_impedance_btn.cget("activebackground")
        self._sync_mode_buttons()

        ttk.Label(controls, text="Sampling rate").grid(row=1, column=2, padx=(20, 4), sticky=tk.E)
        self.sampling_rate_var = tk.StringVar(value="1000")
        ttk.Entry(controls, textvariable=self.sampling_rate_var, width=8).grid(row=1, column=3, padx=4, sticky=tk.W)

        self.include_bipolar_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(controls, text="Include Bipolar channels", variable=self.include_bipolar_var).grid(row=1, column=4, padx=(20, 4), sticky=tk.W)
        self.include_aux_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(controls, text="Include Aux channels", variable=self.include_aux_var).grid(row=1, column=5, padx=4, sticky=tk.W)

        ttk.Label(controls, text="Green below kΩ").grid(row=2, column=0, padx=4, sticky=tk.E)
        self.good_ohm_var = tk.StringVar(value="10")
        self.good_ohm_entry = ttk.Entry(controls, textvariable=self.good_ohm_var, width=10)
        self.good_ohm_entry.grid(row=2, column=1, sticky=tk.W)
        ttk.Label(controls, text="Red above kΩ").grid(row=2, column=2, padx=4, sticky=tk.E)
        self.ok_ohm_var = tk.StringVar(value="20")
        self.ok_ohm_entry = ttk.Entry(controls, textvariable=self.ok_ohm_var, width=10)
        self.ok_ohm_entry.grid(row=2, column=3, sticky=tk.W)
        self.threshold_note_var = tk.StringVar(value="Bands: <10 kΩ green, 10–20 kΩ yellow, >20 kΩ red")
        ttk.Label(controls, textvariable=self.threshold_note_var).grid(row=2, column=4, columnspan=2, sticky=tk.W)
        self.good_ohm_var.trace_add("write", self._on_threshold_inputs_changed)
        self.ok_ohm_var.trace_add("write", self._on_threshold_inputs_changed)

        ttk.Label(controls, text="Electrode spacing").grid(row=3, column=0, padx=4, sticky=tk.E)
        self.layout_spacing_var = tk.DoubleVar(value=1.0)
        self.layout_spacing_slider = ttk.Scale(
            controls,
            from_=0.75,
            to=1.35,
            variable=self.layout_spacing_var,
            command=lambda _value: self.redraw_layout(),
        )
        self.layout_spacing_slider.grid(row=3, column=1, columnspan=2, sticky=tk.EW, padx=4)


        actions = ttk.Frame(root)
        actions.pack(fill=tk.X, pady=8)
        self.start_btn = ttk.Button(actions, text="Start", command=self.start_selected_stream)
        self.start_btn.pack(side=tk.LEFT, padx=4)
        self.stop_btn = ttk.Button(actions, text="Stop", command=self.stop_stream, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=4)

        self.stream_note_var = tk.StringVar(value="Selected mode: impedance state in kΩ. Topomap colours are impedance-only.")
        ttk.Label(actions, textvariable=self.stream_note_var).pack(side=tk.LEFT, padx=14)

        self.status_var = tk.StringVar(value="Load a layout, then detect amplifier.")
        ttk.Label(root, textvariable=self.status_var).pack(fill=tk.X, pady=2)

        body = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        body.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(body)
        right = ttk.Frame(body)
        body.add(left, weight=3)
        body.add(right, weight=1)

        self.canvas = tk.Canvas(left, bg=CANVAS_BG, highlightthickness=1, highlightbackground="#dfe5ea")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda event: self.redraw_layout())

        ttk.Label(right, text="Live values").pack(anchor=tk.W)
        cols = ("electrode", "value", "status")
        self.table = ttk.Treeview(right, columns=cols, show="headings", height=16)
        for col in cols:
            self.table.heading(col, text=col.capitalize())
        self.table.column("electrode", width=90)
        self.table.column("value", width=120)
        self.table.column("status", width=90)
        self.table.pack(fill=tk.BOTH, expand=True)

        ttk.Label(right, text="Messages / errors").pack(anchor=tk.W, pady=(8, 0))
        self.log = tk.Text(right, height=14, wrap=tk.WORD)
        self.log.pack(fill=tk.BOTH, expand=False, pady=(2, 0))

    def _ask_layout_on_start(self):
        answer = messagebox.askyesno("Electrode layout", "Load an electrode layout before using the app?")
        if answer:
            self.load_layout_dialog()

    def _mode_changed(self):
        if self.selected_mode() == "impedance":
            self.stream_note_var.set("Selected mode: impedance state in kΩ.")
            self.last_unit = "kΩ"
        else:
            self.stream_note_var.set("Selected mode: EEG activity in microvolts. Topomap colours use last impedance values only.")
            self.last_unit = "µV"
        self._sync_mode_buttons()
        self.last_values.clear()
        self._refresh_table_names()
        self.redraw_layout()

    def _select_mode(self, mode: str):
        if mode not in {"impedance", "eeg"}:
            return
        if self.mode_var.get() == mode:
            return
        self.mode_var.set(mode)
        self._mode_changed()

    def _sync_mode_buttons(self):
        default_bg = self._mode_default_bg or "SystemButtonFace"
        default_active_bg = self._mode_default_active_bg or default_bg

        if self.mode_var.get() == "impedance":
            self.mode_impedance_btn.configure(bg="#f4c542", activebackground="#f4c542", relief=tk.SUNKEN, bd=2)
            self.mode_eeg_btn.configure(bg=default_bg, activebackground=default_active_bg, relief=tk.RAISED, bd=2)
        else:
            self.mode_impedance_btn.configure(bg=default_bg, activebackground=default_active_bg, relief=tk.RAISED, bd=2)
            self.mode_eeg_btn.configure(bg="#ea9999", activebackground="#ea9999", relief=tk.SUNKEN, bd=2)

    def selected_mode(self) -> str:
        return self.mode_var.get()

    def log_msg(self, msg: str):
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)

    def load_layout_dialog(self):
        path = filedialog.askopenfilename(
            title="Select electrode layout",
            filetypes=[("Layout files", "*.txt *.csv *.tsv *.json"), ("All files", "*.*")],
            initialdir=str(Path(__file__).resolve().parent / "capfiles"),
        )
        if not path:
            return
        try:
            self.electrodes = load_layout(path)
            self.layout_path = Path(path)
            self.last_values.clear()
            self.last_impedance_values.clear()
            n_ref = len(reference_electrodes(self.electrodes))
            n_aux = len(auxiliary_contacts(self.electrodes))
            self.layout_label.configure(text=f"{self.layout_path.name} ({n_ref} EEG + {n_aux} aux contacts)")
            self.status_var.set("Layout loaded. Detect amplifier next.")
            self.redraw_layout()
            self._refresh_table_names()
        except Exception as exc:
            messagebox.showerror("Layout error", str(exc))

    def detect_amplifiers(self):
        address = self.server_address_var.get().strip() or DEFAULT_CHANNEL_ADDRESS
        try:
            sdk = EdiSdk(address)
            devices = sdk.list_devices()
        except EdiSdkError as exc:
            messagebox.showerror("EdigRPC error", str(exc))
            self.status_var.set("Could not connect to the EdigRPC server or detect amplifiers.")
            return
        self.devices = devices
        if not devices:
            self.amp_label_var.set("No amplifier detected")
            self.status_var.set("No amplifier detected.")
            return
        serials = ", ".join(d.Serial or d.Key for d in devices)
        self.amp_label_var.set(f"Detected {len(devices)}: {serials}")
        try:
            # Short-lived probe device -- always cascades every reported device,
            # same as the real stream later -- disposed once it goes out of scope.
            probe = sdk.create_device(devices)
            n_ref = sum(1 for ch in channels_available(probe) if ch.is_referential)
            rates = sorted({int(r) for r in sampling_rates_available(probe)})
            probe = None
        except EdiSdkError as exc:
            self.log_msg(f"INFO: could not probe amplifier channel/rate details: {exc}")
            n_ref, rates = None, []
        ref_text = f", {n_ref} referential channel(s)" if n_ref is not None else ""
        rate_text = f", rates={rates}" if rates else ""
        self.status_var.set(f"Detected {len(devices)} amplifier(s) at {address}{ref_text}{rate_text}.")
        self.battery_var.set("Battery: unavailable")
        self.log_msg("INFO: Battery reporting is not implemented in this app yet.")

    def make_config(self) -> WorkerConfig:
        if not self.devices:
            raise RuntimeError("No amplifier detected. Click 'Detect amplifier' first.")
        if not self.electrodes:
            raise RuntimeError("Load an electrode layout first.")
        refs = reference_electrodes(self.electrodes)
        if not refs:
            raise RuntimeError("The selected layout contains no regular EEG reference electrodes.")
        serial = "+".join(d.Serial or d.Key for d in self.devices)
        return WorkerConfig(
            channel_address=self.server_address_var.get().strip() or DEFAULT_CHANNEL_ADDRESS,
            serial=serial,
            channel_names=[e.name for e in refs],
            sampling_rate=int(self.sampling_rate_var.get()),
            stream_lsl=True,
            selected_reference_count=len(refs),
            include_bipolar=self.include_bipolar_var.get(),
            include_aux=self.include_aux_var.get(),
            last_impedance=dict(self.last_impedance_values) or None,
        )

    def start_selected_stream(self):
        self._start_mode(self.selected_mode())

    def _start_mode(self, mode: str):
        if self.worker and self.worker.is_alive():
            messagebox.showinfo("Stream already active", "Stop the current stream before switching display/stream mode.")
            return
        try:
            config = self.make_config()
        except Exception as exc:
            messagebox.showerror("Cannot start", str(exc))
            return
        self.last_values.clear()
        if mode == "impedance":
            self.last_impedance_values.clear()
        self.last_unit = "kΩ" if mode == "impedance" else "µV"
        self._refresh_table_names()
        self.redraw_layout()
        self.worker = StreamWorker(mode, config, self.queue)
        self.worker.start()
        self.start_btn.configure(state=tk.DISABLED)
        self.mode_impedance_btn.configure(state=tk.DISABLED)
        self.mode_eeg_btn.configure(state=tk.DISABLED)
        self.stop_btn.configure(state=tk.NORMAL)
        self.status_var.set(f"Starting {self._mode_label(mode)} LSL stream...")

    def stop_stream(self):
        if not self.worker:
            return
        self.stop_btn.configure(state=tk.DISABLED)
        self.status_var.set("Stopping stream and closing SDK/LSL resources...")
        self.worker.stop()
        self.after(100, self._check_worker_stopped)

    def _check_worker_stopped(self):
        if self.worker and self.worker.is_alive():
            self.after(100, self._check_worker_stopped)
            return
        self.worker = None
        self.start_btn.configure(state=tk.NORMAL)
        self.mode_impedance_btn.configure(state=tk.NORMAL)
        self.mode_eeg_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
        self.status_var.set("Stopped. Stream closed.")

    def _poll_worker_queue(self):
        try:
            while True:
                msg = self.queue.get_nowait()
                self._handle_worker_msg(msg)
        except queue.Empty:
            pass
        self.after(100, self._poll_worker_queue)

    def _handle_worker_msg(self, msg: dict):
        typ = msg.get("type")
        if typ == "started":
            self.status_var.set(f"Started {self._mode_label(msg.get('mode'))} LSL stream with {len(msg.get('channels', []))} channels.")
            self.log_msg(self.status_var.get())
        elif typ == "impedance":
            self._update_values(msg["names"], msg["values"])
        elif typ == "trigger":
            text = f"TRIGGER: code {msg.get('code')}"
            self.log_msg(text)
            self.status_var.set(text)
        elif typ == "info":
            self.log_msg("INFO: " + msg.get("message", ""))
            self.status_var.set(msg.get("message", ""))
        elif typ == "error":
            self.log_msg("ERROR: " + msg.get("message", "unknown error"))
            messagebox.showerror("Stream error", msg.get("message", "unknown error"))
        elif typ == "stopped":
            self.worker = None
            self.start_btn.configure(state=tk.NORMAL)
            self.mode_impedance_btn.configure(state=tk.NORMAL)
            self.mode_eeg_btn.configure(state=tk.NORMAL)
            self.stop_btn.configure(state=tk.DISABLED)
            self.status_var.set("Stopped. Stream closed.")
            self.log_msg("Stream stopped and SDK stream closed.")

    def _mode_label(self, mode: str | None) -> str:
        return "impedance" if mode == "impedance" else "EEG / microvolt"

    def redraw_layout(self):
        self.canvas.delete("all")
        self.electrode_items.clear()
        self.electrode_text_items.clear()
        self.aux_icon_items.clear()
        self.aux_icon_text_items.clear()
        if not self.electrodes:
            self.canvas.create_text(24, 24, anchor=tk.NW, text="No layout loaded", fill=GRAY, font=("Segoe UI", 11))
            return

        w = max(self.canvas.winfo_width(), 520)
        h = max(self.canvas.winfo_height(), 440)
        cx, cy = w / 2, h / 2 + 10
        radius = min(w, h) * 0.42

        # Soft head outline, ears, and nose. This makes the front/up direction explicit.
        self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, outline=HEAD_OUTLINE, width=3)
        self.canvas.create_arc(cx - radius - 18, cy - 42, cx - radius + 18, cy + 42, start=80, extent=200, outline=HEAD_OUTLINE, width=3, style=tk.ARC)
        self.canvas.create_arc(cx + radius - 18, cy - 42, cx + radius + 18, cy + 42, start=-100, extent=200, outline=HEAD_OUTLINE, width=3, style=tk.ARC)
        self.canvas.create_polygon(cx - 18, cy - radius + 8, cx, cy - radius - 22, cx + 18, cy - radius + 8, outline=HEAD_OUTLINE, fill=CANVAS_BG, width=3)
        self.canvas.create_text(cx, cy - radius - 42, text="front", fill="#687680", font=("Segoe UI", 11))

        self._draw_accessory_icons(cx, cy, radius)

        display_electrodes = reference_electrodes(self.electrodes)
        coords = normalize_to_canvas(display_electrodes, w, h, margin=int(min(w, h) * 0.16), orientation="eego_topomap")
        spacing = float(getattr(self, "layout_spacing_var", tk.DoubleVar(value=1.0)).get())
        if abs(spacing - 1.0) > 1e-6:
            coords = {name: (cx + (x - cx) * spacing, cy + (y - cy) * spacing) for name, (x, y) in coords.items()}

        n = len(display_electrodes)
        r = 17 if n <= 70 else 13
        font_size = 8 if n > 70 else 9

        # Draw in two passes so labels sit cleanly above all electrode circles.
        # IMPORTANT: electrode colour is based only on the last impedance value.
        # EEG voltage values are never used for topomap colouring.
        for e in display_electrodes:
            x, y = coords[e.name]
            color = self._impedance_color_for_name(e.name)
            item = self.canvas.create_oval(
                x - r,
                y - r,
                x + r,
                y + r,
                fill=color,
                outline=ELECTRODE_OUTLINE,
                width=1,
            )
            self.electrode_items[e.name] = item

        for e in display_electrodes:
            x, y = coords[e.name]
            txt = self.canvas.create_text(x, y, text=e.name, fill=DARK, font=("Segoe UI", font_size))
            self.electrode_text_items[e.name] = txt


    def _layout_aux_names(self) -> list[str]:
        """Auxiliary cap contacts to draw for impedance status.

        EOG is Ref 32 in the EE-21x/EE-22x 64-channel Appendix-A order, so it is
        still part of the main EEG/impedance channel list. We also show a
        duplicate, data-aware EOG icon in the Aux box because it is physically
        an auxiliary contact on the cap cable and is useful during preparation.
        """
        aux = {e.name.upper(): e.name for e in auxiliary_contacts(self.electrodes)}
        refs = {e.name.upper(): e.name for e in reference_electrodes(self.electrodes)}
        names: list[str] = []

        # EOG may be listed as a reference contact rather than as an auxiliary
        # contact. Include it if it exists in either place or if impedance has
        # already returned an EOG value.
        for key in ("EOG", "REF", "GND"):
            if key in aux:
                names.append(aux[key])
            elif key in refs:
                names.append(refs[key])
            elif key in self.last_impedance_values:
                names.append(key)

        # De-duplicate while preserving order/capitalisation.
        seen = set()
        out = []
        for name in names:
            up = name.upper()
            if up not in seen:
                out.append(name)
                seen.add(up)
        return out

    def _draw_accessory_icons(self, cx: float, cy: float, radius: float):
        """Draw data-aware EOG/REF/GND markers in the upper-left of the topomap."""
        aux_names = self._layout_aux_names()
        if not aux_names:
            return

        panel_x = cx - radius * 0.92
        panel_y = cy - radius * 0.90
        panel_w = max(132, 50 + 58 * len(aux_names))
        panel_h = 74
        self.canvas.create_rectangle(
            panel_x - 18, panel_y - 22, panel_x - 18 + panel_w, panel_y - 22 + panel_h,
            fill="#eef3f7", outline="#d6dde3", width=1,
        )
        self.canvas.create_text(panel_x - 8, panel_y - 14, anchor=tk.NW, text="Aux", fill="#65727a", font=("Segoe UI", 8, "bold"))

        r = 15
        for i, name in enumerate(aux_names):
            x = panel_x + 24 + i * 58
            y = panel_y + 22
            color = self._impedance_color_for_name(name)
            item = self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill=color, outline=ELECTRODE_OUTLINE, width=1,
            )
            # Keep aux icons separate from the main topomap items. This is
            # essential for EOG, which is also a normal referential channel
            # in the Appendix-A order.
            self.aux_icon_items[name] = item
            self.aux_icon_text_items[name] = self.canvas.create_text(
                x, y, text=name, fill=DARK, font=("Segoe UI", 8, "bold"),
            )

    def _refresh_table_names(self):
        for item in self.table.get_children():
            self.table.delete(item)
        for e in reference_electrodes(self.electrodes):
            self.table.insert("", tk.END, iid=e.name, values=(e.name, "—", "unknown"))
        for name in self._layout_aux_names():
            if not self.table.exists(name):
                self.table.insert("", tk.END, iid=name, values=(name, "—", "unknown"))

    def _update_values(self, names, values):
        # Only impedance is shown live; EEG is streamed to LSL without an in-app display.
        known_names = {e.name for e in reference_electrodes(self.electrodes)} | set(self._layout_aux_names())
        for name, value in zip(names, values):
            if name not in self.electrode_items and name not in known_names:
                continue
            v = float(value)
            self.last_values[name] = v
            self.last_impedance_values[name] = v
            if name in self.electrode_items:
                self.canvas.itemconfigure(self.electrode_items[name], fill=self._impedance_color(v))
            if name in self.aux_icon_items:
                self.canvas.itemconfigure(self.aux_icon_items[name], fill=self._impedance_color(v))
            status = self._impedance_status(v)
            if self.table.exists(name):
                self.table.item(name, values=(name, f"{v:.1f} kΩ", status))
        if values:
            try:
                med = statistics.median([abs(float(v)) for v in values])
                self.status_var.set(f"Live impedance values. Median: {med:.1f} kΩ")
            except Exception:
                pass

    def _thresholds(self):
        good, ok = self._validate_thresholds(show_error=False)
        return good, ok

    def _validate_thresholds(self, show_error: bool = True) -> tuple[float, float]:
        try:
            good = float(self.good_ohm_var.get().replace(",", "."))
            ok = float(self.ok_ohm_var.get().replace(",", "."))
        except Exception:
            if show_error:
                messagebox.showerror("Invalid thresholds", "Impedance thresholds must be numbers, e.g. 10 and 20.")
            return 10.0, 20.0
        if good < 0 or ok < 0 or good >= ok:
            if show_error:
                messagebox.showerror(
                    "Invalid thresholds",
                    "Use two positive values where the green threshold is lower than the red threshold. Example: 10 and 20.",
                )
            return 10.0, 20.0
        return good, ok

    def apply_impedance_thresholds(self):
        good, ok = self._validate_thresholds(show_error=True)
        self.good_ohm_var.set(f"{good:g}")
        self.ok_ohm_var.set(f"{ok:g}")
        self.threshold_note_var.set(f"Bands: <{good:g} kΩ green, {good:g}–{ok:g} kΩ yellow, >{ok:g} kΩ red")
        self.redraw_layout()
        if self.last_unit == "kΩ":
            for name, value in list(self.last_impedance_values.items()):
                if self.table.exists(name):
                    status = self._impedance_status(value)
                    self.table.item(name, values=(name, f"{value:.1f} kΩ", status))

    def _on_threshold_inputs_changed(self, *_args):
        try:
            good = float(self.good_ohm_var.get().replace(",", "."))
            ok = float(self.ok_ohm_var.get().replace(",", "."))
        except Exception:
            return
        if good < 0 or ok < 0 or good >= ok:
            return
        self.threshold_note_var.set(f"Bands: <{good:g} kΩ green, {good:g}–{ok:g} kΩ yellow, >{ok:g} kΩ red")
        self.redraw_layout()
        if self.last_unit == "kΩ":
            for name, value in list(self.last_impedance_values.items()):
                if self.table.exists(name):
                    status = self._impedance_status(value)
                    self.table.item(name, values=(name, f"{value:.1f} kΩ", status))

    def _impedance_status(self, value: float) -> str:
        good, ok = self._thresholds()
        if value < good:
            return "good"
        if value <= ok:
            return "ok"
        return "bad"

    def _impedance_color(self, value: float | None) -> str:
        if value is None:
            return GRAY
        status = self._impedance_status(value)
        if status == "good":
            return GREEN
        if status == "ok":
            return YELLOW
        return RED

    def _impedance_color_for_name(self, name: str) -> str:
        return self._impedance_color(self.last_impedance_values.get(name))


def main():
    if "--add-firewall-rule" in sys.argv:
        # This path is used after the app relaunches itself with administrator
        # permission. No full GUI is needed; only a small hidden Tk root for
        # error/information dialogs.
        root = tk.Tk()
        root.withdraw()
        result = add_firewall_rules()
        if result.ok:
            messagebox.showinfo("Windows Firewall", result.message, parent=root)
        else:
            messagebox.showerror("Windows Firewall", result.message, parent=root)
        root.destroy()
        return

    app = EegoLslApp()
    app.mainloop()


if __name__ == "__main__":
    main()
