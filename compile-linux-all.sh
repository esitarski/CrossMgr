#!/bin/bash
#
virtualenv  env
pip3 install -r requirements.txt
bash compile-linux.sh
cd CrossMgrImpimj
bash compile-linux.sh
