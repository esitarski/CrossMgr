[TOC]

# Animation
Animation shows an animation of riders in the race.  While a race is running, it shows the projected rider's progress in real time.
After a race has finished, the race can be played back in fast-forward.

The default display is a oval track, however, you can also import a GPX file of the actual race course (see [Properties][]).

The top three riders are shown on a leader board (5 in GPX display), and you can enter additional riders you wish to highlight and show on the leader board.

# Screen
The top of the screen contains controls, followed by an idealized race course, including the start/finish line.

# Controls
## Category
Selects the Category of the animation.  Category __All__ will show all riders.

## Finish on Top
Draws the animation with the finish line on the top of the screen rather than on the bottom.
Use this option to give a better approximation of the course layout.
Html output will respect this option.
This option can also be changed in [Properties][].
Does not apply in a GPX display.

## Reverse Direction
Changes the direction of the animation.
Use this option to give a better approximation of the direction of prevailing turns in the race.
Html output will respect this option.
This option can also be changed in [Properties][].
Does not apply in a GPX display.

## Rewind
Rewinds the animation to the beginning.  Not operable while the race is running.

## Play/Stop
Controls the animation.  Not operable while the race is running where riders are shown in real-time.

## Playback Speed
Controls the speed of the playback (slowest to fastest).  Not operable while the race is running where riders are shown in real-time.

## Highlight Numbers
Highlights a list of comma-separated numbers, both in the animation and on the leader board.
The leader board shows the current position of the highlighted riders during the race, in addition to the top three (gold, silver and bronze).

For example, say a rider says he finished in 3rd place, but was ranked 5th.  The rider does not believe that two riders passed him during the race.
By highlighting all the riders in question and running the animiation, you can show exactly when and how the rider was overtaken.

# Animation Area

## Track

Shows an animation of the riders on an idealized course.
A leader board is shown in the middle.
Laps completed is shown in the center, and race time is shown at the bottom right.

Riders are shown in the track based on their average speed for each lap.

## GPX Course

If you upload a GPX Course, the animation will show the riders based on the GPX coordinates and lap times (see [Properties][] for details).

If the GPX course has elevation data in it (most do), CrossMgr uses it to compute the % grade between every segment.
Based on the grade, it uses a power curve to change the rider's animation speed.
The riders will appear to slow down on climbs and speed up on descents.

This is a trick as CrossMgr has no data inside a lap.
For example, say a rider has a flat.
In reality, the rider is at full speed, gets the flat at some point, then continues at full speed after the flat is fixed (perhaps in the feed/tech/pit zone).
Since CrossMgr only knows the time of the beginning and end of the lap, it animates based on the average speed of the lap.
It it cannot show where the mechanical occured or when it was fixed.
