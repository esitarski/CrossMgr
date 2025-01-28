#!/bin/bash

OSNAME=$(uname -s)
PYTHONVER=python3.10
ENVDIR=env
LINUXDEPLOY=linuxdeploy-plugin-appimage-x86_64.AppImage

if [ "$OSNAME" == "Darwin" ]; then
	PYTHONVER="python3"
fi
if [ "$OSNAME" == "Linux" ]; then
	PYTHONVER="python3"
fi

getBuildDir() {
	PROGRAM=$1
	BUILDDIR=.
	if [ "$PROGRAM" != "CrossMgr" ]; then
		BUILDDIR=$PROGRAM
	fi
}

checkEnvActive() {
	if [ -z "$VIRTUAL_ENV" -a -d $ENVDIR ]; then
        . $ENVDIR/bin/activate
        echo "Virtual env ($VIRTUAL_ENV) activated"
    elif [ -n "$VIRTUAL_ENV" ]; then
        echo "Using existing environment ($VIRTUAL_ENV)"
    else
        echo "Python environment not active. Aborting..."
        exit 1
    fi
}

goBack() {
	PROGRAM=$1
	if [ "$PROGRAM" != "CrossMgr" ]; then
		cd ..
	fi
}

doPyInstaller() {
	PROGRAM=$1
	getBuildDir $PROGRAM
    checkEnvActive
	ICONPATH=${PROGRAM}Images/
	DISTPATH=dist
	BUILDPATH=build
	if [ "$PROGRAM" != "CrossMgr" ]; then
		DISTPATH=../dist
		BUILDPATH=../build
	fi
	case $OSNAME in
		Darwin)	echo pyinstaller ${PROGRAM}.pyw --icon=${ICONPATH}/${PROGRAM}.icns --distpath=$DISTPATH -p . --workpath=$BUILDPATH --clean --windowed --noconfirm --exclude-module=tcl --exclude-module=tk --exclude-module=Tkinter --exclude-module=_tkinter --osx-bundle-identifier=com.esitarsk.crossmgr
			cd $BUILDDIR
			pyinstaller ${PROGRAM}.pyw --icon=${ICONPATH}/${PROGRAM}.icns --distpath=$DISTPATH -p . --workpath=$BUILDPATH --clean --windowed --noconfirm --exclude-module=tcl --exclude-module=tk --exclude-module=Tkinter --exclude-module=_tkinter --osx-bundle-identifier=com.esitarsk.crossmgr
			if [ $? -ne 0 ]; then
				goBack $PROGRAM
				echo "Build Failed!"
				exit 1
			fi
			goBack $PROGRAM
		;;
		Linux) echo pyinstaller ${PROGRAM}.pyw --icon=${ICONPATH}/${PROGRAM}.png --distpath=$DISTPATH -p . --workpath=$BUILDPATH --clean --windowed --noconfirm --exclude-module=tcl --exclude-module=tk --exclude-module=Tkinter --exclude-module=_tkinter --osx-bundle-identifier=com.esitarsk.crossmgr
			cd $BUILDDIR
			pyinstaller ${PROGRAM}.pyw --icon=${ICONPATH}/${PROGRAM}.png --distpath=$DISTPATH -p . --workpath=$BUILDPATH --clean --windowed --noconfirm --exclude-module=tcl --exclude-module=tk --exclude-module=Tkinter --exclude-module=_tkinter --osx-bundle-identifier=com.esitarsk.crossmgr
			if [ $? -ne 0 ]; then
				goBack $PROGRAM
				echo "Build Failed!"
				exit 1
			fi
			goBack $PROGRAM
		;;
		*) echo "Unknown OS."
		exit
		;;
	esac
}

getVersion() {
	PROGRAM=$1
	getBuildDir $PROGRAM
	if [ ! -f "${BUILDDIR}/Version.py" ]; then
		echo "No version file in ${BUILDDIR}/Version.py. Aborting..."
		exit 1
	fi
	. ${BUILDDIR}/Version.py
	VERSION=$(echo $AppVerName | awk '{print $2}')
	export VERSION
	echo "$PROGRAM Version is $VERSION"
}

cleanup() {
	echo "Cleaning up everything..."
	rm -rf __pycache__ CrossMgrImpinj/__pycache__ CrossMgrVideo/__pycache__ SprintMgr/__pycache__ PointsRaceMgr/__pycache__ TagReadWrite/__pycache__ CrossMgrAlien/__pycache__ SeriesMgr/__pycache__
	rm -rf dist build release
	rm -f *.spec
}

downloadAppImage() {
	if [ "$OSNAME" == "Linux" ]; then
		if [ -f $LINUXDEPLOY ]; then
			echo "$LINUXDEPLOY already installed"
		else
			wget -v https://github.com/linuxdeploy/linuxdeploy-plugin-appimage/releases/download/continuous/$LINUXDEPLOY
			chmod 755 $LINUXDEPLOY
		fi
	else
		echo "AppImage builder not required for $OSNAME"
	fi
}

compileCode() {
    fixDependencies
    
	PROGRAM=$1
	getBuildDir $PROGRAM
    checkEnvActive
    
	echo "Compiling code"
	python3 -mcompileall -l $BUILDDIR
	if [ $? -ne 0 ]; then
		echo "Compile failed. Aborting..."
		exit 1
	fi
}

buildLocale() {
	echo "buildLocale: Building .mo files from .po locale files ..."
	python3 po_to_mo.py
}

buildHelp() {
	PROGRAM=$1
	
	cd "$PROGRAM"
	
	if [ -f "buildhelp.py" ]; then	
		if [ -d "$PROGRAM"HelpIndex ]; then
			rm -rf "$PROGRAM"HelpIndex
		fi
		echo "buildHelp: Building Help for $PROGRAM ..."
		python3 buildhelp.py
		if [ $? -ne 0 ]; then
			echo "buildHelp: Building help failed. Aborting..."
			cd ..
			exit 1
		fi
	fi
	
	cd ..
}

copyAssets() {
	PROGRAM=$1
	getBuildDir $PROGRAM

	if [ "$OSNAME" == "Darwin" ]; then
		RESOURCEDIR="dist/${PROGRAM}.app/Contents/Resources/"
	else
		RESOURCEDIR="dist/${PROGRAM}/usr/bin/"
	fi
	mkdir -p $RESOURCEDIR
	if [ "$OSNAME" == "Linux" ]; then
                mv dist/${PROGRAM}/* $RESOURCEDIR
                cp -v "${BUILDDIR}/${PROGRAM}Images/${PROGRAM}.png" "dist/${PROGRAM}"
		echo "Setting up AppImage in dist/${PROGRAM}"
		sed "s/%PROGRAM%/$PROGRAM/g" appimage/AppRun.tmpl > "dist/${PROGRAM}/AppRun"
		chmod 755 "dist/${PROGRAM}/AppRun"
		sed "s/%PROGRAM%/$PROGRAM/g" appimage/template.desktop > "dist/${PROGRAM}/${PROGRAM}.desktop"
	fi
	if [ -d "${BUILDDIR}/${PROGRAM}Images" ]; then
		echo "Copying Images to $RESOURCEDIR"
		cp -rv "${BUILDDIR}/${PROGRAM}Images" $RESOURCEDIR
	fi
	if [ -d "${BUILDDIR}/${PROGRAM}Html" ]; then
		echo "Copying Html to $RESOURCEDIR"
		cp -rv "${BUILDDIR}/${PROGRAM}Html" $RESOURCEDIR
	fi
	if [ -d "${BUILDDIR}/${PROGRAM}Locale" ]; then
		buildLocale $PROGRAM
		echo "Copying Locale to $RESOURCEDIR"
		cp -rv "${BUILDDIR}/${PROGRAM}Locale" $RESOURCEDIR
	fi

	# Build help files and indexes.
	if [ "$PROGRAM" == "CrossMgr" ]; then
		if [ -d CrossMgrHelpIndex ]; then
			rm -rf CrossMgrHelpIndex
		fi
		echo "mainline: Building Help for CrossMgr ..."
		python3 buildhelp.py
		if [ $? -ne 0 ]; then
			echo "mainline: Building help failed. Aborting..."
			exit 1
		fi
		cp -rv CrossMgrHelpIndex $RESOURCEDIR
	else
		buildHelp $PROGRAM
	fi
	

	# Copy help files last to wait for them to be built by now.
	if [ -d "${BUILDDIR}/${PROGRAM}HtmlDoc" ]; then
		echo "Copying HtmlDoc to $RESOURCEDIR"
		cp -rv "${BUILDDIR}/${PROGRAM}HtmlDoc" $RESOURCEDIR
	fi
}

package() {
	PROGRAM=$1
	getBuildDir $PROGRAM
        checkEnvActive

	if [ $OSNAME == "Darwin" ]; then
		#if [ "$PROGRAM" != "Crossmgr" ]; then
		#	cd $BUILDDIR
		#fi
		echo "Packaging MacApp into DMG..."
		echo "dmgbuild -s dmgsetup.py $PROGRAM $PROGRAM.dmg"
		dmgbuild -s dmgsetup.py -D builddir=$BUILDDIR $PROGRAM $PROGRAM.dmg
		RESULT=$?
		#if [ "$PROGRAM" != "Crossmgr" ]; then
		#		cd ..
		#fi
		if [ $RESULT -ne 0 ]; then
			echo "Packaging failed. Aborting..."
			exit 1
		fi
	else
		downloadAppImage
		echo "Packaging Linux app to AppImage..."
		export ARCH=x86_64
		./${LINUXDEPLOY} --appdir "dist/${PROGRAM}"
		if [ $? -ne 0 ]; then
			echo "Packaging failed. Aborting..."
			exit 1
		fi
	fi

}

moveRelease() {
	PROGRAM=$1
	echo "Moving to release directory..."
	getVersion $PROGRAM
	mkdir -p release
	if [ "$OSNAME" == "Darwin" ]; then
		mv "${PROGRAM}_${VERSION}.dmg" release/
	else
		mv ${PROGRAM}*.AppImage release/
	fi
}

envSetup() {
	if [ ! -f requirements.txt ]; then
		echo "Script must be run in same main directory with requirements.txt. Aborting..."
		exit 1
	fi
	if [ -z "$VIRTUAL_ENV" ]; then
		if [ -d $ENVDIR ]; then
			echo "Activating virtual env ($ENVDIR) ..."
			. env/bin/activate
		else
			echo "Creating virtual env in $ENVDIR..."
			$PYTHONVER -mpip install virtualenv
            if [ $? -ne 0 ]; then
                echo "Virtual env setup failed. Aborting..."
                exit 1
            fi
			$PYTHONVER -mvirtualenv $ENVDIR -p $PYTHONVER
            if [ $? -ne 0 ]; then
                echo "Virtual env setup failed. Aborting..."
                exit 1
            fi
			. env/bin/activate
		fi
	else
		echo "Already using $VIRTUAL_ENV"
	fi
	
	if   [ $OSNAME == "Linux" ]; then
        # On Linux, the wxPython module install attempts to rebuild the module from the C/C++ source.
        # Unfortunately, this always fails in an virtualenv and/or there are other missing C/C++ libraries.
        # The build also takes >40 minutes, which is an excessive amount of time to wait for a failed build.
        # The solution is to grab the pre-built install for this Ubuntu version from wxPython extras.

		# Old way, but lsb_release is not always included in Linux, so this can fail.
		# UBUNTU_RELEASE=`lsb_release -r | awk '{ print $2 }'`
		
		# New way.  Get version information from /etc/os-release.  Ignore the third version value (if present).
		UBUNTU_RELEASE=$(awk '/^VERSION_ID\s*=/{ gsub(/[^0-9.]/,"",$0); split($0, v, "."); print v[1] "." v[2] }' /etc/os-release)
		if [ $? -ne 0 ]; then
			echo "Pip requirements: could not get UBUNTU_RELEASE from /etc/os-release. Aborting..."
			exit 1
		fi
		sed "s+wxPython+-f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-${UBUNTU_RELEASE} wxPython+g" < requirements.txt | pip3 install -v -r /dev/stdin
	else
		pip3 install -v -r requirements.txt
	fi
	
    if [ $? -ne 0 ]; then
        echo "Pip requirements install failed. Aborting..."
        exit 1
    fi
    
    if   [ $OSNAME == "Windows" ]; then
		pip3 install pywin32
	fi
    if [ $OSNAME == "Darwin" ]; then
		echo "Darwin build..."
		#pip3 install biplist "dmgbuild>=1.4.2"
		pip3 install "dmgbuild>=1.4.2"
	else
		downloadAppImage
	fi
}

updateversion() {
	if [ -z "$PROGRAMS" ]; then
		echo "Updateversion: no programs defined!!"
		exit 1
	fi
	if [ -n "$GITHUB_REF" ]; then
		echo "GITHUB_REF=$GITHUB_REF"
		for program in $PROGRAMS
		do
			getBuildDir $program
			getVersion $program
			# development build
			GIT_TYPE=$(echo $GITHUB_REF | awk -F '/' '{print $2'})
			GIT_TAG=$(echo $GITHUB_REF | awk -F '/' '{print $3'})
			SHORTSHA=$(echo $GITHUB_SHA | cut -c 1-7)
			VERSION=$(echo $VERSION | awk -F - '{print $1}')
			if [ "$GIT_TYPE" == "heads" -a "$GIT_TAG" == "master" ]; then
                echo "Refusing to build an untagged master build. Release builds on a tag only!"
                exit 1
            fi
			if [ "$GIT_TYPE" == "heads" -a "$GIT_TAG" == "dev" ]; then
				APPVERNAME="AppVerName=\"$program $VERSION-beta-$SHORTSHA\""
				VERSION="$VERSION-beta-$SHORTSHA"
			fi
			if [ "$GIT_TYPE" == "tags" ]; then
				VERNO=$(echo $GIT_TAG | awk -F '-' '{print $1}')
				REFDATE=$(echo $GIT_TAG | awk -F '-' '{print $2}')
				MAJOR=$(echo $VERNO | awk -F '.' '{print $1}')
				MINOR=$(echo $VERNO | awk -F '.' '{print $2}')
				RELEASE=$(echo $VERNO | awk -F '.' '{print $3}')
				if [ "$MAJOR" != "v3" -o -z "$MINOR" -o -z "$RELEASE" -o -z "$REFDATE" ]; then
					echo "Invalid tag format. Must be v3.0.3-20200101010101. Refusing to build!"
					exit 1
				fi
				APPVERNAME="AppVerName=\"$program $VERSION-$REFDATE\""
				VERSION="$GIT_TAG"
			fi
            if [ -z "$APPVERNAME" ]; then
                echo "APPVERNAME is empty! [$APPVERNAME] Aborting..."
                exit 1
            fi
			echo "$program version is now $VERSION"
            echo "New Version.py: [$APPVERNAME] - [$BUILDDIR/Version.py]"
			echo "$APPVERNAME" > $BUILDDIR/Version.py
		done
	else
		echo "Running a local build"
	fi
}

buildall() {
		if [ -n "$PROGRAMS" ]; then
            checkEnvActive
			cleanup
			updateversion
			for program in $PROGRAMS
			do
				getVersion $program
				compileCode $program
				doPyInstaller $program
				copyAssets $program
				package $program
				moveRelease $program
			done
		else
			echo "No programs enabled. Use -t, -c, -i, or -a."
			exit
		fi
}

listFiles() {
    let count=0
    ls -1 release | while read file
    do
        echo "FILE_${count}=$file"
        let count=count+1
    done
}

fixDependencies() {
	PROGRAM=$1
	
	if [ -f "$PROGRAM/UpdateDependencies.py" ]; then
		echo "Fixing: $PROGRAM"
		cd $PROGRAM
		python3 UpdateDependencies.py
		if [ $? -ne 0 ]; then
			echo "Fix Dependencies Failed...."
			exit 1
		fi
		cd ..
	fi
}

tagrepo() {
	CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD -- | head -1)
	if [ "$CURRENT_BRANCH" != "master" ]; then
		echo "Unable to tag $CURRENT_BRANCH branch for release. Releases are from master only!"
        exit 1
	fi
    echo "Crossmgr version will be updated by the auto-build system to match the tag"
	getVersion "CrossMgr"
	# Remove the -private from the version
	VERSIONNO=$(echo $VERSION | awk -F - '{print $1}')
	DATETIME=$(date +%Y%m%d%H%M%S)
	TAGNAME="v$VERSIONNO-$DATETIME"
	echo "Tagging with $TAGNAME"
	git tag $TAGNAME
	git push origin $TAGNAME
}

dorelease() {
	CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD -- | head -1)
	if [ "$CURRENT_BRANCH" != "dev" ]; then
		echo "Unable to do release on $CURRENT_BRANCH branch. You must be on dev branch to cut a release".
        exit 1
	fi
    if ! git diff-index --quiet HEAD --; then
        echo "$CURRENT_BRANCH has uncommited changed. Refusing to release. Commit your code."
        exit 1
    fi
    if [ x"$(git rev-parse $CURRENT_BRANCH)" != x"$(git rev-parse origin/$CURRENT_BRANCH)" ]; then
        echo "$CURRENT_BRANCH is not in sync with origin. Please push your changes."
        exit 1
    fi
	getVersion "CrossMgr"
	# Remove the -private from the version
	VERSIONNO=$(echo $VERSION | awk -F - '{print $1}')
	DATETIME=$(date +%Y%m%d%H%M%S)
	TAGNAME="v$VERSIONNO-$DATETIME"
	echo "Releasing with $TAGNAME"
    git checkout master
    git merge dev -m "Release $TAGNAME"
    git push
    echo "Code merged into master..."
	git tag $TAGNAME
	git push origin $TAGNAME
    echo "Code tagged with $TAGNAME for release"
    git checkout dev
    echo "Current branch set back to dev..."
}


doHelp() {
	cat <<EOF
$0 [ -hcitywVqseCtaep: ]
 -h        - Help
 -E [env]  - Use Environment ($VIRTUAL_ENV)
 -p [pythonexe]  - Python version (Default $PYTHONVER)
 -c        - Build CrossMgr
 -i        - Build CrossMgrImpinj
 -t        - Build TagReadWrite
 -y        - Build SeriesMgr
 -w        - Build CrossMgrAlien
 -V        - Build CrossMgrVideo
 -q        - Build PointsRaceMgr
 -s        - Build SprintMgr
 -e        - Build CallupSeedingMgr
 -g        - Build StageRaceGC
 -a        - Build all programs

 -d		   - Download AppImage builder
 -S        - Setup environment
 -C        - Clean up everything
 -B        - Compile code
 -P        - Run pyinstaller
 -o        - Copy Assets to dist directory
 -k        - Package application
 -m        - Move package to release directory
 -A        - Build everything and package
 -l        - list files in release directory
 -f        - Fix SeriesMgr files

 -T        - Tag for release

Running on: $OSNAME

To setup the build environment after a fresh checkout, use:
$0 -S

To build all the applications and package them, use:
$0 -a -A

EOF
	exit
}

gotarg=0
while getopts "hcitaveiCdPBASkomzlTfyqswVZUr" option
do
	gotarg=1
	case ${option} in
		h) doHelp
		;;
		a) 
 		    PROGRAMS="StageRaceGC CallupSeedingMgr CrossMgrImpinj TagReadWrite SeriesMgr CrossMgrAlien CrossMgrVideo PointsRaceMgr SprintMgr CrossMgr"
		;;
		c) PROGRAMS="$PROGRAMS CrossMgr"
		;;
		i) PROGRAMS="$PROGRAMS CrossMgrImpinj"
		;;
		t) PROGRAMS="$PROGRAMS TagReadWrite"
		;;
		y) PROGRAMS="$PROGRAMS SeriesMgr"
		;;
		w) PROGRAMS="$PROGRAMS CrossMgrAlien"
		;;
		q) PROGRAMS="$PROGRAMS PointsRaceMgr"
		;;
		e) PROGRAMS="$PROGRAMS CallupSeedingMgr"
		;;
		g) PROGRAMS="$PROGRAMS StageRaceGC"
		;;
		s) PROGRAMS="$PROGRAMS SprintMgr"
		;;
		V) PROGRAMS="$PROGRAMS CrossMgrVideo"
		;;
		v) 	getVersion "CrossMgr"
			getVersion "CrossMgrImpinj"
			getVersion "TagReadWrite"
			getVersion "SeriesMgr"
			getVersion "CrossMgrAlien"
			getVersion "CrossMgrVideo"
			getVersion "PointsRaceMgr"
			getVersion "SprintMgr"
			getVersion "CallupSeedingMgr"
			getVersion "StageRaceGC"
		;;
		C) 	cleanup
		;;
		p) PYTHONVER=$OPTIONARG
		   echo "Using Python: $PYTHONVER"
		;;
		d) downloadAppImage
		;;
		S) envSetup
		;;
		B) if [ -n "$PROGRAMS" ]; then
				for program in $PROGRAMS
				do
					compileCode $program
				done
			else
				echo "No programs enabled. Use -t, -c, -i, or -a."
				exit
			fi
		;;
		P) if [ -n "$PROGRAMS" ]; then
				for program in $PROGRAMS
				do
					doPyInstaller $program
				done
			else
				echo "No programs enabled. Use -t, -c, -i, or -a."
				exit
			fi
		;;
		Z) if [ -n "$PROGRAMS" ]; then
				for program in $PROGRAMS
				do
					buildLocale $program
				done
			else
				echo "No programs enabled. Use -t, -c, -i, or -a."
				exit
			fi
		;;
		o) if [ -n "$PROGRAMS" ]; then
				for program in $PROGRAMS
				do
					copyAssets $program
				done
			else
				echo "No programs enabled. Use -t, -c, -i, or -a."
				exit
			fi
		;;
		k) if [ -n "$PROGRAMS" ]; then
				for program in $PROGRAMS
				do
					package $program
				done
			else
				echo "No programs enabled. Use -t, -c, -i, or -a."
				exit
			fi
		;;
		m) if [ -n "$PROGRAMS" ]; then
				for program in $PROGRAMS
				do
					moveRelease $program
				done
			else
				echo "No programs enabled. Use -t, -c, -i, or -a."
				exit
			fi
		;;
		U) updateversion
		;;
		A) buildall
		;;
		z) checkEnvActive
		;;
		l) listFiles
		;;
		T) tagrepo
		;;
		r) dorelease
		;;
		f) fixDependencies 'SeriesMgr'
		   fixDependencies 'CrossMgrVideo'
		   fixDependencies 'SprintMgr'
		   fixDependencies 'CallupSeedingMgr'
		   fixDependencies 'StageRaceGC'
		;;
		*) doHelp
		;;
	esac
done

if [ $gotarg -eq 0 ]; then
	echo "No arguments given"
	doHelp
	exit 1
fi

