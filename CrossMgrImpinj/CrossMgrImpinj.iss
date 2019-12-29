; -- CrossMgrImpinj.iss --

[Setup]
#include "inno_setup.txt"
ArchitecturesInstallIn64BitMode=x64
DefaultDirName={commonpf}\CrossMgrImpinj
DefaultGroupName=CrossMgr
UninstallDisplayIcon={app}\CrossMgrImpinj.exe
Compression=lzma2/ultra64
SolidCompression=yes
ChangesAssociations=yes

[Registry]
Root: HKCR; Subkey: "CrossMgrImpinj\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\CrossMgrImpinj.exe,0"
Root: HKCR; Subkey: "CrossMgrImpinj\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\CrossMgrImpinj.exe"" ""%1"""

[Tasks] 
Name: "desktopicon"; Description: "Create a &desktop icon"; 
	
[Files]
Source: "*.*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\CrossMgrImpinj"; Filename: "{app}\CrossMgrImpinj.exe"
Name: "{userdesktop}\CrossMgrImpinj"; Filename: "{app}\CrossMgrImpinj.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\CrossMgrImpinj.exe"; Description: "Launch CrossMgrImpinj"; Flags: nowait postinstall skipifsilent
