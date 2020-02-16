#!/usr/bin/env python3

"""
Analyze capture data in JSON format.

Usage:
    analyze [options] <path>

Options:
    --show-bytes=<direction>           Show bytes (direction=all|inc|out)
    --help                             Output this message

Copyright (C) 2020  Jonas Malaco
"""

from docopt import docopt
import json

DIR_INC = 'inc'
DIR_OUT = 'out'


def parse_inc(msg):
    # found by analyzing how each byte varies over time (see _data_in.ods)
    coolant = msg[8] + msg[7] / 256
    print(f'  coolant: {coolant:.1f}°C')
    for name, base in [('fan1', 14), ('fan2', 21), ('pump', 28)]:
        duty = msg[base] / 255
        rpm = int.from_bytes(msg[base + 1:base + 3], byteorder='little')
        print(f'  {name}: {duty:.0%}, {rpm} rpm ({msg[base]:02x})')
    # only possible match to fw version reported by iCue
    print(f'  firmware: {msg[2] >> 4}.{msg[2] & 0xf}.{msg[3]}')


def parse_out(msg):
    # msg[1] is the only byte left when setting all LEDs to blue
    # seq and cmd found analyzing how each bit varies over time (see _data_out.ods)
    seq = msg[1] >> 3
    cmd = msg[1] & 0x7
    print(f'  cmd: {cmd:03b}')


if __name__ == '__main__':
    args = docopt(__doc__)

    with open(args['<path>'], 'r') as f:
        capture = json.load(f)

    for item in capture:
        packet = item['_source']['layers']

        direction = DIR_INC if packet['usb']['usb.dst'] == 'host' else DIR_OUT

        try:
            if direction == DIR_INC:
                msg = bytes.fromhex(packet['usb.capdata'].replace(':', ''))
            else:
                msg = bytes.fromhex(packet['Setup Data']['usb.data_fragment'].replace(':', ''))
        except:
            # can safely ignore other packets
            continue

        frame = packet['frame']['frame.number']
        time = packet['frame']['frame.time_relative']
        dirsign = '>' if direction == DIR_INC else '<'
        print(f'{dirsign} {direction.upper()} frame: {frame}, time: {time} s')

        if args['--show-bytes'] and args['--show-bytes'].lower() in ['all', direction]:
            print(f'  bytes (hex): {" ".join(map(lambda x: "{:>3x}".format(x), msg))}')
            print(f'  bytes (int): {" ".join(map(lambda x: "{:>3d}".format(x), msg))}')

        if direction == DIR_INC:
            parse_inc(msg)
        else:
            parse_out(msg)
