#!/usr/bin/env python3
"""Summarize Commander DUO USBPcap HID transactions.

Requires tshark in PATH.  The reducer intentionally uses usbhid.data because
USBPcap captures for this device place HID payloads there, not usb.capdata.
"""

from __future__ import annotations

import argparse
import subprocess
from collections import Counter
from pathlib import Path


def _hex_to_bytes(value: str) -> bytes:
    return bytes.fromhex(value.replace(":", ""))


def _tshark_rows(path: Path) -> list[tuple[int, float, str, bytes]]:
    cmd = [
        "tshark",
        "-r",
        str(path),
        "-T",
        "fields",
        "-e",
        "frame.number",
        "-e",
        "frame.time_relative",
        "-e",
        "usb.endpoint_address",
        "-e",
        "usbhid.data",
    ]
    proc = subprocess.run(cmd, check=True, text=True, capture_output=True)
    rows = []
    for line in proc.stdout.splitlines():
        number, time_rel, endpoint, payload = (line.split("\t") + [""] * 4)[:4]
        if not payload:
            continue
        rows.append((int(number), float(time_rel or 0), endpoint, _hex_to_bytes(payload)))
    return rows


def _payload_body(payload: bytes) -> bytes:
    # Older captures include HID report id 00 before 08; newer captures start at 08.
    if len(payload) >= 2 and payload[0] == 0x00 and payload[1] == 0x08:
        return payload[1:]
    return payload


def _command_data(data: bytes) -> bytes:
    if len(data) < 3:
        return bytes()
    command = data[1:3]
    body = data[3:]
    if command == bytes([0x0D, 0x01]):
        return body.rstrip(bytes([0x00]))
    if command == bytes([0x06, 0x01]) and len(data) >= 9:
        length = int.from_bytes(data[3:5], "little")
        return data[3 : 7 + length]
    if command in (bytes([0x06, 0x00]), bytes([0x07, 0x00])) and len(data) >= 5:
        length = int.from_bytes(data[3:5], "little")
        return data[3 : 7 + length]
    return body.rstrip(bytes([0x00]))


def summarize(path: Path) -> None:
    rows = _tshark_rows(path)
    host = [(n, t, _payload_body(p)) for n, t, ep, p in rows if ep == "0x04"]
    dev = [(n, t, _payload_body(p)) for n, t, ep, p in rows if ep == "0x84"]
    opens = []
    endpoint_writes = []
    color_writes = []
    for number, time_rel, data in host:
        if len(data) < 4 or data[0] != 0x08:
            continue
        command = data[1:3]
        if command == bytes([0x0D, 0x01]):
            opens.append(_command_data(data).hex(" "))
        elif command == bytes([0x06, 0x01]) and len(data) >= 9:
            length = int.from_bytes(data[3:5], "little")
            dtype = data[7:9]
            payload = data[9 : 7 + length]
            endpoint_writes.append((number, time_rel, length, dtype, payload))
        elif command in (bytes([0x06, 0x00]), bytes([0x07, 0x00])):
            color_writes.append((number, time_rel, command, data[3:]))

    print(f"{path}")
    print(f"  host writes: {len(host)}")
    print(f"  device responses: {len(dev)}")
    print(f"  open endpoints: {Counter(opens).most_common(12)}")
    print(f"  live color writes: {len(color_writes)}")
    for number, time_rel, length, dtype, payload in endpoint_writes:
        print(
            "  endpoint write "
            f"frame={number} time={time_rel:.6f} len={length} "
            f"dtype={dtype.hex(' ')} payload={payload.hex(' ')}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pcap", nargs="+", type=Path)
    args = parser.parse_args()
    for pcap in args.pcap:
        summarize(pcap)


if __name__ == "__main__":
    main()
