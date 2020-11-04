[TOC]

# Results
Results shows ranked riders in the race.  Riders are ranked first on distance covered (most laps), then by finish order (shortest time).

CrossMgr shows the finish time, gap and speed (if lap/race distances are configured in Categories).  If a rider has been lapped, the Gap column shows the number of laps down instead of the time gap.

There is a peculiar special case that can happen in multi-category races.  In a multi-category race, some riders may finish having been lapped by the leader of a faster category, but not lapped by their own category leader.

Although these riders has completed one less lap than their category leader, they technically are not lapped.  It is therefore impossible to compute a Gap time, nor is if fair to report those riders as down a lap.  In this case, CrossMgr simply shows nothing in the Gap column.

# Screen
The top of the screen contains controls.

The bottom is divided into two parts with an adjustable pane between them.  The left side shows data about the rider (finish order, Bib, name, team, license, finish time, speed, etc.).  The right side shows individual lap information.

In Time Trial mode, the Start and Finish times (in race time) are also shown.

Projected and auto-corrected entries suggested by CrossMgr are highlighed in yellow.  Manually edited times are shown in orange.  Highlights indicate that some adjustment has been made to the times that was not present in the originally collected data.  For more details about why/who/when, double-click on the entry and look at the entry details in RiderDetail.

Clicking on the column header sorts by that column (see below).

# Controls
## Category
Selects the Category of the results.  Category "All" shows results as if all riders were in one category.  This is useful for comparing against manually generated results for the race as a whole.

## Show Rider Data
This toggles whether additional rider data are shown in Results.  If unset, riders' name, team, license, category etc. will not be shown.

## Lap Times
Shows the lap times.  Lap time are computed as the difference between the race times per lap.

## Race Times
Shows the race times per lap.  This is useful to find the leaders for a particular lap for primes or points races.

To find the top riders of a lap:

1. Choose the Race Times option
1. Click on the Lap column header.  This will sort by the Race Times for all riders on that lap.
1. The Lap Winners will be shown in sequence.
1. Click on the lap column header to return to normal ranking.

## Lap Speeds
Shows the speed by lap.  For this feature to work, the Lap Distance must be configured in Categories.

## Race Speeds
Shows the race speed up to that lap in the race.  This is useful to determine how long a race is expected to take.  For this feature to work, the Lap Distance must be configured in Categories.

## Search
Searches for the entered number and highlights it in the Results page.  This is a very useful feature when some asks "what happened to rider XXX?"

## Zoom In/Zoom Out
If you find the text to hard to read (perhaps you are in direct sunlight), or you want to see more information on the screen, you can change the text size by pressing the Zoom In or Zoom Out buttons.

# Results Data

Data about the race is shown.  Data from the [External Excel][]. sheet is also shown.

Column|Description
:-----|:----------
Pos|The position of the rider in the race.  When Category is "All", shows the rider's place with respect to all participants.  When the Category is set, this shows results with respect to that Category only.
Bib|The bib number of the rider
Last Name|Shown if defined in the [External Excel][]. sheet.
First Name|Shown if defined in the [External Excel][]. sheet.
Team|Shown if defined in the [External Excel][]. sheet.
License|Shown if defined in the [External Excel][]. sheet.
Start Time|In Race Time.  Only shown if in Time Trial mode.
Finish Time|In Race Time.  Only shown if in Time Trial mode.
Time|Rider's time.
Gap|Time difference between this rider's finish time and the leader's finish time, with respect to the Category.
Speed (km/h or mph)|The rider's speed.  Only shown is the Distance has been specified in [Categories][].

# Additional Features

## Double-Click
Double-click opens a RiderDetail dialog on the current rider.  This allows adjustments to the rider's status, category and entries.

## Right-Click
Right-click brings up a number of options about what you clicked on:

Option|Action
:-----|:-----
Passings|Jumps to Passings tab with current rider highlighted
RiderDetail|Opens RiderDetail dialog for current rider
Show Photos|Shows photos for the current rider.  See [Properties][] for how to set up a usb webcam to automatically take photos as riders cross the finish line.
Correct...|Correct the current entry
Shift...|Shift current entry forward/backward in time
Delete...|Delete current entry
Swap with Rider Before|Swap current rider's finish time with preceeding rider's finish time
Swap with Rider After|Swap current rider's finish time with the following rider's finish time

Remember, Ctrl-Z is undo!

## Sort by Field
Clicking on any Field header column sort by that column (with the exception of 'Bib', 'Pos', 'Gap', 'Time' and speed).  This allows you to sort by name, team, license, etc. as well as Start and Finish if running in time trial mode.

In time trial mode, it very useful to sort by 'Start' or 'Finish' to check manual results.  In particular, sorting by 'Finish' should match the finish order recorded by a manual timer.

## Sort by Lap
Clicking on the Lap header column will sort the display by that lap, not the finish order.  Lap sort works with the data currently being displayed.  For example, if you are showing Lap Times, the shortest lap time will be sorted to the top.
In square brackets, the rank and bib number are also shown in the sorted column. 

This feature is very useful in the following cases determine the leader of a certain lap (for example, for a prem).  To do so, change the display to "Race Times", then click on the Lap column.  This will show you the current finish order of that lap.

This feature is also important when you need to restart a race after it was stopped, say, based on a course obstruction or weather delay (lightening).  By sorting the riders for the last lap, you can estimate the gaps between them for the restart.  To do so, change the display to "Race Times", then click on the Lap column.  

## Fastest Lap Highlight
The Fastest Lap is always highlighted in green.  This calculation takes the lap distance (both first and subsequent) into account.
