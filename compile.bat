
python -mcompileall -l .
python pypi.py
python CrossMgrSetup.py py2exe

copy helptxt\CrossMgrDocHtml.zip C:\GoogleDrive\Downloads\Windows\CrossMgr
SET /P RESULT=[Press any key to continue...]