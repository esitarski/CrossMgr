
[TOC]

# Windows

## Bib Enter...
Shows the __Bib Enter__ dialog.  This small dialog allows you to manually enter bib numbers, similar to the [Record][] screen.

Use the __Bib Enter__ dialog when you wish to keep up another screen while doing manual bib entry.  For example, if you are working with an official, you may wish to show the [Passings][] screen at all times so you can check entered numbers.  Or, you watch the [Chart][] screen and correct missing splits.

You can move the __Bib Enter__ dialog to the most convenient part of the screen.

## Windows
Opens/Closes screens in a separate window.  This is especially useful if you are using multiple screens and wish to show additional CrossMgr information while entering data in the main screen, or you wish to display the [LapCounter][] on another screen to show the riders.

Choose the screen you wish to open in a separate window.  Drag it/resize it as needed.

For example, you can show the Animation while doing data entry.  Or Results.  Or the Chart.  Or the Situation screen.  Or the Lap Counter.  Any, or all of the above.  Your choice.

The separate screens have identical capabilities as the regular screens.

## Unmatched RFID Tags
This window shows unmatched RFID tags in a Chart.

This screen shows if there are riders with RFID tag recordings that do not have corresponding information in the linked Excel spreadsheet.

If the Excel sheet is updated later so that the missing tags are included, the __Unmatched RFID Tags__ will be added to the race automatically.

Take a close look at the laps in the __Unmatched RFID Tags__ screen.
If the times appear to be in regular laps for a rider, this is an indication that:

1. The rider is genuinely in the race, but has the wrong tag or a missing tag in the Excel sheet.  Fix your spreadsheet.  Then get CrossMgr to refresh, say, buy switching screens.  It will then automatically pull the unmatched RFID tags data into the race.
1. The rider thinks he/she is in this race, but is actually in another race that starts at a different time.  You need to tell the rider to compete in the right event.
1. The rider is knowingly riding in the wrong race (and was stupid enough not to remove his/her tag!).  This is serious.

If there is no pattern to the reads, they are likely to be spurious and can be ignored (rider's tag too close to the finish line).

The unmatched tags can be exported to Excel.  This allows you to cut-and-paste the missing tags into another sheet, or to do further analysis on where the tags came from.

A maximum of 200 unmatched times will be recorded.

If your races is so messed up that this does not work, consider creating another race and importing all the tags (see [ChipReader][]).

