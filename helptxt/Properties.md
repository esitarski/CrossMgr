[TOC]

# Properties
Allows you to configure properties of the race.

Properties include many race options, camera options, web options and the race course in GPX format.

Properties can be saved to a __Template__.  This allows you to save the options you configured for a race and use them in another race - just load the template.

The __Template__ includes all configurable options including FTP, Graphic and GPX Course.
It does not include data specific to the race like the Categories or the Excel spreadsheet.

# Property Screen

## General Options
Property|Description
:-------|:----------
Event Name|Name of the event - also used for the event's filename (along with the Race #).  Multiple races in the day will have the same Event Name, but with different race numbers.
Long Name|Long name of the event.  The __Long Name__ is useful if the __Event Name__ has organizers and sponsors that make the name unwieldy, or contain characers that don't work in file names.  For example "2017 National Championships p/b Trend Setter Organizer" is cumbersome to work with and contains a "slash" that can't be in a filename.  The __Long Name__ will be shown on all results, spreadsheets and web output if it is defined.  Otherwise the __Event Name__ is used.
Date|Date of the race.  Used in the filename and all output.
Race #|The number of the race in the day at the event.  Also used in the race filename.  This is automatically incremented when you do "File/New Next..."
Scheduled Start|Scheduled start of the race.  This is used in the results output.  Of course, the race could actually start at a different time.
Race Minutes|The __global__ number of minutes in the race for timed races (like CycloCross).  See __Notes__ below.
Discipline|The type of race (default Cyclo-cross).  This should reflect the type of race (Road, Mountain Bike, Criterium, etc.).  Currently, this is only used in the [USAC Export][].
Organizer|Organizer of the race.  Included in the HTML results output.
Commissaire|The name of the race official.
Memo|Anything you wish to type in here (weather conditions, your mood, etc.).  This is saved with the race but does not appear on any output.

### Notes
Races can be run by time, or by laps, or both simultaneously for different categories.
In CrossMgr, you can set the __Race Time__ in Properties.  You can also set it individually by Category.

* If you enter the __Race Laps__ in [Categories][], that category will be run by the specified laps.  This overrides all other settings - if you specify the number of laps, CrossMgr will respect that number.
* If you specify the __Race Minutes__ in the [Categories][] screen for a category, CrossMgr will compute the number of laps based on the category leader's lap times divided into the category __Race Minutes__.
* If the __Race Laps__ and __Race Minutes__ fields are both blank for a category, CrossMgr will compute the number of laps based on the __Race Minutes__ Property.  The Lap Counter will be follow the fastest category on course.

When running a race with different __Race Laps__ or __Race Minutes__ by Category, consider that you may need a separate lap counter for each category.  Fortunately, CrossMgr supports up to 4 lap counters (see [LapCounter][] for details).  The Lap Counter can be opened as a separate window and dragged onto another screen to show to the riders (see [Windows][] for details).

When running a race with the global Properties __Race Minutes__, all riders generally finish on the last lap and can be managed with one lap counter.  This can simplify race management considerably.

The __Start Offset__ is not included in the __Race Minutes__ when __Race Minutes__ is specified at the Category level.  For example, if a Category has __Start Offset=2:00__ and __Race Minutes=40__, CrossMgr will target finishing the race at 42 minutes.

While the race is under way, the Race Progress charts at the bottom of the [Record][] screen shows the laps and other race status for each category.

You can change a category's __Race Laps__ and __Race Minutes__ at any time before, during or after a race.
If you don't like CrossMgr's estimate of the laps, by all means, override it by setting the Category __Race Laps__.

See the [Record][] screen for details on managing a race with one lap counter, or multiple lap counters.

## Race Options
Property|Description
:-------|:----------
Time Trial|Specifies Time Trial mode.  In this mode, the rider's start time from the Excel spreadsheet is used.  If pre-seeded start times are not used, or there is no start time for the rider in the Excel sheet, the first time recorded for a rider starts the clock for that rider.  See [Further Explanation](#time-trial-mode).
All Categories Finish After Fastest Rider's Last Lap|Applies to multi-category races only.  Tells CrossMgr that all riders were stopped after the fastest rider in the race finished.  This means you stopped riders lapped by the fastest Category leader, but not lapped by their own Category leader.  This option is ignored for all Categories with "Race Laps" specified (see [Categories][]).
Set "Autocorrect Lap Data" option by Default|If true, CrossMgr sets the Autocorrect option by default when a rider is added to the race.  See [RiderDetail](RiderDetail.html) for details about Autocorrect.  If false, the Autocorrect option will not be set when a rider is added to the race.  You can change the Autocorrect option by rider in RiderDetail.  You can also enable/disable Autocorrect for all riders at once with "Edit/Enable Autocorrect for All Riders" and "Edit/Disable Autocorrect for All Riders".
Distance Unit|km or miles for the distances specified in Categories
Show Times to 100s of Second|You choice to display regular seconds or fractions of seconds in Results and History.  Also configurable from the Options menu.
Road Race Finish Times|Use Road Race rules for finish times.  Decimals are ignored, and all riders in the same group get the same time.  A rider is considered in the same group if separated by a second or less from the rider in front.
Lap Time for 80% Rule|Selects which lap you want to use to calculate the 80% time elimination rule.  If the first lap is significantly longer or shorter than the other laps, choose __2nd Lap Time__.  If the first lap is similar to the length of the other laps, choose __1st Lap Time__.  In Cyclocross, there is often a run-up which makes the first lap longer.  Sometimes it is possible time the run-up, sometimes this is difficult, and it is better to use the 2nd lap to compute the 80% time rule.  In MTB, it is often better to use the 1st lap time.
Consider Riders in Spreadsheet to be DNS if no race data|If there is no race data collected for a rider, and the rider is in the spreadsheet, consider the rider to be a DNS.
Distance Unit|The units distances to show in Results.
Show Lap Notes, Edits and Projected Times in HTML Output|If set, the internal lap edits will be written to the HTML page.  The lap information is shown similarly to the Chart screen.
Show Course Animation|If set, the course animation (either the track or the GPX course) will be shown in the HTML output.
Win and Out|If set, CrossMgr will score riders by fewest laps completed, then increasing finish time (in contrast to the usual rule of most laps completed, then increasing finish time).  Use this option for Win and Out races.  Do a "PUL after last lap..." on the intermediate sprint winners.
Min. Possible Lap Time|Lap times less than this value will be filtered out with AutoCorrect.  This can be used to remove spurious chip reads at the finish line.  The format is hh:mm:ss.ddd.
License Link HTML Template|Text to be put in front of the License code in the HTML output to form a link to get more rider information.  For example, if you enter __http://www.usacycling.org/results/?compid=__, and a rider's License code is __12345__, a link will be generated in the HTML page by combining the two to form __http://www.usacycling.org/results/?compid=12345__.  Clicking on the rider's license code will then open the USAC rider information page for that rider.  CrossMgr has no idea whether the link will succeed - it just generates it.

### Suggestions
Select __Road Race Finish Times__ only after you are satisfied with the results.  It can be confusing to see close finishing riders with the same times and gaps.

## Notes
Text that will appear in the HTML output.  Text entered here will be shown as-is in the HTML web page, including line breaks.  Describe weather conditions, give credit to the CrossMgr operator and number caller, or make notes about race participants.

For example:

    Notes for {=EventName}:
    
    Warning to the following riders for incorrect number placement:
    {=BibList 113, 117, 164}
    
    Special thanks to the following riders for helping out after the race:
    {=BibList 142, 153, 163}

This example uses "variables" which insert race information without having to retype it again.  Variables have the form "{=VariableName}" (no spaces around the "{", "=" or "}").
"BibList" is a special variable that takes a list of bib numbers and expends them into a list (more on that later).

You can also embed Html tags in notes to get nicer formatting or more powerful features, like hyperlinks.  To do so, your note must then start with `<html>` and end with `</html>`.  With Html tags, you can specify a hyperlink to a URL with `<a href="http://XXX">HyperLink</a>`, use a list with `<ol></ol>`, etc.  When using Html, you control your own line breaks: insert `<br/>` where you want a newline.

For example:

    <html>
    <h2>Big Race</h2>
    <p>
    Organizer: <strong> <a href="mailto:organizer.email@gmail.com">Email: Awesome Organizer</a> </strong> <br/>
    CrossMgr Operator: <strong> <a href="mailto:operator.email@gmail.com">Email: Awesome Operator</a> </strong> <br/>
    </p>
    </html>

Notes get even more powerful with html and variables.  For example:

    <html>
    <h2>{=EventName}</h2>
    <h2>{=City}, {=StateProv}, {=Country}</h2>
    <p>
    Organizer: <strong> <a href="mailto:organizer.email@gmail.com">Email: {=Organizer}</a> </strong> <br/>
    Commissaire: <strong> {=Commissaire} </strong> <br/>
    Start Time: <strong> {=StartTime} </strong> <br/>
    Start Method: <strong> {=StartMethod} </strong> <br/>
    </p>
    <p>
    Warning to the following riders for incorrect number placement:
    {=BibList 113, 117, 164}
    </p>
    <p>
    Special thanks to the following riders for helping out after the race:
    {=BibList 142, 153, 163}
    </p>
    </html>

Take notice of the "{=BibList 113, 117, 164}" variable.
"BibList" takes a list of bib numbers and expands them into a list with the "Bib: Last Name, First Name, License, UCI ID, Team" fields from the spreadsheet.  The "Bib", "BibList" and "BibTable" variables  make it easy to add full information about riders (see below for more details).

Variables can be conveniently inserted from the "Insert Variable..." button.  This is also helpful if you forget a variable name.

Variable names are case sensitive, so be careful.  The supported variables are:

Variable|Value
:-------|:----
{=EventName}|Name of the event
{=EventTitle}|Title of the event
{=RaceNum}|Race number
{=City}|City
{=StateProv}|StateProv
{=Country}|Country
{=Commissaire}|Commissaire
{=Organizer}|Organizer
{=Memo}|Memo
{=Discipline}|Discipline
{=RaceType}|"Time Trial" if the the Time Trial flag is set, otherwise "Mass Start"
{=RaceDate}|Date of the race
{=InputMethod}|Data input method.  Either "RFID" or "Manual".
{=StartTime}|Actual start time of the race if the races is started, else the "Scheduled Start Time" from General Options.
{=StartMethod}|Either "Automatic: Triggered by first tag read" or "Manual"
{=CameraStatus}|Either "USB Camera Enabled" or "USB Camera Not Enabled"
{=PhotoCount}|Number of photos taken during the race.  Will be zero if the usb camera is not enabled.
{=ExcelLink}|The file and sheet name of the Excel sheet linked to this race.
{=GPXFile}|The file name of the course in GPX format.
{=Bib NNN}|Expand the bib number NNN to show rider information including "Bib: Last Name, First Name, License, UCIID, Team".
{=BibList AAA, BBB, CCC, DDD, ...}|Expands the comma-separator bib numbers into a list showing "Bib: Last Name, First Name, License, UCIID, Team" in each line.
{=BibTable AAA, BBB, CCC, DDD, ...}|Expands the comma-separator bib numbers into a table showing "Bib: Last Name, First Name, License, UCIID, Team" in each row.
{=Path}|Full path name of the race file.
{=DirName}|Directory of the race file (no file name).
{=FileName}|File name of the race file (no directory name).


## RFID Options
Property|Description
:-------|:----------
Use RFID Reader|Use an RFID reader in the race.  When set, CrossMgr will act as a "server" that can receive real-time messages from a RFID reader.  The reader can be JChip, or the CrossMgrImpinj or CrossMgrAlien bridge programs that communicate with the Impinj and Alien readers, respectively.  See [RFID Reader Setup](Menu-ChipReader.html#rfid-reader-setup-dialog) for details.

### Manual Start: Collect every chip. Does NOT restart race clock on first read.
This option records tags the same as if you entered them manually.  Every tag that is read will be recorded.
The race is started manually.

### Automatic Start: Reset start clock on first tag read. All riders get the start time of the first read.
After the race is started with the Start button, this option resets the race clock to zero on the first tag read.
It also ignores the first tag read for all riders.
After this initialization process which starts the race clock, every tag read will be recorded.

This idea behind this feature is that the riders are stages behind the start line.
After the whistle, the first rider to the line "starts" the race.  All tags are recorded after that.

### Manual Start: Skip first tag read for all riders. Required when start run-up passes the finish on the first lap
After the race is started with the Start button, this option ignores the first tag read for all riders.

The idea behind this feature is that the riders are staged in a start area behind the finish line (say, 200m).  When the race starts, the riders pass the finish line - and the reader antennas.  You do not want to register this tag read as it "does not count".

When using this feature, be sure to set the "First Lap Distance" in [Categories][] to compensate for the run-up distance.  This will ensure that the riders speeds are computed correctly.

### Reader Type
Either JChip/Impinj/Alien or RaceResult.  See [ChipReader][] for more details.

## GPX

CrossMgr can import a course in GPX format and use it to display a race animation in the HTML output.

GPX files are standard files that can be generated from GPS receivers (Garmin, etc.).

The course fill be shown in the Animation screen, as well as in the html web output.

When the GPX file is in use, the animation works a little differently.  The numbers of the top 5 riders are always shown, and the numbers of the Highlight numbers are also shown.

The GPX format contains Latitude/Longitude coordinates, as well as elevations and times.  CrossMgr uses all of this information to make a more realistic animation of the race.

GPX files downloaded from [MapMyRide](http://www.mapmyride.com/) do not contain elevation data.  However, the elevation data can be downloaded separately on the same MapMyRide page to a file called "elevation.csv".  If you wish to use the "elevation.csv" data from [MapMyRide](http://www.mapmyride.com/), save the "elevation.csv" file in the same folder as the GPX file.  CrossMgr will detect it, and pick up the elevation information when it reads the GPX file.

If you select the __Set Category Distances to GPX Lap Length__ in the last screen of the wizard (the default), the Category distances will automatically be filled in with the GPX course length.

### Editing GPX Files

Say you have GPX file from a rider for his entire 8 lap race.  But, CrossMgr requires a GPX for a single lap.  What to do?

Fortunately, there are GPX file editors that allow you to edit a full (for example, [GPX Editor](http://sourceforge.net/projects/gpxeditor/).  If you want to use GPX Editor, download it unzip it into a folder.

GPX Editor has some features that make it easy to edit a multi-lap recording to a single lap.

Open the GPX file.  On the left side of the screen, expand "Tracks".
Then click on the Date entry, then on "Track Segment #1" underneath that.

This shows the track, and brings up an altitude graph at the bottom of the screen.

From the beginning of the altitude graph, hold the left mouse button down and drag to the right.
This selects a part of the path, also showing it in yellow on the screen.

Keep dragging until you select just enough points for the 1st lap.
The first point and lat point do not need to overlap perfectly - CrossMgr will automatically join them to make a circuit.
Depending on whether you have a run up, it might make sense to click-and-drag a middle section of the track.

Then, right-click on your selection in the altitude area.  Choose "Selection|Copy to a new track...".
This make a new track of the single lap called "Track Segment #2".

From the left side of the screen, right-click on "Track Segment #1", and Delete it ("Oui" is french for yes ;).

Then save the file.  Now you have a GPX file with one lap.

### But, I only have a .fit File from a Garmin!

No problem.  You just need to convert it to a GPX file with [GPSBabel](http://www.gpsbabel.org).

1. Download [GPSBabel](http://www.gpsbabel.org).
1. Plug in the Garmin GPS device.  Navigate to the device (it looks like a USB flash drive).  Go to the Activities folder.  There you should find the .fit files.
1. Launch GPSBabel, open the .fit file of the course, then write it out as a .gpx file.
1. Check the .gpx file you just made with [GPX Editor](http://sourceforge.net/projects/gpxeditor/).  See instructions above if it needs to be fixed in some way.

Now, you can import your new .gpx file into CrossMgr.

## Show on Google Map
Creates a course preview web page which includes a Google Map with the course drawn on it as well as an Aligraph (altitude map).
In addition, the page has two buttons:

Button|Action
:-----|:-----
Get Directions|Opens a Google Maps page with the Destination filled in to the Course.
Google Earth Ride|Opens a page showing a 3d course animation - requires the Google Earth plugin.  The animation looks like a helmet camera.

## Export in GPX Format
Write a GPX file of the course in the same format that CrossMgr reads.  Useful when you want to transfer one GPX course to another CrossMgr race or another application.

### Export in KML Format

Creates a KMZ file with an animated fly-over virtual tour of the course (KMZ is compressed KML).  KMZ file formats are compatible with Google Earth.  CrossMgr launches Google Earth after the download.

To see the virtual tour:

1. Ensure you have [Google Earth](http://www.google.com/earth/index.html) installed.
1. Make sure you have a race with an imported GPX course.
1. From CrossMgr, do "DataMgmt/Export Course.../as KMZ Virtual Tour..."
1. After Google Earth comes up, double-click on name of your Race - look for it in the left column.
1. Then, double-click on "`<Race Name>`: Virtual Tour" (the first entry).
1. Watch the virtual tour of your race in real-time.

## Web

Options for HTML output including Contact Email, Google Analytics Tracking ID and Header Graphic.

### Google Analytics Tracking ID

If you have a __Google Analytics Tracking ID__, enter it here to track access to the race results web page.

CrossMgr will insert all the proper Javascript on the html page with your __Google Analytics Tracking ID__.
You can then track access to the page from your Google Analytics account.

For more information about Google Analytics, including how to create an account and get your Tracking ID, see [here](http://www.google.com/analytics).

## FTP

Options for FTP upload including host, password, directory and real-time publish option.

## Camera

CrossMgr can record photos from an inexpensive USB camera as riders cross the finish line.
In addition to making nice pictures of the event for publishing later, this feature is useful in resolving disputes.

It can be used with RFID or manual entry to automatically take a photo of riders as they cross the finish line.

This requires a separate program:  __CrossMgrCamera__.  If you have not done so, download and install this program from the CrosMgr web site.

CrossMgrCamera runs for the entire race and takes photos about 25 times a second.  It holds those frames in a "ring buffer" that is 10 seconds long (a ring buffer just means that the most recent photo replaces the oldest). 

CrossMgr sends it a message with the rider information and a time.  CrossMgrCamera then saves the frame before and after the time after also adding the information as a header at the top of the photo.

Photos are stored in a folder called __<RaceFile>_Photos__ where <RaceFile> is the name of the CrossMgr race file.  Photo names have the form:

__bib-XXXX-time-HH-MM-SS-DDD-X.jpg__

Where bib is the rider's race number, HH-MM-SS-DDD is the race time to millisecond accuracy, and X is the frame - either 1 or 2.

This makes it easy to manage the photos in a regular file browser.  Sort alphabetically to see the files by rider bib number.  Sort by date to see the photos in full order.

The CrossMgrCamera application supports three photo display areas:

1. The top left area constantly shows what the camera is looking at along the top.
1. Two areas below show the frame before and the frame after the last photo taken.

CrossMgr sends messages to it to save photos.

When you run CrossMgrCamera, consider the __Camera Device__.
Normally, the external USB camera default is __device 0__, so you don't need to change this.

On some PCs, the built-in camera is __device 0__ and the external USB camera is __device 1__.
If this is the case on your computer, set __Camera Device__ to __1__.

CrossMgrCamera uses the computer intensively and will drain the battery quickly.  Make sure you have an external source of power.

### Options

Option|Description
:-------|:----------
Do Not Use Camera for Photo Finish|USB Camera not used
Photos on Every Lap|Records a photo from a connected USB camera on every number entry on every lap.  See [Notes](#use-usb-camera-photo-finish) below for details.
Photos at Race Finish Only|This option tells CrossMgr to record photos one minute before the leader's finish time for each Start Wave.  If the leader has not yet finished, CrossMgr uses leader's expected time.  If the leader's time is known, CrossMgr uses the leader's actual finish time.  If this option is disabled, CrossMgr will record photos of every rider on every lap.  If this race is a time trial, this option has no effect and photos will be recorded on every lap.

### Photo Delay

This sets a delay between when a photo is triggered (manual or RFID input) and when the camera is triggered.

This is important when you are using __passive RFID tags__.  The reader will read the tags before the rider crosses the finish.  If the camera takes a photo when the tag is first read, the frame will be blank as the rider is not there yet.  Configuring a photo delay allows time for the rider to get in the frame.

To set a reasonable delay, you need to estimate two pieces of data - the __RFID Read Distance before Finish Line__ and the __Finish Speed__.
To figure this out, you need a helper:

1. Start up CrossMgrImpinj (or CrossMgrAlien).  Make sure it is connected to the reader and working correctly.
1. Take a spare tag, and stand on the finish line.  CrossMgrImpinj will show that the tag is constantly being read.
1. Start walking the course in the opposite direction, away from the finish line.
1. Ask the helper to tell you the moment the tag stops reading.
1. At that point, make a mark on the course.
1. Measure the distance between the mark and the finish with a tape measure.  This is the __RFID Read Distance before Finish Line__.  Enter it into CrossMgr.
1. Estimate a reasonable __Est. Finish Speed__ depending on the type of race.  Ask the riders what their finish speed is.
1. CrossMgr uses this information to calculate the photo delay in milliseconds.

This can be approximate.  CrossMgr takes two photos, one before and one after, 40 milliseconds apart.  This allows for +/-40 milliseconds variation in the photo delay to get the rider in frame.

If riders are consistently before, or after the finish line in the frame, this is easy to fix.

For example, if the riders are 1 meter before the line, reduce __RFID Read Distance before Finish Line__ by one meter.
If the riders are 1 meter after the line, increase __RFID Read Distance before Finish Line__ by one meter.

### Camera Notes:

The purpose of __Photos at Race Finish Only__ is to avoid filling up your disk with uninteresting photos during the race.  This feature is especially useful for high-lap races like criteriums.  Aside from the space required, there is no problem with recording photos every lap, and you may wish to do for the additional information it provides.

When using the __Photos at Race Finish Only__ option, be aware that sometimes CrossMgr does not know who the leader is.  Especially during a criterium, this can happen if the leader takes a free lap and CrossMgr does not auto-correct it, or in any race type, the leader might have a missed read.

This is the reason for the policy of recording photos one minute before the expected leader - this makes it more likely that the leader will be included if misclassified during the race.

One the leader of a Start Wave has been recorded, photos for all riders in the Start Wave will be recorded.  The same reason applies: CrossMgr may not know what lap a particular rider is on with 100% accuracy if the rider has take free laps or had missed reads.  This means that lapped riders may have their photo recorded twice.

When using CrossMgr for track races, recording all photos 60 seconds in advance of the leader may result in photos of all riders for up to the last 4 laps (depending on the length of the track).

In TimeTrial mode, __Photos at Race Finish Only__ has the same effect as __Photos on Every Lap__.

### More Camera Notes

CrossMgr automatically looks for a USB webcam plugged into a USB port.  If it does not find one there, and you have a built-in webcam, it might find the built-in one (not what you want!).  Make sure the USB camera is plugged in and working before starting the race.

The USB camera feature can be turned on and off during the race at any time.  You can turn it on at the start, off in the middle, then on again to capture the last laps and the finish.

Photos are saved in a folder created in the same location as the race.  The Photo folder has the same name as the race with with "_Photos" added to the end.  The photo files have the following format: "bib-XXXX-time-HH-MM-SS-DD-N.jpg" where XXXX is the bib number, HH, MM, SS and DD are hours, minutes, seconds, and decimal seconds, respectively, and N is the photo number.
A header is written on each photo including the rider's Bib, Name, Team, the Event, the Race Time and the Current Date/Time.

Although the pictures taken are far smaller than recording the entire video on disk, they can still take a lot of space.  Make sure you have lots of disk space available to accommodate the potential 500 (or more) pictures that might be taken.

If you only want one photo of each rider for posting (CrossMgr takes two), you can delete all the second photos in the folder from a command line:

    del *2.jpg    &:: Windows cmd window
    rm *2.jpg     # Linux shell prompt

Get a good USB camera.  Some good ones are available for about $100.  Make sure the camera can focus on far-away objects (some webcams only work well for faces in front of a computer).  Use a tripod or other stable support.

For performance reasons, CrossMgr opens a connection to the USB webcam at the start of the race and closes it at the end.  Do Not Disconnect the USB Camera during the race!  This may cause CrossMgr to lock up.  Of course, you can always close CrossMgr and restart it if this happens.

Note that aiming the camera into the sun will "blind" it, and the riders will appear as dark blotches on a white background.  Some experimentation will be required, and don't be surprised if you have to change the camera position throughout the day to compensate for changing lighting conditions.  Periodically review what the camera is seeing in CrossMgrCamera.

## Animation Options
These only apply to the Track animation.  If you are using an uploaded GPX file, the animation will follow the GPX path.

Property|Description
:-------|:----------
Animation Finish on Top|Tells the animation to finish on the top rather than on the bottom.  Also changes HTML output to match.
Animation Reverse Direction|Runs the animation from right-to-left (clockwise) instead of the usual left-to-right (counter-clockwise).  Also changes HTML output to match.

## Files
Excel Sheet|Externally Linked Excel Sheet name.
Categories Imported From|File name of the categories import file.  Of course, the Category properties can be changed afterwards.
File Name|File name generated for this race.

## Team Results

Controls options for the TeamResults page.

### Team Rank Criteria
Team Results can be computed as follows:

1. by Nth Rider Time: time of the nth rider's finish of the team (eg. team time trial, time taken by 5rd team member)
1. by Sum Time: sum of the times of the top results for the team (eg. team results finish, sum time for top 3 team members)
1. by Sum Points: sum of the points of the top results for the team (eg. team results finish, sum points for top 3 team members)
1. by Sum Percent Time: like __by Sum Points__, but points are computed as a percentage of the winner's time.

### Nth Rider
Only used if __Rank Option__ is __by Nth Rider Time__ option.  Indicates which rider's finish time counts for the team.  Not used otherwise.

### # Top Results
Used if __Rank Option__ is __by Sum Time__, __by Sum Points__ or __by Sum Percent Time__.  Indicates the number of top team rider finishers to include in the ranking calculation.

### Finish Points
Only used if __Rank Option__ is __by Sum Points__.  Indicates the points-for-position for the ranking calculation.  A comma-separated list of numbers in order of 1st place, 2nd place, etc.
Points must be the same or decreasing for lower finish positions.

## Notes
Teams that have fewer riders than __Nth Rider__ or __# Top Results__ (depending on the option) will not be shown in Team Results.

For example, if a team Time Trial is taken on the 4th rider, and only 3 riders finish, then the team will not be shown.

For example, if a team is to be ranked by the sum of times for the tope 3 riders, and only 2 riders finish, then the team will not be shown.

Of course, riders with no team, or have team __Independent__ or __Ind.__ are not included in the Team Results.

# Further Details:
## Time Trial Mode
Time Trial mode is a special mode that works differently from the regular race mode.  In TT mode, the first read for a rider starts his/her clock, and subsequent reads are all taken with respect to the rider's start time.

TT start times can also be imported into CrossMgr from an Excel spreadsheet (see [DataMgmt][] for details).  This spreadsheet simply requires a header row with at least two columns: the Bib number, and the Start Time (always remember that Start Time is in __Race__ time, that is, the time after the stopwatches are synced, not clock time).  When start times are imported, each rider's time will start automatically at the imported Start time.

Otherwise, the first input for a rider is taken as his/her start time.

TT mode works with manual input and JChip.  TT results are computed relative to the rider's ride time.

TT penalties and/or adjustments can be made afterwards.  You can add a note to describe what you did.  See the "Note..." feature in [Chart Right-Click][].

## Question: When is a Rider in the Race?
CrossMgr considers a rider in the race if (a) there is a time entry for the rider or (b) the rider Status (DNS, DQ, etc.) is set.  It does not automatically add all riders described in the Excel sheet.

DNS riders can also be added all at once from the spreadsheet after the race.  See [DataMgmt][] and the __Add DNS from External Excel Data...__ section.

# Controls

## Commit
Commits your changes to CrossMgr.  Changing screens will commit your changes automatically.

## Link External Excel Sheet
Allows you to link to an [External Excel][] sheet right from this page.  See [DataMgmt][].

## Save Template
Saves your configuration as a template file.

To create a template that is automatically applied for every New race, save the template as "default".  The "default" template will be applied for New races, and races opened from RaceDB.

## Load Template
Loads an existing configuration into the current race.

This feature is related to File|New Next..., which create a new race based on the existing race.

However, a template can be loaded into a completely New race, and by saving a template as "default", it will be automatically applied to new and RaceDB races.

.
