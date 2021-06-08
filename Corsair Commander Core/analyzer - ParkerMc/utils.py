def bytes_len(msg):  # Checks how long the bytes list is ignoring the extra bytes
    out = 0
    for i in range(0, len(msg)):
        if msg[i] != 0x00:
            out = i + 1
    return out


def bytes_trim(msg):
    return msg[:bytes_len(msg)]


def bytes_to_str(msg):
    return bytes_trim(msg).hex(":")


def byte_to_str(b):
    return hex(b).lstrip("0x").zfill(2)


def append_data(data):
    if bytes_len(data) == 0:
        return ""
    return f'; Data: {bytes_to_str(data)}'


def bytes_to_le(data, i):
    return int.from_bytes(data[i:i+2], byteorder='little', signed=False)