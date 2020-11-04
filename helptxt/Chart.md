[TOC]

# Chart
Results shows ranked riders in the race as a Gantt Chart.  Riders are ranked first on distance covered (most laps), then by finish order (shortest time).

The relative lap times are shown as bars on the graph.  This is an important view to understand the entire data of the race and whether it is correct.  You will find that this is the first view you will look at when trying to make sense of a race.

Missing data and errors are easy to see.

# Screen
The top of the screen contains controls, followed by the race Gantt Chart.

The Gantt chart shows the lap times graphically as horizontal bars.
Rider that have been pulled, DNF or DNS are shown greyed-out at the bottom.

The endpoints of the bars may have indicators:

Indicator|Meaning
:--------|:------
Diamond|Indicates a CrossMgr auto-corrected time that did not appear in the original input.  CrossMgr automatically generates missed times when it thinks it is reasonable to do so
Star|Indicates a User Edit of the original input.  Changes made by users are logged and timestamped (see RiderDetail).
Red Circle|Indicates a duplicate time.  Although rare, times may be entered more than once for the same lap.  For example, a number caller might turn around see the numbers on the backs of riders and call the same number twice.  CrossMgr's Auto-Correct will take care of these, but you will see them if you turn Auto-Correct off.  To fix this situation manually, delete one of the duplicates.  A time is considered a duplicate if it results in a lap that is less than 15 seconds.

# Controls
## Category
Selects the Category of the chart.  Category "All" will show results as if all riders were in the same category.  This is useful for comparing against manually generated results for the race as a whole.

Additionally, there are some statistics shown:

Value|Description
:----|:----------
Total Entries|The total number of data entries in the race
Projected|The number of projected entries (yellow diamonds)
Edited|The number of edited entries (orange stars)
Projected or Edited|The sum of projected and edited entries
Photos|The number of photos triggered in the race when the [USB Webcam][] was enabled.  CrossMgr cannot determine whether the photo was recorded or not, it can only count the number of photo triggers sent.

# Additional Features

## Double-Click
Double-click opens a RiderDetail dialog on the current rider.  This allows adjustments to the rider's status, category and entries.

## Right-Click
Right-click brings up a number of options about what you clicked on:

Option|Action
:-----|:-----
Add Missing Split|Adds missing split times to the lap.  This adds the specified number of times at equal intervals in the lap.  This is the easiest way to correct missing reads.  For example, if there is a missing entry, you will see a lap that is 2x longer than what is should be.  To fix this, you would add one missing split.  Another example is that a rider's number gets muddy, and it takes three laps to figure out who it is.  As you missed this rider for 3 laps, you would add three missing splits.
Pull After Lap End...|Pull this rider and set the pulled time to be just after this lap.
DNF After Lap End...|DNF this rider and set the pulled time to be just after this lap.
Note...|Add a note to this lap.  The note is displayed on the lap in the Chart.  Use this if you want to make a note for yourself about the lap.
Correct Lap End Time...|Correct the lap end time
Shift Lap End Time...|Shift the lap end time forwards or backwards
Delete Lap End Time...|Delete the lap end time
Mass Pull after Lap End Time...|Pulls this rider, and all riders ranked lower in the results after this end time.  Useful when you have a separate sprint for the field in a Criterium and you need to remove the laps of all riders except those in the break.  
Turn off Autocorrect...|Turn off Autocorrect for this rider
Swap with Rider before|Swap current rider's finish time with preceeding rider's finish time
Swap with Rider after|Swap current rider's finish time with the following rider's finish time
Show Lap Details...|Shows the details of the lap.  This includes the lap start, end, time, time down, and any reasons for changes to the start or end of the lap.
RiderDetail|Opens RiderDetail dialog for current rider
Results|Jumps to Results tab with current rider highlighed

Remember, Ctrl-Z is undo!  (Ctrl-Y is redo).
