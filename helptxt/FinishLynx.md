[TOC]

# FinishLynx
Integration to the FinishLynx timing system.  Here is how it works:

1. Create Categories and Start Offsets in CrossMgr (see [Categories][] for details).
1. Link your Excel spreadsheet containing rider information (see [External Excel][] for details).  If your race is a TimeTrial, you must specify Start Times to CrossMgr.
1. From the __DataMgmt__ menu, select __FinishLynx...__ to open the FinishLynx dialog.
1. From this dialog, you can Export or Import information from FinishLynx.

## FinishLynx Export

### Mass Start Races

Make sure the [Categories][] and [External Excel][] are set up for your race.

From the the __DataMgmt__ menu, open the __FinishLynx__ dialog.
The first option is to __Export__.  This does the following:

* In the same folder as the CrossMgr Race, CrossMgr creates a new <RaceName-lynx> to contain the FinishLynx files.
* In this new folder, it writes three files: lynx.ppl, lynx.evt and lynx.sch.  Consult the FinishLynx documentation for details.
* These are the files required by FinishLynx.

The FinishLynx files are written as one Event with no consideration of Category start offsets.

You will start the different Categories on the start line on the start offsets as usual.

CrossMgr will fix up everything on import - FinishLynx doesn't know about the start offsets.

### Time Trials

For __Time Trials__, you will need to set up __Start Times__ (see [TimeTrial][] for details).
You can specify __Start Times__ in a separarate spreadsheet that you import on demand, or in the same [External Excel][] spreadsheet that will pull changes automatically.

With the start times specified in CrossMgr, the Export procedure is exactly the same as a Mass Start.

During the event, the riders are started on their start times by race officials.

Note that FinishLynx does not "know" about the individual start times.  They are applied by CrossMgr during the FinishLynx import.

## FinishLynx Import

During (or after) the race, FinishLynx produces a __*.lif__ file containing times and splits.

From the FinishLynx dialog (DataMgmt|FinishLynx...), import the combined __.lif__ file.

It is important that there is one __.lif__ file containing all the riders in all categories.  Do not split the FinishLynx results into multiple files by Category.

During the import, CrossMgr will do the following:

* Automatically apply the Category start offsets for each rider (or use the specified start times if a Time Trial)
* Auto-correct any missing lap times.
* Apply any rider status (DNF, DNS, etc.).
* Use the FinishLynx race start time as its race start time.

## Import Errors and other Potential Problems

### Unknown Bibs

If the FinishLynx input file contains a bib number unknown to CrossMgr, it will treat its as usual.  That is, if the bib number matches a Category's numbers, the rider will be ranked in that Category.

### Potential Results File Issues

Integration with FinishLynx is done by reading the .lif file.  This is very primitive.
A problem happens when CrossMgr tries to read this file at the same time FinishLynx is writing it.
Although unlikey, there is nothing to prevent this from happening, and it could result in corrupt or missing data.

CrossMgr tries to detect this scenario by checking that the .lif file is non-empty and its last character is a newline.
If this fails, it waits a second-or-so and tries again.  This hopefully gives enough time for FinishLynx to finishg writing the complete file.
If a few attempts, it will return a failure message.

Note that it is still possible (but even less likely) for the .lif file be incomplete but still end in a newline.  CrossMgr has no way of knowing there is a problem in this case.
If the results don't look right after a FinishLynx import, do it again when you know FinishLynx is not currently writing any files.

Unfortuantely, solving this integration problem properly requires changes to FinishLynx.
For example, the file could have and chechsum or an end-of-file marker (say, the last line is "<eof>").  Either would make it easy to determine that the file was correct.
Better yet, FinishLynx could support a messaging API and eliminate files altogether.

### CrossMgr Race Recovery

Because the inputs come from FinishLynx, CrossMgr does not produce an input recovery log.
If something goes wrong in the race, you will need to re-import from the .lif file.
