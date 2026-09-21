
Tkinter-based Python app for ANT eego amplifiers.

It can:

- load an electrode layout (`.txt`, `.csv`, `.tsv`, `.json`),
- detect connected eego amplifiers,
- stream either impedance values or EEG activity to LSL,
- display electrode impedance on a topomap and EEG values numerically/signal-viewer only.

![screenshot of the app](screenshot.png)

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
## Impedance colour scale

The topomap uses three adjustable impedance bands. The defaults are:

- **green:** `< 10 kΩ`
- **yellow:** `10–20 kΩ`
- **red:** `> 20 kΩ`

Change the two threshold boxes in the GUI and press **Apply thresholds**. The topomap and table update immediately for the latest impedance values.has two tabs: **Topomap** and **Signal viewer**. The signal viewer is written directly in Tkinter. It can display up to 64 channels.

## LSL modes

Use the dropdown to choose:

- `Impedance (kOhm)`
- `EEG activity (µV)`

Then press **Start LSL Stream**. To change mode, press **Stop**, select the other mode, and start again.

## Stop behaviour

Pressing **Stop** now requests a full SDK stream close, which should also release the LSL outlet once the worker thread exits. The app waits until the worker confirms that the stream is closed before re-enabling the start controls.

## Notes

- EEG values are assumed to come from the SDK in volts and are converted to microvolts before display/LSL streaming.

## Windows Firewall
The app checks on startup whether Windows Firewall rules exist for the program. If no rule is found, it asks whether to add inbound and outbound allow-rules for Private/Domain networks.

Important details:

- Windows requires administrator permission to add firewall rules.
- During development, the rule applies to `python.exe` because the app is launched through Python.
- The rules do not guarantee LSL visibility if the network itself blocks multicast/broadcast discovery, if the network profile is Public, if a VPN is active, or if a university/router firewall isolates devices.

You can also press **Configure firewall** in the app to run the firewall check manually.

