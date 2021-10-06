[TOC]

# Quick Start
Welcome to __CrossMgrVideo!__

__CrossMgrVideo__ makes it easy to capture and analyze finish line video taken from inexpensive USB webcams.
Video can be triggered manually, or automatically by CrossMgr.

## Camera Compatability

__CrossMgrVideo__ should work with any USB camera that supports [MJPEG](https://en.wikipedia.org/wiki/Motion_JPEG).
MJPEG is a broadly supported by webcams, security cameras and other digital cameras.

The camera must be a USB camera that plugs in with a USB cable (the built-in camera in the computer works too).
__CrossMgrVideo__ does not currently support IP cameras, that is, cameras without a USB cable that are connected to the network via a cable or wifi.

## Overview

__CrossMgrVideo__ has two primary panes:

1. Images and Finish Strip (top)
2. Trigger List (middle of the bottom)

The __Images__ shows photos captured by triggers that can be played back like a movie, or moved frame-by-frame.
The __Finish Stip__ shows photos captured by triggers spread out by time.
Triggers are shown in the __Trigger List__.

A trigger event could be a race finish, a close finish, a points lap, or potentially a race indicent from a live feed.

__CrossMgr__ can automatically generate triggers for __CrossMgrVideo__ evey time a bib number is entered (can be RFID or manual entry).
Alternatively, you can generate triggers in __CrossMgrVideo__ manually with the __AUTO CAPTURE__ and __CAPTURE__ buttons.

### Typical Scenarios

#### Live Feed (example: Velodrome)
You have a live feed of an event.  You see "something" in real-time but want to check it in detail later for an infraction.

#### Conventional Finish Line
You want to check finishes quickly.  You are not using __CrossMgr__.

On each finish, press the __CAPTURE__ button until all the riders have passed.  Then use the __Finish Strip__ and __Photo Dialog__ (with Zoom) to check the finish order of the bib numbers.
Since each __CAPTURE__ is a trigger, it is easy to jump to different finishes.

#### Finish Line with CrossMgr
You have __CrossMgr__, but only want to check close finishes that RFID may not have gotten right.

Set the option in __CrossMgr__ to support a Camera (this can be done for every passing, or just the end of the race).
__CrossMgr__ will then send triggers to __CrossMgrVideo__.
Check the __Trigger List__ for close finishes marked in red and make corrections as necessary.

## Starting CrossMgr Video

When __CrossMgrVideo__ starts, you are prompted for the USB port and camera resolution.
Device 0 is usually the built-in camera, Device 1 is usually the first USB camera available.

You are also prompted for the resolution and frames per second of your camera (see the Reset Camera section for details).

## Main Screen

### Buttons on Top

#### Focus

Opens a big window suitable for focusing the camera.

#### Reset Camera

Allows the camera to be reset including the USB port as well as other parameters:

* __Camera USB__: The USB port of the camera.  CrossMgrVideo shows all the ports that have a camera connect to them.  Choose the port/camera you wish to use.  The computer's built-in camera (if present) is usually port 0.
* __Camera Resolution__:  The resolution of the camera to use.  Use MAXxMAX for maximum resolution.  Check your camera specs for details on which resolutions are supported - some cameras can only support lower frame rates at the highest resolutions.
* __Frames per second__:  The frames per second.  See notes below for more details.
* __FourCC__:  The image encoding.  For maximum performance, set this to MJPG (the default).  If your camera is the rare one that doesn't support MJPG, set it to blank.

__Notes:__

__Camera Resolution__ and __Frames per second__ often work like "hints" rather than specifications.

For example, if you set __Camera Resolution__ to a value that exceeds your cameras capabilities, it may use the highest resolution it has - not the one you set.
Similarly, of you set __Frames per second__ to an unsupported value (or a value unsupported at that resolution), your camera may use a fps lower than what you specified.

In low light conditions, some cameras drop their frame rate.  This allows for a higher exposure time per frame, however, it can also lead to out-of-focus objects.  If you camera drops the frame rate, consider additional lighting.

You can see the actual camera parameters and frames per second (fps) at the top of the screen.

#### Manage Database

Opens a dialog to manage the database including:

* File location and size of the database
* Deleting Triggers and Photos from the database
* "Vacuuming" the database to reduce the file size after deleting records.

Deleting items from the database will not reduce the file size.  However,
"holes" in the file will be reused by future database records.

To actually reduce the database size, select the "Vacuum" option.
Warning - this can take a few minutes.

#### Config Auto Capture

Opens a dialog to configure the how Auto Capture works.
When the __AUTO CAPTURE__ button is pressed (or when __CrossMgrVideo__ is externally triggerd by __CrossMGr__), video frames are captured as follows:

__Capture__:

* __by Seconds__:  specify the number of seconds before and after the trigger to capture (see below)
* __Closest Frame to Trigger__:  capture the closest video frame to the trigger
* __Closest 2 Frames to Trigger__:  capture the closest video two frames, before and after the trigger

If Capture is __by Seconds__:

* __Capture Seconds before Trigger__: seconds to capture before the trigger was pressed
* __Capture Seconds after Trigger__: seconds to capture after the trigger was pressed

For example, say __Capture Seconds before Trigger__=0.5 and __Capture Seconds after Trigger__=2.0 and the __AUTO CAPTURE__ button is pressed at 14:07:21.0.
__CrossMgrVideo__ will capture video from 14:07:20.5 to 14:07:22.

__CrossMgrVideo__ can capture video up to 10 seconds "in the past" because it keeps a 10-second buffer 

#### Snapshot

Takes a single snapshot and saves it to the database.

#### Auto Capture

Captures frames as specified by the __Auto Capture__ dialog described above.

#### Capture

Captures video frames as long as the __CAPTURE__ button is pressed.
Useful for capturing finishes.

Capture can also be triggered by a joystick.  Capture starts when the top joystick button is pressed and stops when it is released.

#### Images

##### Drag Zoom

Dragging a box in the photo will zoom in on the region of interest.
Useful for checking bib numbers, etc.

If you have a particular frame and zoom lined up, save it with __Save View__.
The View (frame and zoom) will be restored when you open the trigger again, or when you press __Restore View__.

##### Buttons

__Frame Control__

The frame time, and the +/- offset from the Trigger time is shown on the left.

* Jump to the trigger frame
* +1 frame.  Also controlled by the mouse wheel.
* -1 frame.  Also controlled by the mouse wheel.
* Rewind.  Jump to the first frame of the sequence.
* Play reverse.  Play the sequence in reverse.
* Stop.  Stop play.
* Play forward.  Play the sequence forward.
* Jump to end.  Jump to the last frame in the sequence.

* Print
* Copy to Clipboard
* Contrast - increases contrast in the photo
* Sharpen - increase sharpness of transitions
* Grayscale - removes color
* Save as PNG - save the photo in PNG format
* Save as MPG - save an mpg file of the entire clip
* Save as GIF - save an animated gif file.  Caution: these files can be large.
* Speed - a wizard that enables you to estimate the speed of a bicycle by analyzing how far the bicycle moved between two video frames.  This only works if the camera is at right angle to the finish line.
* Restore View - returns to the frame and zoom of this trigger.
* Save View - saves the frame and zoom of this trigger.

### Finish Strip

Shows all the frames recorded around the trigger event.

* Move the mouse across the Finish Strip to seen the current frame in the Zoom window.
* Shift-mouse-wheel to change magnification in the zoom window.
* Mouse-wheel, or use the Stretch slider to space the frames so that the objects between frames line up.
* Left-click and Drag (or Scroll Bar) to move sideways.
* Left-click move the current time line.

#### Buttons on Bottom

__Finish Direction__

Controls the direction of the Finish Strip.  Ensure that it matches the direction of the finishers.

### Panes on Bottom

#### Camera Window

Shows what the Camera is looking at.  For performance reasons, this has a slower frame rate than the camera itself.
It is important to look at the Camera window to ensure that the camera is still working and that it is still aligned.

To you have a manual lense and need to focus the camera, press the __Focus...__ button or click in the camera window.  This brings up a much larger window and allows you to see the camera image in much more detail.

#### Triggers

__Show Triggers for__

Sets the Date to show triggers.  Use the __Select Date__ feature to find dates in the past.  __Filter by Bib__ will find a particular bib number you are interested in on a particular date.

__Trigger Window__

Window containing the triggers.

* Left-click: shows the photos associated with the trigger.
* Right-click:  brings up an Edit... and Delete... menu.
* Double-click:  brings up the Edit window.  This allows you to change the Bib, First, Last, Team, Wave, Race and Note of the trigger.

Triggers can be created manually with __Snapshot__, __Auto Capture__, __Capture__ or when connected to CrossMgr, from CrossMgr entries.  CrossMgr can be configured to create a trigger for every entry, or just the last entry in the race (see CrossMgr help for details on the Camera setup).

__Publish Photos__

Publishes the photo closest to each Trigger time to a chosen folder.

__Photo Web Page__

Publishes the photo closest to each Trigger time to a chosen folder, but also creates an html page that can select each photo.  Once the photo is selected, it supports the same drag-and-drop Zoom capability of CrossMgrVideo.  Photos can be saved locally from the web page.

## Web Interface

CrossMgrVideo supports a web browser interface.  Anyone with a web browser can connect to CrossMgrVideo and do their own reviews of the video frames.

This feature is very powerful as it allows any number of people to review the same video.

For example, close finishes could be reviewed by the timer.
Or, officials can check the video to confirm violations.

### Connecting

Make sure the CrossMgrVideo is on a local network (could be a local wifi router, or a hotspot).

In CrossMgrVideo, press the __Web Page__ button.  This will launch the CrossMgrVideo web page in your local browser.

The web page is live connected to CrossMgrVideo on your computer in your browser.

To make it available on other computers or tablet on the same wifi network, press the __QRCode__ button on the right of the screen.

This page shows the QR code which can be used by tablets and smartphones to also connect to CrossMgrVideo.
You can also connect another computer to CrossMgrVideo by entering the url address at the bottom of the QRCode page.

### Triggers Tab

The triggers tab shows all the triggers for the selected day.
Click on the trigger you are interested in.
This will automatically switch to the Images tab.

### Images Tab

This screen is similar to the CrossMgrVideo images screen and allows you all the same control over the images, on-screen zooming, image filtering and the ability to Save and Restore views.
Saving a view makes it available to other web users and CrossMgrVideo.

When the Images tab is display, it defaults to showing the Saved view for the trigger.  If there is no saved view, it shows the closest frame to the trigger time.

Saving and Restoring views is a very powerful capability.  One person can set up the best frame and magnification that shows the issue.  Then, another person can open the same Trigger and see the exact same view - even if their device is different (eg. tablet) with different screen resolution.

Views are updated in the database immediately and can be seen by other users when Images screen is selected again, or when the __Restore View__ button is pressed.

### Form Tab

From this screen you can update any of the Trigger information (Bib, First, Last, Notes, etc.).  Use this to edit details about the trigger or the incident.

Like views, trigger information is stored in the database and can be seen after a __Restore View__.
