# RPICT4V3-Power-Monitor

This project enables monitoring of A/C power usage from two devices.  In my case, I am monitoring a stove and dryer.  The code runs on a Raspberry Pi using Python 3.5.  The reading of the power is done with a RPICT4V3 device attached to the Pi and two SCT-013-000 current sensors attached to the RPICT4V3.

When the stove is turned on, at any power level and any burner, the code makes note of the ON time, then keeps monitoring.  If the stove is still on 20 minutes later, it sends an SMS message using Twillio to my personal number.  The message states that the stove is on, how long it has been on, and the power usage. Until the stove is turned off, it will keep sending an update SMS message every 20 minutes.

The code also logs the On and Off times for the stove to a log file.
