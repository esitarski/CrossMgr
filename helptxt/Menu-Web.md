
[TOC]

# Web

## Introduction

Riders and spectators appreciate live results at the race - it creates a richer experience for the participants and creates a more professional impression for you.

CrossMgr makes it __extremely__ easy to publish real-time results at race on a local wireless network.
CrossMgr itself acts like a web server and serves up real-time content from its race data.

This feature is in great contrast to "the bad old days" of on-site real-time results where you would need to install and configure a web server, an ftp server, and configure the FTP publish from CrossMgr.

Of course, FTP publish is still available in CrossMgr (see ([DataMgmt][] for details) and is great for publishing to a public web site.

For on-site results - especially where there is no access to public internet, the built-in Web feature is far more practical. Especially for busy timers who have more important things to worry about (like getting accurate results).

### Step 1:
__Make sure the CrossMgr computer is connected to a Wifi Network.__

1. The Wifi does not have to be connected to the external internet.  It is better if it isn't as members of the public will be connecting to it to get the race results on site.
1. Make sure the Wifi is __not__ password protected.  Riders and spectators need to connect to it.
1. If you are not using a chip reader, you can just connect the CrossMgr computer to a local wireless network produce from a wireless router.
1. If you are using a chip reader with CrossMgr, use a cable plugged into a wireless router to connect the CrossMgr computer to the chip reader.

### Step 2:
__Publish and Share the Page with Race Attendees__

1. Routers support access through the computer's name.  For example, if your computer is named "results-local", you can access the CrossMgr page with  __http://results-local:8765__.  You may wish to rename you computer to something web-friendly that makes sense.
1. CrossMgr makes sharing the results page easy.  On the __Index Page__ (see below), click on the __Share__ link.
1. Print out, or otherwise share the QR Code with race attendees and participants.  Participants connect to your local Wifi network, then using their QR Code app, they can instantly connect to the live results.  Alternatively, they can type in the url listed on the page.
1. Once connected, participants can easily share their connected by clickong in the __Share__ link right on the page.  This shows the QR Code page which makes it easy for other participants to get access to the page.

That's it!

## Web-based Lap Counters for Mass Start Races

For Mass Start races, CrossMgr supports automatic Lap Counters for each start waves on course (see [LapCounter][] for details about automatic lap counter features).

A web-based Lap Counter is also available from the web Index page.  The lap counter page receives message from CrossMgr's currently running race and changes accordingly.
The same URL is used for all races, if you set up you lap counter displayes you  won't need to touch them again when new races start.  The LapCounter web page automatically changes laps exactly the same as the lap counter page in CrossMgr.

The idea is that you would use a tablet or a computer with an LCD screen as a lap counter.  This device would be connected over wifi to the CrossMgr computer.  The Lap Counter(s) would automatically be flipped during the race.

### Multiple Monitors

You can use multiple monitors, each showing one lap count of each start wave.

By default, the Lap Counter web page shows multiple lap counters on the same screen (max of 6) with a default layout.

To configure the display to show one, two or any combination of lap counters, and to control the layout, click anywhere on the Lap Counter web page.

When the Prompt appears, enter text indicating of the lap counters you want to show.
For example:

* "1", show the first lap counter only.
* "12" show lap counters one and two only.
* "34" show lap counters three and four only.
* "123456", show six lap counters all in a same row.

If you enter a "-" (minus sign), this starts a new row.

For example

* "3-4", two lap counters will be shown, one on each row.
* "1-2-3", three lap counters, each on its own row
* "1-234", four lap counters, the first on row 1, the others on row 2

To check how a display is currently configured, look at the web page URL.  The counters displayed are just before the .html in the LapCounter url.

If there is no start wave corresponding to a LapCounter display number (or the leader has not come around yet to register a lap), that LapCounter web page will show a black screen to conserve power.

## Current and Previous Race Results Web Pages

Although the Index page makes it convenient to show results from races, if you want to show live results on a screen at the event, it is more convenient to have one web page that follows the current race so you don't have to change it during the event.

There are two additional URLs that are recognized by CrossMgr:

* CurrentResults.html
* PreviousResults.html

Current and Previous race results are displayed on the web page.

To get to these pages, open the Index page, then type "CurrentResults.html" or "PreviousResults.html" to the end of the browser's URL.

CurrentResults.html follows the running race in CrossMgr.
PreviousResults.html is updated when a next race starts.

These pages attempt to reconnect to CrossMgr if they lose their connection.  You can also press the browser Refresh button.

Test this out yourself.  Start a Mass Start Race Simulation, open the Index page, and type "CurrentResults.html" in the browser's URL.
Switch the CurrentResults to Kiosk mode by selecting "Kiosk" in the dropdown next to the "Results".
To quick Kiosk mode, remove the options after the "?" in the URL.

## Time Trials and the TT Countdown page.

For Time Trials, a live countdown page is available from the Index page.
This allows the starting official, wip, coaches, spectators and anyone else countdown the riders to the start.
The page beeps at 10 seconds, then a beep at 5, 4, 3, 2, 1 and 0 before each rider.

### Tutorial 1
You can try this out for yourself.  For this experiment, you will need a CrossMgr computer and a tablet on the same wireless network.
Make sure you install a __QR Code__ app onto the tablet.

1. Start CrossMgr
1. Do __Tools|Simulate Race...__.  Pick the Time Trial Option.
1. After the TT starts, do __Web|Index Page...__ to show the index page.  This is live connected to the CrossMgr program.
1. From the Index page, click on the __Share__ link at the top.  This brings up a __QR Code__ for the page.
1. With a tablet on the same wireless network of the CrossMgr computer, launch the tablet's QR Code app and point it at the CrossMgr computer screen.  Follow the link on the tablet read from the QR cCode.
1. The tablet will now show the Index page.  Notice that the tablet also has access to the __Share__ link.  This allows other people to share the link to the race results.
1. If this does not work, you may have to open port 8765 on your computer.  Check the instructions for how to do for your operating system.
1. On the tablet, click on the __Simulation__ race.  The tablet now shows the live results of the race.  Clicking on the logo at the top of the screen will refresh the page.  The page will also refresh automatically after each leader's lap.
1. All races in the same folder will be shown in the Index page - not just the race that is running.  If you have used CrossMgr previously and have a number of races with published html in the same folder, try opening one of the races and refreshing the Index page.
1. Click on the "TT Countdown" link to see the countdown.

What if the tablet and the computer's time don't match?

On opening (or refresh), the "TT Countdown" page synchronizes the tablet's time with the CrossMgr computer.  This can take a second or two.  On a LAN, the countdown tablet is capable of synchronizing itself to within a few milliseconds of the CrossMgr computer.  If you are interested in the details, look at the bottom of the TT Countdown web page for &delta; (delta) and &lambda; (lambda).  Delta is the time correction added to the tablet's time to correct it to the computer's time.  The starts will then be with respect to the CrossMgr Computer's time.

Lambda is the estimated one-way network latency between the CrossMgr and the tablet.  Look for a small lambda as this is an upper bound on the error of the correction estimate.  That does not mean that a longer network latency means a less accurate correction, however, a small latency (a few milliseconds) guarantees that the correction is also within a few milliseconds.

If you really want to have some fun, start a tablet and compare it with a browser countdown page launched on the same computer.  See if you can hear the difference between the beeps.

If at any time you believe that the "TT Countdown" page is out-of-sync with the computer, press the refresh button in the browser.  This will cause a re-sync.

Try clicking on the live results frpom the Index page.

Races in progress are highlighted on the Index page.

### Notes:
__Remember:__ live results are a direct connection between your CrossMgr race and the web.  All changes you make will be immediately visible.  Use caution.

__Multiple versions of CrossMgr open at the same time:__  The first instance open will act as the web server.  If the first on is closed, another will take over after a few seconds.

## Index Page
Opens a browser showing the CrossMgr web index page.

The current race is connected to real-time CrossMgr data.
Other races in the same folder will also be shown.

## QR Code Share Page
Opens a browser and loads the CrossMgr web QR Code Share page.

Publish this to allow people to connect to real-time results.
Print this out and post it at the race.  This will allow people to easily access the real-time results.

## Controlling Results Web Page

### Changing the Results Web Page Format

On the Results web page there is a dropdown at the top which normally shows "Results".
This dropdown supports other display modes:

Mode|Description
:---|:----------
Results|Default.  Shows the results of the competition with animation.
Kiosk|Enables Kiosk Mode.  This cycles through each category showing one at a time.
Kiosk A|Enable Kiosk Arrival Mode.  Similar to Kiosk Mode, however, the riders are shown in reverse rank.  This allows finishing riders to see their finish time without being scrolled off the bottom of the screen.

### Results Web Page Parameters

The CrossMgr web page supports configuration through parameters instead of changing them on the screen.  These are passed to the web page in the usual manner: 

    [page_url]?param1=value&param1=value.

Parameter|Value|Description
:--------|:----|:----------
kioskMode|t or f|Enables Kiosk Mode.  Designed for a live results screen, in Kiosk Mode, one category is shown at a time, and all categories are cycled through.
arrivalMode|t or f|Enables Arrival Mode and only works if Kiosk Mode is set.  Designed for Gran Fondos, this options shows rider in reverse order (i.e. last rider first).  This makes it easy for finishing riders to see their time.  If riders are shown first-to-last, arriving riders are scrolled off the screen and cannot see their time easily.
lang|en or fr or es|Set default language.  Supports English, French and Spanish.  This just sets the default Language.  The display language can still be changed on the page.
highlight|list of comma separated bib numbers|Numbers to highlight in the results (for example, "highlight=31,21,15")
raceCat|race category|A race category to show by default instead of all categories.

Example:

    [page_url]?kioskMode=t&arrivalMode=t&lang=fr

Enable Kiosk Mode, enable Arrival Mode and set default language to French.
