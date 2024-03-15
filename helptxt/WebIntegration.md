
[TOC]

# Web Integration

## Introduction

In addition to the native interfaces, CrossMgr also supports integration via html messaging.

This is an http POST interface which allows RFID tags, or Bib numbers and times to be sent to CrossMgr.  These inputs will be process by CrossMgr as usual.

This can be useful to build your own CrossMgr interfaces, but it comes with some important limiations (see below).

To enable this feature, set __Reader Type__ = __WebReader__ in the __Chip Reader Setup__ dialog.

## Limitations

Unlike the built-in RFID interfaces, the Web interface is very basic:

__No Time Correction__

When CrossMgr connects to an RFID device, it computes a correction between the device's clock and its own.
This means that you don't have to worry about whether the RFID reader's internal clock is accurate.
It could be set to the wrong timezone, or the wrong day.  It doesn't matter.
CrossMgr will compute a correction and you are good to go.

This correction is not possible with the web interface, so you must make sure your device and the CrossMgr computer are synchronized from an internet time server (preferrably the same source).

This is important because CrossMgr ignores times before the start of the race.  The source device should be syncronized within a second-or-two.

__No Reconnect Recovery__

CrossMgr follows an automatic reconnect procedure if it loses the connection to the RFID device.
The interface programs (eg. CrossMgrImpinj) also buffer their reads while the connection is lost, then send the backlogged data when the connection is reestablished.
The design prevents/minimizes data loss.  It is likely that many CrossMgr users have lost a connection without knowing it as the recovery is transparent.

Not so with the web interface.  CrossMgr acts as a web server, and accepts http POST messages from an external client.
It is up to your client implementation to buffer reads and send them again after the network connection is restored.

__No Automatic Update Batching___

CrossMgr automatically batches update messages together to improve responsiveness (if necessary).
One-at-a-time updates from an RFID reader can freeze the CrossMgr user interface.
When CrossMgr detects it is falling behind, if starts processing backlogged messages as a single batch.
This prevents screen lock-up while processing messages quickly.

Currently, in the web interface, updates are processed when received.  It is up to your client to batch the updates to improve CrossMgr performance.

## Specification

Internally, CrossMgr runs a "little web server".  This is used to support the local web pages (live results, and the announcer page).
It isn't a general web server like Apache or nginx, and it servers dynamic content from memory.

The web server will accept RFID tags as follows:

	url:  http://192.168.2.125:8765/rfid.js		# use your path to the CrossMgr computer.
	POST: Content-Type="application/json"
	the json content is as follows:

	{
	data: [
			{ tag:"0123456789", t:"2011-11-04 19:05:23.283" },
			{ tag:"0123456781", t:"2011-11-04 19:05:23.683" },
			...
		]
	}

So, create a http message with your json data as POST.
Call the CrossMgr server with __rfid.js__ as the url.
The __data__ array can be one element at a time, or have many elements.

As usual, configure the CrossMgr Excel sheet linking the tags with the race participants.

The web server will also accept bib numbers as follows.  Note this uses the __bib.js__ url.

	url:  http://192.168.2.125:8765/bib.js		# use your path to the CrossMgr computer.
	POST: Content-Type="application/json"
	the json content is as follows:

	{
	data: [
			{ bib:134, t:"2011-11-04 10:05:23.283" },
			{ bib:156, t:"2011-11-04 10:05:23.683" },
			...
		]
	}

