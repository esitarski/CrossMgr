# Cross Manager Race Scoring Software

Welcome to Cross Manager. Cross Manager is software used to score bike races. It has many features including support for RFID chip readers. Full documentation is in the CrossMgrHtml directory or under Help in the application.

## User Installation

As a user, you can install CrossManager on Windows, Mac OSX, and Linux. Only x86 64 bit platforms are supported. Cross has gone through many iterations. Previous versions require Mac and Linux users to install Python, the source code, and fight with it to get it working. This is no longer the case. As with the Windows version, the MacOSX and Linux versions are available as binary releases.

### Windows Installation

Download the CrossManager-Install.exe and run it. This will setup Cross Manager on your system, and add an icon to your desktop. Additional utilities such as CrossMgrImpinj are required to connect to a RFID reader.

### Mac OSX Installation

Download the CrossManager-VERSION.dmg file. From the finder, double click the DMG file to open it. Ones the window comes up, you simply drag and drop the CrossManager.app and CrossManager-Impinj.app folders to your Applications directory. From the Applications folder, you can now run CrossManager like any other Mac app. Most recent Mac OSX versions will require you to press CTRL before clicking on the app for the first time, and then clicking open. The app is a non-signed program that MacOSX will not open otherwise. This is only require the first time you run it.

### Linux Installation

Download the CrossManager-VERSION.AppImage file. Store this file in a convenient location such as $HOME/bin. Make the executable with

```bash
chmod 755 CrossManager-VERSION.AppImage
```

Next, just run the AppImage with:

```bash
./CrossManager-VERSION.AppImage
```

...from the command prompt.

Alternative, setup a desktop icon to call it directly.


