; Inno Setup Script for KrosDownloadManager

#define MyAppName "KrosDownloadManager"
#define MyAppVersion "1.0"
#define MyAppPublisher "iSekro"
#define MyAppURL "https://github.com/iSekro/krosdownloadmanager"
#define MyAppExeName "KrosDownloadManager.exe"

[Setup]
AppId={{8A3D7F2E-5B1C-4E9A-A2D6-3F8B7C1E9D4A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=installer_output
OutputBaseFilename=KrosDownloadManager_Setup
SetupIconFile=src\krosdownloadmanager\assets\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}

DisableProgramGroupPage=yes


[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Iconos adicionales:"
Name: "startupicon"; Description: "Iniciar con Windows"; GroupDescription: "Opciones:"
Name: "installextension"; Description: "Instalar extension del navegador (Chrome/Edge) para captura de descargas y videos"; GroupDescription: "Extension del navegador:"

[Files]
Source: "dist\KrosDownloadManager.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "extension\*"; DestDir: "{app}\extension"; Flags: ignoreversion recursesubdirs createallsubdirs; Tasks: installextension
Source: "src\krosdownloadmanager\assets\icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "src\krosdownloadmanager\assets\icon.png"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Ejecutar {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: """{app}\{#MyAppExeName}"""; Flags: uninsdeletevalue; Tasks: startupicon
Root: HKCU; Subkey: "Software\{#MyAppName}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\{#MyAppName}"; ValueType: string; ValueName: "ExtensionPath"; ValueData: "{app}\extension"; Flags: uninsdeletekey; Tasks: installextension

[Code]
procedure InstallChromeExtension();
var
  ExtPath: String;
  JsonContent: String;
  ManifestPath: String;
  AppExePath: String;
begin
  ExtPath := ExpandConstant('{app}\extension');
  ManifestPath := ExtPath + '\native_messaging_host.json';

  AppExePath := ExpandConstant('{app}\KrosDownloadManager.exe');
  StringChange(AppExePath, '\', '\\');

  JsonContent := '{' + #13#10 +
    '  "name": "com.krosdownloadmanager.host",' + #13#10 +
    '  "description": "KrosDownloadManager Native Messaging Host",' + #13#10 +
    '  "path": "' + AppExePath + '",' + #13#10 +
    '  "type": "stdio",' + #13#10 +
    '  "allowed_origins": [' + #13#10 +
    '    "chrome-extension://*/"' + #13#10 +
    '  ]' + #13#10 +
    '}';

  SaveStringToFile(ManifestPath, JsonContent, False);

  RegWriteStringValue(HKCU,
    'Software\Google\Chrome\NativeMessagingHosts\com.krosdownloadmanager.host',
    '', ManifestPath);

  RegWriteStringValue(HKCU,
    'Software\Microsoft\Edge\NativeMessagingHosts\com.krosdownloadmanager.host',
    '', ManifestPath);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    if IsTaskSelected('installextension') then
    begin
      InstallChromeExtension();
    end;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    RegDeleteKeyIncludingSubkeys(HKCU, 'Software\Google\Chrome\NativeMessagingHosts\com.krosdownloadmanager.host');
    RegDeleteKeyIncludingSubkeys(HKCU, 'Software\Microsoft\Edge\NativeMessagingHosts\com.krosdownloadmanager.host');
    RegDeleteKeyIncludingSubkeys(HKCU, 'Software\{#MyAppName}');
  end;
end;
