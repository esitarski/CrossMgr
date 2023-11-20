[TOC]

# RiderDetail
RiderDetail shows details about an individual rider.
If is also used to enter the Status of riders that do not have any time entries.

For example, if you want to show that a rider did not start (DNS), you can type in the number, change the Status to DNS, and press Enter.

# Screen
The top of the screen shows specific rider details.

The bottom is divided into two parts with an adjustable pane between them.  The left side shows the time entries of the rider, and right side shows a Gantt chart showing the riders laps, and a line graph showing the rider's time per lap.

## Rider Details (top of screen)

This section shows a table of the rider information.  Much of this information comes from the [External Excel][] sheet.

Field|Description
:----|:----------
Number|Bib number of the rider.  You can also type in the number of the rider you wish to see.
Name|Name of the rider
Team|Team of the rider
Tag(s)|Chip timing tags
Category|The Category of the rider matched by the number ranges in the Categories screen.  If you change the rider's category here, it will automatically add a number exception to the Category number ranges.
Status|The status of the rider.  More details below.
Autocorrect Lap Data|If True, CrossMgr will look for duplicate and missing entries and correct them.  It will also project lap times for the rider for the entire race.  If False, CrossMgr will present all entires exactly as input.
Recommendations|Any recommendations CrossMgr has about this rider that you might want to consider.
Start|In Time Trial mode, shows the start time of the rider.
Finish|In Time Trial mode, shows the finish time of the rider.
Time|In Time Trial mode, shows the rider time of the rider.
Adjust Time Trial Times...|In Time Trial mode, opens a dialog to adjust the Start Time, End Time and Penalty Time of the rider.  If you add a Time Penalty, it will also be visible in the Recommendations screen.  Double-clicking on any Recommendation will open the Rider Detail page again.

Turning off Autocorrect for all riders has major implications for CrossMgr.  Without Autocorrect, CrossMgr cannot reliably count laps, display laps to go, or show the race progress.
It is recommended that you have Autocorrect on for the race leader.

Rider Status has the following values:

Status|Description
:-----|:----------
Finisher|This rider is a Finisher and is ranked in the results.  Riders can finish the race and not complete the same number of laps as the leader.
DNF|This rider is a DNF (Did Not Finish).  DNF riders are not ranked, however, they are shown in the results in order of Race Time (the following field).
PUL|This rider was pulled by race officials but will still be shown in the results.  DNF riders are ranked by laps completed, then by PUL time (the following field).  It is easy to 
DNS|This rider Did Not Start (DNS)
DQ|This rider was disqualified (DQ)
OTL|This rider was eliminated due to being Outside the Time Limit (OTL)
NP|This rider was not placed.  This can be used as a place-holder when the finish status of the rider cannot be determined.

In the results, riders are ranked in order of Status: 

1. Finisher
1. OTL
1. DNF
1. DQ
1. DNS
1. NP

PUL riders are shown as __Finishers__ in the results, but with the time __Gap__ shown as -1, -2, -3, etc. showing the number of incomplete laps.

__Finishers__ are ranked by distance (laps completed), then time.

### Relegated to
If set, the final position this rider was __Relegated__ in the race.
This is only used to give a relegation penalty (for example, for an improper sprint).

This does not change the rider's finish time, only his/her position in the race finish.

The relegation is indicated by __REL__ which is added to the rider's position in the results in the HTML, Excel and Printed output.

Relegations are with respect to the "Start Wave" (that is, all the riders that are in the same Start Wave), not the Component category within the wave.

Relegations are ignored for "Custom" categories as these may consist of riders that were not riding together in the same start.

For more information about Category Types, see [Categories][].

Checking is done so that relegations "make sense".  For example, if you want to relegate a rider to last place, you can enter __999__ and CrossMgr will figure out what position that would be.

For USAC, UCI, CrossResuls and WebScorer Publish, the rider will be also be given the relegated position.
However, there is no way to indicate this in the output.

### Autocorrect Lap Data
If selected, CrossMgr will try to autocorrect entries.
Autocorrect looks for two types of errors:

1. Duplicate entries.  This can happen manually if the number caller calls the same number twice, or if the chip reader records the same chip multiple times.
1. Missing entries.  This can happen if you miss entering riders, or if the chip reader fails to read the tag.

With autocorrect on, CrossMgr will also project future lap times for riders.

As with all approaches, Autocorrect is not perfect, and sometimes CrossMgr gets it wrong.

If this option is deselected, CrossMgr will not try to autocorrect entries.  This allows you to see the raw input data so that you can correct it manually.
However, it also means that CrossMgr will not be able to project future lap times to show in the "Expected:" window.

Chip timing creates different classes of errors that are not similar to manual input.  Specifically, there can by many "spurious reads" from the chip reader if riders stand around the finish line while other riders are finishing.

You may wish to turn off the autocorrect feature when fixing up data from chip timed race (see the Edit menu documentation).

This is useful if you want to make manual corrections.

For example, say you had a rider who missed a lap due to a flat, but CrossMgr is auto-correcting and inserting the missed lap.  Turn off autocorrect.

#### How does Autocorrect Work?

Autocorrect is at the core of CrossMgr and one of its most important features.  Without it, the slightest error would make it appear to "act crazy".

Autocorrect follows a Bayesian philosophy, and improve its correction ability with more data.  Autocorrection is done for all riders every time and entry is added, delete or changed.

Autocorrect first looks for duplicates.  An entry is considered a duplicate when it would make a lap that was half the time of the average lap time of all riders in the race.

There may be many duplicates in a single lap, however, in Manual mode, they are far less common.  With chip timing, it is easy to get dozens of duplicate reads in a short time if a rider is standing next to the antenna.  In Manual mode, duplicates can occur before or after the actual rider's time.  With Chip timing, they can only occur after the rider has passed the reader.

If there are multiple duplicates, CrossMgr first removes all but the first and last one.  Of the remaining two duplicates, it removes the one that would result in making the previous and subsequent lap as equal as possible.

Second, Autocorrect looks for missing entries.  A missing entry causes a long lap with a lap time that is some integer multiple of the rider's average lap time (double or triple being the most common).  Mathematically:

MissedEntryLapTime &#8776; AverageLapTime &times; &mu;; &mu; &isin; {2, 3, 4, ...}

Where "&#8776;" means "approximately equal to within a reasonable standard deviation".

The first problem is how to compute the Average Lap Time.  We can't compute it from the average of the rider's recorded lap times as these may include missed entries.  The laps will skew the average greatly, especially in races with a low number of laps.
So, we approximate the AverageLapTime by first removing long lap times through an outlier detect process based on the average lap time of all riders in the race.

Let's call this the Outlier-Adjusted Average Lap Time (OALT).

Once the OALT is computed, CrossMgr re-examines the lap times looking for times that are within a reasonable standard deviation of an integer multiple of the OALT, up to 3x.  Laps matching this criteria are "split" into equal portions corresponding to the number of entries missed.  Mathematically, 

MissedEntryLapTime &#8776; OALT &times; &mu;; &mu; &isin; {2, 3, 4, ...}

Checking if this has a reasonable solution for &mu;, given that it is an integer greater than 1.  A slightly different procedure is used for the first lap, as it can be a different length from subsequent laps if there is a start run-up.

If this has a solution, we split the lap into equal portions by adding (&mu;-1) split times.

Once the laps have been corrected, a new overall average is taken (again, adjusting for the first lap).  Additional "projected" laps with average time are added to the end of the last rider's lap.  Projected laps are until the maximum time/laps of the race.

Projected laps are used to indicate the 80% rule, the Expected list in CrossMgr, as well as lap counter and projected finish.

Without outlier detection and lap correction in Autocorrect, projections would be meaningless.  This is why lap projection is not available when Autocorrect is turned off for all riders.

For an example of why projection is dependent on Autocorrect, imagine if there were two duplicate reads for one rider in the first lap of a 60 minute race with a 6 minute lap.

Say that rider did a 6:06 lap.  With the two extra reads, the average lap time will be 2:02.  With an average lap time of 2:02, this would be a 30 lap race, not a 10 lap race.  Of course, this makes no sense to a human.  We would automatically recognize the extra times as duplicates and look for long laps that were multiple of the "average" laps.

As outlined above, CrossMgr knows how to do this mathematically.

### Always Filter on Min Possble Lap Time
If selected, CrossMgr will ignore laps shorter than Min. Possible Lap filter __even if__ Autocorrect Lap Data is off.

Min. Possible Lap Time can be set in [Properties][]

This is especially helpful if you want to filter out spurious RFID reads, but do not want CrossMgr to autocorrect what it believes are missing lap splits.
__Always Filter on Min Possble Lap Time__ has no effect if __Autocorrect Lap Data__ is selected, as autocorrect already ignores laps shorter than Min Possible Lap Time.

## Time Entries (bottom left of screen)

Projected, auto-corrected and manually edited times are shown highlighted in yellow.  This indicates that some adjustment has been made to the times that were not present in the originally collected data.

The time entry table has the following columns:

Column|Description
:-----|:----------
Lap|Lap number
Lap Time|Time of the lap
Race Time|Race time of the entry
Lap Speed|Speed of the lap (distances must be configured in Categories)
Race Speed|Race speed up to that entry (distance must be configured in Categories)
Edit|If this is not an original entered time, this shows what was changed in the field.
By|The computer user who made the change
On|The timestamp that the change was made

### Right-Click
Right-click brings up a number of options about what you clicked on:

Option|Action
:-----|:-----
Correct...|Correct the current entry.  Time may be endered in Race Time or 24 hr Clock Time.
Shift...|Shift current entry forward/backward in time
Delete...|Delete current entry
Pull After Lap...|Pull this rider and set the pulled time to be just after this lap.
DNF After Lap...|DNF this rider and set the pulled time to be just after this lap.

## Edit... Button

Clicking this button shows a number of additional actions than can be performed:

Action|Description
:-----|:----------
Delete Rider from Race...|Delete this rider, and all associated entries, from the race.  Useful if you typed in a wrong number at some point and you want to get rid of it.
Change Rider's Number...|Change the number of this rider.  Useful is the rider got the wrong number at registration and needs to be consitent, say,  in a series.
Swap Number with Other Rider...|Swap this rider's number with another rider's number.  Useful if two riders got their numbers switched at registration.
Merge Rider Times...|Merge times from another rider.  Includes the option to delete the other rider from the race.
Copy Rider Times to New Number...|Copies this rider's times to a new number.  Useful if, say, you have a rider who's number fell off, and you have no entries for him/her.  In this case, choose another rider that was racing closely to the missing rider, copy the entries, the make some manual edits to the copy to get the finish order correct.
Change Rider Start Wave Time...|Use this option if a rider started in the wrong start wave by mistake, and you still want to rank the rider by time.  It allows you to add (if the rider started in an earlier wave) or subtract (if the rider started in a later wave) a time adjustment on every lap.  This can only be done after the race is Finished.

Remember, Ctrl-Z is undo!  (Ctrl-Y is redo).

## Gantt Chart and Lap Time Graph (bottom right of screen)
This shows a Gantt chart for this individual rider's times, as well as a line graph showing the lap times.

The Gantt chart 

Option|Action
:-----|:-----
Add Missing Split|Adds missing split times to the lap.  This adds the specified number of times at equal intervals in the lap.  This is the easiest way to correct missing reads.  For example, if there is a missing entry, you will see a lap that is 2x longer than what is should be.  To fix this, you would add one missing split.  Another example is that a rider's number gets muddy, and it takes three laps to figure out who it is.  As you missed this rider for 3 laps, you would add three missing splits.
Correct Lap End Time...|Correct the lap end time
Shift Lap End Time...|Shift the lap end time forwards or backwards
Delete Lap End Time...|Delete the lap end time
Pull After Lap End...|Pull this rider and set the pulled time to be just after this lap.
DNF After Lap End...|DNF this rider and set the pulled time to be just after this lap.
Show Lap Details...|Shows the details of the lap.  This includes the lap start, end, time, and any reasons for changes to the start or end of the lap.

Remember, Ctrl-Z is undo!  (Ctrl-Y is redo).
