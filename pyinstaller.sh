#!/bin/bash

python ../pyinstaller-2.0/pyinstaller.py --noconfirm --out=CrossMgrBuild CrossMgr.pyw
python PyInstallerPostBuild.py
