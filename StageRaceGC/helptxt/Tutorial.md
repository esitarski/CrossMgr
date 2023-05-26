[TOC]

# Introduction

__StageRaceGC__ scores stage races for Individual and Team GC using UCI rules.
All tie-breaking rules are applied, and all details are applied to compute the the Team GC.

It takes an Excel sheet with the Registration and Stage results as input and can produce another Excel sheet with the current GC, Team GC, and shows its work for all stages.

StageRaceGC always scores the race "from first principles", for example, if you have a 5 stage race, and a change is made to stage 2, this change is propagated throughout all subsequent stages.

The Input Excel sheet must have the format described in the Input section below.  Additional sheets that do not follow the the description below are ignored.

# Tutorial

StageRaceGC creates an Excel sheet showing a sample race with results.  Use this to get an idea about how to setup your own race.

# Input

__StageRaceGC__ accepts input from an Excel sheet.  The sheet must be organized as follows:

* There must be one __Registration__ sheet.  It is assumed that only one category is contained in the sheet.
* There can be one or more sheets ending in __-RR__ (RR = __Road Race__).  For example, "Stage 1-RR" and "185km-RR" will be recognized as Road Race stages because they end in "-RR".
* There can be one or more sheets ending in __-ITT__ (ITT = __Individual Time Trial__).  For example, "Prolog-ITT", "Stage 4-ITT" and "62km-ITT" will be recognized as Individual Time Trial stages because they end in "-ITT".
* There can be one or more sheets ending in __-TTT__ (TTT = __Team Time Trial__).  For example, "Stage 6-TTT" and "91km-TTT" will be recognized as Team Time Trial stages because they end in "-TTT".
* There can be one __Team Penalty__ sheet (see below for details).

Unrecognized sheets will be ignored.

__StageRaceGC__ requires that the stage sheets be in left-to-right order.

Column names must match those recognized by StageRaceGC as described below.  Case and spaces are ignored.

## Registration Sheet

The Registration sheet is the main sheet for rider data.  The following header columns are recognized in any order:

Column|Description
:-----|:----------
Bib (or BibNum)|The rider's number
First Name|Optional.  Rider's First name
Last Name|Optional.  Rider's Last name
Name|Optional.  Rider's name, first and last.  Use this field if you don't have the first and last name separately.
Team|Rider's team
UCI ID|Rider's UCI ID (11 digit number issued by the UCI)
License|Rider's local Licence code

This is the "master" rider data sheet.
All rider data will be used from this sheet, even if it is repeated on other sheets.
Make rider data changes on this sheet only.

## -RR Sheets

These sheets contain the data for the results of each __Road Race__ (RR) stage.  All Road Race sheets in the spreadsheet must end with __-RR__.  The following header columns are recognized in any order:

Column|Description
:-----|:----------
Bib (or BibNum)|The rider's number
Time|The rider's actual finish time, not including the time bonus or time penalty.  Use Excel input format __hh:mm:ss__.  Fractions of a second are ignored as per UCI ranking rules.
Place (or Rank or Pos)|Optional.  The rider's finish position.  If there is no __Place__ column, the finish order will be assumed to be from top to bottom.  This field will also accept __AB__ (Did Not Finish/Did Not Start) and __DQ__ (Disqualified).
Bonus|Optional.  Time bonus for this rider in Excel time format.  Suggest Excel input format __mm:ss__.
Penalty|Optional.  Time penalty in Excel time format.  The penalty is added to the rider's time for GC and Team GC calculation.  Suggest Excel input format __mm:ss__.
Sprint1, Sprint2, Sprint3..Sprint8|Optional.  Intermediate sprint points for the sprinter's jersey.  To be recognized, the column name must start with "Sprint X" where X is the number of the sprint.  Each stage can have up to 8 Sprint point opportunities.
Stage Sprint|Optional.  Indicates sprint points for the end of the stage.  There can only be one "Stage Sprint" column per stage.  The stage sprint must be indicated as ties in sprinters points are first broken with the number of stage wins, then number of intermediate sprint wins.
KOM1, KOM2, KOM3..KOM8|Optional.  KOM (King of the Mountain) points for the climbers jersey.  To be recognized, KOM column names must start with "KOM X", where X is the number of the KOM.  Each stage can have up to 8 KOM point opportunities.  The category of the climb (one of 4C, 3C, 2C, 1C ahd HC) can also be included in the column name.  For example, "KOM1 2C", "KOM3 HC" are recognized.  This is required to break ties on KOM points where the number of first places in the highest category climbs is considered first, then if still a tie, the number of first places on the next inferior climb is considered, etc.

### Notes:

__Place__ and __Time__ are treated as separate pieces of information that may not correspond to each other.  For example, if a rider crashes during the last 3km, s/he gets the time of the riders s/he was riding with, but the place when s/he crosses the line.

AB and DQ are interpreted as applying for all future stages, and a rider marked as AB or DQ will no longer be included in the GC from that stage onward.  This also has implications for the Team GC if the number of team members drops below 3.

Make sure that AB and DQ riders appear at the end of the list if you do not have a __Place__ column.

The __Place__ value does not have to be unique.  For example, if a group of riders crash inside the last 3km then fail to cross the finish line, they would get the time of the riders they were riding with and all recieve the same value of last __Place__ in the stage.

Column headers other than the ones above are ignored.  Rider information (name, team, etc.) is always retrieved from the Registration page keyed on the Bib number.

## -ITT Sheets

These sheets contain the data for the results of each __Individual Time Trial__ (ITT) stage.   All Individual Time Trial sheets in the spreadsheet must end with __-ITT__.  The following header columns are recognized in any order:

Column|Description
:-----|:----------
Bib (or BibNum)|The rider's number
Time|The rider's finish time including any time penalties.  Use Excel input format __hh:mm:ss.000__ to record fractions of a second.
Bonus|Optional.  Time bonus for the rider.  Suggest Excel input format __mm:ss__.
Place (or Rank or Pos)|Optional.  Also used to indicate __AB__ (Did not finish) and __DQ__ (Disqualified).  Other values are ignored.
Penalty|Optional.  Time penalty.  The penalty is added to the rider's time for GC and Team GC calculation.  Suggest Excel input format __mm:ss__.

### Notes:

Make sure that AB and DQ riders appear at the end of the list if you do not have a __Place__ column.

AB and DQ are interpreted as applying for all future stages, and a rider marked as AB or DQ will no longer be included in the GC from that stage onward.  This also has implications for the Team GC if the number of team members drops below 3.

Column headers other than the ones above are ignored.  Rider information (name, team, etc.) is retrieved from the Registration page keyed on the Bib number.

## -TTT Sheets

These sheets contain the data for the results of each __Team Time Trial__ (TTT) stage.  All Team Time Trial sheets in the spreadsheet must end with __-TTT__.  The following header columns are recognized in any order:

Column|Description
:-----|:----------
Bib (or BibNum)|The rider's number
Time|The rider's finish time including any time penalties.  Use Excel input format __hh:mm:ss.000__ to record fractions of a second.  Fractions of a second are used for tie-breaking.
Bonus|Optional.  Time bonus for the rider.
Place (or Rank or Pos)|Optional.  Also used to indicate __AB__ (Did not finish) and __DQ__ (Disqualified).  Other values are ignored.
Penalty|Optional.  Time penalty.  The penalty is added to the rider's time for GC and Team GC calculation.  Suggest Excel input format __mm:ss__.

### Notes:

Make sure that AB and DQ riders appear at the end of the list if you do not have a __Place__ column.

AB and DQ are interpreted as applying for all future stages, and a rider marked as AB or DQ will no longer be included in the GC from that stage onward.  This also has implications for the Team GC if the number of team members drops below 3.

Column headers other than the ones above are ignored.  Rider information (name, team, etc.) is retrieved from the Registration page keyed on the Bib number.

## Team Penalty Sheet

As per UCI Rule 12.1.021, it is sometimes necessary to give a Team time penalties.  The __Team Penalty__ sheet enables you to do this.

Column|Description
:-----|:----------
Team|The team.
Penalty|Optional.  A time penalty given to the team.  The penalty is added to the team's GC after it is calculated.  Suggest Excel input format __mm:ss__.

The same Team may appear multiple times in the __Team Penalty__ sheet.  The sum of the time penalties will be applied to the Team GC.

Column headers other than the ones above are ignored.  

# Main Screen
The Main Screen is divided into three major areas:

1. Excel input.
1. Read status.
1. Output.

## Excel Input

Specify your input Excel sheet here by using the Browse button, or click on the dropdown to get previous files.  You Excel workbook must be in the __Input__ format described above.
If you change your Excel sheet, press the __Update__ button to get __StageRaceGC__ to recompute the GC.

## Read Status

Shows any problems with reading the sheets.  It is important to investigate all issues reported here.

## Output

Shows the __Individual GC__ and __Team GC__.  Also shows the intermediate results for each stage.

The full output can be exported to an Excel sheet.

Of course, the Individual GC and the standings after the last stage are identical.

# Notes:

## Team Time Trials

It is up to you to enter the correct time of the team.  StageRaceGC does not know how many riders are on a team nor "which wheel counts" as the finish time.

## Team GC and Minimum Team Size

__StageRaceGC__ will not compute a Team GC when the number of team members drops below 3.  This team will no longer appear on the Team standings.

## ABs and DQs

__StageRaceGC__ expectes AB and DQ riders to have left the competition and not to be present in subsequent stage results.
These riders will be ignored even if they appear again in a results in a later stage.

Make sure that riders who are continuing have an assigned Time (and Place) as required.
