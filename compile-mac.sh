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
pyinstaller CrossMgr.pyw --icon=CrossMgrImages/CrossMgr.icns --clean --windowed --noconfirm --exclude-module=tcl --exclude-module=tk --exclude-module=Tkinter --exclude-module=_tkinter --osx-bundle-identifier=com.esitarsk.crossmgr
exit
echo "Copy the Resource files..."
cp -rv CrossMgrImages dist/CrossMgr.app/Contents/Resources/
cp -rv CrossMgrHtml dist/CrossMgr.app/Contents/Resources/
cp -rv CrossMgrHtmlDoc dist/CrossMgr.app/Contents/Resources/
cp -rv CrossMgrLocale dist/CrossMgr.app/Contents/Resources/
if [ -d CrossMgrHelpIndex ]
then
	rm -rf CrossMgrHelpIndex
fi
echo "Building Help..."
python3 buildhelp.py
cp -rv CrossMgrHelpIndex dist/CrossMgr.app/Contents/Resources/
if [ -n "${SIGNINGCERT}" ]
then
	echo "Signing code..."
	pushd .
	cd dist/CrossMgr.app/Contents/MacOS
	for file in *.dylib *.so
	do
		echo "Signing: ${file}"
		codesign -s "${SIGNINGCERT}" $file
	done
	popd
	echo "Signing the entire app..."
	codesign -s "${SIGNINGCERT}" dist/CrossMgr.app
fi
echo "Building DMG image..."
dmgbuild -s dmgsetup.py "CrossMgr" CrossMgr.dmg
