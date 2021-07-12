[TOC]

# Announcer
Shows a results screen suitable for an announcer to call the race.  It has a number of features to help the announcer:
* Shows a highlighted countdown to every rider's expected arrival.
* Allows the announcer to quickly switch between categories for multi-category races.
* Shows a countdown to the expected leader of every category, even if the category results are not currently displayed.
* As each competitor approaches the finish, the projected postion is shown in grey.  When the competitor cross the finish line on each lap, the row is un-greyed and the known position is shown.
* Shows results information including rider name, team, bib, position, time gap (to leader) and color-coded chase grouup.

The __Annouuncer__ screen is also available as a live web page (see [Web][] for details).  This web page will __automatically__ update with the latest information information from the current race.
With a tablet connected to a local wifi, you can provide the race announcer with mobile access to the __Accouncer__ info.

To see the __Announcer__ screen in action, start a race simulation from [Menu-Tools][] and watch the screen, both in CrossMgr and the web page.

It is great to be able to give a tablet to the race announcer with the live results.  The easiest way to do this is:

* Make sure there is a QRCode reader app installed on the tablet ahead of time.
* Ensure the CrossMgr computer and the tablet are connected to the same wireless LAN.
* From CrossMgr, do __Web|QRCode Share Page__.  This will open up the browser with a web page showing a QRCode that connects to CrossMgr.
* Open the QRCode app on the tablet and point it at the CrossMgr computer screen.  When it recognizes the code, press "Open".
* Now the tablet is connected to CrossMgr's Index page.
* From the Index page, click on __Announcer__ at the top.

## Function

The Announcer screen consists of 2 parts:
1. Category Selection
1. Results Display

### Category Selection

The Announcer screen shows all categories with the __Publish__flag set (see [Categories][] for details).
These can be __Start Wave__, __Component__ or __Custom__ categories.

Each Category can be selected by pressing the button at the top of the screen.

The leader of each Category is also shown with an Estimated Time of Arrival (ETA) on the selection button.
When the countdown gets within 15 seconds the button turns dark green.
It then progressivly turns to light green, getting brightest at 0 seconds.
A negative ETA means the leader is overdue.

### Results Display

The Results display shows the current race standings by each lap.  The competitor's name, team and bib are shown.  Results information is also shown including position in the race, time gap, and chase group.  DNF, DNS, DQ and Pulled riders are not shown.

Greyed-out rows mean that the rider has not passed the finish line yet and the current position is a projection.

When the row is no longer grey, the competitor has passed the finish line and the position in the lap is known.

Each entry also shows ETA (Estimated Time of Arrival) countdown timer.  The timer turns dark green at 15 seconds to go and gets progressivly lighter.  This makes it easy to look for expected competitors.

The ETA color display is also useful to see lapped riders who may be mixed in with leaders.

Competitors who pass the finish line and have "real" results always take precedence to projected results.  For example, say the leader has a mechanical and is significantly delayed on the lap.  That competitor's projected result will "fall down" the results list as other competitors pass the finish and are recorded ahead of him.

The Group shows all riders that are within 1 second of each other.  This is useful to understand chase groups in the race situation.

