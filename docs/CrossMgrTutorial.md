# CrossMgr 3 Tutorial
## An introduction to CrossMgr

January 2020
Edward Sitarski
edward.sitarski@gmail.com

### Table of Contents

- [Introduction](#introduction)
- [Check the Help](#check-for-help)
- [Installation](#installation)
- [Running the Simulation](#running-the-simulation)
- [Fixing a Race Without Auto-Correct](#fixing-a-race-without-auto-correct)
- [If you have done Manual Scoring Before](#if-you-have-done-manual-scoring-before)
- [Running a Real Race](#running-a-real-race)
- [Preparation](#preparation)
- [Creating a New Race](#creating-a-new-race)
- [Starting the Race](#starting-the-race)
- [Recording Numbers](#recording-numbers)
- [During the Race](#during-the-race)
- [After the Race](#after-the-race)
- [Handling Did Not Start DNS Riders](#handling-did-not-start-dns-riders)
- [What if Things get Really Messed Up?](#what-if-things-get-really-messed-up?)
- [Categories](#categories)
- [Number Ranges and Input Shorthand](#[number-ranges-and-input-shorthand)
- [Category Import/Export](#category-import/export)
- [Link to External Excel Data](#link-to-external-excel-data)
- [Format of the Excel File](#format-of-the-excel-file)
- [Headers](#headers)
- [Sheets](#sheets)
- [Advanced Topics](#advanced-topics)
- [Multiple categories with multiple lap counters](#multiple-categories-with-multiple-lap-counters)
- [Fixing Bad Data](#fixing-bad-data)
- [Managing Rider Numbers](#managing-rider-numbers)
- [Quick Shortcuts](#quick-shortcuts)
- [Quick Reference and Frequently Asked Questions](#quick-reference-and-frequently-asked-questions)

# Introduction

Thank you for using CrossMgr!

CrossMgr was designed to do all the crunching necessary to produce Cyclo-cross, MTB, Road , Criterium and time-trial race results quickly and accurately.  Rather than a "back box", CrossMgr has full visibility into all the data behind the results and allows easy manual adjustments before, during and after the race.  This is important for understanding outcomes and mitigating protests as well as fixing any issues.

CrossMgr integrates with 5 different RFID timing systems (Impinj (and other LLRP compatible), Alien, J-Chip, RaceResult and Ultra).

CrossMgr requires that you have some idea of what is involved in scoring a race.  If you are familiar with manual scoring, you will feel right at home with CrossMgr (of course, CrossMgr does all the hard work for you).  If you have never scored a race before, you will wonder how anyone does it manually at all.

CrossMgr requires little preparation ahead of time.  Just hit File|New… and get going.  You can break out results and/or add categories by number ranges later.  You can link with additional rider information in an external Excel spreadsheet.

CrossMgr has sophisticated data cleansing.  It can &quot;guess&quot; missed numbers based on a rider&#39;s other lap times.  It also detects duplicate entries.  It is surprisingly good at making sense of bad input.  CrossMgr has produced correct results when 50% of the riders were missed on the first lap.  It also has great graphics to see the entire race and fix problems manually (for example, the Chart view).

CrossMgr shows expected numbers before they arrive – and what lap they are on.  You only need to click on the expected rider when they come by - without re-keying them again.  CrossMgr also highlights the race and category leaders in advance to help manage the lap counter and last lap.

Features include:

- No data entry or preparation required.  Just &quot;New&quot; a race and go.
- Handles missing and duplicate numbers – even on the first few laps.  Fills in missing numbers when reasonable to do so.
- Shows the expected leader and the leaders for each category in advance.  Shows ETA (Estimated Time of Arrival) for all riders
- Show data history by rider (both in a table and graphically).
- Estimates the number of laps in a timed race.  Allows manual override.
- Results available instantly at all times.
- Allows manual changes to input and rider information.
- Handles simultaneous multiple categories.
- Create results in Excel showing lap times by rider.
- Enter numbers through keypad or touch screen.
- Link to external Excel data for more detailed results
- Data is auto-saved – no lost data.
- Automatically handles the UCI 80% time limit rule.
- Integration with the Impinj and Alien chip readers as well as JChip, RaceResult and Ultra chip reading system

### Warning!

This program comes with no guarantee or warrenty whatsoever expressed or implied! Your use of the software constitutes your agreement to accept full responsible for problems or issues that arrive as the use of the software.

Please always have a manual paper backup, especially if you have not used CrossMgr extensively.  Computers get dropped, batteries fail, screens get rained on and keyboards lock up.  A manual method ensures that you do not lose data.  If you have the data, you can always make sense of it later.

I do my best, but please do not come back to me and say that the program wrecked your event!

Be responsible!

### Getting help

If you thing there is a bug or a problem with the application, and you have a complete steps to reproduce, please submit an issue on our [GitHub issue tracker](https://github.com/esitarski/CrossMgr/issues).

Please check the issue tracker before sending us email. The issue may have already been reported.

Simularly, feature requests should be submitted as an issue and tagged as a feature request.

However, if you have a question regarding the use of the software, and your have read through all the documentation and cannot figure out the answer, please do reach out. We not only wrote the software, we also use it. We may be able to assist. Our support email is [edward.sitarski@gmail.com](mailto:edward.sitarski@gmail.com).


### Check the Help

All CrossMgr features are documented in Help.  The Help section also includes extensive tips and explanations about how to use certain features.  It is the

# Installation

CrossMgr runs on 64 bit versions of Windows 10, MacOSX and Linux. Only Windows 10 and 32 bit operating systems are supported. The minimum recommend amount of RAM is 4G.

On Windows, CrossMgr installs like any Windows program – just run the CrossMgr_Setup installer and follow the instructions.  If you are installing on Windows you will need administration privileges.

If you already have a version of CrossMgr installed, there is no need to uninstall it.  Just install the new one and everything will be taken care of.

### Windows Installation

From the Releases tab, download the CrossMgr-Setup_x64_VERSION.exe file. Run the file and follow the on screen instructions. By default, the program will be installed in C:\Program Files\CrossMgr. You can find Crossmgr from the start menu in the CrossMgr program group.

When running the installer, Windows will complain that it is a unknown publisher. Click the MORE INFORMATION link in that dialog, and then click the RUN ANYWAYS button. The install will proceed. Do not contact us complaining that the software has a virus as it does not. We do not get paid enough to produce the software that will remove this warning. If this bothers you, please go use someone elses software.

CrossMgrImpinj, TagReadWriter, CrossMgrAlien, CrossMgrVideo, and SeriesMgr follow the same install process. They will all install into the CrossMgr program group.

### Mac OSX Installation

From the Releases tab, download the CrossMgr-VERSION.dmg file. From the finder, double click the DMG file to open it. Once the window comes up, you simply drag and drop the CrossMgr.app folder to your Applications directory. From the Applications folder, you can now run CrossMgr like any other Mac app. Most recent Mac OSX versions will require you to press CTRL before clicking on the app for the first time, and then clicking open. The app is a non-signed program that MacOSX will not open otherwise. This is only require the first time you run it. MacOSX will also ask a few questions when the program is run, and you must confirm with YES (Allow Networking, Access to Documents Directory, etc, etc.)

CrossMgrImpinj, TagReadWriter, CrossMgrAlien, CrossMgrVideo, and SeriesMgr follow the same install process.

#### Debugging the Mac Apps

Because MacOSX has added a lot of security to the system, some weird problems can occur that prevent the application from starting. First, and foremost, because the apps are not signed, you must CTRL-CLICK the icon, and select Open from the pop up menu, and then click Open on the dialog box to start the application the first time. Additionally, MacOSX will prompt the user for permissions to access the network, documents folder, etc.. Sometimes, the splash screens for the application will cover this dialog box up, or it could end up behind the application. Unless you select ALLOW, the application can't work. For example, CrossMgr requires network access to run. Additionally, sometimes the application just won't start. Typically, it's icon will start to flash, and then nothing. To see why and what is happening, run the application from the command line from the app's MacOS directory. For example, for CrossMgr:

```bash
cd /Applications/CrossMgr.app/Content/MacOS
./CrossMgr
```

Python is setup to dump logs to stdout which usually indicates the problem. Sometimes, the problem of starting the application will just go away.

### Linux Installation

Download the CrossMgr-VERSION.AppImage file. Store this file in a convenient location such as $HOME/bin. Make the executable with

```bash
chmod 755 CrossMgr-VERSION.AppImage
```

Next, just run the AppImage with:

```bash
./CrossMgr-VERSION.AppImage
```

...from the command prompt.

CrossMgrImpinj, TagReadWriter, CrossMgrAlien, CrossMgrVideo, and SeriesMgr follow the same install process.

Alternative, setup a desktop icon to call it directly.


# Running the Simulation

The first thing you need do to get familiar with CrossMgr is to run the simulation.  Do this now by selecting &quot;Tools|Run Simulation....&quot; from the menu.

The simulation generates some data for a realistic cyclo-cross race, but with much shorter laps.  The whole simulation takes about 10 minutes, but it is well worth watching it to get familiar with the program.

After starting the simulation, you will notice a clock running on the title bar.  This is the race time, and shows you that a race is in progress.  Select the &quot;Record&quot; tab, or press F2 (the numbers on the tabs correspond to the Function keys).  This is the main tab for entering rider numbers as they pass by.  In the simulation, you do not need to enter numbers as they are generated automatically.  In a live race, you will be in this screen most of the time.

You can get help on any screen in CrossMgr by pressing SHIFT-F1.  Try it now.  Notice on the Help page that there is a quick navigation on the left.  Try it now by clicking on &quot;Race Information&quot;.  Click on the &quot;Back&quot; button in your browser to go back to the top of the help screen.
Now, switch to the Results screen in CrossMgr.  Press SHIFT-F1 again – see how you get help on this screen?  Now, Switch back to the Record screen n CrossMgr.

Numbers are recorded and time-stamped when you press the Enter key or button.  The best method is to input the number as you hear it called by the number caller, and then press Enter just as the rider passes the line.  Getting pretty close is good too.   **The important thing is to get the right sequence of numbers as close as possible to the actual times**.

Notice that on the left are some blank areas: **Recorded** and **Expected**.  The **Recorded** section shows the last numbers you entered.  The **Expected** section shows the riders that CrossMgr expects to come.  Wait a minute or two, and you will see numbers appear in this section.

In the **Expected** section, the race leader number is shown in green.  Category leaders are shown in the &quot;Note&quot; column as &quot;Lead&quot; and are also colored green.  Riders that CrossMgr expects but are not yet recorded are shown in orange.  For example, riders that are delayed due to a mechanical or a crash will show up here.  After a while, they will go away automatically.  Riders that are more than 80% of the first lap&#39;s time for their category are indicated with &quot;80%&quot; in red.  You will see some of these in the simulation later.

The simulation will start generating numbers corresponding to riders you would be recording as they cross the line.  These will show up in the Recorded section.  After a lap or two, the Expected section will show the riders and times expected in the future.

Now, click on the Race Animation tab (F7).

This screen shows the riders projected on the course based on their lap times.  In data capture mode, this screen shows how riders are moving around an ideal course.  After the race is over, you can also use this screen to replay an entire race in much shorter time.

Now, click the Passings tab (F4).

Passings is organized like a Cross/MTB scoring sheet (but with &quot;super powers&quot;).  You will see the riders listed on this sheet by lap (CrossMgr automatically figures out the leader) with the lap time, laps to go and race time at the top of each lap.

Notice the &quot;Show Times&quot; button at the top.  This toggles showing the times in the display.  Click this to show all the rider times (click it again to turn them off).

Wait for enough data so that there are a few columns in the Passings table.  Now click on a number in the table.  You will see it highlighted everywhere it appears.  This is a handy feature for checking a rider&#39;s progress lap by lap.

Alternatively, type a number into the Search field on the Passings page and press Enter.  The number will also be highlighted.

Let&#39;s check out live results.  First, make sure you computer is connected to a wifi network.  Now, select &quot;Web|IndexPage…&quot;.  This will open an index page of the race in your browser.  In this case it only shows one race – normally it will show all races in the same folder.

From the web browser, click on the &quot;Junior Men&quot; category.  This brings up the live web page of the race currently underway.  This page will &quot;phone home&quot; to CrossMgr to get updated race information (in tech speak, CrossMgr is also a live web server).  The riders are shown in the course where they are projected to be based on their lap tines (this makes more sense if you upload a GPX file of the course).

Now, click on the &quot;Back&quot; button to return to the index page.

At a race, you want to share the live race results easily on tablets and smartphones.  To do this easily, click on the &quot;Share&quot; button at the top of the index page.  This opens a page with a QR-Code.  Now, if you have a tablet on the same wifi network, point the tablet&#39;s camera at the screen and use the QR-Code app.  The tablet will be sent to the index page.

This makes it as easy as possible to get live results at your event.  Get a wireless wifi router and plug your computer into it, not in the WAN plug (leave this open if have a connection to the internet - required).  Allow race spectators to connect to your local wifi network.  Done.

After watching the simulation for a while, you will notice that some numbers are yellow.  Columns showing future laps are also yellow.  Yellow numbers are CrossMgr&#39;s guesses.  Yellow numbers in the past show where CrossMgr &quot;guessed&quot; that the rider passed at that time.  The simulated data has missing numbers, just like the real world.  CrossMgr guesses numbers if the missing entry is reasonably close to a multiple of the rider&#39;s average lap time.  Yellow numbers in the future are CrossMgr&#39;s guesses for when that rider is expected to cross the finish line.

You can see how this works by watching the Expected numbers and Passings.  Notice how the future yellow numbers in Passings are listed in Expected.  When a number comes in, Passings no longer shows it in yellow, Expected no longer shows it at all, and Recorded show it as an entry.  This makes a lot more sense when you watch it in the demo.

Watch for orange numbers in the Expected window.  These are numbers that are were expected but are significantly behind the race time.  After a while, they are no longer displayed.

Think of the Recorded and Expected windows as a scrolling list showing the input.  Numbers come in at the bottom (Expected), and then scroll up as they are entered (Recorded).

After some numbers have built up, click the Results tab.  This shows the race results at that time - what the placing would be if the race were to stop on the next lap.  Note the &quot;Show Times&quot;, &quot;Show Laps Completed&quot; and &quot;Show Positions buttons&quot;.  Click them all on and off a few times to see what additional information is displayed.  Also click on the Category drop-down to see what it does.  Return the Category to All.

Now, double-click on number 214 in the Results tab.  This automatically opens the Passings page with 214 highlighted.  Does it look like 214 was lapped on lap 3?  Notice how 214 was near the end of the group on Lap 2, was missing entirely from Lap 3, then shows up near the beginning of Lap 4.  This is the &quot;classic&quot; sign that 214 was dropping back in Lap 2, was passed by the leader in Lap 3, then reappears in Lap 4.  CrossMgr is smart enough to know when a rider is reasonably lapped and not simply &quot;missed&quot;.

Now click on the &quot;Chart&quot; page (F8).  Here you will see a Gantt chart for the entire race.  Click on one of the &quot;bars&quot;.  See how you get details about that lap?  Double-click on one of the numbers in the Gantt chart.  This will automatically take you to the Rider Detail for that rider.

.  You will also see a vertical line showing the current race time.  Watch how when the &quot;now&quot; line approaches the start of a rider&#39;s next lap, that rider also shows up in the &quot;Expected&quot; window.

This is a great screen to check if something &quot;fishy&quot; is going on in your race.  Give this a quick scan and look for excessively long or short bars.  Long bar – did the rider have a mechanical?  Short bar – did the rider cut the course (maybe short-circuit through the pit)?

Click on the Categories tab (F7).  Here you can see the 80% time rule as well as the suggested number of laps for each category.  There is more on setting up the Categories later in the document.

Right-click on a number in the Exected list.  Notice that you can Pull or DNF directly from here without having to type in the number in again.  Select the &quot;RiderDetail&quot; option.  This brings you to the details about this rider directly.  Hit (F2) to return to the Record tab.

Wait a while longer for the simulation to finish.  Make sure you look at all the screens.  When it does, click the Passings page (F4).  Notice that there were two numbers missed in lap 1: 197 and 215.  However, CrossMgr projected times for them based on their other lap times even though it did not know about these riders until lap 2.

Now, click on the Results page (F2).

All the results for the race are shown.  To show results for the Senior category, change the Category to Senior.

Look at the leader, 211.  Double click on the number.  This brings you to Passings.  Notice how the leader of this category was lapped on lap 6 of the race.  Clearly, all Seniors must have been lapped at least once.

Return to Results and take a look at 205, shown as 1 lap down among the Senior riders.  Let&#39;s do a quick check to see if this is correct.  Double click on 205 – this brings up the Passings page.   Here we see 205 hanging on at the end of laps 1 and 2, getting lapped on lap 3, falling back again for 4, 5 and 6, then getting lapped again in lap 7.  This is another example of a rider falling off and being lapped.

In the Passings page, double-click on 205.  This brings you to Rider Detail.  Note that 205&#39;s lap 2 is highlighted in yellow. Also, there is a yellow circle on the graph at lap 2.  This means that CrossMgr thought the rider was missed and that it was reasonable to assign a lap time for lap 2.

Almost always, CrossMgr can correctly guess when a rider misses a lap, but sometimes it gets it wrong.  You can always fix extra/missing laps with the Lap Adjust setting in Rider Detail.

Go back to Results.  Double-click on 209 – CrossMgr says is down a lap.  Correct or not?

Now, return to Results and switch the Category to Junior.  Try the Show Times, Show Laps Completed and Show Positions buttons.  They show additional information to the results.

Turn off all the extra information in the Results page.  Double click on 188.  Did he get lapped?  Passings page shows he got lapped in lap 7.  Double-click on 188 in the Passings page.  In the Rider Detail page, see the note &quot;Lapped by Race Leader in 7&quot;. Just as we thought from looking at the Passings page.

Go back to Results and double-click on 191.  Did he get lapped?  What lap?  What does Rider Detail say?

Look at the Recommendations page.  This contains a list of issues to look at in the rider data.  We see numbers 189, 190, 204 and 206 with a &quot;Check for DNF&quot; message.  Double-click on 206.  In the Rider Detail page, we see that this rider has a projected finish time in the last lap (i.e. no recorded time).  Now, this could be a &quot;miss&quot;, or this could be because 189 did not do the last lap and should be DNF.  Further investigation is necessary.

Say we discover that 206 did not want to do the last lap and dropped out.  In Rider Detail, set the Status to DNF.  Now return to the Recommendations page.  See how 206 no longer has a Recommendation.

Now, double-click on 189 in the Recommendations page.  In Rider Detail, we see a projected time for the last lap.  Say we discover that 189 actually did finish the last lap, but as a &quot;straggler&quot; - we somehow missed him when he went by.  We do nothing.  Luckily, 189 is in last place in his category, so we leave his projected time for the last lap as his finish time.  Look at his performance in Passings.  Missing stragglers in the last lap is bad, of course, but CrossMgr helped us reasonably conclude that 189 should be in last place.

**Remember:** check the Recommendations page after a race and investigate all issues.

Now, click on Publish|Print Results Preview.  You can link to an external Excel sheet containing information about the rider (names, teams, license, etc.).  More on this in a later section.

Of course, you need to share results in many file formats including Html, PDF and Excel.  You also need results formatted for upload (USA Cycling or UCI), or publish on CrossResults or RoadResults.

CrossMgr makes it easy to manage these formats with Publish|Batch Publish Files… (click on it now).  From this screen, select which file formats you wish to generate.  To publish all file formats simultaneously, press the &quot;Publish Now&quot; button.

To test what a format looks like, press the &quot;Test&quot; button. Try pressing &quot;Test&quot; for the Excel format, which opens Excel on the generated output.

If you also want to automatically upload the files with FTP, select the FTP option next to the format.  Press the &quot;Configure FTP&quot; button to specify the server, username and password as required.  This screen also gives you the option of setting the URL where the files can be accessed from a hosted web server.

## Fixing a Race Without Auto-Correct

CrossMgr&#39;s auto-correct is based on statistical analysis, and this is based on trends in the data.

Sometimes a rider&#39;s data has no trends and auto-correct does not do what you want.  In this case, it is good to know how to fix up results manually.

For a good simulation of what you sometimes need to fix, with the demo race still up, do &quot;Edit|Change Auto-Correct…&quot;.  In the dialog, select &quot;All&quot;, and press &quot;Clear Auto-Correct Flag&quot;.  This turns off auto-correct for all riders (see RiderDetail for details).

In a race situation, it may make sense to turn off auto-correct for a category, not all categories, but this is a tutorial, so we will turn it off for all riders.

Switch to the &quot;Chart&quot; view (F6) and select &quot;All&quot; categories.  This is the most useful view for fixing problems (notice how the &quot;stars&quot; are gone – these represented CrossMgr&#39;s automatic corrections).

There are two types of errors that need to be corrected:

1. Missing numbers (missed from the number caller or chip reads)
2. Repeated numbers (called twice from the number caller – usually never happens with chip reads).

Missing numbers look like &quot;long bars&quot; in the Chart.  Duplicate numbers show up as &quot;missing colors&quot; in the sequence.

 Look at the Chart.  Notice how 185 has an extra long second bar?  This is what a missing read looks like.  Right-click on 185&#39;s second bar and select &quot;Add Missing Split|1 Split&quot;.  This adds a missing split in the lap.

 Look for your own &quot;long laps&quot;.  Did you see 191&#39;s last lap and 212&#39;s second-last lap?  Add the missing spit.  Fix the rest.

 Now we have to deal with &quot;duplicate&quot; laps.  These don&#39;t happen as often, but they do happen, and you need to be ready.  Duplicate laps show up as missing colors in the bars.

 For example, look at 206, especially Purple, Green, Blue.  Relative to the other riders, 206 is missing Red.  The lap actually is there, but it is a duplicate time, so the lap is actually so short we can&#39;t see it.

 To fix this, we need to remove the duplicate number.  On the last bar before the missing color (the Green bar) on 206, right click, and select &quot;Delete Lap End Time…&quot;.  This will delete the duplicate entry.

 Look at 193.  See the same problem?  Where is the Purple bar?  On the Gold bar, right-click, and do a &quot;Delete Lap End Time…&quot;.

 Now, everything looks fine.  Duplicate numbers don&#39;t show up often, but it is good to know how to deal with them when they do.

 Always, if you do something wrong, use CTRL-z to undo.

# If you have done Manual Scoring Before

If you have experience with manual scoring, you will really appreciate CrossMgr.  By doing the accounting work for you, CrossMgr allows you to concentrate on the sporting aspects of the race.  However, there are some important differences that you should be aware of.

CrossMgr does not require you to do anything for a missed number.  Just don&#39;t enter anything – there is no need to enter a &quot;miss&quot; or leave an empty spot for the number.  CrossMgr will calculate a reasonable time for missed rider based on the rider&#39;s other times.

CrossMgr also does not require you to correct errors.  If you enter the wrong number, don&#39;t worry about it - CrossMgr will figure out if it was a miss.  If you have time, however, you can edit numbers in the Passings page or in the Recorded numbers list.  This will reduce the need to estimate times.  If you enter a number my mistake that does not correspond to a rider in the race, you can delete it from the RiderDetail screen later (click on the Edit… button).

CrossMgr automatically keeps track of the race leader, and the leader by category.  The race leader will be at the top of the lap columns in the Passings page.  The category leader will always be marked in the Expected list before he/she comes.

CrossMgr estimates the number of laps in the race automatically.  Of course, you can always override its suggestions by changing &quot;Automatic&quot; to &quot;Manual&quot; on the Record page..

If the start area is before the finish line so that the first lap would be longer, wait for the beginning of the second lap before recording numbers.  This means that 1st lap will be longer, and that is OK.  CrossMgr handles this fine.

# Running a Real Race

## Preparation

Do not use CrossMgr for the first time in a real race!  Try it out and practice a few times.  Get comfortable with typing numbers under stress and timing pressure.  Learn to relax and not to worry if you miss a few.  Get familiar with the other features of the program and how to navigate to check laps down etc.

Make sure that you have another person doing a paper-based manual backup!

Consider bringing the following items to your race:

1. Chair
2. Table (resting a laptop on your lap can also work, but it helps to have something to put it on to keep the cooling fan clear)
3. Computer stuff:
  - Extra battery.
  - External battery charger.
  - Keyboard and Numeric keypad.  Many touchscreens do not work in cold weather.  Use cables – the batteries in wireless peripherals tend to fail in cold weather.
  - Battery-operated printer to print results.
  - Wireless internet connection card (cell phone network) to upload results to your web site.
  - Big cardboard box to reduce screen glare from the sun (put box on table with the open end facing you and place the computer in box).
4. Notepad and pen for making additional notes.
5. Sunscreen/bug repellent
6. Bell (for ringing at last lap)
7. A good number caller.

## Creating a New Race

Create a new race with &quot;File|New…&quot;.  Fill in the details on the form.  Pay special attention to the race minutes as this effects the automatic race lap computation.  Make sure you select the folder to save the race in.  CrossMgr automatically creates a name for the race file based on the date, name and number.  The Race Number is the sequence number of the race on that day.

You can enter a Categories file to import for the race.  If you don&#39;t have a Categories file, that&#39;s OK.  After creating a new race, go to the Categories page and fill in as much information as you can.  See the Categories section below for more details about how to work with Categories.

&quot;File|New Next…&quot; creates a new race from the existing race.  This saves some time by changing the start time and incrementing the race number automatically.

## Starting the Race

When you are ready to start the race, go to the Actions page and press Start Race.  This will bring you to the Record tab to start recording numbers.  You will likely stay in the Record tab for most of the race, also using the Expected and Missing number lists to record riders after the 1st lap.

Pressing &quot;Start Race at Time&quot; allows you to start a race at a future time.  This is useful if you need to start the race away from the computer.  The computer will start the race automatically at the given time.

Sometimes the course will have a &quot;run-up&quot; on the first lap that makes it longer than the other laps.  For example, the starting area might be 500 meters in front of the finish line on a level road.  In this case, DO NOT record riders as they first go by the finish line (it will be almost impossible to do so anyway).  Wait until they come around again, then start recording numbers.

This means that the 1st lap will be longer than all the other laps.  That is OK.  CrossMgr handles this situation.  All will be well.

## Recording Numbers

After starting the race, you will see the Record page.

You initially type in numbers and pressing the Enter key.  This also timestamps the entry.

You can also DNF and Pull riders by clicking the appropriate buttons.  Pulled riders appear in the results as laps down, but are still ranked in the results.

Most CrossMgr users start by typing in every number.  As you gain more experience, however, you will find that you can click on the numbers in the Expected table in the lower left of the screen.  This is especially convenient when the race is established after the first few laps.

Remember, by looking the Lap column in the Expected table, you can easily see which riders are a lap down.  The Race leader&#39;s number is shown in green.

The Record page also computes the Total Laps in the race based on the leaders lap time and race time.  CrossMgr takes two laps to get enough data to make a good prediction.  If you don&#39;t like the number of laps it comes up with, override it by changing the Race Laps in the Categories screen.

**Critically Important:**   **Do not click on numbers if you don&#39;t see them.  Specifically, don&#39;t click on &quot;miss&quot; numbers just to get them out of the way.**  This won&#39;t work, and you can really mess things up.  If you can&#39;t see a number and you do not get a clarification within the next 10 seconds or so, consider it a &quot;miss&quot; and move on.  The &quot;miss&quot; numbers will disappear from the Expected list.

CrossMgr will estimate a time based on the rider&#39;s other lap times, so don&#39;t worry about it.  If there are any problems with CrossMgr&#39;s estimates, it is a whole lot easier to fix those problems later (they are highlighted in yellow) than to remember what late times were entered and what you need to fix up yourself.

If you miss some numbers, and you still really want to enter them, consider using the &quot;Split…&quot; function described below.  It allows you to enter an entry just before/after an existing number with a correct time.

To correct data entry errors, right-click on the error in the Passings tab.  You can also right-click in the Recorded table on the left side.  You have three editing choices:

**Correct…:** change the number because you mistyped it

**Shift…:** move the time of an entry forward or backward.

**Insert…:** insert a number just before or just after the existing entry.

**Delete…:** delete the entry

Be careful with your edits!  Don&#39;t get carried away.  It is often best not to edit anything during a race.  CrossMgr is very good at making sense of errors and gets better with more data.

On the Record page, you can also press the DNF or Pull buttons instead of pressing enter to register those riders as DNF or Pulled.  Pulled riders show up as OTL (Outside Time Limit) on the results and are ranked by laps completed, then time.  DNF riders are listed in the results as DNF.  Pulled riders are automatically time-stamped with the time they are pulled.

It is also possible to enter riders who Do Not Start (DNS).  Select the &quot;Rider Detail&quot; page.  Type the number you wish to DNS at the top and press Enter.  This finds the number in the race if it is there.  Then, set the Rider Status to DNS.

You can use the same process for disqualified riders.  Disqualified riders show up in the results as NP (Not Placed).

You can check on riders by number.  Go to Rider Detail, type in the number and press Enter.  The rider&#39;s information will be retrieved.  The number will also be selected in Passings and Results.

When the race is over, go to the Actions tab and press Finish Race.

## During the Race

Inevitably, you will be asked for details about the race.  It is easy to answer race questions in CrossMgr, and get back to the Record page if you need to enter numbers (of course, if the number appears in the lower left, you can just click it off).  All screens are accessible from the function keys, and the Passings and Results have Search capabilities.  You can always get back to the Record page by pressing F2.  For example:

- Q: Who came after rider 189?
If you recently entered this number, you might see it in the Recorded section on the upper-left of the screen.  If not, you can also easily find numbers in the Passings page.  Try this:

F4 (takes you to Passings)
type: 189
Enter (searches for 189)

See the number is highlighted.
To get back to the Record screen press:

F2

As you get better with CrossMgr, you will see how you can quickly move between the screens.

- Q: Who is in 6th place?

F3 (takes you to Results)

Look at the rider in 6th place.  This will give you the results for the whole race.  If you are interested in a particular category, select it from the Category list.

F2 to get back to Record.

Try this a few times to get comfortable.

## After the Race

Check the Recommendations page.  Investigate all the messages by double-clicking on them.

Now look at the Results page.  All entries in Yellow have a projected time.  Double-click on each one to see Passings, then check Rider Detail by double-clicking on the number again.

If there are any inconsistent numbers, adjust them in the RiderDetail page.   Just select the Category you want to move the rider to.

Make sure the results look reasonable before printing and publishing them.

### Handling Did Not Start DNS Riders

If CrossMgr has any information about a rider, it considers that rider in the race (for example, a lap time).  But, what about riders registered for the race, but didn&#39;t start?

These riders can be quickly added to the race as DNS (Did Not Start).  To do so, select &quot;DataMgmt|Add DNS from External Excel Data&quot;.  This shows a list of all riders in the Excel sheet that aren&#39;t in CrossMgr already.  Select the riders you want to add as DNS from the list (or press &quot;Select All&quot;) and add them to the race as DNS.

You can add DNS riders during, or at the end of the race.  Give yourself some time if there are late starters.  If you add a DNS rider, you can always change it later.

### What if Things get Really Messed Up?

Not to worry!  Remember, CrossMgr supports full Undo (Ctrl-Z) and Redo (Ctrl-Y).  CrossMgr also stores all your original inputs \*exactly\* as you typed them in a separate file with the ending Input.csv (this is created in the same folder as the race file).

This file contains your original input numbers and timestamps - no edits or corrections are included.  If you really need to, do a &quot;File|Restore from Original Input&quot; and you can start over from scratch and fix up your race.  After restoring, look at the Chart (F8), see what doesn&#39;t look right, and go from there.

You can also open this file in Excel as it is a .csv file (comma separated).  The times look a bit strange, but they are in Excel standard time format (in units of days).  To see the times properly, select the column, and then change the cell format to &quot;Time&quot; (choose HH:MM:SS).

As a last resort, you could even score the race manually from the data in the Excel sheet.

CrossMgr writes to the Input.csv file with every entry.  This makes it a powerful backup.

# Categories

The Categories tab allows you to associate ranges of numbers with different categories.  Press New Category to get a new category.  Use the other buttons to delete and move the categories around in the list.

Categories include the following input fields:

| Type | Description |
|------|-------------|
| Active | Indicates whether this category is active in the race or not.  Inactive categories will not appear in Category drop-downs in the Passings or Results tab. |
| Name | Name of the category |
| Numbers | Numbers and ranges of the category.  Number ranges are indicated by XXX-YYY, for example, 100-199.  You can add exceptions by listing numbers separated by a comma.  You can remove numbers by listing numbers beginning with a minus sign separated by a comma.For example:100-199,504,507,-128,-61This means that all riders with numbers 100-199, plus 504 and 507, but excluding 128 and 61 are in the category. |
| Start Offset | The start offset of this category in the race in MM:SS.  For example, if the 2nd category started 1 minute later, you would enter 01:00.This is used to adjust rider&#39;s lap times in the results based on the start offset. |
| Race Laps | The number of race laps for this category.  Leave this alone, as it is generally not necessary to enter anything here.  The results for each category will be listed for the actual number of laps completed by the lead riders.There are two cases where adjusting this value is required.The first is if you have different categories racing different times.  When the shorter category ends, CrossMgr needs to know how many laps were done by the leaders of this category, otherwise it will continue to project lap times.The second case is less common and takes some explaining.   Say Category A starts first, and Category B starts second.  The leaders of A end up passing most of B in the last lap, but the leaders of B manage to stay in front but are stopped at the line with A&#39;s leaders just behind them. In this case, CrossMgr needs to know the number of laps for B, otherwise it will think that the B leaders did another lap (and were missed, so it projects a time for them), and the rest of the B field is down a lap.This rare situation can be corrected by entering the number of laps for Category B.  If this does not happen at your race, then you don&#39;t need to worry about it.  This is a special case of &quot;different categories racing different times&quot;. |

You can configure categories at any time – before or after a race.  You can change/import/export them at any time.  Categories are stored in the race file itself – changing an External categories file has not effect on an existing race until you Import it again.

It is important to set the number ranges as accurately as possible.  This will automatically enable number shorthand (see below).

The Categories screen also shows the 80% time rule for that category and the recommended number of laps for that category&#39;s race.  Ignore these if you are not pulling riders or you are running the entire race on the same lap counter for all categories.

CrossMgr makes it easy to have multiple categories in the same race.  It can produce an overall result for everyone in the start as well as results broken out by category.  Consult the Help on Categories for a full explanation.

## Number Ranges and Input Shorthand

CrossMgr examines the number ranges for all active categories and determines if input shorthand is possible.

For example, say you have only one category with a number range of 100-199.  The left-most &#39;1&#39; is not required to uniquely identify the riders as all riders have a &#39;1&#39; as the first digit.

When CrossMgr detects this situation, it will automatically add the leftmost &#39;1&#39; to all 2-digit input entered in the Record screen.  This means that you (and your number caller) need not be concerned with calling or inputting the first digit.  This represents a 33% savings in effort and increases the number of riders you can enter accurately in any time interval.  Of course, it is OK to enter the full 3-digit number, but you don&#39;t have to.

CrossMgr will not automatically add a leading number to any 2-digit input if there is no common leading number.  For example, if the ranges are 100-199 and 200-299, there is no common leading number to add so you will have to enter all digits.  Similarly for 1-99 and 100-199 – all digits are required to be unique.

## Category Import/Export

You can import and export categories from one race to another so that you do not need to re-enter them every time.  Categories are stored in the race file.  This is so that any corrections made for registration mistakes and exceptions for a particular race are kept separate from the general categories file.

 Once you have set up categories in one race, go to DataMgmt, and export the categories to a file.  You can now import those categories into another race.

You can configure different categories files for different events, different number ranges and different formats like UCI categories, regional or national.  Configure all your categories, and then use the Active flag to indicate which ones you are using in a particular race.

# Link to External Excel Data

CrossMgr has the ability to link to an external Excel file which contains more information about riders including last name, first name, team, license and license category.  This data is then included in the results output, both Excel and Web.  Without external data, CrossMgr can only create results with the rider numbers recorded during the race.

To link to an Excel file, press the &quot;DataMgmt|Link to Excel...&quot; menu.  This brings you to a Wizard where you specify the Excel \*.xls file, the sheet in that file corresponding to the race, and how the header fields in the sheet correspond to the fields that CrossMgr is looking for (more on that below).

After successfully linking to an Excel file, rider details will automatically appear in the &quot;File|Results...&quot;  The idea is to use an Excel file that is already being used by the organizer.  If this is possible, then no additional data entry is required.  Normally, there is a sign-on sheet containing the numbers and information for all riders in a race.  This is a good Excel sheet to link to.

Remember, CrossMgr links to the Excel file.  This means that if you change data in the Excel file, CrossMgr will automatically pick it up the next time is refreshes the screen.

If you move, rename or delete the file, you will have redo the link.

## Format of the Excel File

### Headers

CrossMgr expects each Excel sheet to have a header row.  CrossMgr identifies the first row with 5 or more non-empty cells as the header row.  There can be more headers in the sheet than CrossMgr cares about.  Rider data must then follow the header row in columns (see the example).  Blank rows, or rows with missing data are OK, however, but obviously, any missing data will not appear in the results.  CrossMgr will skip rows that do not conform to the header.

CrossMgr allows the spreadsheet header names to be different from its internal names, however, you have to tell it what headers correspond to what it is looking for in the Excel Link Wizard.

It is OK if you don&#39;t have all the data CrossMgr is looking for, however, you must at least have field corresponding to &quot;Bib#&quot; in the header.  If you do not want a CrossMgr field to appear in the results, map it to a &quot;blank&quot; header in the Wizard.

CrossMgr matches its recorded numbers with the &quot;Bib#&quot; column in the Excel file.  This allows it to find the row containing the rider data.

The Excel sheet is also where you enter the Tag of the chips assigned to the rider if you are using chip timing.

### Sheets

CrossMgr expects that the &quot;Bib#&quot; field will be unique in the Excel Sheet.  If the &quot;Bib#&quot; field is not unique, CrossMgr has no way of telling which rider number matches the corresponding information.  If there are duplicates (and there should not be duplicate bib numbers in the same race), CrossMgr will use the last &quot;Bib#&quot; in the sheet to get the data (last one wins).

The Excel sheet does not have to be ready before the race starts.  You can start the race while the Excel data is still being input.  The Excel data can be changed before, during or after the race – just run the reports again.

It is also easy to use categories defined in the Excel sheet with the &quot;EventColumn&quot; label.  If set, CrossMgr will automatically define its categories from the Excel sheet.  Consult the Help for full details.

For the chip timing feature to work, the tags for each rider number must be input before the start of the race, and the Excel file must be linked to the CrossMgr race.

Sign-on sheets are ideal files as they are organized with one Sheet corresponding to each race.

# Advanced Topics

## Multiple categories with multiple lap counters

The easiest way to run a race is to use one lap counter with all riders finishing when they see no more laps to go.

However, this can be problematic if all riders in a category get lapped in their last lap.  In this case, they are going to &quot;miss&quot; their bell lap.  To them, the lap counter will appear to go from 2 to go to race end.  Riders get upset because they get no bell and don&#39;t know it is their last lap.

If you expect that a category will do one lap less in the race, you can have a separate lap counter for that category.  Check the Categories screen for the recommended number of laps for each category.

This is very hard to do when scoring manually.  However, CrossMgr shows you the expected leader for each category before the rider arrives.  This makes it much easier to know when to flip the lap counters.

After the race, CrossMgr might generate some &quot;phantom&quot; laps in the Results for the leaders of the category that did fewer laps.  This happens if the leaders for that category finish before being caught by the race leader, but other riders in the category are caught.

The Results can be fixed by setting the Race Laps in the Categories page to the laps actually done by that category.  Don&#39;t worry – there is a Recommendation reminding you to do this when this happens.

## Fixing Bad Data

So you have a race with results that don&#39;t make sense.  Maybe some bad data got entered, maybe some data was missed.  CrossMgr has many features to fix bad data.

The first step in fixing bad data is finding it.  The quickest way to do this is to go to the Chart tab (F6), and look at the race.  This view shows all the laps in a Gantt chart, color coded by lap.  Diamonds are calculated times that CrossMgr inserted.

Look for laps that are too long or too short.

Q: I see a bar in the Gantt view that is about double the length they are supposed to be.  It looks like there was a missed lap.  How do I fix this?

A: Right-click on the long bar and select &quot;Add Missing Split…&quot;.  Pick the number of splits you need to add (usually just one).

**Q: I see a bar in the Gantt view that is too short – it looks like an extra input.  How do I remove this extra time?**

A: Right-click on the bar just before the double entry.  Select &quot;Delete Lap End Time…&quot;.  This will remove the lap end time, and the double-entry.

Q: Some riders did an extra lap that was recorded in CrossMgr, and now CrossMgr thinks that race has an extra lap in it.  How do I fix this?

A: Go to the Categories tab (F9) and manually set the &quot;Race Laps&quot; to the laps for that category.  This will ignore any extra recorded laps for that race.

**Q: I don&#39;t like how CrossMgr is autocorrecting.  How do I turn it off?**

A: Go to the Rider Detail tab (F5) and enter the rider&#39;s number (or double-click on it in most other views).  Turn off the &quot;Autocorrect Lap Data&quot; option.

Sometime the problem is that you have to reconstruct missing data after the race, perhaps from a video reference:

Q: I have some riders who were missed in the finish entirely.  How do I add them?

Q: I have some riders who finished in a different order than CrossMgr is showing.  How do I fix this?

Q: I have some riders who have the wrong finish time.  How do I correct this?

Q: I want to change a rider&#39;s finish time earlier/later.  How do I do this?

Q: Some times were entered incorrectly &quot;after the fact&quot;.  How do I fix them?

A: Go to the Passings page (F4) and select the Category you want (or All).  Select the &quot;Race Times&quot; and &quot;Rider Names&quot; options.

Right-click on an entry in the table.  Here you will see the following options:

- . **Correct…** Allows you to change the rider&#39;s number, or change the time of the entry.
- . **Shift…**  Similar to Correct, but allows you to easily shift the existing time earlier or later.  For example, if you have an entry of 1:46:53 and you need to move it 21 seconds earlier, you just need to enter 21 rather than having to subtract the 21 seconds from the time yourself.
- . **Insert…**  Allows you to insert a new entry just before, or just after the current entry.  The entries will be separated by 1/10,000 of a second.
- . **Delete…**  Deletes an entry.  Use with caution.
- . **Swap with Before…**  Swaps this entry with the entry just before it.  This exchanges the numbers of the entries but keeps the times the same.
- . **Swap with After…**  Similar to &quot;Swap with Before&quot;, but swaps the entry just after it.

  Sometimes you need to use two operations to get what you want.  For example, if you want to insert an entry at a certain time, first use Insert to get the new entry in the right place, then use Correct or Shift to change the time.

**Q: I have a rider that was missed the entire race.  Can I create entries for this rider?**

A: Yes! Say the rider you want to insert finished in 3rd place.  Find the current 3rd place rider, and enter the number in RiderDetail.  Now, click on the &quot;Edit…&quot; button and select &quot;Copy Rider Times to New Number&quot;.  This will duplicate the 3rd rider&#39;s entries under a new number that you enter.  The entries for the new rider will be just before the entries of the existing rider.

## Managing Rider Numbers

Inevitably, a rider will get the wrong number, or two riders get each other&#39;s numbers.  Also, a number might have been entered by mistake that is not in the race.

To deal with these issues, go to Rider Detail, type in the number (or get there by right-clicking on the number in some other screen).  Then click on the Edit… button.

You now have three options to Delete…, Change… or Swap… rider numbers in the race.  Delete will remove the rider, and all his data, from the race.  Change will renumber a rider for all entries.  Swap exchanges the numbers for two riders for all entries.  For Duplicate…, see just above.

## Quick Shortcuts

You can make the Recorded and Expected lists side-by-side.  Just double-click on the splitter bar between Recorded and Expected.

Try the right-click menu in the Recorded and Expected lists.

Try typing in a search number in Passings or Results.

# RFID Timing

Sometimes riders arrive too quickly to enter numbers manually.

This is common in criteiums and road races, where 50-100 riders could all cross the finish line at once, however, it can also happen in very large cross races, or when the course is not very selective and the riders can ride together in a bunch.

CrossMgr supports:

1. **Impinj (LLRP)** readers (passive chips)
2. **Alien** readers (passive chips)
3. **J-Chip** active chips
4. **RaceResult** active and passive chips
5. **Ultra** passive chips

The choice depends on your individual circumstances.  Active chips are much more accurate, but far more expensive.  With used RFID readers and some ingenuity, it is possible to put together a chip timing system based on CrossMgr $500.  For more information, see CrossMgrImpingReadme on the CrossMgr site.

Systems like J-Chip, RaceResult and Ultra are packaged systems with battery backup power – much less of a &quot;science project&quot;.  However, they come at a much higher cost.

RFID timing also requires tag management at the race site (creating tags, replacing lost/inoperative tags, etc.).  It is highly recommended to look at RaceDB (also on the CrossMgr site).  RaceDB can handle all

# Quick Reference and Frequently Asked Questions

## How Do I Print Results?

1. Setup a rider data Excel sheet (see example provided in the Profile Files\data folder).  Make sure the latest changes are saved in the file.
2. Link the Excel sheet to your race (&quot;Data Mgmt\Link to External Excel Data…&quot;).  You only need to do this once.
3. In CrossMgr, do &quot;Publish|Print Results…&quot;
4. To simultaneously create results files in many formats including Pdf and Excel, do &quot;Publish|Batch Publish Files…&quot;, and select the file formats you want.  This option also supports an Ftp upload.  See the Help for full details.

## How Do I Manage Riders About to be Lapped?

1. While the race is running, CrossMgr forecasts the riders who are 80% behind the leader of each category.
2. This is shown in the &quot;Note&quot; field in the &quot;Expected&quot; section of the screen (lower left).
3. When you see riders with an 80% Note, tell the puller that the riders are coming.  Make sure you also check the Lap field to ensure that this is not a result of a missed number entry.  You can also check the rider&#39;s individual data by right-clicking on the number and selecting RiderDetail.
4. When you receive confirmation that the rider was pulled, right-click on the rider number and selected &quot;Pulled&#39;.

## How Do I Start a Race If I am Not At the Computer?

1. Use the &quot;Start Race at Time&quot; feature.
2. In the &quot;Actions&quot; page, select the &quot;Start Race at Time&quot; option.  You must have configured a race beforehand.
3. Press the &quot;Start Race&quot; button.  This will allow you to start a countdown to the start of the race.  The race will start automatically at the end of the countdown.  You can stop the countdown at any time.
4. Use this feature with caution – if you are away from the computer, there will be no way to stop the countdown if something comes up.

## I Entered Two Numbers in the Wrong Order the Riders Crossed the Line.
How do I Fix the Results?

1. Go to the Passings screen.  This also works in the Results screen.
2. Category you want to change (if required).
3. Right-click on the number.  Select &quot;Swap with Before…&quot; or &quot;Swap with After…&quot;, depending on how you want to swap numbers.

## I Entered a Number that Does Not Exist in the Race.
How Do I Get Rid of It?

1. Go to the Passings screen and find the number that is incorrect, Right-click on the number, and choose &quot;RiderDetail. Or type it in RiderDetail.
2. In the &quot;RiderDetail&quot; screen, press the Delete button

## How Do I Enter Riders that Did Not Start (DNS)?

1. Go to the RiderDetail screen.
2. Enter the DNS number, press Enter.
3. Change the Status to DNS.

## How Do I DQ a Rider?

1. From the Record Screen:  Type in the number, press DQ
2. From other screens:  Right-click to go to RiderDetail.  Change the Status to DQ.

## I Missed Entering a Time for a Rider, but CrossMgr did not Automatically Correct It.
How do I Insert a Missing Time Manually?

1. Go to the Chart screen.
2. Look for what looks like a really long lap (the two laps missing the time in the middle).
3. Right-click on the lap in the chart, and select &quot;Split Lap in 2 Pieces&quot;.  This will insert a missing time.

## Somehow a Number was entered too Many Times.
How do I Remove An Entry?

1. Go to the Chart screen.
2. Look for what looks to be a really short lap.
3. Right-click on the first short lap in the chart, and select &quot;Delete Lap End Time&quot;.  This will remove the extra time.

## How do I Fix Bad Data and/or make Manual Changes to Entries?

See the **Fixing Bad Data** section for details.

## I Really Messed Everything Up.  How do I Start Over?

1. Do a &quot;File|Restore from Original Input…&quot;.
2. This will restore the race from the original input with no corrections.

## How Do I Check CrossMgr&#39;s Results with Manual Input?

1. Check it on the screen in the Passings screen.

