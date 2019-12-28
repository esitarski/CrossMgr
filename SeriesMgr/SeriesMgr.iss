; -- SeriesMgr.iss --

[Setup]
#include "inno_setup.txt"
ArchitecturesInstallIn64BitMode=x64
DefaultDirName={commonpf}\SeriesMgr
DefaultGroupName=CrossMgr
UninstallDisplayIcon={app}\SeriesMgr.exe
Compression=lzma2/ultra64
SolidCompression=yes
ChangesAssociations=yes

[Registry]
; Automatically configure SeriesMgr to launch .smn files.
Root: HKCR; Subkey: ".smn"; ValueType: string; ValueName: ""; ValueData: "SeriesMgr"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "SeriesMgr"; ValueType: string; ValueName: ""; ValueData: "SeriesMgr Race File"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SeriesMgr\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\SeriesMgr.exe,0"
Root: HKCR; Subkey: "SeriesMgr\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SeriesMgr.exe"" ""%1"""

[Tasks] 
Name: "desktopicon"; Description: "Create a &desktop icon"; 
	
[Files]
Source: "*.*"; Excludes: "\bugs\*,\install\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\SeriesMgr"; Filename: "{app}\SeriesMgr.exe"
Name: "{userdesktop}\SeriesMgr"; Filename: "{app}\SeriesMgr.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\SeriesMgr.exe"; Description: "Launch SeriesMgr"; Flags: nowait postinstall skipifsilent
