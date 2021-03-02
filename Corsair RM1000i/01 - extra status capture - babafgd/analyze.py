#!/usr/bin/env python3

"""
Analyze capture data in JSON format.

Usage:
    analyze [options] <path>

Options:
    --show-bytes=<direction>           Show bytes (direction=all|inc|out)
    --help                             Output this message

Copyright (C) 2021  Jonas Malaco
"""

from docopt import docopt
import json

DIR_INC = 'inc'
DIR_OUT = 'out'


COMMANDS = {
    0x00: 'PAGE',
    0x03: 'CLEAR_FAULTS',
    0x3b: 'FAN_COMMAND_1',
    0x40: 'VOUT_OV_FAULT_LIMIT',
    0x44: 'VOUT_UV_FAULT_LIMIT',
    0x46: 'IOUT_OC_FAULT_LIMIT',
    0x4f: 'IOUT_OC_FAULT_LIMIT',
    0x88: 'READ_VIN',
    0x89: 'READ_IIN',
    0x8b: 'READ_VOUT',
    0x8c: 'READ_IOUT',
    0x8d: 'READ_TEMPERATURE_1',
    0x8e: 'READ_TEMPERATURE_2',
    0x90: 'READ_FAN_SPEED_1',
    0x96: 'READ_POUT',
    0x97: 'READ_PIN',
    0x99: 'MFR_ID',
    0x9a: 'MFR_MODEL',
    0xd4: 'MFR_SPECIFIC_D4',
    0xd8: 'MFR_SPECIFIC_D8',
    0xee: 'MFR_SPECIFIC_EE (OUTPUT POWER)',
}


def parse_inc(msg):
    pass


def parse_out(msg):
    address = msg[0] >> 1
    write_bit = msg[0] & 0x1
    read_or_write = "READ" if write_bit else "WRITE"
    command_byte = msg[1]
    command = COMMANDS.get(command_byte, 'UNKNOWN')
    print(f'{read_or_write} {command} ({command_byte:#04x}) to {address:#04x}')
    pass


if __name__ == '__main__':
    args = docopt(__doc__)

    with open(args['<path>'], 'r') as f:
        capture = json.load(f)

    for item in capture:
        packet = item['_source']['layers']

        direction = DIR_INC if packet['usb']['usb.dst'] == 'host' else DIR_OUT

        try:
            msg = bytes.fromhex(packet['usbhid.data'].replace(':', ''))
        except:
            # can safely ignore other packets
            continue

        frame = packet['frame']['frame.number']
        time = packet['frame']['frame.time_relative']
        dirsign = '>' if direction == DIR_INC else '<'
        print(f'{dirsign} {direction.upper()} frame: {frame}, time: {time} s')

        truncated_msg = msg.rstrip(b'\x00')

        if args['--show-bytes'] and args['--show-bytes'].lower() in ['all', direction]:
            print(f'  bytes (hex): {" ".join(map(lambda x: " {:0>2x}".format(x), truncated_msg))}')
            print(f'  bytes (int): {" ".join(map(lambda x: "{:>3d}".format(x), truncated_msg))}')

            truncated = len(msg) - len(truncated_msg)
            if truncated:
                print(f'               +{truncated:>2d} zero bytes')

        if direction == DIR_INC:
            parse_inc(msg)
        else:
            parse_out(msg)
