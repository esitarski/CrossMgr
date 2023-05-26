[Setup]
#include "inno_setup.txt"
ArchitecturesInstallIn64BitMode=x64
DefaultDirName={commonpf}\StageRaceGC
DefaultGroupName=StageRaceGC
UninstallDisplayIcon={app}\StageRaceGC.exe
ChangesAssociations=yes
Compression=lzma2/ultra64
SolidCompression=yes

[Registry]
Root: HKCR; Subkey: "StageRaceGC"; ValueType: string; ValueName: ""; ValueData: "StageRaceGC Race File"; Flags: uninsdeletekey
Root: HKCR; Subkey: "StageRaceGC\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\StageRaceGC.exe,0"
Root: HKCR; Subkey: "StageRaceGC\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\StageRaceGC.exe"" ""%1"""

[Tasks] 
Name: "desktopicon"; Description: "Create a &desktop icon"; 
	
[Files]
Source: "*.*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\StageRaceGC"; Filename: "{app}\StageRaceGC.exe"
Name: "{userdesktop}\StageRaceGC"; Filename: "{app}\StageRaceGC.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\StageRaceGC.exe"; Description: "Launch StageRaceGC"; Flags: nowait postinstall skipifsilent
