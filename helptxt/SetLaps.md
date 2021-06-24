[TOC]

# Set Laps

__Set Laps__ is a dialog which allows you to change the number of laps easily while a race is underway.

It two columns - __Current__ and __Proposed__.
These provide all the race information you need to make a decision about changing the number of laps in the race.

As you enter a value in the Proposed __Race Laps__, the race information showing the impact of the change will update automatically.
No value in __Race Laps__ tells CrossMgr to compute the number of laps from the race minutes.

When you are satisfied with your change and its impacts, press OK.

The display shows:

Field|Description
:----|:----------
Race Laps|Number of laps in the race.  If the race is run on time, the Race Laps will be computed from the rider's speed.
Winner Time|Estimated winner's finish time.
Winner Time Delta|Difference (+/-) of the winner's time from the scheduled race time.
Last on Course Time|Estimated finish time of the last rider on course.  This takes lapping into account.
Winner Clock|Clock time (time of day) of winner.
Last on Course Clock|Clock time of the last rider on course.  This takes lapping into account.
Race Time Elapsed|Elapsed time of the race.
Race Time To Go|Estimated time until the winner's finish.
Laps Elapsed|Laps current and completed.
Laps To Go|Laps for the winner to go.
Laps Total|Laps Elapsed + Laps to Go.

__Reminder:__  If no __Race Laps__ are specified for a Start Wave, CrossMgr will run the race on time (see [Categories][] for details).
If __Race Laps__ is set, CrossMgr will run the race according to the Race Laps and will ignore the __Race Minutes__.

Changes from an __OK__ in the __Set Laps__ dialog will be immediately applied to the race.
