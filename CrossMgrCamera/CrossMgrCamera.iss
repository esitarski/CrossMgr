; -- CrossMgrCamera.iss --

[Setup]
#include "inno_setup.txt"
DefaultDirName={pf}\CrossMgrCamera
DefaultGroupName=CrossMgrCamera
UninstallDisplayIcon={app}\CrossMgrCamera.exe
Compression=lzma2/ultra64
SolidCompression=yes
SourceDir=dist\CrossMgrCamera
OutputDir=..\..\install
OutputBaseFilename=CrossMgrCamera_Setup
ChangesAssociations=yes

[Registry]
Root: HKCR; Subkey: "CrossMgrCamera\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\CrossMgrCamera.exe,0"
Root: HKCR; Subkey: "CrossMgrCamera\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\CrossMgrCamera.exe"" ""%1"""

[Tasks] 
Name: "desktopicon"; Description: "Create a &desktop icon"; 
	
[Files]
Source: "*.*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\CrossMgrCamera"; Filename: "{app}\CrossMgrCamera.exe"
Name: "{userdesktop}\CrossMgrCamera"; Filename: "{app}\CrossMgrCamera.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\CrossMgrCamera.exe"; Description: "Launch CrossMgrCamera"; Flags: nowait postinstall skipifsilent
