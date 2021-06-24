[TOC]

# Set Laps

__Set Laps__ is a dialog which allows you to change the number of laps easily while a race is underway.

It shows two columns - __Current__ and __Proposed__.
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

__Note:__  If no __Race Laps__ is specified for a Start Wave, CrossMgr will run the race on time (see [Categories][] for details).
If __Race Laps__ is set, CrossMgr will run the race according to the Race Laps and will not calculate the laps based on __Race Minutes__.

Changes from an __OK__ in the __Set Laps__ dialog will be immediately applied to the race.
