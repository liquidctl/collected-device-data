import utils


def parse_speeds(data):
    count = data[0]
    speeds = []
    speed_data = data[1:]
    for i in range(0, count):
        speeds.append(utils.bytes_to_le(speed_data, i * 2))

    return f'count {count}, speeds(rpm) {speeds}'


def parse_temps(data):
    count = data[0]
    temps = []
    speed_data = data[1:]
    for i in range(0, count):
        if speed_data[i*3] == 0x01:
            temps.append("Disconnected")
        else:
            temps.append(utils.bytes_to_le(speed_data, i * 3 + 1)/10)

    return f'count {count}, temps(°C) {temps}'


def parse_detect_rgb(data):
    count = data[0]
    rgb_count = []
    rgb_data = data[1:]
    for i in range(0, count):
        if utils.bytes_to_le(rgb_data, i * 4) == 0x03:
            rgb_count.append("Disconnected")
        else:
            rgb_count.append(utils.bytes_to_le(rgb_data, i * 4 + 2))

    return f'count {count}, LED count {rgb_count}'