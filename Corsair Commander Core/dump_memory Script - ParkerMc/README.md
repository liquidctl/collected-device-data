# dump_memory Script

This is a really simple script to take what we know of the protocol and just dump every thing in the commander core's memory.

The script has a list(`_DUMP_MODES`) of all known modes. It takes this list and reads the data from all these modes and exports it to `dump.csv`
This script is especially useful when using looking at a diff from before and after a change. 
