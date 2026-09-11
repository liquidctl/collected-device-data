# Aquacomputer Quadro Interface Notes

This document describes the Quadro USB interface details currently known 
via reverse engineering.

The interface is not vendor-documented here. Treat every write as hardware
control: read first, validate CRCs, change the smallest possible set of bytes,
write a backup, and verify the device accepted the exact intended values.

## Device Identity

| Field | Value |
| --- | --- |
| USB vendor ID | `0x0c70` |
| Quadro product ID | `0xf00d` |
| Known firmware | `1033` |
| Example serial | `00725-60872` |
| Example raw serial | `0x02d5edc8` |

Serial text is encoded like the existing plugin:

```text
upper = (serial_raw >> 16) & 0xffff
lower = serial_raw & 0xffff
serial_text = f"{upper:05d}-{lower:05d}"
```

The USB device exposes at least these interfaces:

| Interface | Class | Endpoints | Use |
| ---: | --- | --- | --- |
| 0 | vendor-specific `ff/00/00` | bulk `0x81`, `0x02` | Used by aquasuite for some runtime/soft-sensor traffic. Not needed for basic autonomous fan control. |
| 1 | HID `03/00/00` | interrupt IN `0x83` | Live readings and HID feature/output reports. |

For a cross-platform Python CLI, use HID APIs rather than Linux-only `hidraw`
where practical. `hidapi`/`hid` should make Windows support mostly transparent
for feature reports, while Linux `hidraw` is useful for low-level diagnostics.

## Byte Order And Scaling

All multi-byte numeric fields seen so far are big-endian.

Use these helpers consistently:

| Type | Encoding |
| --- | --- |
| `u16be` | unsigned 16-bit big-endian |
| `s16be` | signed 16-bit big-endian |
| `u32be` | unsigned 32-bit big-endian |

Common scales:

| Quantity | Raw scale |
| --- | --- |
| Temperature | Celsius x 100 |
| Fan/controller output | Percent x 100 |
| Fan voltage | Volts x 100 |
| Missing temperature | `32767` sentinel |

## CRC

Settings and names reports end with a big-endian CRC-16/USB checksum over the
payload only. The HID report ID byte and final two CRC bytes are not included in
the calculation.

CRC parameters:

| Parameter | Value |
| --- | --- |
| Width | 16 |
| Poly | `0x8005` |
| Init | `0xffff` |
| XorOut | `0xffff` |
| RefIn | true |
| RefOut | true |

Equivalent Python implementation:

```python
def crc16_usb(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
            crc &= 0xFFFF
    return crc ^ 0xFFFF
```

## Report Summary

| Report | Direction | Length | Purpose |
| --- | --- | ---: | --- |
| Input report `0x01` | device to host, interrupt IN | 220 | Live device, temperature, fan, controller, alarm, and profile readings. |
| Feature report `0x03` | bidirectional HID feature | 961 | Main persistent settings. |
| Output report `0x02` | host to device HID output | 11 | Commit/apply packet used after settings writes. |
| Feature report `0x08` | bidirectional HID feature | 1013 | Names/labels and related flash data. |

Low-level HID control request identities:

| Operation | bmRequestType | bRequest | wValue | wIndex | wLength |
| --- | --- | --- | --- | ---: | ---: |
| Get settings feature report `0x03` | `0xa1` | `0x01` | `0x0303` | 1 | 1013 requested, 961 returned |
| Set settings feature report `0x03` | `0x21` | `0x09` | `0x0303` | 1 | 961 |
| Set output report `0x02` | `0x21` | `0x09` | `0x0202` | 1 | 11 |
| Set names feature report `0x08` | `0x21` | `0x09` | `0x0308` | 1 | 1013 |

Known commit/output report bytes:

```text
02 00 00 00 02 00 00 00 00 34 c6
```

For settings changes, the safest sequence is:

1. Read feature report `0x03`.
2. Require length at least 961 and report ID byte `0x03`.
3. Validate CRC over bytes `1..958` against bytes `959..960`.
4. Save the original report as a binary backup.
5. Apply the minimal intended edits.
6. Recompute CRC into bytes `959..960`.
7. Write feature report `0x03`.
8. Write output report `0x02` commit bytes.
9. Read feature report `0x03` again and verify the edited fields.
10. Optionally read live input report `0x01` to verify runtime behavior.

On Linux `hidraw`, feature reads may be requested with a 1013-byte buffer even
though settings report `0x03` returns 961 bytes. On Windows through `hidapi`,
the same logical operation should be `get_feature_report(0x03, 1013)`.

## Live Input Report `0x01`

Input report `0x01` is 220 bytes long. Absolute offsets below include the
report ID byte.

### Header

| Offset | Type | Field |
| ---: | --- | --- |
| 0 | `u8` | Report ID, expected `0x01` |
| 1 | `u16be` | Structure ID |
| 3 | `u32be` | Raw serial |
| 7 | `u16be` | Hardware |
| 9 | `u16be` | Device type |
| 11 | `u16be` | Bootloader version |
| 13 | `u16be` | Firmware version |

### Status

| Offset | Type | Field |
| ---: | --- | --- |
| 15 | `u32be` | System state |
| 19 | `u8` | Feature unlock |
| 20 | `u32be` | Device time |
| 24 | `u32be` | Power-up count |
| 28 | `u32be` | Total runtime |

### Sensors And Fans

| Offset | Type | Field |
| ---: | --- | --- |
| 32 | `u16be[10]` | Raw ADC values |
| 52 | `s16be[4]` | Temperature sensors, Celsius x 100 |
| 60 | `s16be[16]` | Software/virtual sensor values |
| 92 | `u8[16]` | Software/virtual sensor units |
| 108 | `s16be` | 12V rail, likely volts x 100 |
| 110 | `s16be` | Flow reading |
| 112 | `FanLive[4]` | Fan live data, 13 bytes each |

`FanLive` entry layout:

| Entry Offset | Type | Field |
| ---: | --- | --- |
| 0 | `s16be` | Output, percent x 100 |
| 2 | `s16be` | Voltage, volts x 100 |
| 4 | `s16be` | Current, raw units unknown |
| 6 | `s16be` | Power, raw units unknown |
| 8 | `s16be` | Speed in RPM |
| 10 | `s16be` | Torque, raw units unknown |
| 12 | `u8` | Fan live flags |

Fan live entry absolute base:

```text
fan_base(index0) = 112 + index0 * 13
```

### Controller Outputs And Tail

| Offset | Type | Field |
| ---: | --- | --- |
| 164 | `ControllerLive[5]` | Controller live data, 8 bytes each |
| 204 | `u32be` | Current alarm state |
| 208 | `u32be` | Last alarm state |
| 212 | `s16be` | RGBpx/strip field, not fully decoded |
| 214 | `s16be` | RGBpx/strip field, not fully decoded |
| 216 | `u8` | RGBpx/strip field, not fully decoded |
| 217 | `u8` | RGBpx/strip field, not fully decoded |
| 219 | `u8` | Active profile ID |

`ControllerLive` entry layout:

| Entry Offset | Type | Field |
| ---: | --- | --- |
| 0 | `s16be` | Input offset |
| 2 | `s16be` | Output offset |
| 4 | `s16be` | Output scale |
| 6 | `s16be` | Output, percent x 100 |

Controller live entry absolute base:

```text
controller_live_base(index0) = 164 + index0 * 8
```

## Settings Feature Report `0x03`

Feature report `0x03` is 961 bytes:

```text
byte 0      report ID, 0x03
bytes 1-958 settings payload
bytes 959-960 CRC-16/USB over bytes 1-958, big-endian
```

All offsets in this section are payload-relative. Add 1 for absolute HID report
offsets.

### Top-Level Layout

| Payload Offset | Type | Field |
| ---: | --- | --- |
| 0 | `u16be` | Structure ID |
| 2 | `u8` | I2C address |
| 3 | `u16be` | Device flags |
| 5 | `u16be` | Flow calibration |
| 7 | `s16be` | Flow factor |
| 9 | `SensorConfig[4]` | Temperature sensor settings, 2 bytes each |
| 17 | `FanConfig[4]` | Fan electrical/safety settings, 9 bytes each |
| 53 | `ControllerConfig[4]` | Fan controller settings, 85 bytes each |
| 393 | `StripConfig` | RGBpx/strip config |
| 396 | `LedControllerConfig[8]` | LED controller settings, 70 bytes each |
| 956 | `u8` | Profile ID |
| 957 | `u8` | Dummy/padding |

### Temperature Sensor Config

`SensorConfig` is 2 bytes:

| Entry Offset | Type | Field |
| ---: | --- | --- |
| 0 | `s16be` | Offset, Celsius x 100 |

Sensor config base:

```text
sensor_base(index0) = 9 + index0 * 2
```

Example: writing `368` to sensor 1 offset means `+3.68 C`.

### Fan Config

`FanConfig` is 9 bytes:

| Entry Offset | Type | Field |
| ---: | --- | --- |
| 0 | `u8` | Fan config flags |
| 1 | `s16be` | Minimum power, percent x 100 |
| 3 | `s16be` | Maximum power, percent x 100 |
| 5 | `s16be` | Fallback power, percent x 100 |
| 7 | `s16be` | Maximum RPM |

Fan config base:

```text
fan_config_base(index0) = 17 + index0 * 9
```

Known fan config flags:

| Bit | Meaning |
| --- | --- |
| `0x01` | Hold minimum power |
| `0x02` | Start boost |

Important tachless/high-current fan note: with a powered bypass adapter and no
working tach signal, start boost can leave the live fan output at `100.00%`
even when the controller is configured for a lower fixed output. For this setup,
clear `0x02` on the relevant `FanConfig.flags`.

Known examples:

| Raw | Decoded |
| ---: | --- |
| `2184` | `21.84%` |
| `7920` | `79.20%` |
| `7111` | `71.11%` |

### Controller Config

`ControllerConfig` is 85 bytes:

| Entry Offset | Type | Field |
| ---: | --- | --- |
| 0 | `u8` | Mode |
| 1 | `s16be` | Fixed/manual power, percent x 100 |
| 3 | `s16be` | Source sensor index |
| 5 | `PidConfig` | Target-temperature controller, 14 bytes |
| 19 | `CurveConfig` | Curve controller, 66 bytes |

Controller config base:

```text
controller_base(index0) = 53 + index0 * 85
```

Known modes:

| Value | Meaning |
| ---: | --- |
| `0` | Fixed power / power preset |
| `1` | Target-temperature controller |
| `2` | Curve controller |
| `4` | Use or mirror another fan controller's settings |

Known source values:

| Value | Meaning |
| ---: | --- |
| `-1` | No source / unused, common in fixed-power configs |
| `0` | Temperature Sensor 1 |
| `1` | Temperature Sensor 2 |

Fan 1 fixed-power fields:

```text
payload[53]       controller[0].mode
payload[54..55]   controller[0].power
payload[17]       fan_config[0].flags
```

To set Fan 1 to fixed 50% for a tachless bypass fan:

```text
controller[0].mode = 0
controller[0].power = 5000
fan_config[0].flags &= ~0x02
```

Then recompute the settings CRC, write report `0x03`, send output report `0x02`,
and read back report `0x03` to verify.

### PID Config

`PidConfig` is 14 bytes:

| Entry Offset | Type | Field |
| ---: | --- | --- |
| 0 | `s16be` | Setpoint, Celsius x 100 |
| 2 | `s16be` | P gain |
| 4 | `s16be` | I gain |
| 6 | `s16be` | D gain |
| 8 | `s16be` | D-Tn |
| 10 | `s16be` | Hysteresis, Celsius x 100 |
| 12 | `u16be` | PID flags |

PID base:

```text
pid_base(index0) = controller_base(index0) + 5
```

Known examples:

| Field | Example Value | Meaning |
| --- | ---: | --- |
| Setpoint | `5000` | `50.00 C` |
| Hysteresis | `10` | `0.10 C` |
| P/I/D/D-Tn preset | `2500`, `2000`, `500`, `10` | A known "faster +1" style preset |
| User-defined P/I/D | `1419`, `1205`, `2` | Known user-defined values |

### Curve Config

`CurveConfig` is 66 bytes:

| Entry Offset | Type | Field |
| ---: | --- | --- |
| 0 | `s16be` | Start value, Celsius x 100 |
| 2 | `s16be[16]` | Curve input temperatures, Celsius x 100 |
| 34 | `s16be[16]` | Curve output powers, percent x 100 |

Curve base:

```text
curve_base(index0) = controller_base(index0) + 19
curve_input(index0, point0) = curve_base(index0) + 2 + point0 * 2
curve_output(index0, point0) = curve_base(index0) + 34 + point0 * 2
```

Known example: point 8 changed from `33.20 C -> 33.37 C` and
`22.60% -> 40.22%`, represented as raw input `3320 -> 3337` and raw output
`2260 -> 4022`.

### Strip Config

Known strip fields:

| Payload Offset | Type | Field |
| ---: | --- | --- |
| 393 | `u8` | Brightness |
| 394 | `u16be` | Strip flags |

Known examples:

| Field | Raw | Meaning |
| --- | ---: | --- |
| Brightness | `255` | Full brightness |
| Brightness | `252` | Slightly reduced brightness |
| Strip flags | `0x0002` | Strip disabled |

### LED Controller Config

Eight LED controller entries start at payload offset `396`, with a 70-byte
stride:

```text
led_controller_base(index0) = 396 + index0 * 70
```

The plugin has a partial structure for these entries, but they are not required
for basic fan and temperature-sensor CLI functionality.

## Names Feature Report `0x08`

Feature report `0x08` is 1013 bytes:

```text
byte 0        report ID, 0x08
bytes 1-1010  names/flash payload
bytes 1011-1012 CRC-16/USB over bytes 1-1010, big-endian
```

Payload layout:

| Payload Offset | Type | Field |
| ---: | --- | --- |
| 0 | `u16be` | Version/structure ID |
| 2 | `Name[42]` | Null-terminated ASCII names, 24 bytes each |

Name slot base:

```text
name_base(slot0) = 2 + slot0 * 24
```

Known slots:

| Slot | Name |
| ---: | --- |
| 0 | Unknown/reserved |
| 1-4 | Fan 1-4 |
| 9-16 | LED Controller 1-8 |
| 17 | Flow |
| 18-21 | Temperature Sensor 1-4 |
| 24 | Strip |
| 25-40 | Software sensors |

Renaming fans, sensors, LED controllers, the strip, and software sensors changes
report `0x08`, not settings report `0x03`.

## Aquasuite XML Profile Backups

Aquasuite profile XML files can contain base64 fields named `settings` and
`flash`.

Known useful behavior:

| XML Field | Decoded Length | Meaning |
| --- | ---: | --- |
| `settings` | 961 | Settings report-compatible bytes, except byte 0 may be `0x00` instead of HID report ID `0x03`. Bytes `1..960` match payload plus CRC format. |
| `flash` | 1013 | Names/flash report `0x08`, including report ID and CRC. |

For tooling, XML backups are useful as import/export sources, but direct device
readback should remain authoritative before writes.

## Vendor Bulk Traffic

The vendor-specific interface has bulk endpoint `0x02` host-to-device traffic.
Some actions that look like runtime-only updates, especially software-sensor
updates, use this path. Known examples include 33-byte and 67-byte bulk OUT
messages.

This is not currently needed for autonomous fan control stored on the Quadro.
Do not build basic persistent fan-control tooling around bulk traffic until the
message format is decoded.

## Linux Notes

Linux exposes the device as `/dev/hidrawN`. The number changes across reconnects,
so discover it through `/sys/class/hidraw` by matching VID/PID.

Useful permission options:

```bash
sudo setfacl -m u:$USER:rw /dev/hidrawN
```

or a persistent udev rule such as:

```text
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="0c70", ATTRS{idProduct}=="f00d", MODE="0660", TAG+="uaccess"
```

Linux `hidraw` feature-report ioctls:

| Operation | ioctl |
| --- | --- |
| Read feature report | `HIDIOCGFEATURE(len)` |
| Write feature report | `HIDIOCSFEATURE(len)` |

The first byte of the buffer is always the HID report ID.

## Windows Notes

Windows support should mostly live in the transport layer if using `hidapi`.
The encoder/decoder, CRC, scaling, and report layouts should be identical.

Watch for these platform differences:

| Topic | Linux `hidraw` | Windows HID/hidapi |
| --- | --- | --- |
| Device path | `/dev/hidrawN` discovered via sysfs | HID path returned by enumeration |
| Permissions | May require ACL/udev | Usually available to the user session |
| Feature report buffers | First byte is report ID | First byte is report ID |
| Input reports | Can read from hidraw file descriptor | Use HID read API |
| Output report `0x02` | `os.write()` works on hidraw | Use HID write/output report API |

Keep platform-specific code behind a small interface:

```python
class QuadroTransport:
    def get_feature_report(self, report_id: int, length: int) -> bytes: ...
    def set_feature_report(self, report: bytes) -> None: ...
    def write_output_report(self, report: bytes) -> None: ...
    def read_input_report(self, length: int, timeout_ms: int) -> bytes: ...
```

## Known Unknowns

These are not required for basic autonomous fan control but should stay visible:

| Area | Status |
| --- | --- |
| Vendor bulk endpoint format | Partially observed, not decoded. |
| Software sensor writes | Appear to use vendor bulk traffic and likely require host services. |
| Current and power live-unit scaling | Raw fields decoded but engineering units still unknown. |
| Flow scaling | Raw field decoded, calibration relationship not fully documented. |
| LED controller entry layout | Large area present in settings; only strip brightness/flags are currently useful. |
| Mode `4` details | Known to mean use/mirror another controller, but source mapping is not complete. |
| Firmware compatibility | Layout confirmed on firmware `1033`; plugin history references `1032`. |
