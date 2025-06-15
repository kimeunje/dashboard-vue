@echo off

::  --> 관리자 권한 실행 코드
:-------------------------------------
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

if '%errorlevel%' NEQ '0' (
 goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
 echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
 echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"

"%temp%\getadmin.vbs"
 exit /B

:gotAdmin
 if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )
 pushd "%CD%"
 CD /D "%~dp0"
:--------------------------------------


::  --> UTF-8 인코딩 설정
:-------------------------------------
chcp 65001 > nul

::  --> 배치 파일 기본 설정
:-------------------------------------
TITLE %~n0
SETLOCAL enabledelayedexpansion
:-------------------------------------

::  --> 검사 후 조치
:-------------------------------------
CLS
ECHO.
ECHO * 주의사항 - 조치 중에는 키보드, 마우스를 움직이지 말아주세요.

ECHO.
echo ※ 윈도우 시스템 설정값 변경 ※
echo.

echo 1.1 화면보호기 설정, 잠금 설정, 10분 설정 완료
Reg add "HKEY_CURRENT_USER\Control Panel\Desktop" /v SCRNSAVE.EXE /t REG_SZ /d C:\\Windows\\System32\\scrnsave.scr /f | find /v "success"
Reg add "HKEY_CURRENT_USER\Control Panel\Desktop" /v ScreenSaveActive /t REG_SZ /d 1 /f | find /v "success"
Reg add "HKEY_CURRENT_USER\Control Panel\Desktop" /v ScreenSaverIsSecure /t REG_SZ /d 1 /f | find /v "success"
Reg add "HKEY_CURRENT_USER\Control Panel\Desktop" /v ScreenSaveTimeOut /t REG_SZ /d 600 /f | find /v "success"
echo.

echo 2.1 암호 복잡도 설정 완료
secedit /export /cfg "%temp%\secpol.cfg" > nul
powershell -Command "(Get-Content '%temp%\secpol.cfg') -replace 'PasswordComplexity = 0', 'PasswordComplexity = 1' | Set-Content '%temp%\secpol.cfg'"
secedit /configure /db %windir%\security\local.sdb /cfg "%temp%\secpol.cfg" /areas SECURITYPOLICY > nul
del "%temp%\secpol.cfg" > nul
echo.

echo 2.3 최소 암호 길이 8자리로 변경 완료
net accounts /minpwlen:8 | find /v "success"

echo 2.4 암호 복잡도 요구사항 활성화 완료
Reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Lsa" /v NoLMHash /t REG_DWORD /d 0x00000001 /f | find /v "success"

echo 2.5 최대 암호 사용 기간 90일로 변경 완료
net accounts /maxpwage:90 | find /v "success"

echo 2.7 최근 암호 기억 5개로 변경 완료
net accounts /uniquepw:5 | find /v "success"
echo.

echo 3.1 불필요한 공유폴더 삭제 완료 (C$, D$, E$, F$, ADMIN$ 제거, IPC$ 유지)
net share C$ /delete /y > nul 2>&1
net share D$ /delete /y > nul 2>&1
net share E$ /delete /y > nul 2>&1
net share F$ /delete /y > nul 2>&1
net share ADMIN$ /delete /y > nul 2>&1
Reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Lsa" /v restrictanonymous /t REG_DWORD /d 0x00000001 /f | find /v "success"
Reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" /v AutoShareServer /t REG_DWORD /d 0x00000000 /f | find /v "success"
Reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" /v AutoShareWks /t REG_DWORD /d 0x00000000 /f | find /v "success"
echo.

echo 3.3 원격데스크톱 해제 완료
Reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0x00000001 /f | find /v "success"
Reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" /v UserAuthentication /t REG_DWORD /d 0x00000001 /f | find /v "success"
echo.

echo 4.1 자동 로그온 비활성화 완료
Reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v AutoAdminLogon /t REG_SZ /d 0 /f | find /v "success"
Reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v DefaultPassword /f > nul 2>&1
echo.

echo 4.2 게스트 계정 비활성화 완료
net user guest /active:no > nul 2>&1
echo.

echo 4.3 불필요한 서비스 중지 완료
sc config RemoteRegistry start= disabled > nul 2>&1
sc stop RemoteRegistry > nul 2>&1
sc config TelNet start= disabled > nul 2>&1
sc stop TelNet > nul 2>&1
echo.

echo 5.1 Windows 업데이트 자동 설정 완료
Reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update" /v AUOptions /t REG_DWORD /d 0x00000004 /f | find /v "success"
echo.

echo 5.2 UAC 활성화 완료
Reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v EnableLUA /t REG_DWORD /d 0x00000001 /f | find /v "success"
Reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v ConsentPromptBehaviorAdmin /t REG_DWORD /d 0x00000002 /f | find /v "success"
echo.

echo 6.1 시스템 복원 활성화 완료
powershell -Command "Enable-ComputerRestore -Drive 'C:\'" > nul 2>&1
echo.

echo 6.2 방화벽 활성화 완료
netsh advfirewall set allprofiles state on > nul
echo.

TIMEOUT /t 2 > NUL
echo.
echo ※ 모든 보안 조치가 완료되었습니다. ※
echo ※ 시스템 재시작을 권장합니다. ※
:-------------------------------------

pause