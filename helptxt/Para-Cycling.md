[TOC]

# Para-Cycling

CrossMgr supports Para-Cycling.  There are a number of configurations that need to be done.

## Performance Factors

Athlete's Performance Factors for combined Para categories are entered in the linked Excel sheet under a __Factor__ column.
The Factor must be a percent.  See [External Excel][] for details.

When a Factor is present, it will be multiplied by the athlete's time to get an adjusted time.  The athlete's will them be ranked according to the adjusted time.

There is no additional configuration required.  If Factor is present, CrossMgr will use it.

In all published output for combined categories using Factors (this includes Results, Spreasheet, HTML, Printing), the ElapsedTime, Factor and adjusted Time are shown, making it easy to validate the result.  Gap is not shown, as it make little sense with adjusted times.

For Component and Custom Categories (see [Categories][]) where all the athletes have the same Factor, the __regular__ results are shown without ElapsedTime and Factor, and the Time is the race time.  Gap is shown.

## Combined Handcycling Category Example

Say you have a combined category handcycle race with H3, H2 and H1 Men, and some H5 women athletes.

To configure this in CrossMgr, you could set up the category structure as follows:

* (Start Wave) Combined (Open)
	* (Component) H3 (Men)
	* (Component) H5 (Women)
	* (Component) H2 (Men)
	* (Component) H1 (Men)

That is, you have a Combined race (a Start Wave) consisting of four Components: H5, H3 and H1 Men, and H5 Women.

If you don't want CrossMgr to split out the results for individual classifications, you can put everyone into one Start Wave Category as follows:

* (Start Wave) Combined (Open)

Assign number ranges corresponding to the athlete's numbers to your Category(ies).

Because lapped riders could still be in contention, set the __Lapped Riders Continue__ flag of the __Combined__ category.  This is very important!  H1 athletes may be lapped by the H3 riders, but because of the Performance Factor, an H1 athlete might be the winner.  All riders must complete the full distance.

In your Excel spreadsheet, create a Factor column (in addition to the athlete information) and enter the factors from the UCI table (see [here](http://www.uci.ch/includes/asp/getTarget.asp?type=FILE&id=MzQwMzY)).

You use the column in the table corresponding to the highest classificiation in the race.  In this case, the highest category in the race is H3 Men, so we use the 3rd column in the Division H table in the UCI rules.

If your highest classification was H5 Men, you would use the first column in the table.  If it was H3 Women, you would use the 7th column.

So, in the Factor column of your Excel spreadsheet, all H3 Men get a factor of 100, H5 Women get a factor of 90.19, H2 Men get 79.40, and H1 Men get 58.24.

That's it!  CrossMgr will then automatically apply the factors and score the results properly from there.
You can change the Factors at any time - before, during or after the race.  CrossMgr will re-rank the riders accordingly.

Whether a Road Race or a Time Trial, use the same procedure for setting up the Categories and Factors.

Be mindful that there can be a number of complexities with Performance Factors.  For example, say a fast H3 athlete wants to compete in an H4-H5 race.  In this case, the H3 rider would __not__ get a 97.25 factor because he is __racing up__.  Although he has an H3 classification, he is not entitled to the H3 performance factor in this case.

## Para-Cycling and RFID

It is __highly recommended__ to use RFID chips with Para-Cycling, in fact, an RFID system is a __must have__ not a __nice to have__.

First, the RFID counts all the laps of every athlete on course.  This is critical: athletes are ranked by distance completed, then by factor-adjusted finish time.  With athletes of different abilities on course, counting laps can be difficult and requires a lot of manual backup.

Second, factor-adjusted results __require__ a finish time for each athlete.  A finish order is insufficient - you need the __finish time__ of every athlete.  CrossMgr with an RFID system will automatically record the finish times and lap splits.  This greatly reduces the burden on officials and volunteers, and eliminates data input errors.

Third, handcycles are very low to the ground and the numbers can be very hard to see.  A chip reader will automatically identify the athletes and eliminate the reliance on manual identification.

So, consider an RFID chip system for para events.
