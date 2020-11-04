[TOC]

# Lap Counter and Countdown Timer
Shows a __lap counter__, or a __countdown timer__ for the race.  The lap counter flashes before it changes to draw attention to itself.

The Lap Counter is also available on a web page that can be displayed on any computer connected to the CrossMgr wifi.  See [Web][] for details on the web-based Lap Counter.

Use:

1. Create a separate __LapCounter__ screen from the __Windows__ menu.
1. Drag the __LapCounter__ screen to separate monitor.
1. Set up the monitor so the riders can see it.

_Lap Cycle__ cycles through laps for the duration of the race.
For example, if __Lap Cycle__ is set to 3, the lap counter will show 2, 1, 0, 2, 1, 0 etc. for the duration of the race.  The last 1 will be on the last lap.
This is useful for Elimination races.

## Lap Counter Function

The LapCounter function relies on CrossMgr's ability to predict the leader.  Be default, it flips the lap counter 15 seconds before the leaders are expected.  There are a few considerations:

1. Without any data, CrossMgr has no method to predict the first lap time.  The LapCounter will start working after the first data entry.  This means the leader(s) will not see anything on the lap counter for the first lap, but all other riders will see the correct lap count.  This is fine in a timed Cyclo-cross race, but may an issue for MTB or Road races, especially with a small number of laps.
1. If the first lap is a different distance than subsequent laps (due to a start area/run up), the LapCounter may not be correct until lap 3.  This is because CrossMgr has no timing information about lap 2 until the leaders are recorded.
1. If the riders significantly speed up during a lap, they can get to the finish before CrossMgr expects them, and the lap counter will not have been changed early enough.

To address (1) and (2), consider not showing the lap counter until the 2nd or 3rd lap of the race.  This also gives the riders some time to find their pace after the chaos of the first lap as riders establish themselves.

Of course, if the race is 2 laps, just bell the riders on their second lap.

(3) generally only happens if the lap time is less than 3 minutes.  On longer lap times, rider's sprint and recovery intervals tend to cancel out and they stay closer to their average lap speed.  Riders also tend to slow down slightly lap-per-lap, so arriving earlier tends not to happen.

For Cyclo-cross, MTB and Road races longer than 2 laps, the automatic lap counter works fairly well.  The longer the lap time, the more in advance the lap counter can be flipped.  This also helps to solve the problem with riders arriving early, but can create a problem if some riders are just about to be lapped on their last lap.

If the lap time is short and highly variable, like a criterium (especially with primes) or a track race, the automatic lap counter may not work well.   CrossMgr will by unable to predict the rider's arrival times accurately.

## Countdown Timer Function

Select this option by right-clicking on the LapCounter screen and choosing __Countdown Timer__ instead of __Lap Counter__ from the options.

After the race starts, this feature will show the time remaining based on the __Race Minutes__ configured in [Properties][].

After the __Race Minutes__ time has expired, the __Countdown Timer__ will begin to count up with a __+__ sign.

You can start with the __Countdown Timer__, then switch to the __Lap Counter__ when the number of laps stabilizes.

When CrossMgr gets busy, the seconds in the __Countdown Timer__ may not be updated perfectly regularly.  Sometimes it might skip a second, or a second might be shown a little longer or shorter than expected.  Do not be alarmed - the timer follows the computer's clock and it will correct itself to the accurate countdown time.

# Screen
Shows a Lap Counter.

If you are running the race by time, one lap counter is shown and follows the category doing the most laps.

If you have categories with specified __Race Laps__ (see [Categories][] for more details), a separate lap counter will be shown for each category.

Right-click on the Lap Counter screen to set options.  You can change the foreground and background color, as well as the seconds before the expected leader to change the lap counter.

* 5 seconds before the Lap Counter changes, it will flash with the current lap count.
* After 5 seconds, it will switch to the new lap count.

This draws attention to the lap counter just before it changes.
