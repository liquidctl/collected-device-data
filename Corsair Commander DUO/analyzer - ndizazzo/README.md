# analyzer - ndizazzo

Provided-by: @ndizazzo
Provided-at: 2026-05-13

Helper scripts used during Commander DUO protocol analysis.

- `duo_hid_summary.py`: summarizes HID host writes, open endpoints, live RGB writes, and endpoint payloads.
- `duo_extract_hid_csv.py`: extracts HID packets to CSV for manual inspection.

Both scripts require `tshark` in PATH and read HID payloads from `usbhid.data`.
