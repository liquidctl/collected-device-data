

First capture file: cap1.pcapng

In this file there are the requests and responces from the liquidctl commands
- status
- fan speed 20 20 40 70 50 100
- led superfixed 8 colors


This is an attempt to find if any command causes the color cycle mode to be changed

can pull out only the fields with the following command:



tshark -r  cap1.pcapng -2 -R "usb.capdata" -e "usb.capdata" -T json



in capture 2 it is from the windows OS booting and icue starting.
on setup I beliuve it adjusts 
- the fan curves to quiet
- the pump to balanced
- sets the LED mode to solid
- sets other register values
- sets the leds to solod white as per the icue not open state




- check the change in the values of the status response that are unknown to see if any of them are the LED modes
- also check for any unknown commands (aside from the periodic get status message with an empty payload)

these repeated status requests can be filterd by greping them out (requires calculating all of the sequence numbers that they are expected to have as there are some bitmasked sequence numbers that would be important)

cap 3 
open icue
lighting mode changged to the normal lighting mode
new profile got crreated
leds  tuened off


This command will filter out all of the basic get status commands and the basic set color commands

$ tshark -r  cap3.pcapng -2 -R "usb.data_fragment" -e "usb.data_fragment" -Tfields | grep -v -E "^3f[0-9a-f][08]ff0+..$" | grep -v -E "^3f[0-9a-f][45cd]"| sed 's/^\(3f..\)\(.*\)\(..\)$/\1:: \2 :\3/'




From the captures when the LED controller gets set there seems to be a magic set of 3 packets that get sent with the general form of

(from cap4)
0101ffffffffffffffffffffffffff7f7f7f7fff00ffffffff00ffffffff00ffffffff00ffffffff00ffffffff00ffffffffffffffffffffffffffffff
000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f2021222324252627ffffffffffffffffffffffffffffffffffffffffff
28292a2b2c2d2e2f303132333435363738393a3b3c3d3e3f404142434445464748494a4b4c4d4e4fffffffffffffffffffffffffffffffffffffffffff

(from cap3)
0101ffffffffffffffffffffffffff7f7f7f7fff00ffffffff00ffffffff00ffffffff00ffffffff00ffffffff00ffffffffffffffffffffffffffffff
000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f2021222324252627ffffffffffffffffffffffffffffffffffffffffff
28292a2b2c2d2e2f303132333435363738393a3b3c3d3e3f404142434445464748494a4b4c4d4e4fffffffffffffffffffffffffffffffffffffffffff



with the command masks of
0b001
0b010
0b011

respectivly



after these messages get sent the LED commands seem to work as expected


