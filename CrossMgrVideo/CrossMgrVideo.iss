; -- CrossMgrVideo.iss --

[Setup]
#include "inno_setup.txt"
ArchitecturesInstallIn64BitMode=x64
DefaultDirName={pf}\CrossMgrVideo
DefaultGroupName=CrossMgrVideo
UninstallDisplayIcon={app}\CrossMgrVideo.exe
Compression=lzma2/ultra64
SolidCompression=yes
SourceDir=dist\CrossMgrVideo
OutputDir=..\..\install
OutputBaseFilename=CrossMgrVideo_Setup
ChangesAssociations=yes

[Registry]
Root: HKCR; Subkey: "CrossMgrVideo\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\CrossMgrVideo.exe,0"
Root: HKCR; Subkey: "CrossMgrVideo\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\CrossMgrVideo.exe"" ""%1"""

[Tasks] 
Name: "desktopicon"; Description: "Create a &desktop icon"; 
	
[Files]
Source: "*.*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\CrossMgrVideo"; Filename: "{app}\CrossMgrVideo.exe"
Name: "{userdesktop}\CrossMgrVideo"; Filename: "{app}\CrossMgrVideo.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\CrossMgrVideo.exe"; Description: "Launch CrossMgrVideo"; Flags: nowait postinstall skipifsilent
