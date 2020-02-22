[TOC]

# Restart
Enables a Mass Start race to be restarted (it is not possible to restart a time trial).

The scenario is as follows:

* a race is running
* the race is stopped (crash, weather, course obstruction, etc.)-*
* the stoppage is addressed
* the race is restarted manually - possibly with time gaps between groups of riders.
* the laps before the restart are combined with the laps after the restart
* it may be necessary to shorten the race (reduce the laps, or reduce the race time) after the race is restarted
* a race may be stopped and restarted more than once

The CrossMgr Restart feature supports this scenario.

# Procedure
To Restart a Mass Start race:

1. Switch to the [Passings][] and select the __Time Down per Lap__ option.  Decide which lap you consider to be the __Last Lap__ before the restart (ignore cooldown laps and other noise).  With the __Time Down per Lap__ option, it is easy to see the race composition. This is useful to restart riders with time gaps, if you so choose.
1. Select __Tools|Restart Race__.  If you have not already __Finished__ the current race, you will be prompted to do so.
1. Choose the __Restart After Lap__ you previously decided to restart the race from.
1. Adjust the __RFID Delay after Restart__ if necessary in case the default doesn't work doesn't work for you (see below).
1. When you have organized the riders for the restart (all together or in time-offset groups) and are ready, press __Restart Now__ and confirm.
1. The riders contine the race.  Any RFID reads during the __RFID Delay after Restart__ will be ignored.
1. If you need to shorten the race (reduce laps, reduce race time), you can do so in the [Categories][] screen.  This can be done before or after the Restart.

### RFID Delay after Restart

At the restart, riders will likely be staged at the finish line near the RFID reader.  When the Restart is triggered, you do not want those riders to trigger RFID reads - you only want to recording reads at the end of the restart lap.

During the __RFID Delay after Restart__, RFID reads will be ignored.  This allows the riders to get away from the finish line RFID reader so they do not create meaningless reads .

This value defaults to 75% of the average lap time up to a maximum of 5 minutes.
You may need to adjust __RFID Delay after Restart__ depending on your start gaps.

## Can I Undo a Restart?

It is possible to Undo after a Restart.
To do so, you first Finish the race from [Actions][], then hit Ctrl-Z.
RFID reads during __RFID Delay after Restart__ will not be included.

Be careful.
