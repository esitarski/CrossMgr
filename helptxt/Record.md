[TOC]

# Record
The Record screen allows you to manual enter numbers.
It also support a number of real-time displays showing important details about the course.

# Screen
The screen is roughly divided into four parts:

1. [Number Entry](#number-entry)
1. [Race Information](#race-information)
1. [Riders on Course](#riders-on-course)
1. [Race Lap Chart](#race-lap-chart)

## Number Entry

This is the section of the screen where data is entered manually.  Data from chip timing flows into CrossMgr directly.

CrossMgr offers two "modes" to manually enter data: __Keypad__ and __Time Trial__.
The different modes are switched by a pressing button at the top left of the screen which either shows a Keypad or a Stopwatch, depending on the mode you will switch to.

In Keypad mode, the number is timestamped when you press Enter.

In Time Trial mode, you can get accurate times first, then add the bib numbers afterwards.

Each approach has pros and cons, and you can switch modes at any time.  Generally speaking you will use the modes for:

Race Format|Input Mode
:----------|:---------
Cyclo Cross|Keypad
MTB|Keypad
Road|Keypad
Time Trial|Time Trial
Downhill|Time Trial

### Keypad Number Entry Mode

When you enter a number in this mode, the number is "timestamped" when you press __Enter__ (or __Tab__ or __Space__).  This is the standard input mode for Road, Cyclo Cross and MTB races when you have number caller, and riders arrive in quick succession on their laps.

When you hear the number caller, you type in the number on the keyboard and press __Enter__ (or __Tab__ or __Space__, whichever is most comvenient).
After the first lap of a race, CrossMgr will predict the arrival of each rider in the [Expected](MainScreen.html#expected) window.  To enter the number again, you can just click on th number in the __Expcted__ list rather than typing it in again.

Entering a number also triggers the [USB Webcam][] if it has been enabled.

You can enter data through the regular computer keyboard or an external numeric keypad.  If you have a touchscreen, you can also enter data by pressing the on-screen buttons.  To enable touchscreen mode, press on the touchscreen button.  This will toggle an on-screen keypad.

CrossMgr understands common leading digits and does not require that the full number of digits be entered if the leading digits are all the same.  For example, say you have one number range 100-199.  You can enter the following:

* 0 --> 100
* 1 --> 101
* 10 --> 110
* 150 --> 150 (three digits are always OK).

That is, common leading digits will automatically be added, and you don't need to type them.

CrossMgr only checks for leading digits, and it is not all-knowing.  For example, if you have ranges 100-120 and 250-270, CrossMgr is not smart enough to know that the last two digits are always unique.  In this case, all three digits will be required.

And of course, if there aren't common leading digits in all categories across the entire race, you will need to enter the entire digits.

Experience has shown that a touch-screen is less accurate.  Additionally, touch screens can get sluggish in cold or hot weather.  This is frustrating in a race situation when you are trying to enter a number and the touchscreen doesn't respond.  Use a keyboard or external keypad for reliability.

Pressing Esc, 'c' or 'C' will clear the input.  This can be a handy shortcut when you need to re-enter a number.

Tip: the most accurate way to enter numbers is to type in the number when you hear the number caller, then press an __Enter__ key just as the rider crosses the line.  This is primarily important in timetrials.  In bunch races, the objective is to get the passing order as the times are far less important.  When groups pass in bunch races, just enter the numbers as you hear them from the number caller.

You can also enter multiple numbers separated by commas on the same line.  When you press an __Enter__ key, all the numbers be entered with exactly the same time.  This is useful for starting a team time trial, when youj want all riders on the team to get exactly the same start time.

There are a number of additional buttons:

Button|Description
:-----|:----------
DNF|Enter the rider as a DNF, and uses the current time as the DNF time.
DNS|Enter the rider as a DNS.
Pull|Enters the rider as PUL, and uses the current time as the PUL time.
DQ|Enters the rider as DQ, and uses the current time as the DQ time.

Remember: if you change any rider's status here, you can always change it back again from the [RiderDetail][] screen.

### Time Trial Entry Mode

This is the standard input mode for time trial finishes.  It follows a similar process to a manual stopwatch, except you use the computer.

In time trial mode, you get times as the riders pass by pressing the __Tap for Time__ button (similar to using a recording stopwatch).  This also triggers the [USB Webcam][] to take a picture, if enabled.  Rather then using the mouse, pressing the 't' key is a shortcut to __Tap for Time__.

You then enter the Bib numbers next to the times - you many not be able to see the number on the back of the rider until he/she has passed.

When you have entered the corresponding bib numbers for the times, press the __Save__ button.  This saves the input and clears the display for the next arrival(s).  Rather than using the mouse, pressing the 's' key is a shortcut to __Save__.

Press __Save__ as soon as you can.  This records the entry in CrossMgr.
Normally, you would __Tap for Time__ once, then enter the Bib for that time, then press __Save__.  One entry at a time.

It is important to get comfortable with doing this on the keyboard alone as it will save a __lot__ of mousing.  Consider using your left hand to operate the 't' and 's' keys, and your right hand to enter bib numbers from a numeric keypad.

Sometimes, 3-4 riders will bunch up at the finish.  In this case, press __Tap for Time__ for each each rider, enter the Bib for each rider, then press __Save__.

CrossMgr gives you up a number of entries before you must press Save.  If you see large groups of riders finishing together, they are drafting, which is not permitted.

If you cannot read a rider's number, and can't find it in time, enter an invalid, but unique temporary Bib number for the rider, say 8000.
After the race you can correct the number, but retain the correct time.  This is an exceptional process.

__Shortcut Key Summary__

Shortcut Key|Description
:-------|:----------
t|Equivalent to pressing the __Tap for Time__ button.
s|Equivalent to pressing the __Save__ button.

Warning: The Time Trial input mode only works when there are start gaps between the riders.  If you have a timed mass single-start event, you may need Keypad mode, or alternatively, consider a [ChipReader][].

## Race Information

Field|Description
:----|:----------
Race Time|The time since the race started.
Manual/Automatic Start|The time the race was started.  Start can be triggered by RFID depending on option.
Last Rider on Course|The est. finish time of the last rider on course.  Includes name, team and category.  Projected lapped and pulled riders are taken into account.  The Last Rider on Course may have nothing to do with the last rider in the race if riders are lapped.
Photo Count and Camera Button|Shows the photo count and camera button if the [USB Webcam][] is enabled.  Pressing the camera button brings up the last picture taken in the race.
Clock|The current time of day.

## Riders on Course

This display shows the total riders on course, a breakdown of the riders by category, and a count of which riders are on each lap.

## Race Lap Chart

This display shows graphically, by Category:

* the total number of laps in the race, and the laps to go
* the Category leader's number
* a Progress bar as showing where the leader is in the race
* a Timer counting down to when the leader is next expected
* the projected Finish Time of the race (finish line flag)
* the projected Expected Time of the last rider on course (broom)

Use this display to manage lap counters by category.  It allows you to easily see what lap each category is on, when to ring the last lap bell, etc.

For additional information, move the mouse over the lap.  This will show more start/end times and lap time.
