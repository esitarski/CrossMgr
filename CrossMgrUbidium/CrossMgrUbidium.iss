; -- CrossMgrUbidium.iss --

[Setup]
#include "inno_setup.txt"
ArchitecturesInstallIn64BitMode=x64
DefaultDirName={commonpf}\CrossMgrUbidium
DefaultGroupName=CrossMgr
UninstallDisplayIcon={app}\CrossMgrUbidium.exe
Compression=lzma2/ultra64
SolidCompression=yes
ChangesAssociations=yes

[Registry]
Root: HKCR; Subkey: "CrossMgrUbidium\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\CrossMgrUbidium.exe,0"
Root: HKCR; Subkey: "CrossMgrUbidium\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\CrossMgrUbidium.exe"" ""%1"""

[Tasks] 
Name: "desktopicon"; Description: "Create a &desktop icon"; 
	
[Files]
Source: "*.*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\CrossMgrUbidium"; Filename: "{app}\CrossMgrUbidium.exe"
Name: "{userdesktop}\CrossMgrUbidium"; Filename: "{app}\CrossMgrUbidium.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\CrossMgrUbidium.exe"; Description: "Launch CrossMgrUbidium"; Flags: nowait postinstall skipifsilent
