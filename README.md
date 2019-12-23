![](https://github.com/mbuckaway/CrossMgr/workflows/Build%20MacOSX/badge.svg)
![](https://github.com/mbuckaway/CrossMgr/workflows/Build%20Linux/badge.svg)

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

## Building Cross Manager

Each platform has a build script to install the dependancies, build the binaries for the application, and package the programs.

| Script  | Purpose |
|---------|---------|
| compile-mac-all.sh | Install dependancies, build CrossMgr and CrossMgrImpinj as Mac DMG file images |
| compile-mac.sh | Build CrossMgr as Mac DMG file images |
| CrossMgrImpinj/compile-mac.sh | Build CrossMgrImping as Mac DMG file images |
| compile-linux-all.sh | Install dependancies, build CrossMgr and CrossMgrImpinj as Linux AppImage file images |
| compile-linux.sh | Build CrossMgr as Linux AppImage file images |
| CrossMgrImpinj/compile-Linux.sh | Build CrossMgrImping as Linux AppImage file images |
| compile.bat | Old Windows build script |

Windows builds require InnoSetup from [https://www.jrsoftware.org/isdl.php].

Mac builds currently require a virtualenv using python 3.7 in order to build the package. Changes to pyinstaller are required to make it work with python 3.7. The compile-mac-all.sh script sets up the virtualenv before it starts. No special programs are required to build the mac app as the mac app directory is build "by hand".

The Linux build requires the libpython3.8-dev package (Ubuntu) and the linuxdeploy-plugin-appimage-x86_64.AppImage binary from https://github.com/linuxdeploy/linuxdeploy-plugin-appimage. The compile-linux-all.sh will attempt to download https://github.com/linuxdeploy/linuxdeploy-plugin-appimage if it does not exist in the current directory.

The build procedure for all platforms starts as follows:

- Setup a virtual env and activate:

Linux:
```bash
  virtualenv env
  . env/bin/activate
```

MacOSX:
```bash
  virtualenv -p python3.7 env
  . env/bin/activate
```

MacOSX requires Python3.7 as Python 3.8.1 does not support pyinstaller.

Windows:
```cmd
  virtualenv env
  env\scripts\activate.cmd
```
or

```powershell
  virtualenv env
  env\scripts\activate.ps
```

DO NOT SETUP CROSS MANAGER OUTSIDE OF A VIRTUAL ENVIRONMENT AS CONFLICTS CAN ARRISE.

- Run pip to install the requirements:

```bash
pip3 install -r requirements.txt
```

The requirements.txt has all modules required to build and run CrossManager.




   
