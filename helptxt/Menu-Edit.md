
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
