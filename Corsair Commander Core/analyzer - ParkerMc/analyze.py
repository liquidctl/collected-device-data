#!/usr/bin/env python3

"""
Analyze capture data in JSON format.
By @ParkerMc

Usage:
  analyze.py <path> [options]

Options:
  -h --help         Show this screen.

  --hide-in         Hides input data
"""

import json
import re

from docopt import docopt
import rw_data_formatting
import utils

data_types = {
    0x06: rw_data_formatting.parse_speeds,
    0x10: rw_data_formatting.parse_temps,
    0x0f: rw_data_formatting.parse_detect_rgb
}

channel_names = {
    bytes.fromhex('17'): 'Get Speeds',
    bytes.fromhex('20'): 'Detect LEDs',
    bytes.fromhex('21'): 'Get Temperatures',
    bytes.fromhex('6b6d'): 'Hardware Speed %'
}

modes = {}
last_channel = 0x00


def parse_in(msg):
    if hide_in:  # Return if it shouldn't be printed
        return

    if not msg[0] == 0x00:  # Ensure we have the suspected prefix
        print(f'    IN; Unknown prefix for input: {msg[0:1]}')
        return

    command = msg[1]
    data = msg[3:]

    if command == 0x01:
        # INIT/Wakeup
        print(f'IN; Wake up/Sleep{utils.append_data(data)}')
    elif command == 0x02 and last_channel == 0x13:
        # Get Firmware version
        print(f'IN; Get Firmware Version: {data[0]}.{data[1]}.{data[2]}')
    elif command == 0x05:
        # Reset channel
        print(f'IN; Reset Channel{utils.append_data(data)}')
    elif command == 0x06:
        # Write
        print(f'    IN; Write {utils.append_data(data)}')
    elif command == 0x08:
        # Read
        mode = modes[last_channel]
        if mode in channel_names:
            data_type = utils.bytes_to_le(data, 0)
            if data_type in data_types:
                print(f'IN; Read {channel_names[mode]}; {data_types[data_type](data[2:])}')
            else:
                print(f'    IN; Read {channel_names[mode] + utils.append_data(data)}')
        else:
            print(f'    IN; Read Mode {utils.bytes_to_str(mode)}; Unknown{utils.append_data(data)}')
    elif command == 0x0d:
        # Set Channel mode
        print(f'IN; Set Channel{utils.append_data(data)}')
    else:
        print(f'    IN; Unknown message: {utils.bytes_to_str(msg)}')


def parse_out(msg):
    if not msg[0] == 0x08:  # Check the suspicion for the prefix
        print(f'    OUT; Unknown prefix for output: {msg[0:1]}')
        return

    global last_channel

    command = msg[1]
    channel = msg[2]
    last_channel = channel
    data = msg[3:]

    if command == 0x01 and channel == 0x03 and data[0] == 0x00:
        # Wake up/Sleep
        if data[1] == 0x01:
            print(f'OUT; Sleep')
        elif data[1] == 0x02:
            print(f'OUT; Wake up')
        else:
            print(f'    OUT; Unknown message: {utils.bytes_to_str(msg)}')
    elif command == 0x02 and channel == 0x13:
        # Get Firmware version
        print(f'OUT; Get Firmware Version')
    elif command == 0x05 and channel == 0x01:
        # Reset channel
        print(f'OUT; Reset Channel {utils.bytes_to_str(data)}')
    elif command == 0x06:
        # Write
        # TODO add data formatting after figuring out exact format
        if modes[channel] in channel_names:
            print(f'    OUT; Write on channel {utils.byte_to_str(channel)} mode {channel_names[modes[channel]]}; '
                  f'unknown: {data[:2].hex(":")}; data: {utils.bytes_to_str(data[2:])}')
        else:
            print(f'    OUT; Write on channel {utils.byte_to_str(channel)} mode {utils.bytes_to_str(modes[channel])}; '
                  f'unknown: {data[:2].hex(":")}; data: {utils.bytes_to_str(data[2:])}')
    elif command == 0x08:
        # Read
        if modes[channel] in channel_names:
            print(f'OUT; Read on channel {utils.byte_to_str(channel)} mode {channel_names[modes[channel]]}')
        else:
            print(f'    OUT; Read on channel {utils.byte_to_str(channel)} mode {utils.bytes_to_str(modes[channel])}')
    elif command == 0x0d:
        # Set Channel mode
        if utils.bytes_trim(data) in channel_names:
            print(f'OUT; Set Channel {utils.byte_to_str(channel)} to {channel_names[utils.bytes_trim(data)]}')
        else:
            print(f'    OUT; Set Channel {utils.byte_to_str(channel)} to {utils.bytes_to_str(data)}')
        modes[channel] = utils.bytes_trim(data)
    else:
        print(f'    OUT; Unknown message: {utils.bytes_to_str(msg)}')


if __name__ == '__main__':
    args = docopt(__doc__)

    hide_in = args['--hide-in']

    with open(args['<path>'], 'r') as f:
        capture = json.load(f)

    for item in capture:
        layers = item['_source']['layers']
        if 'Setup Data' in layers:
            continue
        elif 'usbhid' in layers:
            continue
        elif 'usbhid.data' in layers:  # Limited to only the data messages
            bData = bytes.fromhex(
                (
                        re.sub(r'(?::00)*$', '', layers['usbhid.data']) +  # Trim most of the zeros from the end
                        ':00'*50  # Add 50 back to avoid processing errors
                ).replace(':', '')  # Replace for convention to python bytes
            )
            if layers['usb']['usb.src'] == 'host':
                parse_out(bData)
            else:
                parse_in(bData)
        elif 'STRING DESCRIPTOR' in layers:
            continue
        elif 'DEVICE DESCRIPTOR' in layers:
            continue
        elif 'CONFIGURATION DESCRIPTOR' in layers:
            continue
        elif len(layers.keys()) > 2:
            print(f'Missing handler for pack with layers: {layers.keys()}')
