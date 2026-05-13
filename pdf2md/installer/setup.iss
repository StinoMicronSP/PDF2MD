[Setup]
AppName=PDF2MD
AppVersion=1.0
DefaultDirName={autopf}\PDF2MD
DefaultGroupName=PDF2MD
OutputBaseFilename=PDF2MD_Setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\PDF2MD_GUI\*"; DestDir: "{app}\PDF2MD_GUI"; Flags: recursesubdirs createallsubdirs
Source: "dist\PDF2MD_DragDrop\*"; DestDir: "{app}\PDF2MD_DragDrop"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\PDF2MD (GUI)"; Filename: "{app}\PDF2MD_GUI\PDF2MD_GUI.exe"
Name: "{commondesktop}\PDF2MD"; Filename: "{app}\PDF2MD_GUI\PDF2MD_GUI.exe"; Tasks: desktopicon

[Tasks]
Name: desktopicon; Description: "Bureaubladpictogram aanmaken"; GroupDescription: "Extra opties:"

[Registry]
; Rechtsklik op map → "Converteer naar Markdown"
Root: HKCR; Subkey: "Directory\shell\PDF2MD"; ValueType: string; ValueName: ""; ValueData: "Converteer naar Markdown"
Root: HKCR; Subkey: "Directory\shell\PDF2MD\command"; ValueType: string; ValueName: ""; ValueData: """{app}\PDF2MD_DragDrop\PDF2MD_DragDrop.exe"" ""%1"""
