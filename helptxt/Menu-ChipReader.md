
[TOC]

# ChipReader

CrossMgr can accept real-time messages from [JChip](http://mts.greentag.to/english/index.html) and [RaceResult](http://www.raceresult.ca/en-ca/home/index.php) receivers as well as an Impinj and Alien readers through the CrossMgrImpinj or CrossMgrAlien bridge programs respectively.
CrossMgr can also import a file that was generated from the JChip and RaceResult systems, or the CrossMgrImpinj or CrossMgrAlien bridge programs.

All chip systems log the time and code when it reads a chip, and each chip has a unique code.  This code may be the same as the rider's Bib number, or it might be something different.  The code must to be associated with a rider's name, team, bib, etc.
CrossMgr allows you to configure which tag goes with which rider through the [External Excel][] sheet.  CrossMgr supports two columns, Tag and optionally Tag2, that contain the chip tag code(s) for that rider.  CrossMgr supports two tags in case you wish to give one two tags - the one intended for a backup bike.  Alternatively, multpiple chip tags can be programmed to the same code enablig a rider to be identiified from race to race or on different bikes (this is what RaceDB does).

If you are using RaceDB, this is managed for you from the RaceDB database and communicated to CrossMgr transparently.

To reduce "spurious" reads, CrossMgr will only register the Tags defined in the [External Excel][] sheet during a race.  This eliminates interference from reads from riders in other races.

When a rider's chip is read, the chip receiver sends a timestamped message to CrossMgr with the tag.  CrossMgr does a lookup on the tag to find which rider it was, and then uses the time to automatically make an entry - just as would be done manually.

CrossMgr always uses the chip reader's time.  This ensures accuracy even if CrossMgr gets busy and cannot look at its incoming messages for a few seconds.

CrossMgr supports __any number of simultaneous connections of JChip, CrossMgrImpinj or CrossMgrAlien readers__ (in any combination).

It computes a time correction between each reader's time and the CrossMgr computer's time.  This synchronizes the reads to a consistent time even if the clocks on all the readers are different (which is likely).

For other readers, only one connection to one reader is supported at a time.

Notes about Chip reader input:

1. All reads before the start of the race are ignored.
1. Reads after the start of the race, but before the Start Offset of a category will be registered, but ignored in the results.
1. A race can be started by the first tag read.  See [Actions][] for more details.  When a race is started with the first tag read, the riders are staged behind the start/finish line, CrossMgr is started, then the riders are started.  The first rider over the line will reset the CrossMgr start clock.  This allows you to start a race without being at the computer.

## Chip Reader Setup
Open the Chip Reader Setup Dialog.

### Chip Reader Setup Dialog
Used to configure and test the Chip receiver.

#### Configure the Reader
If using CrossMgrImpinj or CrossMgrAlien to talk to the Impinj or Alien reader, make sure those programs are running and the reader is plugged in, on the network, etc.  Then skip to "Do Reader Test".

__JChip:__ make sure you have your [JChip Documentation](http://mts.greentag.to/ControlPanelSoftManual.pdf) ready if you are configuring JChip for the first time.

__RaceResult:__ make sure your RaceResult reader is plugged into the network.

__JChip:__ The JChip Setup Dialog provides the needed parameters to allow you to configure JChip.  Go to the "7 Setting of Connections" section in the JChip "Control Panel Soft Manual" and configure a JChip connection as follows:

__Impinj and Alien bridge:__ CrossMgr will find these programs automatically as they are running on the same machine.

CrossMgr communicates with the Chip or RaceResult reader through a TCP/IP interface (that is, an internet connection).  This can be done with cable or wireless.  CrossMgr listens for a connection on all network connections including cable and wireless.  Check what hardware you need to accomplish this.

Field|Value|Description
:----|:----|:----------
Type|JChip/Impinj/Alien or RaceResult|The type of reader you are using.
Remote IP Address|One of the IP addresses shown on the screen|__JChip/Impinj/Alien:__ this is the IP address of the CrossMgr computer.  If there are more then one, one is generally for the LAN and the other is for the wireless connection.  To tell which is which, on Windows, in a "cmd" window, run "ipconfig".  On Mac/Linux, open a terminal and run "ifconfig".  Choose the IP address which matches you connection - LAN or wireless that you are using to connect the JChip receiver.  __RaceResult:__ this is the IP address of the RaceResult reader.  If you are on a LAN, the __AutoConnect__ button should find the reader automatically.  If not, or you are using a static IP, enter the IP of the RaceResult reader here.
Remote Port|53135 or 3601|__JChip/Impnj/Alien:__ port on the CrossMgr computer that JChip reader or bridge programs connect to.  __RaceResult__ port that CrossMgr uses to talk to RaceResult.  You should not have to change these.

__JChip__

The __Remote IP Address__ will be the one shown in CrossMgr.  Don't worry about the other JChip fields, however, the CrossMgr connection must be checked for "Use".
You may have to power down/power up JChip after making this change.

__RaceResult__

The __Remote IP Address__ is the address of the RaceResult reader.  If the AutoDetect button cannot find it on the LAN, of if you are using a fixed IP, you will have to enter it manually.

#### Do Reader Test

Press the "Start RFID Test" button in CrossMgr.  This tells CrossMgr to connect to the reader and start processing tag reads.

You may receive a warning if you do not have an Excel sheet configured.
If you just want to test the receiver, you don't need to worry about the warning.  If you are trying to use RFID tags during a race, you will need a properly configured Excel sheet to associate the tags to the rider information.

__JChip:__ turn on the JChip receiver.  In the CrossMgr Messages section, you should soon see the connection succeed.  If not, check that you have the correct "Remote IP Address" and "Remote Port".  Make sure you open port 50353 on your operating system.

__RaceResult:__ make sure it is on and plugged into the network.  If CrossMgr cannot find it, you may need to open port 3601 in Windows.

__Impinj/Alien__: ensure the CrossMgrImpinj and CrossMgrAlien programs are running.  Maks sure you open port 50353 and port 5084 on your operating system.

After starting the test, you should immediately see the connection between CrossMgr and the reader..

If Windows asks you if it is OK for CrossMgr to open a port - don't worry - it's OK.

Now, walk through the antenna (or across the matt) with some chips.  You should see the connection and tag information showing up in the "Messages" section.  Something like this:

>    listening for RFID connection...  
>    *******************************************  
>    connected: RFID receiver  
>    waiting: for RFID receiver to respond  
>    receiver name: JCHIP-TEST12  
>    transmitting: GT command to RFID receiver (gettime)  
>    getTime: 013005032=14:00:50.32  
>    timeAdjustment: RFID time will be adjusted by 0:00:00.02 to match computer  
>    transmitting: S0000 command to RFID receiver (start transmission)  
>    1: tag=413A74, time=2012-07-24 14:00:50.3510, Bib=not found  
>    2: tag=413A3B, time=2012-07-24 14:00:50.3510, Bib=not found  
>    ...  

You can see some of the nuts-and-bolts of the communication between the two systems.
When finished testing, press the "Stop RFID Test" button or close the dialog.

It is recommended that you test the RFID receiver connection before every race.

#### Accept RFID Data During Race
Sets the "RFID Integration" property (see [Properties][]).

When the race starts, CrossMgr will start its server, wait for a RFID connection and start recording RFID entries.  Of course, manual input still works as usual in CrossMgr while the JChip integration is running.

## Import JChip Formatted File...
Imports a JChip-formatted input file.  This is highly useful if you want to get results for a race recorded with JChip at an earlier time, or if you lose the connection to JChip during a race.

### JChip Data File
The JChip formatted data file to import.

### Data Policy
CrossMgr supports two policies regarding existing race data:

1. Clear All Existing Data Before Import
1. Merge New Data with Existing

The first option will clear all timing data from the race and import it again fresh from the import file.  This is the option you would normally want to use.

The second option will keep all existing data in the race and merge the data from the import with it.  This is useful, for example, if you start a time trial manually, then import data into it at a later time from a chip reader.

### JChip Data Times Are (Behind/Ahead)
This option is only useful if you are merging JChip data with manually-entered data.  If you are importing all data from JChip then you can ignore it.

The HH:MM:SS.SSSS time the JChip clock was ahead of or behind the computer's clock when the data was captured by the JChip receiver.  This adjust will be applied to each time to correct it to be consistent with the computer's time.

For example, say you started a time trial manually in one location and want to import data later from the chip reader which has been set up at the time trial finish.  After checking, you see that the JChip receiver was running 4.2 seconds behind your computer's time.

To import the times accurately relative to the earlier manually entered times, you would enter a "Behind 00:00:04.2" seconds adjustment.

If you have access to the JChip receiver and its time has not been adjusted, you can set this field automatically.

To do so, open the "Menu/JChip Setup..." dialog and run a JChip test including connecting to the JChip receiver.  After the connection has been established, close the "JChip Setup..." dialog.  Althogh the dialog is closed, the time adjustment has been determined from JChip.

Now, return to the JChip Import.  You will see the time correction automatically filled in based on the last JChip connection.

### Race Start Time (if NOT first recorded time)

If you are importing into a new race, this option gives you the ability to start the race at the time specified, then import the timing data contained in the file.  Otherwise, the race will be taken to start with the first recorded chip read.

Do not use this option if you are merging with existing data, as the race must already been started for existing data to be present.

## Import Alien Formatted File...
Imports an Alien-formatted input file.
See above for options.

## Import Orion Formatted File...
Imports an Orion-formatted input file.
See above for options.

## Import RaceResult Formatted File...
Imports an RaceResult-formatted input file.
See above for options.
