#!/bin/bash

BUILD_CROSSMGR=0
BUILD_CROSSMGRIMPINJ=0
BUILD_TAGREADWRITE=0
OSNAME=$(uname -s)
PYTHONVER=python3.8
ENVDIR=env
LINUXDEPLOY=linuxdeploy-plugin-appimage-x86_64.AppImage
if [ "$OSNAME" == "Darwin" ]; then
	PYTHONVER="python3.7"
fi
if [ "$OSNAME" == "Linux" ]; then
	PYTHONVER="python3.7"
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

doPyInstaller() {
	PROGRAM=$1
	getBuildDir $PROGRAM
    checkEnvActive
	ICONPATH=${BUILDDIR}/${PROGRAM}Images/
	case $OSNAME in
		Darwin)	echo pyinstaller ${BUILDDIR}/${PROGRAM}.pyw --icon=${ICONPATH}/${PROGRAM}.icns --clean --windowed --noconfirm --exclude-module=tcl --exclude-module=tk --exclude-module=Tkinter --exclude-module=_tkinter --osx-bundle-identifier=com.esitarsk.crossmgr
			pyinstaller ${BUILDDIR}/${PROGRAM}.pyw --icon=${ICONPATH}/${PROGRAM}.icns --clean --windowed --noconfirm --exclude-module=tcl --exclude-module=tk --exclude-module=Tkinter --exclude-module=_tkinter --osx-bundle-identifier=com.esitarsk.crossmgr
			if [ $? -ne 0 ]; then
				echo "Build Failed!"
				exit 1
			fi
		;;
		Linux) echo pyinstaller ${BUILDDIR}/${PROGRAM}.pyw --icon=${ICONPATH}/${PROGRAM}.png --clean --windowed --noconfirm --exclude-module=tcl --exclude-module=tk --exclude-module=Tkinter --exclude-module=_tkinter --osx-bundle-identifier=com.esitarsk.crossmgr
			pyinstaller ${BUILDDIR}/${PROGRAM}.pyw --icon=${ICONPATH}/${PROGRAM}.png --clean --windowed --noconfirm --exclude-module=tcl --exclude-module=tk --exclude-module=Tkinter --exclude-module=_tkinter --osx-bundle-identifier=com.esitarsk.crossmgr
			if [ $? -ne 0 ]; then
				echo "Build Failed!"
				exit 1
			fi
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
	echo "$PROGRAM Version is $VERSION"
}

cleanup() {
	echo "Cleaning up everything..."
	rm -rf __pycache__ CrossMgrImpinj/__pycache__ TagReadWrite/__pycache__ 
	rm -rf dist build release
	rm -f *.spec
	case $OSNAME in
		Darwin) rm -f *.dmg
		;;
		Linux) rm -f *.AppImage
		;;
	esac
}

downloadAppImage() {
	if [ "$OSNAME" == "Linux" ];then
		if [ -f $LINUXDEPLOY ]; then
			echo "$LINUXDEPLOY already installed"
		else
			wget -v https://github.com/linuxdeploy/linuxdeploy-plugin-appimage/releases/download/continuous/$LINUXDEPLOY
			chmod 755 $LINUXDEPLOY
		fi
	else
		echo "AppImage builder not requried for $OSNAME"
	fi
}

compileCode() {
	PROGRAM=$1
	getBuildDir $PROGRAM
    checkEnvActive
	echo "Compiling code"
	python3 -mcompileall -l $BUILDDIR
	if [ $? -ne 0 ];then
		echo "Compile failed. Aborting..."
		exit 1
	fi
}


copyAssets(){
	PROGRAM=$1
	getBuildDir $PROGRAM

	if [ "$OSNAME" == "Darwin" ]; then
		RESOURCEDIR="dist/${PROGRAM}.app/Contents/Resources/"
	else
		RESOURCEDIR="dist/${PROGRAM}/usr/bin/"
	fi
	mkdir -p $RESOURCEDIR
	if [ "$OSNAME" == "Linux" ];then
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
	if [ -d "${BUILDDIR}/${PROGRAM}HtmlDoc" ]; then
		echo "Copying HtmlDoc to $RESOURCEDIR"
		cp -rv "${BUILDDIR}/${PROGRAM}HtmlDoc" $RESOURCEDIR
	fi
	if [ -d "${BUILDDIR}/${PROGRAM}Locale" ]; then
		echo "Copying Locale to $RESOURCEDIR"
		cp -rv "${BUILDDIR}/${PROGRAM}Locale" $RESOURCEDIR
	fi

	if [ "$PROGRAM" == "CrossMgr" ];then
		if [ -d CrossMgrHelpIndex ]
		then
			rm -rf CrossMgrHelpIndex
		fi
		echo "Building Help for CrossMgr ..."
		python3 buildhelp.py
		cp -rv CrossMgrHelpIndex $RESOURCEDIR
	fi
}

package() {
	PROGRAM=$1
	getBuildDir $PROGRAM
    checkEnvActive

	if [ $OSNAME == "Darwin" ];then
		#if [ "$PROGRAM" != "Crossmgr" ];then
		#	cd $BUILDDIR
		#fi
		echo "Packaging MacApp into DMG..."
		echo "dmgbuild -s dmgsetup.py $PROGRAM $PROGRAM.dmg"
		dmgbuild -s dmgsetup.py -D builddir=$BUILDDIR $PROGRAM $PROGRAM.dmg
		RESULT=$?
		#if [ "$PROGRAM" != "Crossmgr" ];then
		#		cd ..
		#fi
		if [ $RESULT -ne 0 ]; then
			echo "Packaging failed. Aborting..."
			exit 1
		fi
	else
		if [ ! -f $LINUXDEPLOY ]; then
			downloadAppImage
		fi
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
	if [ -z "$VERSION" ]; then
		getVersion $PROGRAM
	fi
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
            if [ $? -ne 0 ];then
                echo "Virtual env setup failed. Aborting..."
                exit 1
            fi
			$PYTHONVER -mvirtualenv $ENVDIR -p $PYTHONVER
            if [ $? -ne 0 ];then
                echo "Virtual env setup failed. Aborting..."
                exit 1
            fi
			. env/bin/activate
		fi
	else
		echo "Already using $VIRTUAL_ENV"
	fi
	pip3 install -r requirements.txt
    if [ $? -ne 0 ];then
        echo "Pip requirememnts install failed. Aborting..."
        exit 1
    fi
    if [ $OSNAME == "Darwin" ];then
		pip3 install dmgbuild
	else
		downloadAppImage
	fi
}

buildall() {
		if [ -n "$PROGRAMS" ]; then
            checkEnvSetup
			cleanup
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

doHelp() {
	cat <<EOF
$0 [ -hcCtaep: ]
 -h        - Help
 -E [env]  - Use Environment ($VIRTUAL_ENV)
 -p [pythonexe]  - Python version (Default $PYTHONVER)
 -c        - Build CrossMgr
 -i        - Build CrossMgrImpinj
 -t        - Build TagReadWrite
 -y        - Build CrossMgrAlien
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

Running on: $OSNAME

To setup the build environment after a fresh checkout, use:
$0 -S

To build all the applications and package them, use:
$0 -a -A

EOF
	exit
}

gotarg=0
while getopts "hcitaviCdPBASkomzl" option
do
	gotarg=1
	case ${option} in
		h) doHelp
		;;
		a) 
 		    PROGRAMS="CrossMgr CrossMgrImpinj TagReadWrite"
		;;
		c) PROGRAMS="$PROGRAMS CrossMgr"
		;;
		i) PROGRAMS="$PROGRAMS CrossMgrImpinj"
		;;
		t) PROGRAMS="$PROGRAMS TagReadWrite"
		;;
		v) 	getVersion "CrossMgr"
			getVersion "CrossMgrImpinj"
			getVersion "CrossMgrAlien"
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
		A) buildall
		;;
		z) checkEnvActive
		;;
		l) listFiles
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

