[TOC]

# Introduction

CrossMgr can access Events in RaceDB directly.  Events can be __Opened__ before the race starts and __Uploaded__ after it ends to publish the results.

Published results are available in the __Hub__ as individual results for Events or combined in a Series.

## Configuring the CrossMgr connection to RaceDB

RaceDB and CrossMgr support a simple mechanism to enable a more secure connection between CrossMgr and RaceDB.
This is important if RaceDB is running on the web as it prevents "bad actors" from uploading unsanctioned results to a race.

If you are only run RaceDB on a local machine and you don't care about any security, then skip this section.  The default for RaceDB and CrossMgr is no security whatsoever.

If not, it is highly recommended that you follow the procedure below and configure some security.

To begin, from the RaceDB home page, press __Passwords__ in the __Crossmgr Access__ section.

Create a password record in RaceDB.
It can be convenient to configure more than one password to control access of individual machines or groups, however, you need at least one.
For example, if you want to need temporary access to a certain CrossMgr computer, you can create a password for it, then delete it later.
By making this a separate password, you don't need change anything on your other computers.

Now, on the CrossMgr computer, start CrossMgr.

Go to __File|Open from RaceDB Server...___.  From here, press __Config...__.

From the __Config Edit__ dialog, press the __Initialize Template__ button.  This creates a template for your config file.  Edit the configuration, replacing the values between the double brackets:

* change the __url__ to be the base name of your RaceDB server
* change the __password__ to be one of the passwords you configured in RaceDB
* change the __user__ to be the user that identifies accesses from this computer.

Lines that begin with # are comments.  Make sure you keep the structure of the file starting with the RaceDB in square brackets at the top.

This ultimately creates a file in your home directory called __CrossMgrRaceDB.ini__.

Now, press __Save and Verify__ to check that your connection is set up correctly.  The RaceDB server will need to be accessible for this to work.

Now press __OK__.

You are now ready to __Open__ and __Upload__ CrossMgr races to RaceDB.

## Opening a RaceDB Event in CrossMgr

If RaceDB is running in the cloud, you will need access to the internet from the CrossMgr computer.
Depending on your router set, you may need to temporarily disconnect the CrossMgr computer from the RFID Reader so it can find a wireless connection, then reconnect it afterwards.  For safety reasons, CrossMgr does not require an internet connection while it is running.

When you have all the starters issued in RaceDB and are ready to start, do a __File|Open from RaceDB Server...__ in CrossMgr.  The date defaults to today (change it if you need to).

CrossMgr will then show all __Events__ for the specified date from RaceDB.  Select an __Event__ to open it.

Behind the scenes, this downloads a CrossMgr-compatible Excel file from RaceCB (exactly the same file as when you press the CrossMgr download button from RaceDB).
CrossMgr stores this Excel file in the __Race Folder Base__ folder and create a corresponding CrossMgr race file to go with it.

As usual, the Excel file contains all the Category and Participant information for CrossMgr.

If the same RaceDB event is opened again, CrossMgr replaces the Excel file, but does not touch the corresponding CrossMgr race file.  This means that it is completely safe to __Open__ the same RaceDB event again even after CrossMgr has timed the event.  This is because the CrossMgr file is not touched.

You can make changes in RaceDB (update bibs, chip tags, etc.) and re-open the RaceDB again in CrossMgr after or during the race.
Again, only the Excel sheet is changed.  The CrossMgr timing data remains safe.

For example, say a rider started late with a new chip tag that wasn't entered in RaceDB before the race started.  Make the change in RaceDB, then after the race, re-open the event in CrossMgr.  With the updated information about the chip tag, the rider now appears in the CrossMgr results.

CrossMgr works with RaceDB with timing chips or without (this is an option in RaceDB).

__Best Practice:__ wait until a few minutes before the start of the race before opening it in CrossMgr.  Otherwise, you may miss last-minute changes.

### When do you need to re-open a RaceDB event in CrossMgr?

CrossMgr uses bib numbers to communicate its results back to RaceDB.  If the following information changes in RaceDB, then you need to reopen the event in CrossMgr:

* Changes that affect categories (rider changing categories, new categories added, etc.)
* Missing or changed bib numbers
* Missing or changed chip tags

Chanaged to other rider information (eg. names, teams) does not require a re-open.

## Uploading CrossMgr results to RaceDB

When the race is finished, it's time to publish the results back to RaceDB.  The results will then be publicly available in the __RaceDB Hub__, and race __Series__ will be updated instantly based on the new results.

The upload uses the same RaceDB configuration as opening a race (url, password, user): no additional configuration is required.

To upload, do __File|Upload Results to RaceDB Server...___.

If you make changes in CrossMgr and upload again, each new upload replaces the previous one.
Riders are identified by Bib number only during the upload.  All other rider information is ignored.

Of course, __Series__ results are updated automatically after new uploads.

### Uploading Results during a Race

It is possible to upload from CrossMgr to RaceDB while the race is running.  Ensure that the RaceDB server is accessible from the CrossMgr computer and do __File|Upload Results to RaceDB Server...___.

Currently this is not done automatically.

