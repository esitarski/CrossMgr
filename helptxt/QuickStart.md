[TOC]

# Quick Start
Welcome to CrossMgr!

CrossMgr is easy to use.  You can start with a simple race with manual entry and numbers, move on to linking rider information from an [External Excel][] sheet, and progress with producing professional web output live during a race.

CrossMgr has the *best* capabilities for analysing and fixing problems after a race (see [Recommendations][], [Chart][] and [RiderDetail][]).

## Getting Help
At any point, press [CTRL+H](Main.html) to get help on any screen.

## Learning More about CrossMgr

Read and work through [CrossMgrTutorial.doc.](https://www.sites.google.com/site/crossmgrsoftware/file-cabinet).  CrossMgr has a built-in [Demo](Menu-Demo.html) showing a realistic race with two categories racing at once.  The data shows how to manage missed data and lapped riders.

### Watch the Demo

Do __Tools/Simulate Race...__.  Explore the program features with simulated race data.

## File / New a Race
Configure the [Properties][] of your race.  There are a lot of Properties there but don't worry - you only need to fill in the ones that are important to you.

For a simple race, you will only need to set up the following:

* Race Name
* Organizer
* Date
* Scheduled Start
* Race Minutes
* Distance Unit (km or miles)

That's really all you need to do.  At this point you are ready to start a race.

For the next race, do File/New Next... (see [File][] ).  This increments the race number but keeps all the other information to save typing.

## Start a Race
When you are ready to start a race, goto [Actions][] and press Start.  This will bring you to the [Record](Record.html) screen.  Type in the numbers as the riders go by on the first lap.  After the first lap, CrossMgr will predict the riders in the lower left.

When a rider comes around again, you don't have to type in the number again - just click on the number in the lower left (it's still OK if you type it in again).

It's also OK if you miss a few numbers.  CrossMgr will reasonably autocorrect missing entries as it builds a profile about each rider.

[Results][] are continously updated during the race.

From [Actions][], press "Finish" when the race is over.

## Configure Categories

CrossMgr can handle multiple categories in one race at one time.  It comes with some defaults, but they are not very descriptive.  Configure more descriptive categories in [Categories][].

You configure the lap (or race) distance in [Categories][].  Distance Units are the same as configured in [Properties][].

CrossMgr works best when you have number ranges for each category, but it's OK if you don't.  It's also OK if there are riders who's numbers don't match the category range.  Just make sure that all the numbers are unique in a race!

If a rider is showing in the wrong categegry in the [Results][], double-click on the rider.  This will bring up the [RiderDetail][] dialog.  From this dialog, change the rider to the right category.

You can setup or change [Categories][] before, during and after a race.

## Configure Rider Names, Teams, etc.
CrossMgr reads external information from an Excel Sheet that you maintain externally.  CrossMgr "links" with the external sheet, reading the information based on the Bib numbers.  This is very easy to set up - read about the details in [DataMgmt][].  There is also an example sheet in the CrossMgr installation.

You can setup or change the Excel sheet before, during and after a race.  It is commonplace for the organizer to type in rider names at registration while the race is running, then link up the Excel sheet after the race.

## Publish Results
After the race is finished, review the results in the [Results][] screen.  If you see issues, double-click on the rider and fix problems in the [RiderDetail][] screen.

Review CrossMgr's issues by checking the [Recommendations][] screen.

You also see all problems at once yourself from the [Chart][] screen.  CrossMgr has full undo and redo in case you don't want the change you just made.  CrossMgr also tracks changes and whether they were part of your original data, or whether they were changed.  The user and timestamp of the change is recorded.

Watch an fast-forward [Animation][] of your race and check for problems the same as how they happened in the race.

Post corrected results on your web site with [File/Publish Results as HTML...](Menu-File.html#publish-results-as-html).

# Using CrossMgr to the Fullest
There are many features available in CrossMgr that you can use as you feel more comfortable.  Here are some suggestions for improving your Results:

1. Publish results in HTML to post on your website.  See [File/Publish Results as HTML...](Menu-File.html#publish-results-as-html).
1. Customize the Graphic in your published output.  See [Options][] for details.
1. Set the Email in the published output so people can email comments and corrections.  See [Options][] for details.
1. Publish results directly to a website with FTP.  See [File/Publish HTML Results with FTP...](Menu-File.html#publish-html-results-with-ftp) for details.
1. Publish results live during a race.  See [File/Publish HTML Results with FTP...](Menu-File.html#publish-html-results-with-ftp) for details.  Look at the "Automatically Upload Results During Race" feature.
1. Use CrossMgr for Time Trials.  See [Time Trial Mode](Properties.html#time-trial-mode).
1. Use a Chip Timing system system.  See [ChipReader][].
1. Use a USB Camera to capture finishes.

Remember: press [CTRL+H](Main.html) on each screen to find out what it does and how it works.  Review [CrossMgrTutorial.doc.](https://www.sites.google.com/site/crossmgrsoftware/file-cabinet).
