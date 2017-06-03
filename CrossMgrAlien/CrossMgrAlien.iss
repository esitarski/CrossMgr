; -- CrossMgrAlien.iss --

[Setup]
AppName=CrossMgrAlien
#include "Version.py"
ArchitecturesInstallIn64BitMode=x64
DefaultDirName={pf}\CrossMgrAlien
DefaultGroupName=CrossMgrAlien
UninstallDisplayIcon={app}\CrossMgrAlien.exe
Compression=lzma2/ultra64
SolidCompression=yes
SourceDir=dist\CrossMgrAlien
OutputDir=..\..\install
OutputBaseFilename=CrossMgrAlien_Setup
ChangesAssociations=yes

[Registry]
Root: HKCR; Subkey: "CrossMgrAlien\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\CrossMgrAlien.exe,0"
Root: HKCR; Subkey: "CrossMgrAlien\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\CrossMgrAlien.exe"" ""%1"""

[Tasks] 
Name: "desktopicon"; Description: "Create a &desktop icon"; 
	
[Files]
Source: "*.*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\CrossMgrAlien"; Filename: "{app}\CrossMgrAlien.exe"
Name: "{userdesktop}\CrossMgrAlien"; Filename: "{app}\CrossMgrAlien.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\CrossMgrAlien.exe"; Description: "Launch CrossMgrAlien"; Flags: nowait postinstall skipifsilent
