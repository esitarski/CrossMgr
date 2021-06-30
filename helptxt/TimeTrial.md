[TOC]

# Time Trial
CrossMgr supports Time Trials.

It can operatate with a start list (automatic starts) or without a start list (manual starts).

## With a Start List: Automatic Starts

If CrossMgr has a start list, it will start riders on their specified times automatically.

Configuring a start list can be done in a separate Excel sheet, or in the same Excel sheet as the rider info (see [DataMgmt][] for details).

### Configuring the Start Time Excel sheet

Start Time must be relative to the start of the race, not "clock on a wall" time.  For example, the event starts when the stopwatches start at 00:00:00.
This corresponds to when you push the Start Race button on the [Actions][] screen.

The first rider usually leaves a minute or two after the event start time, for example, at 00:01:00.  Subsequent riders leave on one minute gaps like 00:01:00, 00:02:00 etc. or 30 second gaps like 00:01:30, 00:02:00, etc.

A start time of "10:00:01" means that the rider's start is 10 hours and one minute after the start of the race, not one minute after 10 o'clock in the morning.

If you want to configure the start times in the same Excel sheet as the rider information, make sure there is a __StartTime__ column in the Header row, that it is the first column in the spreadsheet, and that you spell it exactly as shown (with no space and matching capitalization).

If starts times are in a separate spreadsheet, it must have the __StartTime__ and __Bib__ number as header columns.

The easiest procedure for configuring start times is:

+  Create the rider registration sheet in Excel.  This will include the Bib number and other information about the rider including, names, teams, tags, etc.
+  Add a column called "StartTime" to the spreadsheet.  Make sure this is the first column.
+  Change the Excel format for the column to a HH:MM:SS time format.
+  Change the order of the rows (sort) to the start order you want.  Normally, the fastest riders start at the end.  Pay attention to teammates starting consecutively too, as they may try to work together if they catch each other.
+  When you are satisfied with the start order, set the first rider's start time to "00:01:00".  One minute after the "race start".
+  Set the second rider's start time to "00:01:30".
+  Select the "00:01:00" and "00:01:30" cells.
+  Drag the small box at the bottom of the selection down to the last rider.  This will automatically populate the start times on 30 seconds.  You can also use 60 or 20 seconds - whatever you like.
+  Add gaps between categories to accomodate latecomers and walk-ups if necessary.  Add extra time between the fastest riders if you like.

Alternatively, you can use formulas.  To make those work you have to understand that Excel thinks of time as a "fraction of a day".
For example, one minute = 1/(24 * 60), one second = 1/(24 * 60 * 60).

If you set the format to HH:MM:SS, Excel will "do the right thing" when you enter times.  However, you have to understand Excel's quirky "fraction of a day" to use formulas.

Consider the formula: A2 = OFFSET(A2,-1,0) + 1/(24 * 60).  It is clear that 1/(24*60) is one minute, so, A2 is one minute later from the cell directly above it.

Why the __OFFSET__ function?  Why not A2 = A1 + 1/(24 * 60) ???

__OFFSET__ is far superior for three reasons:

1. You won't mess up when you change the order of the rows.  Cell references cause times that are out-of-order when the rows change sequence.
2. You won't get an "undefined reference" error when you delete a row.
3. You won't mess up when you copy the formula to a new row.

Never use cell references for this.  Always use OFFSET.  It just works.

On race day:

+  Import the start times into CrossMgr race ahead of time if you have them in a separate spreadsheet.  If they are in the same spreadsheet, they will auto-import.
+  Get together with the manual timers (or on phone/radio) to synchronize the CrossMgr start with the manual stopwatches.  On a countdown of 5, Start the race, and get everyone to start the stopwatches at the same time.  Remember the race start Confirm dialog - get it up on the screen first, then press OK.
+  If you mess up syncing the stop watches, Ctrl-Z will "undo" the start (for safety, it only works 8 seconds after the start).  After undoing the start, get everyone to reset, then start the race and stopwatches again.
+	Use the TTCountdown feature on a tablet (see [Web][] for details).  This does a UCI-style countdown on a tablet complete with the correct "beeps" on the 10s, 5, 4, 3, 2, 1, 0.  Using the Countdown page eliminates confusion regarding the start time and the rider.

## Without a Start List: Manual Starts

CrossMgr can be used for "informal" time trials - without a start list.

With no start times, the first recorded time will start the rider's clock.
Simply enter the bib number to start the rider.

Subsequent entries for that rider will count as usual (either the finish, or towards laps if the TT is multi-lap).

## Both Automatic Starts and Manual Starts

Starts from the start list will happen automatically.  However, if you have a rider not on the start list (eg. late entry), just do a Manual Start.
You can then update the Excel sheet with rider information at any time.

## Frequently Asked Questions

__What happens if the Start Times change during a race?__

CrossMgr assumes that all the "new" start times are the correct ones.

For all riders who have not started yet, CrossMgr will use the new start time.  The TTCountDown page will also update.
It is bad practice to make the the "new" start times earlier as it can lead to rider's missing the "new" time as they were expecting the old one.

If a rider has already started (or finished), CrossMgr will make the rider's start the "new" time, and not the "old" time.

The rider's time will be updated accordingly.

For example if the "new" time is 1 minute earlier than the "old" time, the rider's overall time will be adjusted longer by 1 minute.
If the "new" time is 1 minute later than the "old" time, the rider's overall time will be adjusted shorter by 1 minute.

Try hard to avoid changing the start times during a time trial as it can lead to incredible confusion.

Also, use the TTCountDown page so you get perfect starts every time.

__Things really messed up and I have to change the Start Times after the race.  What do I do?__

Just change them in Excel.  CrossMgr will automaticaly apply the same adjustments for the "new" times (see above).
