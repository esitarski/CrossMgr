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
+	Use the TTCountdown feature on a tablet (see [Web][] for details).  This does a UCI-style countdown on a tablet complete with the correct "beeps" on the 10s, 5, 4, 3, 2, 1, 0.  Using the Countdown page eliminates errors regarding the start time and the rider.

## Without a Start List: Manual Starts

CrossMgr can be used for "informal" time trials - without a start list.

With no start times, the first recorded time will start the rider's clock.
Simply enter the bib number to start the rider.

Subsequent entries for that rider will count as usual (either the finish, or towards laps if the TT is multi-lap).

## Both Automatic Starts and Manual Starts

Starts from the start list will happen automatically.  However, if you have a rider not on the start list (eg. late entry), just do a Manual Start.
You can then update the Excel sheet with rider information at any time.

## TTCountdown Page

The TTCountdown page counts down riders in the time trial from a web page.
The screen shows the riders bib, name, team and category.  A big countdown clock is shown.
It counts down the rider's start, beeping on 10s, 5, 4, 3, 2, 1 and a high beep on zero (very UCI).
At the bottom of the screen is an updated list of the next riders.

This eliminates start errors, especially if there are changes in the start gaps.

The TTCountdown page is generated by __Batch Publish__ (see [Publish][]).  It is also directly accessible from the CrossMgr Web page:

* Make sure there is a QRCode reader app installed on the tablet ahead of time.
* Make sure you have disabled the screen timeout on the tablet.  On some Android tablets this requires an additional app from the PlayStore (for example, "Keep Screen On").
* Ensure the CrossMgr computer and the tablet are connected to the same wireless LAN.
* From CrossMgr, do __Web|QRCode Share Page__.  This will open up the browser with a web page showing a QRCode that connects to CrossMgr.
* Open the QRCode app on the tablet and point it at the CrossMgr computer screen.  When it recognizes the code, press "Open".
* Now your tablet is connected to CrossMgr's Index page.
* From the Index page, click on TTCountdown for your TT event.
* When the page comes up on the tablet, there will be a large "Click Me" button.  Clicking will play some beeps to adjust the volume, start the TTCountdown clock and switch to full screen.
* You can now start all your riders, UCI style.
* To get out of fullscreen mode on the tablet, press the "Back" arrow.

If you start (or reload) the TTCountdown page after you start the race in CrossMgr from the CrossMgr web page, the countdown page will compute a correction with CrossMgr's race start time.  This is necessary because the clock on the start device (tablet) may have a different time of day than the CrossMgr computer.  CrossMgr uses (Christian's Algorithm)[https://en.wikipedia.org/wiki/Cristian%27s_algorithm#:~:text=Cristian's%20algorithm%20(introduced%20by%20Flaviu,used%20in%20low%2Dlatency%20intranets.].  This process usually results in one millisecond of synchronization.

If you start the TTCountdown page from a static web page, it will not be able to make a correction to the CrossMgr computer.  In this case, the TTCountdown page will use the device's internal clock.  This may be off by a few seconds relative to the CrossMgr computer.
This makes no difference to the rankings of a time trial as all the times will be measured consistently between the start and the finish.
However, rider's using their own timing computers may notice the difference.  And of course, it matters if there is a course record.

If you use TTCountdown from a static web page, be sure to set the device's clock and your CrossMgr computer to the same atomic clock time to minimize any differences.

If you start TTCountdown before you start the race in CrossMgr, it will countdown to the race start and automatically switch to rider countdown at the race's scheduled start time.

If the race starts at a different time than scheduled and the TTCoundown page is connected to the CrossMgr computer, refreshing the TTCoundown page will pick up the actual race time.

To maintain the best timing accuracy, the TTCountdown page does not "phone home" to CrossMgr after it starts (network delays could cause it to hang).
Changes to the rider Excel spreadsheet, or changes to start times requires a refresh to see them in the page.

This means that the TTCountdown page does not need a live network connection to CrossMgr.
For example, you can start it from the CrossMgr computer, then move to a different location for the finish,
leaving the tablet at the start.  Of course, it is important that no one touch the TTCountdown tablet in this case as there is no way to reload it.

Another scenario is to generate a statis TTCountdown page ahead of time:

+ generate the TTCountdown page (see [Publish][]) and upload it to an accesible web site ahead of time.
+ load a start tablet on location with the generated page (say, from a hotspot or internet connection).
+ start the race in CrossMgr based on the TTCountdown to the race start time.  This can be done by time-of-day, or by phone/radio communication with the start line.

Starting from time-of-day is convenient for hill climbs and other situations when there is no communication between the start and the finish.
Just make sure that your watches, computers and devices are all synced ahead of time.

## Frequently Asked Questions

__What happens if the Start Times change during a race?__

CrossMgr assumes that all the "new" start times are the correct ones.

For all riders who have not started yet, CrossMgr will use the new start time.  The TTCountDown page will __not__ update until you reload it.
It is a disaster in waiting to make the the "new" start times earlier as it will inevitably lead to riders missing the "new" time as they were expecting the old.

If a rider has already started (or finished), CrossMgr will use the rider's "new" time, and not the "old" time.

The rider's time will be adjusted accordingly.

For example if the "new" time is 1 minute earlier than the "old" time, the rider's overall time will be adjusted longer by 1 minute.
If the "new" time is 1 minute later than the "old" time, the rider's overall time will be adjusted shorter by 1 minute.

Try very hard to avoid changing the start times during a time trial as it can lead to incredible confusion.  The integrity of all times will be questioned.

Also, use the TTCountDown page so you get perfect starts every time.

If you do change the start times during the race, you will have to manually refresh the TTCountdown page to see the changes.

__Things really messed up and I have to change the Start Times after the race.  What do I do?__

Just change them in Excel.  CrossMgr will automatically apply the same adjustments for the "new" times (see above).
