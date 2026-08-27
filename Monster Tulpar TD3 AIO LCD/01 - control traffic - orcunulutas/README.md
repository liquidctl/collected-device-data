# Monster Tulpar TD3 AIO LCD — capture 01

USB traffic captures of the Monster Tulpar TD3 AIO LCD controller, recorded
while the official Monster Windows application was running. This is the raw
data from which the device control protocol implemented in liquidctl
([liquidctl/liquidctl#921]) was reconstructed.

Media upload traffic (on-screen display file transfers, the `0x5c`-prefixed
block records and their `POST transport 1` / `POST transported 1` framing)
has been removed from these files and is not included here.

## Device

- USB ID: `1d6b:0130`
- Manufacturer string: `Monster Inc.`
- Product string: `Monster USB Device`
- bcdDevice: `0x0100`
- Device class: HID (`bInterfaceClass = 0x03`)
- Data endpoints: interrupt OUT `0x01`, interrupt IN `0x81`

## Capture environment

- OS: Windows 11 25H2 (build 26200)
- Capture backend: USBPcap (pcapng, LINKTYPE 152 / USBPcap header)
- Capture date: 2026-08-21 (all timestamps UTC+03)
- Host software: official Monster application, active for the whole session

Note: the files were filtered down from full-bus captures; they contain only
the traffic of the target device (USB device address 8). Traffic of other
devices on the bus was removed.

## Files

| File                         | Time range (UTC+3)    | Duration | Packets (after media removal) | Content |
|------------------------------|-----------------------|----------|-------------------------------|---------|
| `monster-td3-usbpcap.pcapng` | 15:07:34 – 15:07:44   | 9.8 s    | 517                           | enumeration, control framing |
| `monster-td3-usb2.pcapng`    | 15:12:00 – 15:12:32   | 31.8 s   | 262                           | brightness + rotate commands with device responses |
| `monster-td3-usb3.pcapng`    | 15:15:07 – 15:17:03   | 116 s    | 643                           | enumeration, keep-alive polling |

## Observed traffic

### Control commands (`monster-td3-usb2.pcapng`)

The only file containing host-initiated control commands, after media removal:

- `POST rotate 1` with `{"degree":...}` (2 commands);
- `POST brightness 1` with `{"value":...}` (2 commands);
- the corresponding device responses (`1 200` / `AckNumber`).

### Keep-alive behavior

The official Windows application keeps the LCD awake by uploading a fresh
`.osd` on-screen display file approximately once per second — i.e. the
observed Windows keep-alive is implemented through media upload. Because
media transfers were removed from these files, `monster-td3-usb3.pcapng`
(the 116 s session) contains only the accompanying interrupt polling and
enumeration traffic, not `POST power` / `STATE all` style messages. The
`POST power` / `STATE all` control-path keep-alive documented in
`docs/developer/protocol/monster_lcd.md` (liquidctl) was reconstructed from
separate Linux testing, not from these Windows captures.

### Media upload (not included)

`.osd` files were pushed over interrupt OUT `0x01` in 1024-byte blocks framed
by an HTTP-like envelope (`POST transport 1` ... `POST transported 1`, with
`SeqNumber`, `Date`, `ContentType`, `ContentLength` headers and JSON metadata
such as `{"type":"media","fileSize":985,"fileName":"....osd"}`). This traffic
is intentionally excluded from the files above; contact the contributor if a
reference copy is needed.

## See also

- liquidctl driver: [liquidctl/liquidctl#921]
- Protocol documentation: `docs/developer/protocol/monster_lcd.md` (in the PR above)
- Standalone Linux implementation: <https://github.com/orcunulutas/monster-td3-aio-lcd-linux>

[liquidctl/liquidctl#921]: https://github.com/liquidctl/liquidctl/pull/921
