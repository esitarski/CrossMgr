![](https://github.com/mbuckaway/CrossMgr/workflows/CrossMgr_Build/badge.svg)

# Cross Manager Race Scoring Software

Welcome to Cross Manager. Cross Manager is software used to score bike races. It has many features including support for RFID chip readers. Full documentation is in the CrossMgrHtml directory or under Help in the application.

## User Installation

As a user, you can install CrossManager on Windows, Mac OSX, and Linux. Only x86 64 bit platforms are supported. Cross has gone through many iterations. Previous versions require Mac and Linux users to install Python, the source code, and fight with it to get it working. This is no longer the case. As with the Windows version, the MacOSX and Linux versions are available as binary releases. The MacOSX and Linux versions are built on github as a release automatically when the code changes.

### Windows Installation

Download the CrossManager-Install.exe and run it. This will setup Cross Manager on your system, and add an icon to your desktop. Additional utilities such as CrossMgrImpinj are required to connect to a RFID reader.

### Mac OSX Installation

Download the CrossMgr-VERSION.dmg file. From the finder, double click the DMG file to open it. Ones the window comes up, you simply drag and drop the CrossManager.app and CrossManager-Impinj.app folders to your Applications directory. From the Applications folder, you can now run CrossManager like any other Mac app. Most recent Mac OSX versions will require you to press CTRL before clicking on the app for the first time, and then clicking open. The app is a non-signed program that MacOSX will not open otherwise. This is only require the first time you run it. MacOSX will also ask a few questions when the program is run, and you must confirm with YES (Allow Networking, Access to Documents Directory, etc, etc.)

CrossMgrImpinj and TagReadWriter follow the same install process.

### Linux Installation

Download the CrossMgr-VERSION.AppImage file. Store this file in a convenient location such as $HOME/bin. Make the executable with

```bash
chmod 755 CrossMgr-VERSION.AppImage
```

Next, just run the AppImage with:

```bash
./CrossMgr-VERSION.AppImage
```

...from the command prompt.

CrossMgrImpinj and TagReadWriter follow the same install process.

Alternative, setup a desktop icon to call it directly.

## Building Cross Manager

There are two scripts to build CrossMgr and the associated tools. One for Linux and Mac and one for Windows. Each platform has a build script to install the dependancies, build the binaries for the application, and package the programs.

| Script  | Purpose |
|---------|---------|
| compile.sh | Install dependancies, build CrossMgr and CrossMgrImpinj as Mac DMG file images |
| compile.bat | Old Windows build script |

Windows builds require InnoSetup from [https://www.jrsoftware.org/isdl.php].

Mac and Linux builds currently support Python 3.7.x. Python 3.8 thus far has cause build errors with pyinstaller. The build has been automated, and releases are built on github when the code changes. Releases are created by creating a release tag in the repo. All required operations are done through the compile.sh script on Mac/Linux.

Linux dependancies are contained in the linuxdeps.sh script. The linuxdeploy-plugin-appimage-x86_64.AppImage binary is required from https://github.com/linuxdeploy/linuxdeploy-plugin-appimage. The compile.sh script will download linuxdeploy-plugin-appimage if it does not exist in the current directory automatically.

The build procedure for Linux and MacOSX platforms are as follows:

- Install the Linux dependancies (Linux only!)

```bash
  bash linuxdeps.h
```

- Setup a virtual env, download the required python modules:

```bash
bash compile.sh -S
```

- Build all the code and publish to releases directory

```bash
bash compile.sh -a -A
```

When the build is complete, the resultant DMG files will be in the release directory. The above process is what the build.yml Workflow (.github/workflows/build.yaml) uses to build the code.

The build procedure for windows currently is a manual process:

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

- Build the code and installer

```powershell
python3 CrossMgrSetup.py
```

The requirements.txt has all modules required to build and run CrossManager. CrossMgrSetup.py currently assumes you have a Google Drive configured to publish the code. This will be fixed in the future.

