#!/usr/bin/env python3

"""
Usage:
    render_frame.py <input> <output>
"""

from docopt import docopt
import json

if __name__ == '__main__':
    args = docopt(__doc__)

    with open(args['<input>'], 'r') as f:
        capture = json.load(f)

    pixels = bytearray()

    for item in capture:
        packet = item['_source']['layers']
        msg = bytes.fromhex(packet['usb.capdata'].replace(':', ''))
        pixels = pixels + msg

    pam = b'P7\nWIDTH 320\nHEIGHT 320\nDEPTH 4\nMAXVAL 255\nTUPLTYPE RGB_ALPHA\nENDHDR\n' + pixels
    with open(args['<output>'], 'bw') as f:
        f.write(pam)
