#!/usr/bin/env python3

"""
Analyze capture data in JSON format.

Usage:
    analyze <path>
"""

from docopt import docopt
import json

DIR_INC = '< INC '
DIR_OUT = '> OUT '
DETAIL =  '  '


def parse_inc(msg):
    coolant = msg[8] + msg[7] / 256
    print(f'{DETAIL}coolant: {coolant:.1f}°C')
    for name, base in [('fan1', 14), ('fan2', 21), ('pump', 28)]:
        duty = msg[base] / 255
        rpm = int.from_bytes(msg[base + 1:base + 3], byteorder='little')
        print(f'{DETAIL}{name}: {duty:.0%}, {rpm} rpm ({msg[base]:02x})')
    print(f'{DETAIL}firmware: {msg[2] >> 4}.{msg[2] & 0xf}.{msg[3]}')


def parse_out(msg):
    seq = msg[1] >> 4
    cmd = msg[1] & 0xf
    print(f'{DETAIL}cmd: {cmd:04b}')


if __name__ == '__main__':
    args = docopt(__doc__)

    with open(args['<path>'], 'r') as f:
        capture = json.load(f)

    for item in capture:
        packet = item['_source']['layers']

        direction = DIR_INC if packet['usb']['usb.dst'] == 'host' else DIR_OUT
        frame = packet['frame']['frame.number']
        time = packet['frame']['frame.time_relative']
        print(f'{direction}frame: {frame}, time: {time} s')

        try:
            if direction == DIR_INC:
                msg = bytes.fromhex(packet['usb.capdata'].replace(':', ''))
            else:
                msg = bytes.fromhex(packet['Setup Data']['usb.data_fragment'].replace(':', ''))
        except:
            continue

        print(f'{direction}{" ".join(map(lambda x: "{:>3x}".format(x), msg))}')
        print(f'{direction}{" ".join(map(lambda x: "{:>3d}".format(x), msg))}')

        if direction == DIR_INC:
            parse_inc(msg)
        else:
            parse_out(msg)
