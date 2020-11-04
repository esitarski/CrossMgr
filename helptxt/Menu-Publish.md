
[TOC]

# Publish

## Page Setup...
Setup the printing page when printing the results directly from CrossMgr.

## Preview Print Results...
Shows how the results would look if printed.

## Print Results...
Prints formatted results directly to a printer.
Select the Categories you want to print in the dialog, the select the Printer and Print Options.

You can print results for a Category only if there are riders of that Category in the race.

## Print Podium Results...
Prints formatted results directly to a printer in a format suitable to announce podium results.

Select the Categories you want to print in the dialog, select the Podium positions, then select the Printer and Print Options.

The output will not include lap times, nor will it include DNF, DNS or DQ riders (only finishers for podium).

You can print results for a Category only if there are riders of that Category in the race.

The report will include the specified number of podium positions, or the number of finishers in the category - whichever is less.

## Print Categories...
Prints a summary of the Categories with number of laps and number ranges.  This can be useful as a quick reference to all the categories on course and not a bulky as a full start list.

## Batch Publish Files...

This brings up a dialog that allows you to publish results in many formats.  __Batch Publish__ will update all the output file formats simultaneously so they are synchronized.  All output files are written to the same folder as the race file.

You can also generate individual output files by pressing the __Test__button.  __Test__ will also open the application associated with the generated file (Excel for .xlsx, your browser for .html, etc.).

Some files have the option to publish with FTP to a remote server, allowing results to be published to a web site.  You need to configure the connection details of the remote FTP server to make this work (see [Properties][]).

### HTML
Publish the results as an HTML file.  Includes the Race Animation and the Chart if specified in [Properties][].

The HTML web page has a drop-down button next to the __Refresh__ button to control __Kiosk Mode__.
The options are __Results__ (regular), __Kiosk__ (__Kiosk Mode__ leader board) and __Kiosk Arrival__ (__Kiosk Mode__ with participants ordered by arrive time - most recent arrivals at the top).
__Kiosk Mode__ cycles through results for each category every 15 seconds.  It is useful to show results at live events.

__Kiosk Arrival__ mode is useful for Gran Fondos and Time Trials.
In this mode, the most recent finisher is shown at the top.
The position (both in the start wave and in any specific category) is shown in a separate column.

A competitor can quickly check his/her result at the top of the screen after crossing the finish rather than having to scroll down to the bottom of the screen.  In this way, competitors in Gran Fondo's with 1,000s of participants can still see the results at the finish.

__Tip:__ After selecting Kiosk mode, Press __F11__ to put the browser into full-screen mode (press F11 to exit full screen).  This shows the maximum screen area.

For automatic control, the HTML web page includes additional options that can be controlled by setting query values in the URL.
For example:

   <your-race>.html?kioskMode=t
   
This will put the page into __Kiosk Mode__.  In this mode, the page will automatically cycle through all categories while hiding the map, title, and all other non-essential information.  __Kiosk Mode__ is useful if you have a computer/big screen showing live results at the race.

	<your-race>.html?arrivalMode=t
	
In this mode, the most recent finisher is shown at the top of the results.

Modes can be combined together:

	<your-race>.html?kioskMode=t&arrivalMode=t

This combination combines category cycling with listing the latest result at the top.  Good for live Gran Fondos finishes.

You can also change the default language of the page:

	<your-race>.html?lang=__xx__
	
Where __xx__ is either __en__, __fr__ or __es__ for English, French or Spanish respectively.  When a language is specified with the __lang=xx__ option, it is shown first in the language list.

### Index HTML
Creates the Index (navigation) page for the race.

### PDF
Publish the results in pdf format.

### Excel
Publish the results in Excel format, one category per sheet.

### CrossResults.com
Creates a CrossResults.com compatible file.  Only Categories flagged as __Upload__ will be considered.
Launches your web browser to the CrossResults.com upload page to upload it automatically.

### WebScorer.com
Creates a WebScorer.com compatible file.  Only Categories flagged as __Upload__ will be considered.
Follow the instructions on the WebScorer.com site to upload this file.

### USAC
Export the results for race categories in a format acceptable to [USACycling][].  Only Categories flagged as __Upload__ will be considered.
Follow the USAC instructions to upload this file.

Columns in the exported spreadsheet are as follows:

Column|Description
:-----|:----------
rider place|Corresponds to the __Pos__ field in CrossMgr [Results][].
race gender|The gender of the this Category as specified in [Categories][]
race discipline|As specified in the race [Properties][].  This must match the USAC standard discipline name.
race category|The name of the Category of this rider as specified in [Categories][].
rider last name|Corresponds to the rider's __LastName__ as configured in the [External Excel][] sheet.
rider first name|Corresponds to the rider's __FirstName__ as configured in the [External Excel][] sheet.
rider team|Corresponds to the rider's __Team__ as configured in the [External Excel][] sheet.
time|Corresponds to the __Time__ field in CrossMgr [Results][].

In the __rider place__ column, USAC only recognizes a place (number) and the statuses __DNF__, __DNS__ and __DNP__ (Did Not Place).

CrossMgr's status codes are translated to USAC's status codes as follows:

Description|CrossMgr Code|USAC Code
:----------|:-----------:|:-------:
Disqualified|DQ|DQ
Did Not Start|DNS|DNS
Did Not Finish|DNF|DNF
Pulled|PUL|DNP
Not Placed|NP|DNP
Outside Time Bound|OTL|DNP

### UCI

Export the results in standard UCI Dataride format (both start list and results).  Only Categories flagged as __Upload__ will be considered.
Follow the UCI Dataride instructions to upload this file to the UCI site.

### Facebook
Publish the results as PNG image files suitable for posting to Facebook or Tumblr, which do not allow PDF or HTML content.
The PNG files are written into a folder called __ResultsPNG__ in the same folder as the CrossMgr race file.

Although __quick and dirty__, this is not a recommended way to publish to Facebook.
The image files cannot be indexed by Google, Bing, Yahoo or other search engines.  This makes it impossible for people to find your results by searching.

See [Facebook][] for some better suggestions about how to publish results in a search engine-friendly format.

### Post Publish Command

Runs a command after the publish.  This is useful if you want to move the files to another location, or perform other post-processing on the file.  You can use substitions in the command:

Substitution|Description
:-----------|:----------
%*         |Inserts all the published file names.
{=Value}    |Inserts a [Properties][] Notes value, for example {=EventName}, {=RaceDate}

### Details, Logic and Example of Live Results:

Publishing results during a race does not slow down or lock up CrossMgr even if it loses the connection with the FTP server or the publish fails.  This is because publishing is run in a separate background thread.  You will not notice it is happening.

Results are published with FTP in a way that balances response time with bandwidth.

You will see a publish latency of 4 seconds after each group passes the line, and no updates when there are no events.
The latency will increase when riders get strung out, to a maximum of 32 seconds.

The update logic was inspired by [exponential-backoff](http://en.wikipedia.org/wiki/Exponential_backoff), also used in TCP/IP.
The idea is to minimize bandwidth and while while maximizing response time.

An update timer is triggered when a rider's time is entered.  If all riders are on the back side of the course and there is no data input, no update will occur.

A time entry (manual or chip) starts a timer.  When the timer fires, CrossMgr does the FTP upload.
Additional time entries recorded while the timer is running are included in the upload.  The FTP publish time is recorded - let's call this the __LastPublishTime__.

Initially, the timer interval is 4 seconds - let's call this the __TimerInterval__.

Now, let's consider the next time entry - call it __T__.

* If the timer is running:
    * Do nothing - __T__ will be included when the timer fires.
* Else, the timer is not running:
    * If __T__ > __LastPublishTime__ + __TimerInterval__, then set __TimerInterval__ = 4
    * Else set __TimerInterval__ = min(__TimerInterval__ * 2, 32)
    * Start the timer

In short, if the gap from the last update exceeds the last __TimerInterval__, reset it to 4.
If the gap does not exceed the last __TimerInterval__, double it to a max of 32 seconds.

For example, say the lap time is 5 minutes, and the bunch is all together on the first lap.
The first rider in the bunch crosses the line and triggers the 4 second timer.  While the timer is running, the rest of the group crosses the line and is recorded.  After 4 seconds, the upload runs and includes the times of all riders.

This is superior to publishing on a fixed schedule like every 30 or 60 seconds.  On a fixed schedule, bandwidth is wasted if nothing changed.  Worse, the results might not be updated for a full interval after some action.
For example, if a new rider takes the lead, the update might take as long as 60 seconds to publish.
This can feel like a very long time - especially if you are the race announcer.

Back to our example.  Say a break develops with a gap of 10 seconds.  An update will occur 4 seconds after the break, then 4 seconds after the group.  The timer is reset between the groups because the gap time (10 seconds) exceeds the timer interval (4 seconds).

Say the break increases to 30 seconds and a chase group forms 10 seconds after that.  No problem - the logic will now do three publishes, each 4 seconds after the break, group and the bunch respectively.

Say the bunch now splits up with a line of stragglers, and the whole race now takes 2 minutes to pass the finish line.  We will see an update 4 seconds after the break, then 4 seconds after the chase group, then 4 seconds after the beginning of the bunch, then 8 seconds for the following stragglers, then 16 seconds, then 32 seconds (repeating) as all the stragglers go by.

When the leaders return, the timer will reset back to 4 seconds because the gap between the last bunch rider and the leaders exceeds 32 seconds.

This approach follows race activity - no activity - no publish.
If riders are so strung out that there are no discernible groups, it backs off to sending an update every 32 seconds - like a fixed-interval approach.

