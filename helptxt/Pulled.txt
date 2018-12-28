[TOC]

# Pulled
The __Pulled__ screen allows you to record riders pulled from a race and have them ranked by lap and pulled sequence.

When riders are pulled from an 80% zone, the riders do not cross the finish.  We must rely on an official to do the pulling, records the __Laps to Go__ and the sequence in which the riders were pulled in that lap.  This information can then be entered on the __Pulled__ screen.

The Pulled screen overrides any recorded laps.  For example, say a rider is pulled with 3 laps to go, but fails to stop, and crosses the finish line for his last 3 laps anyway.
His last 3 lap times will be ignored and he will show in the results with a gap of -3 laps.

There is no time recorded for pulled riders, only the sequence they were pulled in each lap.

Of course, pulled riders will be ranked in the Results by the number of laps completed, then by the sequence they were pulled in each lap.

# Controls

## Category
Selects the Category.  Pulling only makes sense with respect to all riders in each Start Wave (not Component categories within the Start Wave).  The __Start Wave__ category is shown at the top of the screen.

## Commit
Commits changes so they are reflected in the Results.  Commit is also done automatically when you change screens.

Commit is useful when you want to update the results but do not want to change screens.  For example, while a race is running, you want to update real-time results with Pulled riders without changing the screen.
After a Commit, more rows are added to the table.

# Pulled Table

The Pulled table has the following columns:

Column|Description
:-----|:----------
Laps to Go|The number of laps to go when the rider was pulled.
Bib|The bib number of the rider
Name|Automatic.  The name of the rider (as retrieved from the spreadsheet).
Team|Automatic.  The team of the rider.
Component|Automatic.  The Component category of the rider if the Start Wave has more than one component.
Error|Automatic.  Any error.  Rows with errors will not be committed.

It is unnecessary to repeat the __Laps to Go__ on each row if subsequent rows are for the same lap.

You can drag-and-drop rows to change the sequence (click and drag the left-most cell of each row).

