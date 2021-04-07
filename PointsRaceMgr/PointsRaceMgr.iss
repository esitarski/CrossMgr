; -- PointsRaceMgr.iss --

[Setup]
#include "inno_setup.txt"
ArchitecturesInstallIn64BitMode=x64
DefaultDirName={commonpf}\PointsRaceMgr
DefaultGroupName=PointsRaceMgr
UninstallDisplayIcon={app}\PointsRaceMgr.exe
ChangesAssociations=yes
Compression=lzma2/ultra64
SolidCompression=yes

[Registry]
; Automatically configure PointsRaceMgr to launch .tp5 files.
Root: HKCR; Subkey: ".tp5"; ValueType: string; ValueName: ""; ValueData: "PointsRaceMgr"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "PointsRaceMgr"; ValueType: string; ValueName: ""; ValueData: "PointsRaceMgr Race File"; Flags: uninsdeletekey
Root: HKCR; Subkey: "PointsRaceMgr\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\PointsRaceMgr.exe,0"
Root: HKCR; Subkey: "PointsRaceMgr\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\PointsRaceMgr.exe"" ""%1"""

[Tasks] 
Name: "desktopicon"; Description: "Create a &desktop icon"; 
	
[Files]
Source: "*.*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\PointsRaceMgr"; Filename: "{app}\PointsRaceMgr.exe"
Name: "{userdesktop}\PointsRaceMgr"; Filename: "{app}\PointsRaceMgr.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\PointsRaceMgr.exe"; Description: "Launch PointsRaceMgr"; Flags: nowait postinstall skipifsilent
