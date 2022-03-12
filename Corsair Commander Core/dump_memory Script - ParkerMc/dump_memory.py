#!/usr/bin/env python3
# Install hidapi
# The purpose of this script is to dump the memery of the controller
# When running the program it will first connect to the commander core
# Then it go through all the "modes" and dump the data into dump.csv
try:
    import hidraw as hid
except ModuleNotFoundError:
    import hid


_DUMP_MODES = [(0x07, 0x00), (0x17, 0x00), (0x18, 0x00), (0x1a, 0x00), (0x1e, 0x00), (0x1f, 0x00), (0x20, 0x00),
               (0x21, 0x00), (0x22, 0x00), (0x27, 0x00), (0x31, 0x00), (0x60, 0x6d), (0x61, 0x6d), (0x62, 0x6d),
               (0x63, 0x6d), (0x64, 0x6d), (0x65, 0x6d), (0x6a, 0x6d), (0x6b, 0x6d), (0x6c, 0x6d), (0x6d, 0x6d)]

_VENDOR_ID = 0x1b1c
_PRODUCT_IDS = [0x0c1c, 0x0c2a]
_INTERFACE_NUMBER = 0

_REPORT_LENGTH = 1024
_RESPONSE_LENGTH = 1024

_CMD_WAKE = (0x01, 0x03, 0x00, 0x02)
_CMD_SLEEP = (0x01, 0x03, 0x00, 0x01)
_CMD_RESET = (0x05, 0x01, 0x00)
_CMD_SET_MODE = (0x0d, 0x00)
_CMD_GET = (0x08, 0x00)

dev = None
infos = hid.enumerate(_VENDOR_ID)
for info in infos:
    if info['product_id'] in _PRODUCT_IDS and info['interface_number'] == _INTERFACE_NUMBER:
        dev = hid.device()
        dev.open_path(info['path'])
        print(f'Found matching HID device: {info["product_string"]}')
        break

if dev is None:
    print("No device found")
    exit()


def _send_command(command, data=()):
    # self.device.write expects buf[0] to be the report number or 0 if not used
    buf = bytearray(_REPORT_LENGTH + 1)

    # buf[1] when going out is always 08
    buf[1] = 0x08

    # Indexes for the buffer
    cmd_start = 2
    data_start = cmd_start + len(command)
    data_end = data_start + len(data)

    # Fill in the buffer
    buf[cmd_start:data_start] = command
    buf[data_start:data_end] = data

    # self.device.clear_enqueued_reports()
    if dev.set_nonblocking(True) == 0:
        timeout_ms = 0  # use hid_read; wont block because call succeeded
    else:
        timeout_ms = 1  # smallest timeout forwarded to hid_read_timeout
    discarded = 0
    while dev.read(max_length=1, timeout_ms=timeout_ms):
        discarded += 1
    
    # self.device.write(buf)
    res = dev.write(buf)
    if res < 0:
        raise OSError('Could not write to device')

    # buf = bytes(self.device.read(_RESPONSE_LENGTH))
    dev.set_nonblocking(False)
    buf = bytes(dev.read(_RESPONSE_LENGTH))
    assert buf[1] == command[0], 'response does not match command'
    return buf


def _read_data(new_mode):
    _send_command(_CMD_RESET)
    _send_command(_CMD_SET_MODE, new_mode)
    raw_data = _send_command(_CMD_GET)

    return raw_data


with open("dump.csv", "w") as f:
    f.write("Mode, Data Type, Data\n")
    print("Saving data to file")
    try:
        _send_command(_CMD_WAKE)
        for mode in _DUMP_MODES:
            response = _read_data(mode)
            f.write(bytes(mode).hex(':') + ',' + response[3:5].hex(':') + ',' + response[5:].hex(':') + '\n')
        print("Data saved to file")
    finally:
        _send_command(_CMD_SLEEP)
