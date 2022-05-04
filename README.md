# RPICT4V3-Power-Monitor

This project enables monitoring of A/C power usage from two devices.  In my case, I am monitoring a stove and dryer.  We have had our kids leave the stove on accidentally and wanted a way to be notified if this happens in the future.

The code runs on a Raspberry Pi using Python 3.5.  The reading of the power is done with a RPICT4V3 device attached to the Pi and two SCT-013-000 current sensors attached to the RPICT4V3.

When the stove is turned on, at any power level and any burner, the code makes note of the ON time, then keeps monitoring.  If the stove is still on 20 minutes later, it sends an SMS message using Twillio to my personal number.  The message states that the stove is on, how long it has been on, and the power usage. Until the stove is turned off, it will keep sending an update SMS message every 20 minutes.

The code also logs the On and Off times for the stove to a log file.

The power consumption is sent from the RPICT4V3 to the Pi via serial port.  Readings are sent every five seconds, so the code averages the last ten readings and considers the stove turned on if the current is over a threshold (determined experimentally).  Most stoves on low heat simply cycle on and off, so averaging the readings over the past 50 seconds is a fairly reliable way to determine whether the stove is on.  This does mean there is a delay in determining when the stove was turned on, but my concern is only when the stove is on for an extended time.
