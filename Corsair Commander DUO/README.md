# Corsair Commander DUO

Provided-by: @ndizazzo
Provided-at: 2026-05-13

USBPcap captures used to reverse engineer liquidctl support for the Corsair Commander DUO.

Highlights:

- Standard 5 V ARGB software lighting uses live RGB writes on endpoint `0x22`.
- Device Memory fixed/off lighting commits use endpoint `65 6d` with data type `7e 20`.
- Focused readback confirms static Device Memory color order `ff bb gg rr`.
- Device Memory rainbow commits use endpoint `65 6d` with data type `02 a4`.
- Captured `61/62/63 6d` writes appear related to cooling/profile data and were not used as lighting writes.

The Python scripts in `analyzer - ndizazzo/` summarize HID payloads from these USBPcap files.

Capture groups:
- `01 - ndizazzo - initial hardware mode captures/`: Initial exploratory USBPcap captures used to compare startup, hardware-mode enable/disable, live lighting preview, and fan/cooling preset traffic.
- `02 - ndizazzo - device memory preview and apply captures/`: Follow-up captures for Device Memory preview, fixed/off lighting, global red, LED-count changes, rainbow/speed/direction previews, palette preview, save/apply, and after-replug behavior.
- `03 - ndizazzo - focused device memory commits and readback/`: Focused captures that confirm persistent rainbow commit, fixed-color 112233 commit byte order, and Device Memory readback payloads.
