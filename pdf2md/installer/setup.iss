[Setup]
AppName=PDF2MD
AppVersion=1.0.0
AppPublisher=PDF2MD
DefaultDirName={autopf}\PDF2MD
DefaultGroupName=PDF2MD
OutputBaseFilename=PDF2MD_Setup
OutputDir=installer\Output
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin

[Languages]
Name: "dutch"; MessagesFile: "compiler:Languages\Dutch.isl"

[Tasks]
Name: desktopicon; Description: "Bureaubladpictogram aanmaken"; GroupDescription: "Extra opties:"

[Files]
; GUI applicatie (alle bestanden inclusief DLL's van PyInstaller)
Source: "dist\PDF2MD_GUI\*"; DestDir: "{app}\PDF2MD_GUI"; Flags: recursesubdirs createallsubdirs ignoreversion

; DragDrop applicatie
Source: "dist\PDF2MD_DragDrop\*"; DestDir: "{app}\PDF2MD_DragDrop"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\PDF2MD (GUI)"; Filename: "{app}\PDF2MD_GUI\PDF2MD_GUI.exe"
Name: "{group}\PDF2MD verwijderen"; Filename: "{uninstallexe}"
Name: "{commondesktop}\PDF2MD"; Filename: "{app}\PDF2MD_GUI\PDF2MD_GUI.exe"; Tasks: desktopicon

[Registry]
; Rechtsklik op map → "Converteer naar Markdown"
Root: HKCR; Subkey: "Directory\shell\PDF2MD"; ValueType: string; ValueName: ""; ValueData: "Converteer naar Markdown"; Flags: uninsdeletekey
Root: HKCR; Subkey: "Directory\shell\PDF2MD\command"; ValueType: string; ValueName: ""; ValueData: """{app}\PDF2MD_DragDrop\PDF2MD_DragDrop.exe"" ""%1"""

[Run]
Filename: "{app}\PDF2MD_GUI\PDF2MD_GUI.exe"; Description: "PDF2MD starten"; Flags: nowait postinstall skipifsilent
