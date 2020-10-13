# Breakdown of known communication protocol for the Corsair H100i Platinum AIO cooler


General types of commands
- set fan speeds and pump speed
- set LEDs to specific colors
- get the cooler status
- magic packet to be able to set individual led values

All commands that are sent have a total of 64 bytes, the first is a known prefix and the last is a checksum value.

Byte fields start at position 0.


#### Table of key values

| Name | value | description |
| ----- | ----- | -------- |
| _PREFIX | `0x3F` | The first byte in all message sent to the cooler |
| _STATUS_COMMAND | `0xFF` | The command byte to get the status of the cooler. |
| _COOLING_COMMAND | `0x14` | The command to set the fan and pump speeds |
| _LIGHT_1 | `0b100` | The first sequence of setting the LED values |
| _LIGHT_2 | `0b101` | The second sequence of setting the LED values |
| _LIGHT_3 | `0b110` | The third sequence of setting the LED values |
| PROFILE_LEN | `0x07` | The number of (temp, fan) speed pairs in a fan curve |

#####  Sequence number

The sequence number is a one byte value that is based on an incrementing number in the range of `[1, 31]`. However, instead of using this value directly it is shifted to the left by 3 bits and sometimes masked with a command operator.

As Hex values the sequence number typically looks something like: `08`, `10`, `18`, `20`. (or fits the regex pattern `[0-91-f][08]`).

The value is incremented with every command that is sent to the device.

#### Get status command

This message is sent by icue periodically (around once per second) to get the liquid temperature value, and the fan speeds.

| 0   | 1   | 2   | 3 .... 62 | 63  |
| --- | --- | --- | --------- | --- |
| _PREFIX | SEQ | _STATUS_COMMAND | 00 | CHECK |



#### Set LEDs to specific colors

This is a multi message command. The number of messages is dependant on the number of LEDs that are available to be set. Each command message is capable of setting the RGB value for `20` LEDs. Without swapping out the fans the H100i Platinum cooler has `24` LEDs `16` on the pump and `4` on each of the 2 `ML` type fans (the `HD` fans have 12 LEDs each, and the `LL` fans have 16 LEDs each).



The `LED_COMMAND` is set to `_LIGHT_[123]` depending on which message number it is. to set LEDs 1-20 it is `_LIGHT_1`, 21-40 it is `_LIGHT_2`, 41-60 it is `_LIGHT_3`. Note that if you only want to set LED1 and leave the rest as is, not sending the other message will result in the LEDs being turned off.


| 0   | 1   | 2 .... 61 | 62 | 63  |
| --- | --- | ----------- | --- | --- |
| _PREFIX | SEQ `\|=` LED_COMMAND| \<BB\> \<GG\> \<RR\> | 00 | CHECK |


LED ordering
- 1-4  : interior of the pump
- 5-15 : exterior ring of the pump (clockwise from bottom right corner)
- 16-19: fan 1
- 20-24 : fan 2


#### Set Fan and Pump speeds


The values for `PUMP_MODE` are:

| value | description |
| ----- | ------ |
| `0x00` | QUIET |
| `0x01` | BALANCED |
| `0x02` | EXTREME |

The values for `FAN[12]_MODE` are:

| value | description |
| ----- | ------ |
| `0x00` | CUSTOM PROFILE |
| `0x01` | CUSTOM PROFILE external sensor |
| `0x02` | FIXED duty |
| `0x04` | FIXED rpm |


| 0   | 1   | 2   | 3   | 4   | 5   | 6   | 7   | 8   | 9   | 10  | ... |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| _PREFIX | SEQ | _COOLING_COMMAND | 00 | FF | 05 | FF | FF | FF | FF | FF | ... |



| 11  | 12...15  | 16  | 17   | 18...21 | ... |
| --- | --- | ---  | ---- | ---  | --------
| FAN1_MODE | XX  | FAN1_const | FAN2_MODE | XX | ... |


| 22  | 23 | 24...28 | 29  | 30...43 | 44...58 | 59.... 62 | 63  |
| --- | --- |------- | --- | ------- | ------- | --------- | --- |
| FAN2_const | PUMP_MODE | XX| PROFILE_LEN | 7 fan1 \<Temp\> \<percent\> pairs | 7 fan2 \<Temp\> \<percent\> pairs | XX | CHECK |



#### magic packet to be able to set the RGB LEDs

The exact purpose of this message is unknown but sending this payload allows the set LED commands to function properly. Some of the fields are different in some messages but the differences seem small and unimportant.

| _ENABLE_1 | `0b001` | The first sequence |
| _ENABLE_2 | `0b010` | The second sequence |
| _ENABLE_3 | `0b011` | The third sequence |



| 0       |        1            | 2 .... 62 |  63  |
| ------- | ------------------- | ----------- | --- |
| _PREFIX | SEQ `\|=` _ENABLE_1 | `0101ffffffffffffffffffffffffff7f7f7f7fff00ffffffff00ffffffff00ffffffff00ffffffff00ffffffff00ffffffffffffffffffffffffffffff` | CHECK |

| 0       |        1            | 2 .... 62 |  63  |
| ------- | ------------------- | ----------- | --- |
| _PREFIX | SEQ `\|=` _ENABLE_2 | `000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f2021222324252627ffffffffffffffffffffffffffffffffffffffffff` | CHECK |

| 0       |        1            | 2 .... 62 |  63  |
| ------- | ------------------- | ----------- | --- |
| _PREFIX | SEQ `\|=` _ENABLE_3 | `28292a2b2c2d2e2f303132333435363738393a3b3c3d3e3f404142434445464748494a4b4c4d4e4fffffffffffffffffffffffffffffffffffffffffff` | CHECK |



## Response messages

All messages have the same response format.


| 0       |  1  | 2          | 3          | 4   | 5           | 6           | 7           | 8          |  9...14 | 15 | 16 | 17...21 | 22 | 23 | 24...28 | 29 | 30 | 31...62 |  63  |
| ------- | --- | ---------- | ---------- | --- | ----------- | ----------- | ----------- | ---------- | ----- | ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| _PREFIX | SEQ | FIRMWARE_1 | FIRMWARE_2 | 00  | COUNTER_LSB | COUNTER_MSB | liquid temp | liquid temp | XX    | Fan1 speed | fan1 speed | XX | fan2 speed | fan2 speed | XX | pump speed | pump speed | XX | CHECK |  
