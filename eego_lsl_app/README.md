
Tkinter-based Python app for ANT eego amplifiers.

It can:

- load an electrode layout (`.txt`, `.csv`, `.tsv`, `.json`),
- detect connected eego amplifiers,
- stream either impedance values or EEG activity to LSL,
- display live electrode impedance on a topomap.

![screenshot of the app](screenshot.png)

## Requirements

This app talks to an **EdigRPC (EDI 2.0) server** over gRPC -- it no longer loads the eego SDK DLL
directly. Start the EDI gRPC server (EdigRPCApp / EDX-Service-TinyUI) first, then run this app;
by default it connects to `localhost:3390` (configurable in the GUI).



## Install
Be sure to have installed `python3-tk`

then clone and run
```bat
uv init

```

## Run

```bat
uv run app.y
```

## CLI presets

A few settings can be preset on the command line so they do not have to be
ticked in the GUI every time:

```bat
uv run app.py --aux --no-bip --layout capfiles/64ch.txt --sampling-rate 500
```

- `--aux` / `--no-aux` — include Aux channels (yes/no)
- `--bip` / `--no-bip` — include Bipolar channels (yes/no)
- `--layout PATH` — electrode layout file to load at startup (skips the startup dialog)
- `--sampling-rate HZ` — sampling rate in Hz

Any option that is omitted keeps the GUI default. Everything else (server
address, thresholds, mode) stays in the GUI.
## Impedance colour scale

The topomap uses three adjustable impedance bands. The defaults are:

- **green:** `< 10 kΩ`
- **yellow:** `10–20 kΩ`
- **red:** `> 20 kΩ`

Change the two threshold boxes in the GUI and press **Apply thresholds**. The topomap and table update immediately for the latest impedance values.

## LSL modes

Use the dropdown to choose:

- `Impedance (kOhm)`
- `EEG activity (µV)`

Then press **Start LSL Stream**. To change mode, press **Stop**, select the other mode, and start again.
Only the impedance mode is shown live in the app; EEG activity is streamed straight to LSL with no in-app display.

## Stop behaviour

Pressing **Stop** now requests a full SDK stream close, which should also release the LSL outlet once the worker thread exits. The app waits until the worker confirms that the stream is closed before re-enabling the start controls.

## Notes

- "Detect amplifier" always cascades every device the server reports into a single stream (never a user-selected subset).
- If the app cannot connect, make sure the EdigRPC server is running and reachable at the configured address.

- EEG values are assumed to come from the SDK in volts and are converted to microvolts before display/LSL streaming.

## Windows Firewall
The app checks on startup whether Windows Firewall rules exist for the program. If no rule is found, it asks whether to add inbound and outbound allow-rules for Private/Domain networks.

Important details:

- Windows requires administrator permission to add firewall rules.
- During development, the rule applies to `python.exe` because the app is launched through Python.
- The rules do not guarantee LSL visibility if the network itself blocks multicast/broadcast discovery, if the network profile is Public, if a VPN is active, or if a university/router firewall isolates devices.

You can also press **Configure firewall** in the app to run the firewall check manually.

