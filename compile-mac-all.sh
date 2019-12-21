#!/bin/bash
#
# Create a virtual environment for Python 3.7 (3.8 does work with pyinstaller)
virtualenv -p python3.7 env
pip3 install -r requirements.txt
bash compile-mac.sh
cd CrossMgrImpimj
bash compile-mac.sh
