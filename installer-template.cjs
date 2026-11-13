'use strict';
function installer(config){return String.raw`#define AppName "${config.name}"
#define AppExe "${config.exe}"
#define AppVersion "${config.version}"
[Setup]
AppId={{${config.appId}}
AppName={#AppName}
AppVersion={#AppVersion}
VersionInfoVersion=${config.version}.0
AppPublisher=${config.creator||'Zeruik / TechABJ'}
AppCopyright=Copyright 2026 ${config.creator||'Zeruik / TechABJ'}
VersionInfoCompany=${config.studio||'ZTH Studio'}
VersionInfoDescription=${config.displayName||config.name} / ${config.name}
AppPublisherURL=mailto:zeruik@qq.com
DefaultDirName={code:DefaultInstallFolder}
DefaultGroupName={#AppName}
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir=.
OutputBaseFilename=Install-${config.folder}-v${config.version}
Compression=lzma2/fast
SolidCompression=yes
WizardStyle=modern
DisableWelcomePage=no
DisableDirPage=no
DisableProgramGroupPage=yes
ShowLanguageDialog=no
UsePreviousLanguage=yes
UsePreviousAppDir=yes
LicenseFile=LICENSE
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\{#AppExe}
UninstallFilesDir={app}\uninstall
CloseApplications=no
RestartApplications=no
[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"
[Messages]
chinesesimp.WelcomeLabel1=欢迎使用 ${config.displayName||config.name}
chinesesimp.WelcomeLabel2=${config.studio||'ZTH Studio'} · ${config.parentStudio||''}旗下子工作室%n创作者与权利人：${config.creator||'TechABJ'}%n%n本安装包已包含 Electron 与 Python 便携运行环境，安装和运行助手无需另外安装 Node.js、Python 或浏览器。%n%n安装器不会修改 PATH、注册系统 Python 或安装全局依赖。网站发布和 DNS 查询需要您明确操作后才联网。%n%n请使用英文安装路径。运行时与个人数据均保存在所选安装目录。data 子文件夹卸载时保留。请勿选择 Program Files 等不可写位置。
english.WelcomeLabel1=Welcome to {#AppName}
english.WelcomeLabel2=${config.studio||'ZTH Studio'}, a subsidiary studio of ${config.parentStudio||''}.%nCreator and rightsholder: ${config.creator||'TechABJ'}%n%nElectron and portable Python runtimes are included. No separate Node.js, Python or browser is needed.%n%nSetup does not edit PATH or register global Python. Website publishing and DNS checks need explicit user actions.%n%nUse an English installation path. Runtimes and personal data stay inside the installation folder; data is retained on uninstall. Choose a writable folder outside Program Files.
[CustomMessages]
chinesesimp.StartMenu=创建开始菜单快捷方式
english.StartMenu=Create a Start menu shortcut
chinesesimp.Launch=打开 {#AppName}
english.Launch=Open {#AppName}
[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"
Name: "startmenu"; Description: "{cm:StartMenu}"
[Dirs]
Name: "{app}\data"; Flags: uninsneveruninstall
[Files]
Source: "payload\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; WorkingDir: "{app}"; AppUserModelID: "${config.id}"; Tasks: desktopicon
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"; WorkingDir: "{app}"; AppUserModelID: "${config.id}"; Tasks: startmenu
[Run]
Filename: "{app}\{#AppExe}"; Description: "{cm:Launch}"; Flags: postinstall nowait skipifsilent
[Code]
const UninstallKey = 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{${config.appId}}_is1';
function Tr(const ZH, EN: String): String;
begin if ActiveLanguage = 'english' then Result := EN else Result := ZH; end;
function EnglishPath(const Value: String): Boolean;
var I: Integer;
begin
 Result := (Length(Value) > 3) and (Value[2] = ':') and (Value[3] = '\');
 if not Result then Exit;
 for I := 1 to Length(Value) do if (Ord(Value[I]) < 32) or (Ord(Value[I]) > 126) then Result := False;
 if Pos('..',Value) > 0 then Result := False;
end;
function DefaultInstallFolder(Param: String): String;
begin
 Result := ExpandConstant('{localappdata}\Programs\') + '${config.folder}';
 if not EnglishPath(Result) then Result := ExpandConstant('{sd}\') + '${config.folder}';
end;
function GetFileAttributesW(FileName: String): LongWord; external 'GetFileAttributesW@kernel32.dll stdcall';
function CanonicalDirectory(const Value: String): String;
begin Result := Value; while (Length(Result)>3) and (Result[Length(Result)]='\') do Delete(Result,Length(Result),1); end;
function Within(const Child, Parent: String): Boolean;
var A,B:String;
begin A:=Lowercase(CanonicalDirectory(Child));B:=Lowercase(CanonicalDirectory(Parent));Result:=(A=B) or (Pos(B+'\',A)=1);end;
function RegisteredDirectory: String;
begin
 Result := '';
 if RegQueryStringValue(HKCU64,UninstallKey,'InstallLocation',Result) then Exit;
 if RegQueryStringValue(HKCU32,UninstallKey,'InstallLocation',Result) then Exit;
 if RegQueryStringValue(HKLM64,UninstallKey,'InstallLocation',Result) then Exit;
 RegQueryStringValue(HKLM32,UninstallKey,'InstallLocation',Result);
end;
function PathProblem(const Value: String): String;
var Cursor,Probe:String; Attributes:LongWord; Counter:Integer;
begin
 Result := '';
 if not EnglishPath(Value) then begin Result:=Tr('请选择英文绝对路径（允许空格）。','Choose an English absolute path; spaces are allowed.');Exit;end;
 if Within(Value,ExpandConstant('{win}')) or Within(Value,ExpandConstant('{commonpf}')) or Within(Value,ExpandConstant('{commonpf32}')) then begin Result:=Tr('此软件将数据写入安装目录。请改选当前账户可写的普通文件夹，不要选 Windows 或 Program Files。','This app writes data beside its executable. Choose a normal writable folder outside Windows and Program Files.');Exit;end;
 Cursor:=Value;
 while Length(Cursor)>3 do begin
  if DirExists(Cursor) then begin Attributes:=GetFileAttributesW(Cursor);if (Attributes and $400)<>0 then begin Result:=Tr('安装路径不能经过目录联接或符号链接，请选择普通文件夹。','Install paths cannot traverse junctions or symbolic links. Choose a normal folder.');Exit;end;end;
  Cursor:=ExtractFileDir(Cursor);
 end;
 if not ForceDirectories(Value) then begin Result:=Tr('无法创建安装目录，请检查写入权限。','Cannot create the installation folder. Check write permissions.');Exit;end;
 Counter:=0;repeat Probe:=AddBackslash(Value)+'.zth-install-write-'+IntToStr(Counter)+'.tmp';Counter:=Counter+1;until (not FileExists(Probe)) or (Counter>100);
 if (Counter>100) or (not SaveStringToFile(Probe,'ZTH permission probe',False)) then begin Result:=Tr('安装目录不可写，请选择当前账户可读写的文件夹。','Installation folder is not writable by this account.');Exit;end;
 if not DeleteFile(Probe) then begin Result:=Tr('无法删除权限检测文件，请检查目录权限后重试。','Cannot remove the write probe. Check folder permissions before retrying.');Exit;end;
end;
function MigrationProblem(const Target: String): String;
var OldDir:String;OldMarker,NewMarker:AnsiString;
begin
 Result:='';OldDir:=RegisteredDirectory;
 if (OldDir='') or (CompareText(CanonicalDirectory(OldDir),CanonicalDirectory(Target))=0) then Exit;
 if (not LoadStringFromFile(AddBackslash(OldDir)+'data\installation-id.json',OldMarker)) or
    (not LoadStringFromFile(AddBackslash(Target)+'data\installation-id.json',NewMarker)) or
    (Length(Trim(OldMarker))<40) or (Length(OldMarker)>512) or
    (Trim(OldMarker)<>Trim(NewMarker)) or (not FileExists(AddBackslash(Target)+'{#AppExe}')) then
  Result:=Tr('检测到另一个安装目录。为防止存档看似丢失，不能直接换目录。请退出安装，先正常启动旧版本生成存储标识，再关闭并完整复制旧文件夹（包含 data）到目标目录，随后重新运行安装器。原目录必须仍可读取；本安装器不会自动迁移或删除它。','A different installation directory is registered. To avoid losing sight of your data, exit Setup, launch the old app once, close it, and copy its entire folder including data to the target. Then run Setup again. The original folder must remain readable. Setup does not migrate or delete it.');
end;

function Newer(const Version: String): Boolean;
var Existing,Current: Int64;
begin
 Result := StrToVersion(Version,Existing) and StrToVersion('{#AppVersion}',Current);
 if Result then Result := ComparePackedVersion(Existing,Current) > 0;
end;
function RegisteredNewer: Boolean;
var Version: String;
begin
 Result := (RegQueryStringValue(HKCU64,UninstallKey,'DisplayVersion',Version) and Newer(Version)) or
 (RegQueryStringValue(HKCU32,UninstallKey,'DisplayVersion',Version) and Newer(Version)) or
 (RegQueryStringValue(HKLM64,UninstallKey,'DisplayVersion',Version) and Newer(Version)) or
 (RegQueryStringValue(HKLM32,UninstallKey,'DisplayVersion',Version) and Newer(Version));
end;
function RunningError: String;
var Locator,Services,Processes: Variant;
begin
 Result := '';
 try
  Locator := CreateOleObject('WbemScripting.SWbemLocator');
  Services := Locator.ConnectServer('.', 'root\CIMV2');
  Processes := Services.ExecQuery('SELECT ProcessId FROM Win32_Process WHERE Name="{#AppExe}"');
  if Processes.Count > 0 then Result := Tr('请先保存并正常退出应用，再重试。安装器不会强制关闭应用。','Save and exit the application, then retry. Setup will not force it to close.');
 except
  Result := Tr('无法检查应用运行状态；尚未覆盖文件，请检查 Windows 管理服务。','Cannot check application state. Files were not overwritten; check Windows management services.');
 end;
 if Result <> '' then Log('APP_RUNNING_OR_CHECK_UNAVAILABLE');
end;
function InitializeSetup: Boolean;
begin
 Result := not RegisteredNewer;
 if not Result then begin Log('DOWNGRADE_BLOCKED');if not WizardSilent then MsgBox(Tr('已安装更新版本，禁止降级覆盖。','A newer version is installed. Downgrade is blocked.'),mbError,MB_OK);end;
end;
procedure InitializeWizard;
var Notice:TNewStaticText;
begin
 Notice := TNewStaticText.Create(WizardForm);Notice.Parent := WizardForm.SelectDirPage;
 Notice.SetBounds(ScaleX(0),ScaleY(148),WizardForm.SelectDirPage.Width,ScaleY(60));
 Notice.WordWrap := True;Notice.AutoSize := False;
 Notice.Caption := Tr('请使用英文绝对路径（允许空格）。'+#13#10+'运行时与 data 存档均在安装目录；卸载保留 data。'+#13#10+'安装器不修改 PATH。升级沿用旧目录；迁移前完整备份。','Use an English absolute path; spaces are allowed.'+#13#10+'Runtimes and data stay here. Uninstall retains data.'+#13#10+'PATH is unchanged. Upgrade in place; copy before moving.');
end;
function PrepareToInstall(var NeedsRestart: Boolean): String;
var Version:String;
begin
 Result := '';
 if not EnglishPath(ExpandConstant('{app}')) then begin Result := Tr('安装路径必须为英文绝对路径。','Choose an English absolute installation path.');Log('ENGLISH_PATH_REQUIRED');Exit;end;
 if RegisteredNewer or (GetVersionNumbersString(ExpandConstant('{app}\{#AppExe}'),Version) and Newer(Version)) then begin Result := 'DOWNGRADE_BLOCKED';Exit;end;
 Result := MigrationProblem(ExpandConstant('{app}'));if Result<>'' then begin Log('MIGRATION_NOT_VERIFIED');Exit;end;
 Result := PathProblem(ExpandConstant('{app}'));if Result<>'' then begin Log('INSTALL_PATH_UNWRITABLE');Exit;end;
 if DirExists(ExpandConstant('{app}\data')) then begin Result:=PathProblem(ExpandConstant('{app}\data'));if Result<>'' then Exit;end;
 Result := RunningError;
end;
function InitializeUninstall: Boolean;
var Error:String;
begin
 Error := RunningError;Result := Error = '';
 if (not Result) and (not UninstallSilent) then MsgBox(Error,mbError,MB_OK);
end;
`;}
module.exports={installer};
