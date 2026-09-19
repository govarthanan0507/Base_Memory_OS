; Inno Setup script for Base Memory OS.
;
; Build (on Windows, after PyInstaller has produced dist\BaseMemoryOS.exe):
;   iscc packaging\installer.iss
;
; Produces dist\installer\BaseMemoryOS-Setup.exe - a normal Windows
; installer with a Start Menu entry, Desktop shortcut, and an
; uninstall entry in "Apps & features". No Python/pip/Git/terminal
; is required on the end user's machine; BaseMemoryOS.exe already
; bundles its own runtime.

#define MyAppName "Base Memory OS"
#define MyAppVersion "0.1.0"
#define MyAppExeName "BaseMemoryOS.exe"

[Setup]
AppId={{B8B9B6D2-6C7B-4B1A-9E9E-BASEMEMORYOS1}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\dist\installer
OutputBaseFilename=BaseMemoryOS-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Files]
Source: "..\dist\BaseMemoryOS.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
