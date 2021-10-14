
[TOC]

# Edit

## Undo (Ctrl-Z)
Undo the last change.  Undo can be called repeatedly to keep undoing the changes in sequence.

Undo is not enabled while a race is running.  This is so that you do not undo race entries.

## Redo (Ctrl-Y)
Redo the last change.  Redo can be called repeatedly to keep redoing the last changes that were undo'ed.

Redo is not enabled while a race is running.  This is so that you do not redo race entries.

## Find... (Ctrl-F)
Open a window to allow searching for any data.  This window stays open until closed.

* The Find window shows all data associated in the [External Excel][] sheet.
* Double-clicking in this window shows that rider in the RiderDetail screen.
* Clicking on the column name sorts by that column.  Ths sorted column name will be shown surrounded by <>.
* When in JChip test mode, the Tag will be automatically looked up if the Find window is up.  This makes it easy to check if a given chip read corresponds to the right rider.

## Set "Autocorrect Lap Data" flag for All Riders
Turns on the autocorrect flag for all riders.
Data for all riders will be corrected, and projected lap times will be computed.

With projected lap times, the "Expected:" section will show the expected riders before they arrive.

This option does not change the race [Properties][], it sets the Autocorrect option for all riders in the race.

## Delete Bib Number

Delete a bib number from the race.
This could be as a result of a typo or a bad call (if entering numbers manually).

If the race is running, there is no undo.  If the race is Finished, undo is enabled.

## Swap Bib Numbers

Swap two Bib Numbers in the race.
This could be a result of two riders getting each other's number.

If the race is running, there is no undo.  If the race is Finished, undo is enabled.

## Change Bib Number

Change the Bib Number of a rider.
This could be a result of a rider getting the wrong bib number which is corrected to match the information in the spreadsheet.

Note:  CrossMgr will warn you if the new Bib number does not match a Category.  You can change the Category number range later to see the rider show up.

If the race is running, there is no undo.  If the race is Finished, undo is enabled.

## Add Missing Bib Number

Add a missing Bib number to a race.  CrossMgr also prompts you for a reference rider to get times to the new Bib number.
Choose a reference rider who finished just after the rider you want to add.

A rider could be missing from the race as a result of chip read failure.

If the race is running, there is no undo.  If the race is Finished, undo is enabled.



## Clear "Autocorrect Lap Data" flag for All Riders
Turns off the autocorrect flag for all riders.
Data for all riders will not be corrected, and projected lap times will not be computed.

The "Expected:" section will show nothing as there will be no projected lap times to show.

It is not recommended to do this unless you are running a race by laps only and not by time.

This option does not change the race [Properties][], it clears the Autocorrect option for all riders in the race.

## Reissue Bib Numbers

This feature allows you to change an existing Bib number into another one.

Normally this is done before a race by changing your Excel sheet.  And if you have reasonable number ranges, the new bib number will match the number ranges in the same Category.

But, in the worse case:

* You have a long time-trial (eg. all day).
* You have already imported the TT start times for all riders and you have started the time trial.
* Riders show up during the day who have lost their bib numbers, you don't have any duplicates, and you give out new ones.
* You don't have reasonable number ranges for your categories and/or the new number you give out don't match existing number ranges.

To fix this, you would need to change your Excel sheet from the old number to the new number to get the rider information.
You also need to change or re-import your start times to update the start time for the rider.
You need to change the number ranges in the Categories so that the rider remains in the same category.
The final problem is that if you didn't get this done before the rider finished, the rider's finish time under the new Bib number will be the start time (as there is no start time for the new bib).

This is not feasible to do during a live event.

__Reissue Bib Numbers__ to the rescue.  It takes a list of the Old and New bib numbers and does everything requires to make the change:

* Automatically updates the Excel workbook so that the old rider data is matched to the new number (it makes a backup first).
* Ensures that the Category numbers are updated properly so that the riders remain in the same Categories as before.
* If running a Time Trial and the rider was already started with the new bib number, the times will be fixed up so that the start time will become a lap time.

It is important for the Excel file not to be open in Excel (otherwise this will cause a file sharing error).

