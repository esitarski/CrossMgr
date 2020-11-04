
[TOC]

# DataMgmt

## Link to External Excel Data...
Link to an external Excel file containing additional rider data.

This option opens up a Wizard to configure a link to an Excel sheet.  The Excel sheet must have a header row with the column names.  The Wizard takes you through the following steps:

1. Choose the Excel workbook containing your additional data.
1. Choose the sheet within the Excel workbook.
1. Choose how the CrossMgr's fields should correspond to the column names in your Excel sheet.  The CrossMgr fields are on the first row, and the Excel column names are the drop-downs in the second row.  In the drop-downs, select the Excel column corresponding to the CrossMgr field.
The Excel sheet may contain more fields than CrossMgr uses, and the column names in the sheet do not have to be named the same as CrossMgr's names.  You just have to tell CrossMgr what Excel columns correspond to its fields.  CrossMgr can usually use the same Excel sheet used as the rider sign-on sheet or pre-reg download.
1. Consider the __Initialize CrossMgr Categories from Excel EventCategory and Bib# columns__ option.  If selected, CrossMgr will use the __EventCategory__ and __Bib#__ columns to Add missing categories, Update existing categories with bib numbers from the spreadsheet or Delete empty categories.  All Categories are initially added as __Open__ gender and 00:00:00 __Start Offset__ (see [Categories][] for details).  Changes to Categories made in CrossMgr __except bib numbers__ will be preserved when data in the Excel spreadsheet is updated, provided the Category is not empty and deleted.
1. After the configuration, CrossMgr will show how many records it was able to read from the Excel workbook.

Additional external information will now be shown throughout CrossMgr including in Results, HTML and Excel output.

Specifying a spreadsheet creates a dynamic "link" to the Excel sheet - CrossMgr does not store the Excel data inside CrossMgr.  If data in the Excel sheet changes at any time (before, during or after the race), CrossMgr will automatically pick up the changes and display them the next time the screen is refreshed (for example, after switching between screens).

This allows you to start a race without the full details entered into Excel, or without an Excel sheet entirely.  As the race is underway, you can update the spreadsheet, and the changes will automatically be reflected in the results when CrossMgr next updates.

If you move the the Excel file to a different folder, you will have to update the link to tell CrossMgr where to find the new location.

CrossMgr supports the following fields from an external Excel sheet:

Field|Description
:----|:----------
Bib#|Required.  Rider's bib number in the race.  Bib numbers should be allocated in logical number ranges if there are multiple categories in the race (for example, 1-99 = one category, 100-199 = another category, etc.)
LastName|Optional.  Rider's last name.  CrossMgr will automatically capitalize the last name. Used for display only.
FirstName|Optional.  Rider's first name. Used for display only.
Team|Optional.  Rider's team. Used for display only.
Team Code|Optional.  Rider's 3-letter team. Used for UCI DataRiver Excel upload.
Category|Optional.  Rider's category.  This field is shown in the Results as information only, and does not have to match the rider's racing category.
EventCategory|Optional.  If __Initialize CrossMgr Categories from Excel Category and Bib# columns__ is selected, values in this column will be added to the race as a category (if not already present), and this rider's bib number will be included in that category.  If __Initialize CrossMgr Categories from Excel Category and Bib# columns__ is not selected, the rider's category will be determined by matching the number ranges of the categories (see [Categories][] for details).
Age|Optional.  Rider's age.  Used for display only.
License|Optional.  Rider's license.  This can be the UCI code, a national code, or a regional code.  CrossMgr uses this for display only.
UCI ID|Optional.  Rider's UDI ID.  Will be included in UCI DataRiver upload Excel sheets.
NatCode|Optional.  Rider's Nation Code.  Will be included in UCI DataRiver upload Excel sheets.
Factor|Optional.  Athlete's Performance Factor, as a Percent.  Used for Para Cycling to rank athletes with different abilities competing in the same combined event.  The athlete's race time is multiplied by the Factor, yielding an adjusted time.  The athlete's are then ranked by the adjusted times.  The Performance Factor will depend on the athlete's classification, as well as the classifications of the other athlete's in the combined race.  When using Performance Factors, you almost always want to set the "Lapped Riders Continue" option (see [Categories][]).  This is because, after applying the Performance Factors, lapped athletes may still be in contention for winning the combined category.
Tag1-9|Optional for manual input, required for chip input.  Rider's chip tag.
CustomCategory1-9|Custom categories to add this rider to.

To save space, CrossMgr may combine the first and last names into one field as "LASTNAME, Firstname".  In the scoreboard, it uses a further shorthand of "LASTNAME, F" where "F" is the first letter of the first name.

### Notes on __Initialize CrossMgr Categories from Excel EventCategory and Bib# columns__

This feature is useful if you do not have number ranges for different categories and you want to initialize the bib numbers and categories from the Excel spreadsheet using the __Bib#__,  __EventCategory__ and __Custom Category__ columns.  The behavior is as follows:

1. Initialization:  For each existing Category in CrossMgr, remove all Bib numbers.
1. New Category: If a category is found in the spreadsheet in the EventCategory column that does not exist in CrossMgr, add the new category (StartOffset=00:00:00, Gender=Open, Type=Wave), and insert the Bib# of that rider.
1. Update Category:  If a category is found in the spreadsheet that exists in CrossMgr, add the Bib# to that category.
1. Finalization:  After reading the Excel sheet, all empty Categories in CrossMgr are deleted.

The first time the Excel Link is read, you will get all the categories in the spreadsheet into CrossMgr as __Start Wave__ categories.
You can then organize your into __Components__ (see [Categories][]) and add combined __Start Waves__ to match the schedule and structure of your race.

Subsequence reads of the spreadsheet will use the existing Categories, but of course, the bib numbers be replaced based on the categories in the spreadsheet.
This means that changes you make to categories (laps, start offset, start wave, etc.) will be preserved when the Excel spreadsheet changes.

Alternatively, you can import a Category structure before linking to the spreadsheet (or use "File/New Next..." from an existing race).

__Big Warning__:  This option tells CrossMgr that the spreadsheet is the "source of truth" for rider categories.  This means that any changes to rider categories made in CrossMgr will be over-written the next time the spreadsheet is read.  So, if you use this feature, don't make change to rider categories in CrossMgr - always do this in Excel.

## Add DNS from External Excel Data...

Add DNS (Did Not Start) riders quickly and automatically.  This dialog allows you to select all or some riders who are defined in the Excel sheet, but have no data entered during the race.

These riders are likely DNS riders.  Of course, the possibility exists that some of the rides actually started but DNFed (Did Not Finish), were PUL (Pulled) or DQ (Disqualified).  Be mindful of the riders you set as DNF.  Of course, you can always change the status later.

There are a number of buttons on the DNS Manager screen:

Action|Description
:-----|:----------
Category|Select the category.  Default is all categories in the race.
Select All|Select all the potential DNS riders.  You can also manually select by clicking on the rows.  You can multi-select with Shift-Click and Ctrl-Click.
Deselect All|Deselect all the potential DNS riders.  You can also manually deselect by clicking on the rows.  You can multi-deselect with Shift-Click and Ctrl-Click.
DNS Selected|Adds all the selected riders into CrossMgr, and sets the status to DNS (Did Not Start)

Clicking on a column name will sort the potential DNS riders by that column.

Remember Ctrl-Z (Undo) and Ctrl-Y (Redo) if you need to.

## Import Time Trial Start Times...

Imports start times for a time trial from a spreadsheet.
The race must be in TimeTrial mode (see [Properties][]).

If CrossMgr has no imported start times, the first recorded time will start the rider's clock.  Otherwise the rider's clock will start automatically on the start time.

The times must be relative to the start of the stopwatch start time, not clock time.  For example, the event starts when the stopwatches start at 00:00:00.
This also corresponds to when you push the Start Race button on the [Actions][] screen.

The first rider usually leaves a minute or two after the event start time, for example, at 00:01:00.  Subsequent riders leave on 30 second gaps with start times of 00:01:30, 00:02:00, etc.

The spreadsheet must have a Header row, and must have the Bib number and Start Time of the rider as columns.

Again, the times are not "on the clock on the wall", rather, they are relative to what would be seen on a stopwatch started at the beginning of the event.

The procedure for using imported start times is:

+  Create the rider registration sheet in Excel.  This will include the Bib number and other information about the rider including, names, teams, tags, etc.
+  Add a column called "Start Time" to the spreadsheet.
+  Change the Excel format for the column to a HH:MM:SS time format.
+  Change the order of the rows to the start order.  Normally, the fastest riders start at the end.  Pay attention to teammates starting consecutively too, as they may try to work together if they catch each other.
+  When you are satisfied with the start order, set the first rider's start time to "00:01:00".
+  Set the second rider's start time to "00:01:30".
+  Select the "00:01:00" and "00:01:30" cells.
+  Drag the small box at the bottom of the selection down to the last rider.  This will automatically populate the start times on 30 seconds.  You can also use 60 or 20 seconds - whatever you like.
+  Add gaps between categories to latecomers and day-ofs.  Add extra time between the fastest riders.
+  Import the start times into CrossMgr race ahead of time.
+  Get together with the manual timers (or get them on phone/radio) to synchronize CrossMgr and the manual stopwatches.  On a countdown of 5, Start the race, and get everyone to start the stopwatches at the same time.  Remember the Confirm dialog - get it up on the screen first, then press OK.
+  If you mess up pressing, remember that Ctrl-Z will "undo" the start (for safety, it only works 8 seconds after the start).  After undo-ing the start, get everyone to reset, and start the race and stopwatches again.

## Import Categories from File...
Read the categories from a previously exported Categories file.

## Export Categories to File...
Export the currently defined categories to a file.  This is useful is you find yourself configuring the same categories many times and wish to reuse the same category definitions from one race to another.

## Export Passings to Excel...
Export the Passings data to Excel.  This is useful for manual review.

## Export Raw Data as HTML...
Export the raw data of the race into an HTML file.  This is useful for checking input received from a chip timing system, or manual input.
Edited entries are also shown with edit details, however, any missing entries projected by CrossMgr are not included.

Columns in the table are as follows:

Column|Description
:-----|:----------
Sequence Number|Number of the entry
Clock Time|Clock time of the entry
Race Time|Race time of the entry (= Clock Time - Race Start Time)
Bib#|Bib number of the rider
Count|The count of the number of reads for this rider.
Race Cat.|Race category of the rider, if found
Name|"LAST, First" name of the rider (if present in the [External Excel][] sheet)
Team|Team of the rider (if present in the [External Excel][] sheet)
Category|Category of the rider (if present in the [External Excel][] sheet)
License|License of the rider (if present in the [External Excel][] sheet)
Tag|Chip tag associated with the entry (if chip timing, and if present in the [External Excel][] sheet)
Tag2|2nd chip tag associated with the entry (if chip timing and if present in the [External Excel][] sheet)
Edit|Reason for the data edit
By|Username who made the edit (login name on the computer)
On|Date and Time when the edit was made.

