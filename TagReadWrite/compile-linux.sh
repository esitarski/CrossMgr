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
pyinstaller TagReadWrite.pyw --distpath dist --icon=TagReadWriteImages/TagReadWrite.png --clean --windowed --noconfirm --exclude-module=tcl --exclude-module=tk --exclude-module=Tkinter --exclude-module=_tkinter
echo "Copy the Resource files..."
mkdir -p dist/TagReadWrite/usr/bin
mv dist/TagReadWrite/* dist/TagReadWrite/usr/bin/
cp -rv TagReadWriteImages dist/TagReadWrite/usr/bin
cp -v appimage/* dist/TagReadWrite
chmod 755 dist/TagReadWrite/AppRun
cp -v TagReadWriteImages/TagReadWrite.png dist/TagReadWrite
export ARCH=x86_64
linuxdeploy-plugin-appimage-x86_64.AppImage --appdir dist/TagReadWrite

