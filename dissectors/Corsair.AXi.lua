--[[
  Dissector for the USB protocol used by Corsair AXi PSUs.

  Work in progress.

  The protocol uses a balanced code with 569a nibbles.[1]

  This dissector does not distinguish between AXi PSUs and other USB devices.
  Disable the dissector when looking at data from non AXi devices.

  Copyright 2021  Jonas Malaco and contributors.
  SPDX-License-Identifier: GPL-3.0-or-later

  [1] https://github.com/ka87/cpsumon/blob/fd639684d7f9/libcpsumon/src/cpsumon.c#L80-L123
]]

local p = Proto("Corsair.AXi", "Corsair AXi PSU Protocol")

p.fields = {}
p.fields.original = ProtoField.bytes("axi.original", "Original", base.COLON)
p.fields.decoded_payload = ProtoField.bytes("axi.decoded_payload", "Decoded payload", base.COLON)

-- Map input nibbles to 569a-encoded output bytes.
local encode569a = {
[0]=0x55, 0x56, 0x59, 0x5a,
    0x65, 0x66, 0x69, 0x6a,
    0x95, 0x96, 0x99, 0x9a,
    0xa5, 0xa6, 0xa9, 0xaa
}

-- Map 569a-encoded output bytes back into input nibbles.
local decode569a = {}
for i = 0, 15 do
  decode569a[encode569a[i]] = i
end

-- Return a ByteArray decoded from a 569a-encoded range.
-- The caller must ensure that the range has an even number of bytes.
function decode569a_buffer(range)
  local ret = ByteArray.new()
  ret:set_size(range:len() / 2)
  for i = 0, range:len() - 2, 2 do
    lsn = decode569a[range(i, 1):uint()]
    msn = decode569a[range(i + 1, 1):uint()]
    ret:set_index(i / 2, bit.bor(bit.lshift(msn, 4), lsn))
  end
  return ret
end

-- Actual AXi dissector
function p.dissector(buffer, pinfo, tree)
  if buffer:len() == 0 then
    return
  end

  local subtree = tree:add(p, buffer(), p.description)

  subtree:add(p.fields.original, buffer(0, buffer:len()))

  if buffer:len() % 2 == 0 and buffer:len() >= 4 then
    local payload = decode569a_buffer(buffer(1, buffer:len() - 2))
    local payload_tvb = ByteArray.tvb(payload, "Decoded payload")
    subtree:add(p.fields.decoded_payload, payload_tvb(0, payload:len()))
  end
end

-- Register the dissector
DissectorTable.get("usb.bulk"):add(0xff, p)
