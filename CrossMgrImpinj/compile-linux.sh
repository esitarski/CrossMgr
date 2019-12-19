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
pyinstaller CrossMgrImpinj.pyw --distpath dist --icon=CrossMgrImages/CrossMgr.png --clean --windowed --noconfirm --exclude-module=tcl --exclude-module=tk --exclude-module=Tkinter --exclude-module=_tkinter
echo "Copy the Resource files..."
mkdir -p dist/CrossMgrImpinj/usr/bin
mv dist/CrossMgrImpinj/* dist/CrossMgrImpinj/usr/bin/
cp -rv CrossMgrImpinjImages dist/CrossMgrImpinj/usr/bin
cp -v appimage/* dist/CrossMgrImpinj
chmod 755 dist/CrossMgrImpinj/AppRun
cp -v CrossMgrImpinjImages/CrossMgrImpinj.png dist/CrossMgrImpinj
linuxdeploy-plugin-appimage-x86_64.AppImage --appdir dist/CrossMgrImpinj

