# Lian Li HydroShift LCD 360S

Captures collected for the driver added in [liquidctl/liquidctl#890][pr].

- `lsusb` — `lsusb -v -d 0416:7398` output (descriptor info; report
  descriptor unavailable without root binding to the device).
- `debug-initialize.log` — `liquidctl --debug initialize`, exercises
  Get-firmware (`A 0x86`) and Handshake (`A 0x81`).
- `debug-status.log` — `liquidctl --debug status`, just Handshake.
- `debug-set-fan-speed.log` — `set fan speed 50` (`A 0x8b`).
- `debug-set-pump-speed.log` — `set pump speed 70` (`A 0x8a`).
- `debug-set-fan-color-static.log` — `set fan color static ff8000`
  (`A 0x85`).
- `debug-set-lcd-brightness.log` — `set lcd screen brightness 80`,
  exercises the LCD-control B-command (`B 0x0c`, full 1024-byte report).
- `debug-set-lcd-orientation.log` — `set lcd screen orientation 0`,
  no USB writes (rotation is persisted in `RuntimeStorage` and applied
  client-side on the next image).

Hardware: HydroShift LCD 360S, firmware reported as
`N9,01,HS,SQ,HydroShift,V3.0B.02C,0.7` (build `Oct 22 2024,17:12:18`).

[pr]: https://github.com/liquidctl/liquidctl/pull/890
