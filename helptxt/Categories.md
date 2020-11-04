[TOC]

# Categories

A race category is a pattern of numbers ranked together - it does not have to be the same as the category that appears on a rider's license code.

It is easy to change CrossMgr categories before, during and afterwards.  A rider can be moved between categories before, during and after a race, and the results will automatically update.

Ideally, each category in the race would have a unique number range, for example 1-99 would be in one category, 100-199 would be in another, etc.
This is not only easier to configure in CrossMgr, it makes it easy for riders and race officials to know the set of competitors in the same race.

If you don't have number ranges by category, and you have "arbitrary" numbers, consider using the __Initialize CrossMgr Categories from Excel EventCategory/CustomCategory and Bib# columns__ option in [DataMgmt][].  This feature allows you to set the Category numbers automatically from a spreadsheet.

It is commonplace to combine categories together into a single start wave (for example, Elite Women and Master Women, or Cat 3 and Cat 4).
Or, sometimes categories are in different start waves with a time offset between them.

Sometimes prizes are only given for the combined finish.  Sometimes prizes are also given for each component category in the combined race.  Ranking by component category can also be important for upgrade points.

Sometimes there are special ranking criteria.  For example, although non-Canadian nationals are allowed to compete in the Canadian National Road Race, only Canadian Nationals are eligible for the Canadian National Champion ranking.

Sometimes organizers come up with creative ranking criteria.  For example, a ranking for "Fastest Non-Elite Women" even though the Masters Women and Junior Women are in different start waves.

CrossMgr makes this easy by supporting three types of Categories:

1. __Start Wave:__ a group of riders that start at the same time.  The riders may all be in the same category, or they may be made up of multiple component categories riding together.  A "Start Wave" may, or may not have "Components".  Riders in a "Start Wave" are considered in the same race, and can work together.  Each "Start Wave" is managed in CrossMgr with a race progress bar on the [Record][] page.
1. __Component:__ a sub-group of riders part of a "Start Wave", all of which are in the same category with respect to each other.  Riders in a "Component" can work together with other riders in their "Component", as well as other riders in their "Start Wave".  "Component" categories use the same "Start Offset", "Race Laps" and other options as their "Start Wave".
1. __Custom:__ a group of riders defined by any criteria - they don't even need to be part of the same "Start Wave".  A "Custom" category could be a completely imaginary ranking of riders in different Start Waves.

## Step by Step Configuration

### Combined Categories

For example, say that you have Cat 3, Cat 4 and Junior Men and Elite Women, Master Women and Junior Women, and you want to combine them into two Start Waves, with a start offset of 60 seconds for the women's race.
First, set up those Categories in CrossMgr.

Now, we need the Start Waves.  A Start Wave is simply the whistle that a group of riders starts on.  By default, CrossMgr ranks riders both by the Start Wave overall, and by the Components in the Start Wave.  If you don't want the overall ranking in the results, you can de-select the __Publish__ flag on the Category row (more on that later).

To create some Start Waves, press the "New Category" button, and change the new category name to "Combined Men".
Do the same and make a category for "Combined Women".
Notice that the default "Category Type" is "Start Wave.

Press and hold on the left grey cell (first cell in the row) of the "Combined Men" and drag the row up to be the 1st row.
Drag the men's categories (Cat 3, Cat 4 and Junior) so that are in rows directly below "Combined Men".

Drag the "Combined Women" category to the row just after all the men's categories.

Click on the "Category Type" cell in the "Cat 3" Men row.  Change it to a "Component" category.  Do the same for the other Men's categories.

Set the "Category Type" to "Component" for the Master and Junior categories.

Now, set the "Start Offset" for the "Combined Women" category to be 60 seconds.

You should see something like this:

- __Start Wave__  Combined Men
    - __Component__ Cat 3
    - __Component__ Cat 4
    - __Component__ Junior
- __Start Wave__  Combined Women  StartOffset=60
    - __Component__  Elite Women
    - __Component__  Master Women
    - __Component__  Junior Women

That's it.  You now have two Start Waves, with the appropriate Component categories within each wave.

The fastest way to do this for lots of categories is by using keyboard shortcuts, but using the mouse works fine too.

By default, a rider is ranked within the Start Wave as well as each Component.  If you don't want the Start Wave to appear in the published results, de-select the "Publish" checkbox for that Category (to the right in the Category row).  Overall Start Wave results are always available in CrossMgr because that is what the race officials will need to validate.

You can configure as many "Start Wave" combined categories you like in a race.  The "Start Wave" is always the first row in a group, followed by the "Component" rows, which are indented automatically.

All the Components in a Start Wave "inherit" the Race Laps, Distance, etc. of the Start Wave (that's why those fields are greyed-out).  The bib numbers in a Start Wave will automatically update to include all the numbers in the Components.

CrossMgr makes the following assumptions about bib numbers in a race:

* __All numbers in a Race are unique__.  If the number ranges for two "Start Waves" overlap, CrossMgr will consider the rider to be in the __first__ matching "Start Wave"
* __All numbers in a "Start Wave" are unique__.  If the number ranges for two "Components" overlap, CrossMgr will consider the rider to be in the the __first__ matching "Component" in the "Start Wave".

This means that if you have overlapping number ranges in two or more categories, the first category will "win".

### Custom Categories

"Custom" categories are just a set of Bib Numbers.  The Numbers don't all have to be in the same "Start Wave".  Riders in a "Custom" category are first scored with respect to their actual "Start Wave", then re-scored __as if__ they all started in the same imaginary "Start Wave".

No overlap checking is done on numbers in a "Custom" category - you can enter any number ranges you want, and multiple Custom categories can have overlapping numbers.
"Custom" category number ranges __can also overlap with any other categories__.  A rider may appear multiple times in "Custom" categories.

For example, consider the following "Custom" categories which could be active in the same race (let's say that the number ranges have been configured appropriately):

* All Riders in Lightning Cycling Club (LCC)
* All Riders in LCC who are <19 years old
* All Riders <19 years old

Riders would be ranked as:

* If Adam is a member of LCC and 17 years old, he would appear in all three "Custom" categories.
* If Bart is not a member of LCC and 18 years old, he would appear in the "All Riders <19 years old" Custom category.
* Is Calvin is not a member of LCC and is 23, he would not appear in any of these "Custom" categories.

## Multiple Categories, Uploading and Series

Result uploading is controled with the __Upload__ flag.

Carefully consider how you want to publish to web/Excel/printouts, CrossResults, WebScorer and USA Cycling.
The site may want to see a rider once in the results - not in the combined categpry, or other multiple categories.

Set the __Upload__ flag to control whether you want to upload the the "Start Wave" (combined) results, or the "Component" results (usually not both).

The __Series__flag works similarly, but indicates that a category should be included in a race Series.  The program SeriesMgr looks at this flag.

### Note about __Initialize CrossMgr Categories from Excel EventCategory/CustomCategory and Bib# columns__ option in [DataMgmt][]/Link to External Excel Data...
If you choose this option, the Categories and Bib numbers will be determined by the contents of the Excel sheet.
Any changes you make in CrossMgr will be over-written by the information in the Excel sheet.

If you choose this option, always your changes in the Excel spreadsheet, not in CrossMgr.

The __EventCategory__ column initializes the "Start Wave" or "Component" CrossMgr category.

The __CustomCategory__ initializes the "Custom" CrossMgr category (for a description of "Start Wave" and "Custom" categories, see above).

For example, say you had a Gran Fondo with Fast, Medium and Slow start waves, each starting 10 minutes apart.
Riders pick which start they want at registration.

You also need to rank the riders by Age Group, regardless of the wave they started in.
Riders of any age can choose any Wave, so you could have 20-29, 30-39, 40-49 etc. riders in each Wave.

Because there is no relationship between Start Wave and Age Group, you cannot use Start Wave/Component categories.

This is where the __CustomCategory__ comes in.  From the spreadsheet, set the Wave as the __EventCategory__, and set the Age Group as the __CustomCategory__.
This tells CrossMgr to add the rider to two categories - the Start Wave, and the Age Group.
It will then rank the riders in both.  This allows you to produce results for the Wave as well as the Age Group at the same time.

# Controls

## Drag and Drop Rows
Category rows will drag-and-drop by pressing in the left-most cell in the row under the "up-down" arrow.  The "up-down" arrow is in the upper-left of the Categories table.

## Activate All
Activate all Categories.  Active Categories will be considered in the race.

## Deactivate All
Deactivate all Categories.  Deactivated Categories will not be considered in the race.

## New Category
Add a new Category to the race.

## Delete Category
Delete an existing new Category to the race.  Click anywhere on the row of the Category you want to delete, then press this button.

## Move Up
Move a Category up in the table.  Click anywhere on the row you want to move and press this button.  The number ranges of this category will be considered before all subsequent categories (see explanation below).

## Move Down
Move a Category up in the table.  Click anywhere on the row you want to move and press this button.  The number ranges of this category will be considered after all preceding categories (see explanation below).

## Add Bib Exception
Allows you to automatically add a bib exception to a selected category.  This action also adds the appropriate exceptions to the other categories.  Although you can do this here, it is more convenient to manage category exceptions directly from the [RiderDetail](RiderDetail.html) screen.

## Normalize
Press this button to format the number ranges in a more compact format with as many number ranges as possible.  For example, __1,2,3,4,5,8,9,10,11,12,-8__ will change to __1-5,9-12__.

## Update Start Wave Numbers
Press this button to automatically adjust the Start Wave category to include all the Component categories numbers.  __This button is pressed automatically when you leave the Categories page.__

# Category Screen

The Category screen is a table with the category details:

Property|Description
:-------|:----------
Active|If selected, this Category will be considered in the race.  If deselected, this Category will be ignored.  Some CrossMgr users configure an external Category file with all possible categories in it.  The then select only the categories that are in this race.
Category Type|Either "Start Wave", "Component" or "Custom"
Name|Name of the Category
Gender|Gender of the Category.  Choices are "Men", "Women" or "Open".
Numbers|The numbers of riders in this Category.  Numbers can be expressed individually like 103,105 or a range, like 100-199.  Exclusions exceptions are expressed by preceding the excluded number with a '-' sign.  Exceptions can be express individually, like -201,-205 or in a range -201-205.  See [Number Patterns](#number-patterns) for more details below.  You can cut-and-paste in numbers from Excel, either in vertical columns or horizontally in rows.  This makes it easier to enter irregular number ranges from Excel when necessary.  When using the __Initialize CrossMgr Categories from Excel EventCategory and Bib# columns__ option, the number ranges will be automatically determined from the Excel sheet.
Start Offset|When starting multiple categories at the same time, here is where you enter the offset of later starts from the first start.
Race Laps|If you know the number of laps, enter it here.  If you leave this blank, CrossMgr will compute the laps for this category based on the __Race Minutes__ defined in the next field, or in [Properties][].  Specifying a __Race Laps__ will override CrossMgr's computation.
Race Minutes|If you want to run this category on a time different from the Properties' __Race Minutes__, enter the minutes here.  If __Race Laps__ is defined, __Race Minutes__ is ignored.  If both fields are blank, the number of laps will be determined from the [Properties][] __Race Minutes__.
Lapped Riders Continue|If selected, riders who are lapped by their category leader will be expected to complete the full number of laps in the race, not just the laps completed on the winners lap.  In normal CycloCross and MTB events, all riders finish on the last lap, and this option should not be set.  With combined Paracycling categories, you will need to select this as lapped athletes may still be in contention due to the Performance Factors.
Distance|The distance of the lap or the race (depends on the value of the next column).  The distance unit will be what you configured in Properties.
Distance is By|This field is either "Lap" if the distance you entered is by lap, or "Race" if the distance is for the entire race.  If distance is by "Race", CrossMgr will not compute lap speeds as it does not know the lap distance.  Generally, you would only use Distance by Race if the race was a point-to-point race, or if the laps were not the same distance.
First Lap Distance|Fill in this field if the first lap of your race is not the same as the subsequent laps.  This can happen in many situations, for example, when the rider staging area is not at the start/finish line.  If there is a run-up to the start, make the first lap longer than the rest of the laps.  For example, if the lap distance is 3.6km, and there is a 200m run-up to the start, make the first lap 3.8km, and do not log riders mapping the finish after the run-up.  If you are using chip timing, see appropriate chip timing start options here [Actions][].
80% Lap Time|This is computed by CrossMgr.  It is the maximum time a rider can fall behind the leader before being a candidate to be pulled in a UCI CycloCross or MTB race.  It is computed as 80% of each category leader's first lap time.  If the first lap distance is not the same as the regular lap distance (see above), the second lap time is used.  Riders outside the 80% time boundary are shown in red in the [Expected](Expected.html#expected) screen.
CrossMgr Estimated Laps|Computed by CrossMgr by dividing the lap time into the race time.  Important if you are running a race by time rather than laps.  The "Race Laps" column overrides this field.  Use the "Race Laps" field if you know the number of laps in the race.
Publish|If selected, this Category will be included in Web and Print results.  This feature is useful is you need a combined Wave Category to determine finish order for the officials, but only want to publish the Component categories in the results.
Upload|If selected, this Category will be included in CrossResults, WebScorer and USAC publish.
Series|If selected, this Category will be included as part of a Series in SeriesMgr.

## Number Patterns
Number patterns are expressive and flexible, and are used to identify the number range of riders in a Category.

For example, each Category could have number in a simple range like 1-99, 100-199, etc.

You should always assign a number range to each Category ahead of time.  Hand out numbers to riders consistent with the Category range - not "off the top of the pile in the order the riders showed up".
This is a common first-timers mistake.

Category number ranges make it trivial for riders, officials and you to know a rider's Category just by his/her number.  This greatly reduces all sorts of errors at the race.  It allows anyone to quickly ensure riders are in the right race, at the right start, for riders to know their competitors in a mixed-category race, and for officials to follow what is going on.

Consistent number ranges by Category are essential at high-level races for applying the 80% rule and pulling riders in a category.
Be a pro - assign number ranges to Categories.

Of course, sometimes numbers don't follow simple ranges, and CrossMgr can handle that too.

For example, consider "100-199, -151, -155, 205, 220-229, -170-179".

This complex example matches the numbers from 100 to 199, excluding 151 and 155, including 205, 200 to 229 and excluding the range 170-179. 
Of course, this is insanity for riders and officials.

If you have a lot of exceptions, it can be easier set the exception from the [RiderDetail][] screen rather than from Categories.   Assigning the category from [RiderDetail][] automatically takes care of the number patterns.

To find the category of a rider, CrossMgr starts with the first active category and checks for a match in the number pattern.  If that fails, it continues to the second active category, etc.  The first active Category that matches the rider's number is considered the rider's Category for the race.

### Copy and Paste Bib Numbers from Excel

Sometimes you have inconsistent numbers for your race categories, but everything is correct in your Excel sheet.
If so, consider using the __Initialize CrossMgr Categories from Excel EventCategory and Bib# columns__ option in [DataMgmt][] feature.

However, you can also copy-and-paste a row of numbers from Excel into CrossMgr.
To make your new CrossMgr number ranges more comprehensible, press the __Normalize__ button at the top of the Categories screen.  This reformats the individual numbers into compact ranges.
  
## Question: Why does CrossMgr configure lap distance by Category instead of the entire race?

Well, sometimes different categories have a different lap distance, especially in a time trial.  To provide for this flexibility, CrossMgr requires the lap distance at the Category level, not the race level.

Yes, it's a little extra trouble, but with copy-and-paste (Ctrl-C, Ctrl-V), it isn't so bad.  It is great to have this flexibility when you need it.
