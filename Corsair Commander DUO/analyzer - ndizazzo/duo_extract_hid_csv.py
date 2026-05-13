#!/usr/bin/env python3
"""Extract focused Commander DUO HID packet rows from USBPcap captures."""

from __future__ import annotations

import argparse
import csv
import subprocess
from pathlib import Path


def _hex_to_bytes(value: str) -> bytes:
    return bytes.fromhex(value.replace(":", ""))


def _payload_body(payload: bytes) -> bytes:
    if len(payload) >= 2 and payload[0] == 0x00 and payload[1] == 0x08:
        return payload[1:]
    return payload


def extract(path: Path, output: Path, endpoint_filter: set[str] | None) -> None:
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
    with output.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["frame", "time_relative", "endpoint", "direction", "command", "payload_hex"])
        for line in proc.stdout.splitlines():
            frame, time_rel, endpoint, payload = (line.split("\t") + [""] * 4)[:4]
            if not payload or (endpoint_filter and endpoint not in endpoint_filter):
                continue
            data = _payload_body(_hex_to_bytes(payload))
            if not data or data[0] != 0x08:
                continue
            direction = "host" if endpoint == "0x04" else "device"
            command = data[1:3].hex(" ") if len(data) >= 3 else ""
            writer.writerow([frame, time_rel, endpoint, direction, command, data.hex(" ")])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pcap", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--endpoint",
        action="append",
        help="Endpoint to include, e.g. 0x04 or 0x84. Repeatable. Defaults to all HID endpoints.",
    )
    args = parser.parse_args()
    extract(args.pcap, args.output, set(args.endpoint) if args.endpoint else None)


if __name__ == "__main__":
    main()
