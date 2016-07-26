; -- TagReadWrite.iss --

[Setup]
#include "inno_setup.txt"
ArchitecturesInstallIn64BitMode=x64
DefaultDirName={pf}\TagReadWrite
DefaultGroupName=TagReadWrite
UninstallDisplayIcon={app}\TagReadWrite.exe
Compression=lzma2/ultra64
SolidCompression=yes
SourceDir=dist\TagReadWrite
OutputDir=..\..\install
OutputBaseFilename=TagReadWrite_Setup
ChangesAssociations=yes

[Registry]

[Tasks] 
Name: "desktopicon"; Description: "Create a &desktop icon"; 
	
[Files]
Source: "*.*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\TagReadWrite"; Filename: "{app}\TagReadWrite.exe"
Name: "{userdesktop}\TagReadWrite"; Filename: "{app}\TagReadWrite.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\TagReadWrite.exe"; Description: "Launch TagReadWrite"; Flags: nowait postinstall skipifsilent
