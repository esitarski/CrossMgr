#!/usr/bin/env bash
. env/bin/activate
python3 -m nuitka --follow-imports --report=CrossMgr-report.xml CrossMgr.pyw
