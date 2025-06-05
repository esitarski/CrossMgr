![](https://github.com/esitarski/CrossMgr/workflows/DevelopmentBuild/badge.svg)
![](https://github.com/esitarski/CrossMgr/workflows/ReleaseBuild/badge.svg)

# Cross Manager Race Scoring Software

Welcome to Cross Manager! Cross Manager is software used to score bike races. It has many features including support for RFID chip readers. Full documentation is in the CrossMgrHtml directory or under Help in the application.

In addition to the application help files, there is a tutorial for CrossMgr [here](/https://github.com/esitarski/CrossMgr/blob/master/CrossMgrTutorial.docx)
and an explanation of an RFID implementation using CrossMgrImpinj [here](https://github.com/esitarski/CrossMgr/blob/master/CrossMgrImpinj/CrossMgrImpinjReadme.docx).

The software consists of a set of executables.  For Cyclocross, MTB CX, TimeTrial, Road and Criterium races, you will need:

* CrossMgr for mass-start races and TT.
* CrossMgrImpinj or CrossMgrAlien if you plan to use an RFID reader.
* SeriesMgr if you plan to score a series of races.
* TagReadWrite create your own tags.
* CallupSeedingMgr to create callups using multiple criteria.

If you are scoring Track races you will need:

* PointsRaceMgr - for scoring races with intermediate sprints and Laps gained/lost.
* SprintMgr - for Track sprint races as well as MTB (4x, eliminator, etc.)

CrossMgr was designed to work with [RaceDB](https://github.com/esitarski/RaceDB), a web-based database for competition management and race check-in.
RaceDB handles race check-in including issue bib numbers and creating RFID tags on-the-fly.  This eliminates most sources of administration error (missing/non-working/wrong RFID tag).
Additionally, RaceDB supports a self-serve kiosk feature that allows riders to check-in with their tags automatically.

## System Requirements

All applications are written in Python and compiled into machine code. Builds are made available for Windows and MacOSX. In order to publish results, an internet connection is required.

The minimum system requires are as follows:

### Windows

- Windows 11 x64
- 4G RAM
- 10G HD space

### MacOSX

- Apple MacOSX 10.10 or better
- 4G RAM
- 10G HD space

### Linux

- ubuntu (and flavors) or centos, debian, fedora, rocky on x64
- 4G RAM
- 10G HD space

## User Installation

As a user, you can install the CrossManager applications on Windows, Mac OSX, and Linux. Only x86 64 bit platforms are supported. The Windows and MacOSX versions are available as binary releases.
See the Releases tab in the github repo for binaries.

You can still run on Linux too, but you have to use the install script (more on that later).

### Windows Installation

From the Releases tab, download the CrossMgr_x64_VERSION.exe file. Run the file and follow the on screen instructions.

When running the installer, Windows will likely complain that it is a unknown publish. Click the MORE INFORMATION link in that dialog, and then click the RUN ANYWAYS button. The install will proceed.

CrossMgrImpinj, TagReadWriter, CrossMgrAlien, CrossMgrVideo, SeriesMgr, PointsRaceMgr and SprintMgr follow the same install process. They will all install into the CrossMgr program group.

### Mac OSX Installation

From the Releases tab, download the CrossMgr-VERSION.dmg file. From the finder, double click the DMG file to open it. Once the window comes up, you simply drag and drop the CrossMgr.app folder to your Applications directory. From the Applications folder, you can now run CrossMgr like any other Mac app

If you still get a message that the dmg file is damaged and to delete it, you will need to temporarily disable GateKeeper to complete the install.  To do so, open a Terminal and enter:

    sudo spctl --master-disable
    
Then, double-click on the CrossMgr .dmg file.

Re-enable GateKeeper from the terminal as follows:

    sudo spctl --master-enable

Some Mac OSX versions accept pressing CTRL before clicking on the app for the first time, and then clicking open.
The app is non-signed and MacOSX may not open it otherwise.
This is only required the first time you run it. MacOSX will also ask a few questions when the program is run, and you must confirm with YES (Allow Networking, Access to Documents Directory, etc, etc.)

CrossMgrImpinj, TagReadWriter, CrossMgrAlien, CrossMgrVideo, SeriesMgr, PointsRaceMgr and SprintMgr follow the same install process.

## Installation with the CrossMgr Install Script

Windows and Mac have become increasingly difficult to deal with due to virus checkers incorrectly flagging CrossMgr installs as containing a virus.
And, it is difficult to create a standard install for Linux due to all its flavors and variants.

To address this problem, there is now a cross-platform install which solves many of these problems.

To clear the air about viruses, all CrossMgr installs are submitted to [VirusTotal](https://www.virustotal.com/gui/home/upload).  VirusTotal runs 70 virus checkers and logs the result in a public database.
Regardless, Windows and Mac virus checkers often flag CrossMgr installs as suspicious (this stops sometimes after a sufficient number of installs).
The Mac's GateKeeper is the worst offender as it falsely claims that the .dmg file is damaged and should be deleted.  Yikes!

`rant`
I get that Microsoft and Apple want all installs from their online store, but these policies don't serve the open-source community well where there isn't enough money to pay the fees.
Posting to the Apple online store also requires a submitting and approval process for every version (costly, with delays).
Microsoft has [winget](https://winget.run/), but it isn't available for Mac or Linux.
And overall, I don't have the time to maintain and test separate release mechanisms for each platform.
If anyone has any suggestions, please let me know.
`/rant`

To install from the script:

1. Make sure you have an internet connection.
1. On Windows and Mac only, install Python onto your machine from [here](https://www.python.org/) if you don't currently have it.  If presented with an option to add Python to your PATH, choose Yes.  You only need to install Python once.  Python is the computer language CrossMgr is written in.  Skip this step on Linux as Python is already installed.
1. Download [crossmgr-install.py](https://github.com/esitarski/CrossMgr/blob/master/crossmgr-install.py) and save it into a folder on your machine.  You only need to do this once.
1. Open a terminal and "cd" to the directory you downloaded crossmgr-install.py
1. In the terminal, enter:  __python3 crossmgr-install.py install__
1. Wait a few minutes while the install pulls the latest release from github, updates the Python env, and creates the desktop shortcuts.  You can now launch the CrossMgr apps from the desktop shortcuts.
1. To use the shortcuts on Linux, right-click on them and select "Allow Launching".  You only need to do this once.
1. You can associate file types with CrossMgr apps on Windows.  For example, to launch CrossMgr when you double-click on .cmn files, click on a .cmn file, then set __~/CrossMgr-master/bin/CrossMgr.ps1__ as the app to use to open it (~ is your home directory).  Similar for Mac, but the app name ends in .sh.

After the install completes, there is an __Update CrossMgr__ shortcut on your desktop.
This is all you need to run to update CrossMgr going forward - you don't have to spend time finding the latest CrossMgr release.

None of the CrossMgr apps require an internet connection to run.

The script also supports __uninstall__ and __restore__ commands which allow you to remove all CrossMgr apps, or to revert back to the last version you installed, respectively.

There are a number of application in the CrossMgr suite, but as you work more races, you need many of them, especially CrossMgr (mass start and TT), SeriesMgr (for series) CrossMgr Impinj (for RFID), TagReadWrite (to make RFID tags)
and CallupSeedingMgr (if you have callups for high-level events for MTB and CX).

In addition to being faster and more convenient, the script requires much less disk space as each app reuses the Python runtime, rather than bundling in each .exe or .dmg file.

If you are running with a .exe (Windows) or .dmg (Mac) install, you should uninstall all the apps first before switching to the script method.

I investigated a number of ways to solve this problem (containers, python setup, nuitka as well as the existing solution).
However, nuitka takes an hour to compile, downloading an .exe or .dmg is out anuyway, containers are at least as complicated to install as Python, and python setup does not deal with resource and data files well (not to mention shortcuts, etc.).

This solution requires the extra step to install Python, but on the whole, I think this effort is worth it.
Perhaps there will be a better way to solve this in the future (for example, on Windows, install it automatically with winget).
Suggestions are welcome.

## Building Cross Manager (for developers)

There are two scripts to build CrossMgr and the associated tools. One for Linux/Mac and one for Windows
Each platform has a build script to install the dependancies, build the binaries for the application, and package the programs.

| Script  | Help Parameter |Purpose |
|---------|---------|--------|
| compile.sh | -h | Linux/MacOSX Build script |
| compile.ps1 | -help | Windows build script |

Use the help parameter to find the available command line options. You can build programs individual or run parts of the build process individual using different command line options.

All platforms currently work with Python 3.7.x. Python 3.8 and newer is not yet supported by pyinstaller which freezes the python code to binary form.

Windows builds require [InnoSetup V6.x](https://www.jrsoftware.org/isdl.php). If you do not have Inno Setup installed, the windows build will fail.

The build has been automated, and compile.sh/ps1 script does everything to enable the developer to build CrossMgr and the associated tools. However, you can also download the binary from the github Releases tab.

Linux dependancies are contained in the linuxdeps.sh script.

The build procedure for Linux and MacOSX platforms are as follows:

- Install the Linux dependancies (Linux only!)

```bash
  bash linuxdeps.sh
```

- Setup a virtual env, download the required python modules:

```bash
bash compile.sh -S
```

- Build all the code and publish to releases directory

```bash
bash compile.sh -a -A
```

When the build is complete, the resultant DMG/AppImage files will be in the release directory. The above process is what the build.yml Workflow file (.github/workflows/build.yaml) uses to build the code on GitHub.

The build procedure for windows are as follows:

- Setup a virtual env, download the required python modules:

```powershell
.\compile.ps1 -setupenv
```

- Build all the code and publish to releases directory

```powershell
.\compile.ps1 -all -everything
```
When the build is complete, the resultant exe installer files will be in the release directory. The above process is what the build.yml Workflow file (.github/workflows/devbuild.yaml) uses to build the code on GitHub.

### Making a Release

By default, the version of the programs is setup with -private in the name to indicate any local builds are alpha versions and not meant for distribution. Any local builds will receive this version number tag and it will be displays on startup and in the About dialog. Updating the version number for any one of the applications requires that this private tag remain intacted, or the build will fail on github. The private tag is replaced with the appropriate version by the build script on github on a development or release build.

With the workflow setup on Github, builds are automatic. Development is a two stream or branch system. The dev branch is where all development work occurs. Developers are encouraged to branch dev into feature and bugfix branches to do actual work, and then merge changes back into dev. Changes to the dev branch pushed to github are automatically built as a "Development Release" under the 'latest' tag. Only one development release is available at any one time. The purpose of the development release is to allow for beta testing of new code before it is released. The version number of all applications will be denoted with "beta" and the git short release number to ensure users can report issues against a specific version.

When code is complete, and ready for a production release, the code is merged back into master, and tagged with a semver style tag. The tag format must be in the format v3.0.0-2020010101010. The tag number is used to create the version number for each application. The build is setup to reject building a release where the tag is not this format. Developers should use the compile script to create the release to ensure a proper merge and tag is created. The build system automatically creates a release build on github when the tag is detected and places the binaries in the Releases tab on github.

Every time a build is run, github will build the code. The purpose of this build is to ensure the code will build on all platforms. When a release is added, it will appear in the releases tab, and github will run the workflow to build the code for MacOSX, Linux, and Windows.

To make a release, do the following:

Linux/Mac:

```bash
bash compile.sh -r
```

Windows:

```powershell
.\compile.ps1 -release
```

You must be on the dev branch without any pending changes to make a release. If the version number of an application is to be incremented, it should be done in the dev branch, and checked in prior to making the release.

A build can also be forced by tagging the master branch.  This is done with the -T option (Linux/Mac) and -tag (windows). You can only tag the master branch with this option.

