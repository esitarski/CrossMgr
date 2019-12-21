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
pyinstaller TagReadWrite.pyw --icon=TagReadWriteImages/TagReadWrite.icns --clean --windowed --noconfirm --exclude-module=tcl --exclude-module=tk --exclude-module=Tkinter --exclude-module=_tkinter --osx-bundle-identifier=com.esitarsk.crossmgr
echo "Copy the Resource files..."
cp -rv TagReadWriteImages dist/TagReadWrite.app/Contents/Resources/
if [ -n "${SIGNINGCERT}" ]
then
	echo "Signing code..."
	pushd .
	cd dist/TagReadWrite.app/Contents/MacOS
	for file in *.dylib *.so
	do
		echo "Signing: ${file}"
		codesign -s "${SIGNINGCERT}" $file
	done
	popd
	echo "Signing the entire app..."
	codesign -s "${SIGNINGCERT}" dist/TagReadWrite.app
fi
echo "Building DMG image..."
dmgbuild -s dmgsetup.py "TagReadWrite" TagReadWrite.dmg
