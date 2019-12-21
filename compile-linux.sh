#!/bin/bash
. Version.py
echo "New version is ${AppVerName}"
VERSION=$(echo ${AppVerName} | awk '{print $2}')
echo "$VERSION"
export VERSION
echo "Cleaning up..."
rm -f $(find . -name "*.pyc")
rm -rf dist build
rm -f *.dmg
echo "Compiling...."
python3 -mcompileall -l .
echo "Building Mac App..."
pyinstaller CrossMgr.pyw --distpath dist --icon=CrossMgrImages/CrossMgr.png --clean --windowed --noconfirm --exclude-module=tcl --exclude-module=tk --exclude-module=Tkinter --exclude-module=_tkinter
echo "Copy the Resource files..."
mkdir -p dist/CrossMgr/usr/bin
mv dist/CrossMgr/* dist/CrossMgr/usr/bin/
cp -rv CrossMgrImages dist/CrossMgr/usr/bin
cp -rv CrossMgrHtml dist/CrossMgr/usr/bin
cp -rv CrossMgrHtmlDoc dist/CrossMgr/usr/bin
cp -rv CrossMgrLocale dist/CrossMgr/usr/bin
cp -v appimage/* dist/CrossMgr
chmod 755 dist/CrossMgr/AppRun
cp -v CrossMgrImages/CrossMgr.png dist/CrossMgr
if [ -d CrossMgrHelpIndex ]
then
	rm -rf CrossMgrHelpIndex
fi
echo "Building Help..."
python3 buildhelp.py
cp -rv CrossMgrHelpIndex dist/CrossMgr/usr/bin
export ARCH=x86_64
linuxdeploy-plugin-appimage-x86_64.AppImage --appdir dist/CrossMgr

