Unicode true
!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "WinVer.nsh"
!include "x64.nsh"
Name "ZTH-平面设计器 / ZTH Design Studio"
OutFile "../release/ZTH-Design-Studio-1.0.0-Setup.exe"
InstallDir "$LOCALAPPDATA\Programs\ZTH Design Studio"
InstallDirRegKey HKCU "Software\ZeroToHand\DesignStudio" "InstallDir"
RequestExecutionLevel user
SetCompressor /SOLID lzma
!define MUI_ABORTWARNING
!define MUI_ICON "icon.ico"
!define MUI_UNICON "icon.ico"
!define MUI_FINISHPAGE_RUN "$INSTDIR\ZTH Design Studio.exe"
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "license.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "SimpChinese"
!insertmacro MUI_LANGUAGE "English"
Function .onInit
${IfNot} ${RunningX64}
 MessageBox MB_ICONSTOP "ZTH Design Studio requires 64-bit Windows. / 需要 64 位 Windows。"
 Abort
${EndIf}
!insertmacro MUI_LANGDLL_DISPLAY
${IfNot} ${AtLeastWin10}
 MessageBox MB_ICONSTOP "ZTH Design Studio requires Windows 10 or later. / 需要 Windows 10 或更新版本。"
 Abort
${EndIf}
FunctionEnd
Section "ZTH Design Studio"
 SetOutPath "$INSTDIR"
 File /r "../release/win-unpacked/*"
 File "icon.ico"
 WriteRegStr HKCU "Software\ZeroToHand\DesignStudio" "InstallDir" "$INSTDIR"
 WriteUninstaller "$INSTDIR\Uninstall.exe"
 CreateShortcut "$DESKTOP\ZTH-平面设计器.lnk" "$INSTDIR\ZTH Design Studio.exe" "" "$INSTDIR\icon.ico"
 CreateDirectory "$SMPROGRAMS\ZTH Design Studio"
 CreateShortcut "$SMPROGRAMS\ZTH Design Studio\ZTH-平面设计器.lnk" "$INSTDIR\ZTH Design Studio.exe" "" "$INSTDIR\icon.ico"
 CreateShortcut "$SMPROGRAMS\ZTH Design Studio\卸载 Uninstall.lnk" "$INSTDIR\Uninstall.exe"
 WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\ZTHDesignStudio" "DisplayName" "ZTH-平面设计器"
 WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\ZTHDesignStudio" "DisplayVersion" "1.0.0"
 WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\ZTHDesignStudio" "Publisher" "ZeroToHand Studio / TechABJ"
 WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\ZTHDesignStudio" "UninstallString" '"$INSTDIR\Uninstall.exe"'
 WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\ZTHDesignStudio" "DisplayIcon" "$INSTDIR\icon.ico"
 WriteRegStr HKCU "Software\Classes\.zthpmsj" "" "ZTHPosterProject"
 WriteRegStr HKCU "Software\Classes\ZTHPosterProject" "" "ZTH Poster Design Project"
 WriteRegStr HKCU "Software\Classes\ZTHPosterProject\shell\open\command" "" '"$INSTDIR\ZTH Design Studio.exe" "%1"'
SectionEnd
Section "Uninstall"
 Delete "$DESKTOP\ZTH-平面设计器.lnk"
 RMDir /r "$SMPROGRAMS\ZTH Design Studio"
 DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\ZTHDesignStudio"
 DeleteRegKey HKCU "Software\ZeroToHand\DesignStudio"
 DeleteRegKey HKCU "Software\Classes\ZTHPosterProject"
 DeleteRegKey HKCU "Software\Classes\.zthpmsj"
 ; Remove application files only. User projects and autosave data are retained.
 !include "uninstall-files.nsh"
SectionEnd
