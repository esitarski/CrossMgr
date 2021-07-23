#!/bin/sh
# Ubuntu dependancies required for wxPython 4.0
sudo apt update
# The following is no longer necessary as we are installing from a pre-built wheel, not rebuiding wxpython from source.
# sudo apt install libjpeg9 libtiff5 libsdl2-2.0-0 libnotify-bin freeglut3 libsm6 libgtk-3-0 libwebkitgtk-3.0-0 libgstreamer1.0-0 libgtk-3-dev python3.9-dev

# Some libraries are still required for wxPython.
sudo apt install libsdl2-2.0-0 libgtk-3-0 libwebkitgtk-3.0-0 libgstreamer1.0-0 libgtk-3-dev
