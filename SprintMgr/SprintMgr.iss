; -- SprintMgr.iss --

[Setup]
#include "inno_setup.txt"
ArchitecturesInstallIn64BitMode=x64
DefaultDirName={commonpf}\SprintMgr
DefaultGroupName=SprintMgr
UninstallDisplayIcon={app}\SprintMgr.exe
ChangesAssociations=yes
Compression=lzma2/ultra64
SolidCompression=yes

[Registry]
; Automatically configure SprintMgr to launch .smr files.
Root: HKCR; Subkey: ".smr"; ValueType: string; ValueName: ""; ValueData: "SprintMgr"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "SprintMgr"; ValueType: string; ValueName: ""; ValueData: "SprintMgr Race File"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SprintMgr\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\SprintMgr.exe,0"
Root: HKCR; Subkey: "SprintMgr\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SprintMgr.exe"" ""%1"""

[Tasks] 
Name: "desktopicon"; Description: "Create a &desktop icon"; 
	
[Files]
Source: "*.*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\SprintMgr"; Filename: "{app}\SprintMgr.exe"
Name: "{userdesktop}\SprintMgr"; Filename: "{app}\SprintMgr.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\SprintMgr.exe"; Description: "Launch SprintMgr"; Flags: nowait postinstall skipifsilent
