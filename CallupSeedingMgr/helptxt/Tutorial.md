[TOC]

# Tutorial

## Introduction
__CallupSeedingMgr__ makes it easy to create a __Callup__ or __Seeding__ sequence for a race.
It can do it in seconds and save hours of error-prone work.

__CallupSeedingMgr__ processes a spreadsheet with the registration and callup/seeding criteria rather than keeping the data itself.  This makes it easy as you likely have this information in Excel anyway (or can get it there).

Unlike Excel vlookup formulas, __CallupSeedingMgr__ correctly handles athletes with the same number of points and preserving that order.  To change it by using other callup criteria, or to not respect it is an error.

In this tutorial, we will be using an input spreadsheet automatically generated by the __CallupSeedingMgr__ program.
If you don't have it, start the tutorial from __CallupSeedingMgr__ and it will generate one and open it for you.

We are doing callups, that is, we want the highest ranked rider to be first in the list.

If you are doing seeding for a time trial, you want the highest ranked rider to go last.  This is easily accomplished by selecting the __Seeding: Highest ranked LAST (Time Trial)__ option (more on that later).

__CallupSeedingMgr__ handles any number of callup/seeding criteria.  In this example, we are going to use 6 criteria to control the callups for an age-based category:

1. by current National Champ
1. by previous Regional Champ
1. by __UCIPoints__
1. if none, then by the Western Series __Ability__ and __Points__.
1. if none, then by the Eastern Series __Points__.
1. if none of the above, random.

Finally, we want riders to alternate between the Western and Eastern series.

Of course, in your own race you will configure a spreadsheet with your own data.

Overall, __CallupSeedintMgr__ does the following:

    For each rider in Registration:
        For each Criteria sheet in the spreadsheet:
            Match the rider's information to a criteria row based on some common column header data
            If successful, append the criteria's Points or Position to the sort criteria
            If no match, skip the critera
    Sort by the criteria found.

Criteria are sorted in [Lexographic Order](http://en.wikipedia.org/wiki/Lexicographical_order) for callups, reversed for seeding.

__CallupSeedingMgr__ can also 

# Structure of the Input Excel File

Take a moment and look at the example spreadsheet.  You will be configuring a similar sheet for your race, but different for your race particulars.  Let's start by looking at the __Sheets__ at the bottom of the screen.

## Registration Sheet

Click on the __Registration__ sheet to select it.

This specifies the riders that are registered for the race.
Normally this is the first sheet in the Excel file, but it doesn't have to be.
However, there must be exactly one sheet named __Registration__.

The __Registration__ sheet should include as much information as you have about the competitors.
For example, it might look something like this:

Bib|First Name|Last Name|UCI ID|License|Team
:--|:---------|:--------|:-------|:------|:---
...|...|...|...|...|...
...|...|...|...|...|...

A full list of __CallupSeedingMgr__ recognized fields can be found [here](#column-header-fields).

Observe that the header row __must__ be the first row, and there are no blank lines.
This must be true of all the sheets in the Excel file.  When you create your own sheet, follow the example format.

Notes:

* It's OK if you have fields unrecognized by __CallupSeedingMgr__.  It will ignore them.
* You do not need Bib numbers as they are not used for matching.  Include them if you do, leave them off if you don't have them.
* Columns can be in any order in the sheet.
* UCI ID is accepted as an 11-digit number, or in the human readable "XXX XXX XXX XX" format.

Try to get First Name, Last Name, UCI ID and License (if available).
This will allow you to add just about any other criteria.

## Criteria Sheets

__Criteria__ sheets contain the information used for the ranking.  In the example, these are __National Champ__, __Regional Champ__, __UCIPoints__, etc.

It is OK if the criteria sheets contain information for other riders that are not in your race.  For example, you might have the entire UCIPoints standings in a sheet.  However, only the entries matching your __Registration__ will be used.

The sheets must be in the same order in Excel as you want the callup criteria applied.

In the example, the __National Champ__ and __Regional Champ__ sheets only have one entry.  That's OK - we only want one entry there to give priority to those riders.

### Criteria Sheet Data

__Criteria__ sheets contain a __Value__ field used for the ranking, and __Matching__ fields used to find the competitor from __Registration__.

The __Value__ field is simple.  There are four recognized formats:

1. Points
1. Position
1. Ability and Points
1. Ability and Position

Let's start with Points and Position.

__Points__ are considered in __decreasing__ order (more points = higher rank).  __Position__ is considered in __increasing__ order (lower position = higher rank).

Click on the __UCIPoints__ sheet.  Notice the __Points__ column.

Click on the __UCIPoints__ sheet.  Notice that it has both:

* If your sheet has both __Points__ and __Position__, the __Position__ field will be used.
* If your sheet does not have either a __Points__ or __Position__ field then the row number will be used as the __Position__.

__Ability__ and __Points__ (or __Position__) is used to combine rankings from ability-based results.

Other than the __Value__ field, the __Matching__ fields are used to match the criteria to a rider in __Registration__.

## Using CallupSeedingMgr

Return to the __CallupSeedingMgr__ window.  The Excel file is at the top, the options are next.  A summary of the fields per sheet is next,  The callup results are below in a the big table, and below that are the options to send the output to Excel.

__CallupSeedingMgr__ has already computed the callups and put the results in the big grid.

Scroll the big grid.  Notice how the riders with the most __UCIPoints__ are ranked first, followed by __UCIPoints__, followed by __Last Year's Results__, just as we want.

Tie order is preserved in the order the rows appear in the sheet.
For example, if two riders have the same UCIPoints, the order is preserved.  It is incorrect to use another criteria to break the tie as additional UCI rules regarding race sanction, recent results, etc. have been used.

### Get Explanation for Criteria

In the big grid, find a cell with a criteria number in it (perhaps in the __UCIPoints__ column).  Click on it.

The display shows you the __Registration__ entry and the __Criteria__ entry used to get the value.
It also includes the row number in the sheet, which makes it easy of you need to fix up your data.

If you get a wrong match and you need to change some data in the Excel sheet, save it, then press the __Update__ button to see the new values.

Sometimes you will see Orange or Yellow cells in the grid.  Orange cells indicate multiple matches, with the number of stars showing the number of matches.  If you click on those cells, you will see all the records that matched.

Multiple matches are most commonly caused by Soundalike matches.  To fix these problems, make the first and last name spelling consistent for the rider in all sheets in Excel.  When you are done, save the sheet, the press __Update__.

A single match that was a result of a Soundalike match is shown in Yellow.  

### Manually Editing the Sequence

You can manually edit the entries in the grid.  Press and hold the left-mouse button on the row numbers on the left, and drag the rider to another row.  For example, let's say for some reason you wanted to move the 3rd ranked rider to the 1st position.  Try to drag-and-drop this now.

### Change from Callups to Seeding

The program shows Callup order, that is, the highest ranked riders first.  Try selecting the "Seeding" option (to the left of the Update button).  Then press "Update".

Notice that now the riders are in the opposite sequence from Callup order.  Of course, you can manually change the sequence by drag-and-drop (this is useful if you want to separate riders on the same team).

## Saving Ouput to Excel

When you are satisfied with your sequence, press the __Save as Excel...__ button.  This will create a separate Excel file with the same name as your original file, with "_Callups" or "_Seeding" added to the name.

You can edit the output file directly in Excel if you like.

There are two output options:

1. __Exclude riders with no ranking info__ will exclude riders with no points or position criteria.  This is intended if you only want to call up the top riders with ranking information.
1. __Output__ allows you to control the top number of riders you want in the call-ups.  You almost always want to use this with the __Exclude riders with no ranking info__ option, so make sure you set them both.

For Time Trial Seeding applications, you will not use these options.

# Criteria Matching

__Registration__ rows are matched with __Criteria__ rows as follows:

1. If both __Registration__ and the __Criteria__ sheet contain a __UCI ID__ column, the licenses will be used and must match exactly.  No other matching criteria are considered in this case.  This is a reliable way to match registration with criteria.
1. If both __Registration__ and the __Criteria__ sheet contain a __License__ column, the licenses will be used and must match exactly.  No other matching criteria are considered in this case.  This is ta reliable way to match registration with criteria.
1. If still no match, then the Soundalike process is used on the First and Last names.
1. If the sheets only contains __First Name__ and __Last Name__ fields, they are checked for both exact and soundalike match.

Soundalike matches are not performed if the "Match misspelled names with Soundalike" is unchecked.

For more details see [Matching Issues](#matching-issues).

To see exactly what columns __CallupSeedingMgr__ is matching on, see the __Match Columns__ column in the summary.  For example, the __Registration__ sheet has a __License__ field and the __UCIPoints__ sheet has a __License__ filed.  By the above rules, the records are matched on the __License__ field.

# Getting UCIPoints Data

It is important to get the most up-to-date UCIPoints data before your race as follows:

* Go to the [UCI web site](http://www.uci.org).
* Click on the __Discipline__.  These are along the top of the screen.
* Click on __Rankings__
* Click on __Individual Rankings__
* Click on the __EXPORT RANKINGS__ option

Open the downloaded spreadsheet, then copy the contents into a sheet in your scoring spreadsheet as shown in the Tutorial.

# Matching Issues

There are three types of matching problems:

1. A rider fails to match a criteria, but should (false Negative)
1. A rider successfully matches a criteria, but shouldn't (false Positive)
1. A rider matches more than one row in a criteria (multiple matches)

To avoid matching these issues entirely, use the __License__ code everywhere you can.  If __Registration__ has the __License__ code, and the criteria sheet has a license code, the system will use exact __License__ match.

Matching Issues are shown on the __CallupSeedingMgr__ Screen in the cells.  

Of course, the __UCI IDs__ are more complicated because alone, the do not guarantee uniqueness - we also need to consider the First and Last name.

The problem with names is that they are often not spelled consistently, or have missing accents on the characters.  For example, I have seen my own last name misspelled as follows:

* Sitarski (correct!)
* Setarske
* Sitarsky
* Satirskie

Rather than giving up on misspelled names, __CallupSeedingMgr__ uses a "soundalike" system [Double Metaphone](http://en.wikipedia.org/wiki/Metaphone#Double_Metaphone).
The "Double Metaphone" index will match all the above as the same "soundalike".

But... this can lead to another problems, like thinking two names are the same when they aren't.

Soundalike matches and multiple matches are shown in the grid in Yellow and Orange.  Always click on Yellow and Orange cells to check whether the match is correct.

If not, modify the spreadsheet, save it, then press the __Update__ button.

# Column Header Fields

The following fields are recognized by __CallupSeedingMgr__:

Column Name|Type|Comment
:----|:---|:------
First Name,First|Matchable|
Last Name,Last|Matchable|
UCI ID,UCIID|Matchable|11-digit UCI ID.  XXX XXX XXX XX format also accepted.
License,Lic,LicenseNumber|Matchable|Regional or National license code.  Must be unique for all riders.  Try to link as much information together using the __License__ field.
Name|Converted|Field where the first name and last name appear together, but the last name is capitalized and the first name is in mixed-case.  The program will automatically convert this to a __First Name__ and __Last Name__ for matching.
Age|Converted|Used to get an incomplete DOB
Nation|Informational|Text of rider's nation.
Nation Code|Informational|Three-character nation code.
Date of Birth,DOB|Informational|Must be an Excel date.
Ability|Criteria|The rider's ability classification
Points|Criteria|The number of points awarded to the rider by that criteria.
Position|Criteria|The finish position of the rider by that criteria.
Rank|Criteria|Alias for __Position__
Pos|Criteria|Alias for __Position__
Bib,BibNum,Num|Informational|Rider's bib number.  Read in the __Registration__ sheet and repeated in the Output.  Not used for matching.
Team|Informational|Rider's team.  Read in the __Registration__ sheet and repeated in the Output.  Not used for matching.
Team Code,TeamCode|Informational|Rider's team code.  Read in the __Registration__ sheet and repeated in the Output.  Not used for matching.
City|Informational|Rider's city
StateProv,State,Prov,Province|Rider's State or Province

__Notes:__

* If a sheet has both a __Points__ and __Position__ field, the __Points__ field will be used and the __Position__ field will be ignored.
* If a sheet is missing both a __Points__ and __Position__ field, a __Position__ will be automatically generated equal to the row number in the sheet.

When matching fields, accents are removed, non-ascii characters are removed as are spaces.  Capitalization is ignored.  The following are all equivalent:

* Last Name
* LastName
* LASTNAME
* lastname
* Last-Name
* Last-Name*
* last_name

# Ability Criteria

Sometimes you need to rank riders from a number of ability categories into a single age-based category.  __CallupSeedingMgr__ supports this as follows:

Create an __Ability__ column in one of your sheets.  In the __Ability__ column, __CallupSeedingMgr__ recognizes:

* numbers on their own (1, 2, 3, 4)
* text followed by a number (Cat1, Cat2... M1, M2...).  Spaces don't matter.
* "Grade" with a letter (Grade A, Grade B, ...).  Spaces don't matter.

Where 1 and A are the highest ability.

Now, make sure you also have a __Points__ or __Position__ column to indicate the rank of the rider within that ability.  If no __Points__ or __Position__ column is present, __CallupSeedingMgr__ will use the row number as the position.

__CallupSeedingMgr__ will then group the riders by __Ability__, then by __Points__ (or __Position__) within each ability to form an overall ranking.

Of course, Ability criteria sheets can be combined with other sheets in the overall ordering.

In the tutorial, take a look at the __Western Series__ sheet where there are rider rankings by Ability and Points.

# Cycling by Criteria

Sometimes you need to combine the results from independent championships or series by cycling entries between them.

For example, in the tutorial, we want to cycle between the Western Series and the Eastern Series.

Tell __CallupSeedingMgr__ about the cycling by setting __Cycle Criteria__.

In the tutorial, set __Cycle Criteria__ to __Last 2__ to tell it that we want to cycle callups between the last two criteria.

Now, scroll down and take a look.  The riders alternate between the criteria, "leftover" riders are in the same sequence, and riders with no criteria are randomized.  Just as we want.

If __CallupSeedingMgr__ has more then 2 critera to cycle through, it will cycle the remaining elements as sets become empty.

The cycling starts with the first sheet in the Excel workbook (Western Series in this example).

__Cycle Criteria__ can cycle up to the last 4 criteria.

# Conclusion

This tutorial shows how to do callups and seeding with many criteria, including converting ability-based rankings to age-based, and cycling through multiple criteria.
Hopefully you will never encounter a situation this complicated.

In practice, collect and organize your criteria sheets ahead of time.  Then, when you get the final registration list (could be the day of the competition), generate the callups or seeding instantly.
