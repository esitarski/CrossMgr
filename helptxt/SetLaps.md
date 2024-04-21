[TOC]

# Set Laps

__Set Laps__ is a dialog which allows you to change the number of laps easily while a race is underway.

It is accessible from the [Categories][] by clicking on "&#x27F3;", [Record][] by clicking on the race progress bar at the bottom of the screen and [LapCounter][] by clicking on the lap number.

__Set Laps__ only opens __when the race is running.__  If the race is not started or is finished, it doesn't come up.

It shows two columns: __Current__ and __Proposed__.
These provide all the race information you need to make a decision about changing the number of laps in the race.

As you enter a value in the Proposed __Race Laps__, the race information showing the impact will update automatically.
No value in __Race Laps__ tells CrossMgr to compute the number of laps from the race minutes.

When you are satisfied with your change, press OK.  This will immediately apply the change to the race.
You can seen the changes on the [Record][] screen and the [LapCounter][].

The display shows:

Field|Description
:----|:----------
Race Laps|Number of laps in the race.  If Race Laps is not specified, the race is run on time, and CrossMgr will compute the laps based on the lap times.
Winner Time|Estimated winner's finish time.
Winner Time Delta|Difference (+/-) of the winner's time from the scheduled race time.
Last on Course Time|Estimated finish time of the last rider on course.  This takes lapped participants into account as appropriate.
Winner Clock|Clock time (time of day) of winner.
Last on Course Clock|Clock time of the last rider on course.  This takes lapped participants into account as appropriate.
Race Time Elapsed|Elapsed time of the race.
Race Time To Go|Estimated time until the winner's finish.
Laps Elapsed|Current and completed laps.
Laps To Go|Laps to go for the winner.
Laps Total|Laps Elapsed + Laps to Go.
Early Bell Time|Race time of the __Early Bell__ (see Notes). The can be set with the __Tap for NOW__ button.

__Notes:__  If __Race Laps__ is unspecified for a Start Wave, CrossMgr will run the race on time (see [Categories][] for details).
If __Race Laps__ is set, CrossMgr will run the race according to the Race Laps and will ignore __Race Minutes__.

If the __Early Bell Time__ is set, all riders after this time will be treated as if they on their last lap.
To disable __Early Bell Time__, delete it and press __OK__.

__Early Bell Time__ is a great way to keep a competition on schedule.  Consider setting __Early Bell Time__ about three quarters through the 2nd last lap.
Any riders after the __Early Bell Time__ will get the bell and start their last lap (potentially doing one lap less).
Riders who are out of contention know they have one lap to go.

Pressing __OK__ from __Set Laps__ will apply any changes.  The race [Record][] and [LapCounter][] will update immediately.
If the __Early Bell Time__ is set, the Bell and Finish Flag icons will update.
Riders starting their last lap have a bell (🔔), riders finishing has a finish flag (🏁).  See [MainScreen][].
