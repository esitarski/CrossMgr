; -- CrossMgr.iss --

[Setup]
AppName=CrossMgr
#include "Version.py"
DefaultDirName={pf}\CrossMgr
DefaultGroupName=CrossMgr
UninstallDisplayIcon={app}\CrossMgr.exe
Compression=lzma
SolidCompression=yes
SourceDir=dist
OutputDir=..\install
OutputBaseFilename=CrossMgr_Setup
ChangesAssociations=yes

[Registry]
; Automatically configure CrossMgr to launch .cmn files.
Root: HKCR; Subkey: ".cmn"; ValueType: string; ValueName: ""; ValueData: "CrossMgr"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "CrossMgr"; ValueType: string; ValueName: ""; ValueData: "CrossMgr Race File"; Flags: uninsdeletekey
Root: HKCR; Subkey: "CrossMgr\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\CrossMgr.exe,0"
Root: HKCR; Subkey: "CrossMgr\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\CrossMgr.exe"" ""%1"""

[Tasks] 
Name: "desktopicon"; Description: "Create a &desktop icon"; 
	
[Files]
Source: "*.*"; DestDir: "{app}"; Flags: recursesubdirs
Source: "..\CrossMgrTutorial.doc"; DestDir: "{app}";
Source: "..\data\*.*"; DestDir: "{app}\data";

[Icons]
Name: "{group}\CrossMgr"; Filename: "{app}\CrossMgr.exe"
Name: "{userdesktop}\CrossMgr"; Filename: "{app}\CrossMgr.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\CrossMgr.exe"; Description: "Launch CrossMgr"; Flags: nowait postinstall skipifsilent