
[TOC]

# Camera

CrossMgr can use a USB camera to take photos of riders as they cross the finish line.
This is especially effective when using an RFID reader.

CrossMgr will use the timestamp provided by the RFID to take photos automatically.  A header is added to the photos with the rider's name and team, as well as the race time and time-of-day.  The photos are then stored with logical filenames making them easy to retrieve.

Photos are instantly accessible right from CrossMgr.  One convenient method is the Chart screen.  Laps with photos are shown with a camera icon.  Right-clicking on the bar allows you to bring up the picture.

When photos are triggered by the RFID reader, and two riders are recorded within the video buffer frame rate, a second photo is recorded.  This gives more information for close finishes.

Technical wizardry solves the problem of latency between the RFID reader and triggering the camera.  Photos are synchronized to show the athletes as they cross the finish line.

## Test USB Camera...

Opens a window that shows what the USB Camera is looking at.  Useful for positioning the USB camera on the finish line before a race.
The USB Camera cannot be tested while the race is running.
