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
        duty = msg[base] / 255  # TODO check
        rpm = int.from_bytes(msg[base + 1:base + 3], byteorder='little')
        print(f'  {name}: {duty:.0%}, {rpm} rpm')
    # only possible match to fw version reported by iCue
    print(f'  firmware: {msg[2] >> 4}.{msg[2] & 0xf}.{msg[3]}')


def parse_fanctl(fan_no, msg):
    base = 0xb + fan_no * 6
    cbase = 0x1e + fan_no * 14
    fan_mode = ['custom', 'external', 'fixed_duty', None, 'fixed_rpm'][msg[base]]
    if fan_mode == 'custom':
        temps = msg[cbase:(cbase + 14):2]
        duties = map(lambda x: f'{x / 255:.0%}', msg[cbase + 1:(cbase + 14):2])  # TODO check
        print(f'  fan{fan_no} mode := {fan_mode}, (temperature,duty) := {list(zip(temps, duties))}')
    elif fan_mode == 'external':
        print(f'  fan{fan_no} mode := {fan_mode}, do not know how to parse details')
    elif fan_mode == 'fixed_duty':
        duty = msg[base + 5] / 255  # TODO check
        print(f'  fan{fan_no} mode := {fan_mode} with duty := {duty:.0%}')
    elif fan_mode == 'fixed_rpm':
        rpm = int.from_bytes(msg[base + 1:base + 3], byteorder='little')
        print(f'  fan{fan_no} mode := {fan_mode} with rpm := {rpm} rpm')
    else:
        raise ValueError(f'Unknown fan{fan_no} mode: {msg[base]}')


def parse_out(msg):
    # msg[1] is the only byte left when setting all LEDs to blue
    # seq and cmd found analyzing how each bit varies over time (see _data_out.ods)
    # cmd parsing done with device emulation
    seq = msg[1] >> 3
    cmd = msg[1] & 0x7
    if cmd == 0b100:
        print(f'  cmd: set lighting (1/2)')
    elif cmd == 0b101:
        print(f'  cmd: set lighting (2/2)')
    elif cmd == 0b000 and msg[2] == 0x14:
        print(f'  cmd: set cooling')
        for no in range(2):
            parse_fanctl(no, msg)
        pump_mode = ['quiet', 'balanced', 'extreme'][msg[23]]  # TODO check
        print(f'  pump mode := {pump_mode}')
    elif cmd == 0b000 and msg[2] == 0xff:
        print(f'  cmd: get status')
    else:
        raise ValueError(f'Unknown command: {cmd:03b}')


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
