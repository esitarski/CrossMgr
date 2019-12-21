#!/bin/bash
#SIGNINGCERT="Mac Developer: MARK BUCKAWAY (8JR73M9YJC)"
. Version.py
echo "New version is ${AppVerName}"
echo "Cleaning up..."
rm -f $(find . -name "*.pyc")
rm -rf dist build
rm -f *.dmg
echo "Compiling...."
python3 -mcompileall -l .
echo "Building Mac App..."
pyinstaller CrossMgrImpinj.pyw --icon=CrossMgrImpinjImages/CrossMgrImpinj.icns --clean --windowed --noconfirm --exclude-module=tcl --exclude-module=tk --exclude-module=Tkinter --exclude-module=_tkinter --osx-bundle-identifier=com.esitarsk.crossmgr
echo "Copy the Resource files..."
cp -rv CrossMgrImpinjImages dist/CrossMgrImpinj.app/Contents/Resources/
if [ -n "${SIGNINGCERT}" ]
then
	echo "Signing code..."
	pushd .
	cd dist/CrossMgrImpinj.app/Contents/MacOS
	for file in *.dylib *.so
	do
		echo "Signing: ${file}"
		codesign -s "${SIGNINGCERT}" $file
	done
	popd
	echo "Signing the entire app..."
	codesign -s "${SIGNINGCERT}" dist/CrossMgrImpinj.app
fi
echo "Building DMG image..."
dmgbuild -s dmgsetup.py "CrossMgrImpinj" CrossMgrImpinj.dmg
