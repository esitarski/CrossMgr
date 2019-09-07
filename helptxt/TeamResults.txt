[TOC]

# TeamResults
TeamResults shows ranked riders ranked by Team.  Teams can be ranked in a number of ways (see [Properties][]).

CrossMgr shows the Team criteria (Time, Points, Percentage of Winner's Time) and the Gap from the lead Team.

There is a peculiar special case that can happen in multi-category races.  In a multi-category race, some riders may finish having been lapped by the leader of a faster category, but not lapped by their own category leader.

Although these riders has completed one less lap than their category leader, they technically are not lapped.  It is therefore impossible to compute a Gap time, nor is if fair to report those riders as down a lap.  In this case, CrossMgr simply shows nothing in the Gap column.

# Controls
## Category
Selects the Category of the Team Results.

# TeamResults Data

Data about the ream results is shown.  The Team comes from the [External Excel][]. sheet.

Column|Description
:-----|:----------
Pos|The position of the rider in the race.  When Category is "All", shows the rider's place with respect to all participants.  When the Category is set, this shows results with respect to that Category only.
Team|The team names.
Time/Points|Time or Points
Gap|Gap between lead team and current team (time or points).

## Notes

Riders without a Team name in the [External Excel][] sheet, or have team name "Independent" or "Ind" are not shown.

Teams that have too few members to meet the ranking criteris (fewer than "Nth Rider Time" or "Top Team Results") are not shown (see [Properties][] for more details).
