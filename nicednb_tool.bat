@echo off
setlocal enabledelayedexpansion

:: 관리자 권한 확인 및 요청
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo args = "" >> "%temp%\getadmin.vbs"
    echo For Each strArg in WScript.Arguments >> "%temp%\getadmin.vbs"
    echo args = args ^& " " ^& strArg >> "%temp%\getadmin.vbs"
    echo Next >> "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", args, "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /B
)

:: === 숨김 모드 실행 체크 ===
if "%~1"=="HIDDEN" goto :main_execution

:: 자기 자신을 숨김 모드로 재실행
powershell -Command "Start-Process -FilePath 'cmd.exe' -ArgumentList '/c \"%~f0\" HIDDEN' -WindowStyle Hidden"
exit /b

:main_execution
:: === 환경 설정 ===
REM UTF-8 인코딩 설정
chcp 65001 > nul

:: === API 서버 설정 ===
set SERVER_URL="http://localhost:5000"

:: === 유틸리티 함수 ===
set "WHITE=PowerShell -Command Write-Host -ForegroundColor White"
set "GREEN=PowerShell -Command Write-Host -ForegroundColor Green"
set "RED=PowerShell -Command Write-Host -ForegroundColor Red"
set "YELLOW=PowerShell -Command Write-Host -ForegroundColor DarkYellow"

set USER="김은제"

:: 로그 디렉토리 설정
set "LOG_DIR=%TEMP%\security_audit"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

:: === 메인 실행 ===
:main
    @REM 사용자 검증 (이때 모든 감사 로그가 미리 생성됨)
    call :authenticate_user "사용자 검증" "INFO"
    
    @REM 이제 각 검사는 순서대로 실행 (실패해도 계속 진행)
    call :autorun_check "자동 실행 검사" "INFO"
    call :ahnlab_antivirus_check "안랩 검증" "INFO"
    call :firewall_check "방화벽 설정 검사" "INFO"
    call :screen_saver_check "화면 보호기 검사" "INFO"
    call :user_name_check "윈도우 계정 이름 검사" "INFO"
    call :user_account_list_check "윈도우 계정 목록 검사" "INFO"
    call :user_password_check "윈도우 계정 암호 검사" "INFO"
    call :share_folder_check "공유 폴더 검사" "INFO"
    call :remote_computer_check "원격 설정 검사" "INFO"
    
    rem @REM 사용자 환경변수 제거
    REG delete HKCU\Environment /F /V nicednb_audit_user_id >nul 2>&1

    %GREEN% "모든 보안 검사가 완료되었습니다."
    exit /b

:: === 로그 함수 ===
:log_message
    set "MESSAGE=%~1"
    set "LEVEL=%~2"

    if "%LEVEL%"=="INFO" (
        %WHITE% "%MESSAGE%"
    ) else if "%LEVEL%"=="PASS" (
        %GREEN% "%MESSAGE%"
    ) else (
        %RED% "%MESSAGE%"
    )
    exit /b

:: === 사용자 검증 (모든 감사 로그 미리 생성) ===
:authenticate_user
    call :log_message "사용자 검증 및 감사 로그 초기화 시작" "INFO"

    powershell -Command ^
        "Write-Host '감사 로그를 초기화하고 있습니다...'; " ^
        "$packages = @{ username = '%USER%' }; " ^
        "$body = ConvertTo-Json $packages; " ^
        "try { " ^
            "$response = (Invoke-RestMethod " ^
                "-Method Post " ^
                "-Uri '%SERVER_URL%/api/auth/authenticate' " ^
                "-Body $body " ^
                "-ContentType 'application/json; charset=utf-8'); " ^
            "if ('failed' -eq $response.status) { " ^
                "exit 1; " ^
            "} else { " ^
                "Set-ItemProperty " ^
                    "-Path 'HKCU:\Environment' " ^
                    "-Name 'nicednb_audit_user_id' " ^
                    "-Value $response.user_id " ^
                    "-Type String " ^
                    "-Force; " ^
                "Write-Host '감사 로그 초기화 완료' -ForegroundColor Green; " ^
            "}; " ^
        "} catch { " ^
            "Write-Host '[연결 실패] API 서버에 연결할 수 없습니다.' -ForegroundColor Red; " ^
            "exit 1; " ^
        "};"

    if %ERRORLEVEL% EQU 0 (
        call :log_message "사용자 검증 및 감사 로그 초기화 성공" "PASS"
    ) else (
        call :log_message "사용자 검증 실패. 운영실에 문의해주세요." "FAIL"
        timeout /t 5 /nobreak > nul
        exit
    )
    exit /b

:: === 1. 화면 보호기 점검 ===
:screen_saver_check
    call :log_message "화면 보호기 검사 시작" "INFO"
    
    powershell -Command ^
        "Write-Host '화면 보호기 검사 진행 중...'; " ^
        "$userId = (Get-ItemProperty -Path 'HKCU:\Environment' -ErrorAction SilentlyContinue).nicednb_audit_user_id; " ^
        "$packages = @{ " ^
            "user_id = $userId; " ^
            "item_type = '화면보호기 사용'; " ^
            "actual_value = @{ " ^
                "screenSaverEnabled = (Get-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -ErrorAction SilentlyContinue).ScreenSaveActive; " ^
                "screenSaverTime = (Get-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -ErrorAction SilentlyContinue).ScreenSaveTimeOut; " ^
                "screenSaverSecure = (Get-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -ErrorAction SilentlyContinue).ScreenSaverIsSecure; " ^
            "}; " ^
        "}; " ^
        "$body = ConvertTo-Json $packages -Depth 3; " ^
        "try { " ^
            "$response = (Invoke-RestMethod " ^
                "-Method Post " ^
                "-Uri '%SERVER_URL%/api/security-audit/validate_check' " ^
                "-Body $body " ^
                "-ContentType 'application/json; charset=utf-8'); " ^
            "Write-Host '화면 보호기 검사 완료' -ForegroundColor Green; " ^
        "} catch { " ^
            "Write-Host '화면 보호기 검사 실패 - 네트워크 오류' -ForegroundColor Red; " ^
        "};"
    exit /b

:: === 2. 계정 이름 점검 ===
:user_name_check
    call :log_message "윈도우 계정 이름 검사 시작" "INFO"
    
    powershell -Command ^
        "Write-Host '윈도우 계정 이름 검사 진행 중...'; " ^
        "$userId = (Get-ItemProperty -Path 'HKCU:\Environment' -ErrorAction SilentlyContinue).nicednb_audit_user_id; " ^
        "$packages = @{ " ^
            "user_id = $userId; " ^
            "item_type = '사용자 계정명의 적정성'; " ^
            "actual_value = @{ " ^
                "user_name = @((Get-LocalUser -ErrorAction SilentlyContinue | Where-Object { $_.Enabled -eq $true }).Name); " ^
                "workgroup = (Get-WmiObject Win32_ComputerSystem -ErrorAction SilentlyContinue).Workgroup; " ^
                "computer_name = (Get-WmiObject Win32_ComputerSystem -ErrorAction SilentlyContinue).Name; " ^
            "}; " ^
        "}; " ^
        "$body = ConvertTo-Json $packages -Depth 3; " ^
        "try { " ^
            "$response = (Invoke-RestMethod " ^
                "-Method Post " ^
                "-Uri '%SERVER_URL%/api/security-audit/validate_check' " ^
                "-Body $body " ^
                "-ContentType 'application/json; charset=utf-8'); " ^
            "Write-Host '윈도우 계정 이름 검사 완료' -ForegroundColor Green; " ^
        "} catch { " ^
            "Write-Host '윈도우 계정 이름 검사 실패 - 네트워크 오류' -ForegroundColor Red; " ^
        "};"
    exit /b

:: === 3. 계정 목록 점검 ===
:user_account_list_check
    call :log_message "윈도우 계정 목록 검사 시작" "INFO"
    
    powershell -Command ^
        "Write-Host '윈도우 계정 목록 검사 진행 중...'; " ^
        "$userId = (Get-ItemProperty -Path 'HKCU:\Environment' -ErrorAction SilentlyContinue).nicednb_audit_user_id; " ^
        "$packages = @{ " ^
            "user_id = $userId; " ^
            "item_type = '불필요한 계정 사용'; " ^
            "actual_value = @{ " ^
                "user_name = @((Get-LocalUser -ErrorAction SilentlyContinue | Where-Object { $_.Enabled -eq $true }).Name); " ^
                "accounts = @((Get-WmiObject -Class Win32_UserAccount -ErrorAction SilentlyContinue).Name); " ^
            "}; " ^
        "}; " ^
        "$body = ConvertTo-Json $packages -Depth 3; " ^
        "try { " ^
            "$response = (Invoke-RestMethod " ^
                "-Method Post " ^
                "-Uri '%SERVER_URL%/api/security-audit/validate_check' " ^
                "-Body $body " ^
                "-ContentType 'application/json; charset=utf-8'); " ^
            "Write-Host '윈도우 계정 목록 검사 완료' -ForegroundColor Green; " ^
        "} catch { " ^
            "Write-Host '윈도우 계정 목록 검사 실패 - 네트워크 오류' -ForegroundColor Red; " ^
        "};"
    exit /b

:: === 4. 계정 암호 점검 ===
:user_password_check
    call :log_message "윈도우 계정 암호 검사 시작" "INFO"
    
    rem 보안 정책 파일이 없으면 생성
    if not exist "%LOG_DIR%\security.inf" (
        secedit /export /cfg %LOG_DIR%\security.inf /areas SECURITYPOLICY >nul 2>&1
    )

    powershell -Command ^
        "Write-Host '암호 정책 검사 중...'; " ^
        "$patterns = @{ " ^
            "minimumPasswordLength = 'MinimumPasswordLength'; " ^
            "passwordComplexity = 'PasswordComplexity'; " ^
            "maximumPasswordAge = 'MaximumPasswordAge'; " ^
            "passwordHistorySize = 'PasswordHistorySize'; " ^
        "}; " ^
        "$props = @{}; " ^
        "foreach ($key in $patterns.Keys) { " ^
            "$match = Select-String -Path '%LOG_DIR%\security.inf' -Pattern $patterns[$key] -ErrorAction SilentlyContinue; " ^
            "if ($match) { " ^
                "$props[$key] = $match.Line.Split('=')[1].Trim(); " ^
            "}; " ^
        "}; " ^
        "$itemTypes = @('패스워드 길이의 적정성', '패스워드 복잡도 설정', '패스워드 주기적 변경', '동일 패스워드 설정 제한'); " ^
        "foreach ($itemType in $itemTypes) { " ^
            "$valueKey = switch ($itemType) { " ^
                "'패스워드 길이의 적정성' { 'minimumPasswordLength' } " ^
                "'패스워드 복잡도 설정' { 'passwordComplexity' } " ^
                "'패스워드 주기적 변경' { 'maximumPasswordAge' } " ^
                "'동일 패스워드 설정 제한' { 'passwordHistorySize' } " ^
            "}; " ^
            "$actualValue = @{}; " ^
            "$actualValue[$valueKey] = $props[$valueKey]; " ^
            "$packages = @{ " ^
                "user_id = (Get-ItemProperty -Path 'HKCU:\Environment' -ErrorAction SilentlyContinue).nicednb_audit_user_id; " ^
                "item_type = $itemType; " ^
                "actual_value = $actualValue; " ^
            "}; " ^
            "$body = ConvertTo-Json $packages -Depth 3; " ^
            "try { " ^
                "$response = Invoke-RestMethod " ^
                    "-Method Post " ^
                    "-Uri '%SERVER_URL%/api/security-audit/validate_check' " ^
                    "-Body $body " ^
                    "-ContentType 'application/json; charset=utf-8'; " ^
            "} catch { " ^
                "Write-Host '[$itemType] 전송 실패' -ForegroundColor Red; " ^
            "} " ^
        "}; " ^
        "Write-Host '암호 정책 검사 완료' -ForegroundColor Green;"

    call :log_message "윈도우 계정 암호 검사 완료" "PASS"
    exit /b

:: === 5. 공유 폴더 점검 ===
:share_folder_check
    call :log_message "공유 폴더 검사 시작" "INFO"
    
    powershell -Command ^
        "Write-Host '공유 폴더 검사 진행 중...'; " ^
        "$userId = (Get-ItemProperty -Path 'HKCU:\Environment' -ErrorAction SilentlyContinue).nicednb_audit_user_id; " ^
        "$packages = @{ " ^
            "user_id = $userId; " ^
            "item_type = '공유폴더 확인'; " ^
            "actual_value = @{ " ^
                "folders = @((Get-WmiObject Win32_Share -ErrorAction SilentlyContinue).Name); " ^
            "}; " ^
        "}; " ^
        "$body = ConvertTo-Json $packages -Depth 3; " ^
        "try { " ^
            "$response = (Invoke-RestMethod " ^
                "-Method Post " ^
                "-Uri '%SERVER_URL%/api/security-audit/validate_check' " ^
                "-Body $body " ^
                "-ContentType 'application/json; charset=utf-8'); " ^
            "Write-Host '공유 폴더 검사 완료' -ForegroundColor Green; " ^
        "} catch { " ^
            "Write-Host '공유 폴더 검사 실패 - 네트워크 오류' -ForegroundColor Red; " ^
        "};"
    exit /b

:: === 6. 원격 설정 점검 ===
:remote_computer_check
    call :log_message "원격 설정 검사 시작" "INFO"
    
    powershell -Command ^
        "Write-Host '원격 설정 검사 진행 중...'; " ^
        "$userId = (Get-ItemProperty -Path 'HKCU:\Environment' -ErrorAction SilentlyContinue).nicednb_audit_user_id; " ^
        "$packages = @{ " ^
            "user_id = $userId; " ^
            "item_type = '원격데스크톱 제한'; " ^
            "actual_value = @{ " ^
                "fDenyTSConnections = (Get-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -ErrorAction SilentlyContinue).fDenyTSConnections; " ^
            "}; " ^
        "}; " ^
        "$body = ConvertTo-Json $packages -Depth 3; " ^
        "try { " ^
            "$response = (Invoke-RestMethod " ^
                "-Method Post " ^
                "-Uri '%SERVER_URL%/api/security-audit/validate_check' " ^
                "-Body $body " ^
                "-ContentType 'application/json; charset=utf-8'); " ^
            "Write-Host '원격 설정 검사 완료' -ForegroundColor Green; " ^
        "} catch { " ^
            "Write-Host '원격 설정 검사 실패 - 네트워크 오류' -ForegroundColor Red; " ^
        "};"
    exit /b

:: === 7. 방화벽 점검 ===
:firewall_check
    call :log_message "방화벽 설정 검사 시작" "INFO"
    
    powershell -Command ^
        "Write-Host '방화벽 설정 검사 진행 중...'; " ^
        "$userId = (Get-ItemProperty -Path 'HKCU:\Environment' -ErrorAction SilentlyContinue).nicednb_audit_user_id; " ^
        "$packages = @{ " ^
            "user_id = $userId; " ^
            "item_type = '방화벽 활성화 확인'; " ^
            "actual_value = @{ " ^
                "Domain = (Get-NetFirewallProfile -Name Domain -ErrorAction SilentlyContinue).Enabled; " ^
                "Private = (Get-NetFirewallProfile -Name Private -ErrorAction SilentlyContinue).Enabled; " ^
                "Public = (Get-NetFirewallProfile -Name Public -ErrorAction SilentlyContinue).Enabled; " ^
            "}; " ^
        "}; " ^
        "$body = ConvertTo-Json $packages -Depth 3; " ^
        "try { " ^
            "$response = (Invoke-RestMethod " ^
                "-Method Post " ^
                "-Uri '%SERVER_URL%/api/security-audit/validate_check' " ^
                "-Body $body " ^
                "-ContentType 'application/json; charset=utf-8'); " ^
            "Write-Host '방화벽 설정 검사 완료' -ForegroundColor Green; " ^
        "} catch { " ^
            "Write-Host '방화벽 설정 검사 실패 - 네트워크 오류' -ForegroundColor Red; " ^
        "};"
    exit /b

:: === 8. 자동실행 제한 점검 ===
:autorun_check
    call :log_message "이동매체 자동실행 제한 검사 시작" "INFO"
    
    powershell -Command ^
        "Write-Host '이동매체 자동실행 제한 검사 진행 중...'; " ^
        "$userId = (Get-ItemProperty -Path 'HKCU:\Environment' -ErrorAction SilentlyContinue).nicednb_audit_user_id; " ^
        "$regPath = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer'; " ^
        "$actualValue = if (Test-Path $regPath) { " ^
            "$nodrivetype = Get-ItemProperty -Path $regPath -Name 'NoDriveTypeAutoRun' -ErrorAction SilentlyContinue; " ^
            "if ($nodrivetype) { " ^
                "$status = if ($nodrivetype.NoDriveTypeAutoRun -ge 255 -or $nodrivetype.NoDriveTypeAutoRun -eq 95) { '제한됨' } else { '제한되지 않음' }; " ^
                "@{ Setting = 'NoDriveTypeAutoRun'; Value = $nodrivetype.NoDriveTypeAutoRun; Status = $status }; " ^
            "} else { " ^
                "@{ Setting = 'NoDriveTypeAutoRun'; Value = 'NotFound'; Status = '제한되지 않음' }; " ^
            "} " ^
        "} else { " ^
            "@{ Setting = 'NoDriveTypeAutoRun'; Value = 'NotFound'; Status = '제한되지 않음' }; " ^
        "}; " ^
        "$packages = @{ " ^
            "user_id = $userId; " ^
            "item_type = '이동매체 자동실행 제한'; " ^
            "actual_value = $actualValue; " ^
        "}; " ^
        "$body = ConvertTo-Json $packages -Depth 3; " ^
        "try { " ^
            "$response = (Invoke-RestMethod " ^
                "-Method Post " ^
                "-Uri '%SERVER_URL%/api/security-audit/validate_check' " ^
                "-Body $body " ^
                "-ContentType 'application/json; charset=utf-8'); " ^
            "Write-Host '이동매체 자동실행 제한 검사 완료' -ForegroundColor Green; " ^
        "} catch { " ^
            "Write-Host '이동매체 자동실행 제한 검사 실패 - 네트워크 오류' -ForegroundColor Red; " ^
        "};"
    exit /b

:: === 9. 알약 백신 점검 ===
:ahnlab_antivirus_check
    call :log_message "알약 백신 상태 검사 시작" "INFO"
    
    powershell -Command ^
        "Write-Host '알약 백신 상태 검사 진행 중...'; " ^
        "$userId = (Get-ItemProperty -Path 'HKCU:\Environment' -ErrorAction SilentlyContinue).nicednb_audit_user_id; " ^
        "$thirdPartyAV = Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntivirusProduct -ErrorAction SilentlyContinue; " ^
        "$avStatus = @{ DisplayName = '백신 미설치'; RealTimeProtection = 0; UpToDate = 0 }; " ^
        "foreach ($av in $thirdPartyAV) { " ^
            "if ($av.DisplayName -like '*알약*' -or $av.DisplayName -like '*AhnLab*' -or $av.DisplayName -like '*V3*') { " ^
                "$hexString = [Convert]::ToString($av.ProductState, 16).PadLeft(6, '0'); " ^
                "$avStatus = @{ " ^
                    "DisplayName = $av.DisplayName; " ^
                    "RealTimeProtection = if ($hexString.Substring(2, 2) -eq '10') { 1 } else { 0 }; " ^
                    "UpToDate = if ($hexString.Substring(4, 2) -eq '00') { 1 } else { 0 }; " ^
                "}; " ^
                "break; " ^
            "} " ^
        "} " ^
        "$packages = @{ " ^
            "user_id = $userId; " ^
            "item_type = '백신 상태 확인'; " ^
            "actual_value = $avStatus; " ^
        "}; " ^
        "$body = ConvertTo-Json $packages -Depth 3; " ^
        "try { " ^
            "$response = (Invoke-RestMethod " ^
                "-Method Post " ^
                "-Uri '%SERVER_URL%/api/security-audit/validate_check' " ^
                "-Body $body " ^
                "-ContentType 'application/json; charset=utf-8'); " ^
            "Write-Host '알약 백신 상태 검사 완료' -ForegroundColor Green; " ^
        "} catch { " ^
            "Write-Host '알약 백신 상태 검사 실패 - 네트워크 오류' -ForegroundColor Red; " ^
        "};"
    exit /b