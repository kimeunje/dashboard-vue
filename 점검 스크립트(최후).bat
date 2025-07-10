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
set SERVER_URL="http://172.30.1.63:5000"



rem @REM 사용자 환경변수 제거
REG delete HKCU\Environment /F /V nicednb_audit_user_id >nul 2>&1
REG delete HKCU\Environment /F /V NICEDNB_USER >nul 2>&1
del "%LOG_DIR%\security.inf" > nul 2>&1

:: 로그 디렉토리 설정
set "LOG_DIR=%TEMP%\security_audit"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

:: === 메인 실행 ===
:main
    @REM 모든 보안 검사를 통합하여 순서대로 실행
    call :run_all_security_checks
    
    rem @REM 임시 파일 정리
    del "%LOG_DIR%\security.inf" > nul 2>&1

    echo "모든 보안 검사가 완료되었습니다."
    exit /b


:: === 모든 보안 검사 통합 실행 ===
:run_all_security_checks
    echo 통합 보안 검사 시작

    rem 보안 정책 파일 생성 (패스워드 검사용)
    if not exist "%LOG_DIR%\security.inf" (
        secedit /export /cfg %LOG_DIR%\security.inf /areas SECURITYPOLICY >nul 2>&1
    )

    powershell -Command ^
        "Write-Host 'IP 기반 사용자 정보 조회 중...'; " ^
        "try { " ^
            "$ipResponse = (Invoke-RestMethod -Method GET -Uri '%SERVER_URL%/api/auth/ip-info' -ContentType 'application/json; charset=utf-8'); " ^
            "$clientIp = $ipResponse.client_ip; " ^
            "$ipCheckBody = @{ } | ConvertTo-Json; " ^
            "$userResponse = (Invoke-RestMethod -Method Post -Uri '%SERVER_URL%/api/auth/check-ip' -Body $ipCheckBody -ContentType 'application/json; charset=utf-8'); " ^
            "if ($userResponse.success) { $username = $userResponse.username; Write-Host '사용자 설정 완료: ' $username -ForegroundColor Green; } else { $username = '기본사용자'; Write-Host '사용자 설정 실패. 기본 사용자를 사용합니다.' -ForegroundColor Yellow; }; " ^
            "Write-Host '감사 로그를 초기화하고 있습니다...'; " ^
            "$authPackages = @{ username = $username }; " ^
            "$authBody = ConvertTo-Json $authPackages; " ^
            "$authResponse = (Invoke-RestMethod -Method Post -Uri '%SERVER_URL%/api/auth/authenticate' -Body $authBody -ContentType 'application/json; charset=utf-8'); " ^
            "if ('failed' -eq $authResponse.status) { Write-Host '사용자 검증 실패. 운영실에 문의해주세요.' -ForegroundColor Red; exit 1; }; " ^
            "$userId = $authResponse.user_id; " ^
            "Write-Host '사용자 검증 및 감사 로그 초기화 성공' -ForegroundColor Green; " ^
            "Write-Host 'User ID:' $userId -ForegroundColor Cyan; " ^
            "Write-Host '알약 백신 상태 검사 진행 중...'; " ^
            "$thirdPartyAV = Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntivirusProduct -ErrorAction SilentlyContinue; " ^
            "$avStatus = @{ DisplayName = '백신 미설치'; RealTimeProtection = 0; UpToDate = 0 }; " ^
            "foreach ($av in $thirdPartyAV) { if ($av.DisplayName -like '*알약*' -or $av.DisplayName -like '*AhnLab*' -or $av.DisplayName -like '*V3*') { $hexString = [Convert]::ToString($av.ProductState, 16).PadLeft(6, '0'); $avStatus = @{ DisplayName = $av.DisplayName; RealTimeProtection = if ($hexString.Substring(2, 2) -eq '10') { 1 } else { 0 }; UpToDate = if ($hexString.Substring(4, 2) -eq '00') { 1 } else { 0 }; }; break; } }; " ^
            "$avPackages = @{ user_id = $userId; item_type = '백신 상태 확인'; actual_value = $avStatus; }; " ^
            "$avBody = ConvertTo-Json $avPackages -Depth 3; " ^
            "Write-Host 'AV Body:' $avBody -ForegroundColor Yellow; " ^
            "try { $avResponse = (Invoke-RestMethod -Method Post -Uri '%SERVER_URL%/api/security-audit/validate_check' -Body $avBody -ContentType 'application/json; charset=utf-8'); Write-Host '알약 백신 상태 검사 완료' -ForegroundColor Green; } catch { Write-Host '알약 백신 상태 검사 실패:' $_.Exception.Message -ForegroundColor Red; }; " ^
            "Write-Host '화면 보호기 검사 진행 중...'; " ^
            "$screenPackages = @{ user_id = $userId; item_type = '화면보호기 사용'; actual_value = @{ screenSaverEnabled = (Get-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -ErrorAction SilentlyContinue).ScreenSaveActive; screenSaverTime = (Get-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -ErrorAction SilentlyContinue).ScreenSaveTimeOut; screenSaverSecure = (Get-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -ErrorAction SilentlyContinue).ScreenSaverIsSecure; }; }; " ^
            "$screenBody = ConvertTo-Json $screenPackages -Depth 3; " ^
            "try { $screenResponse = (Invoke-RestMethod -Method Post -Uri '%SERVER_URL%/api/security-audit/validate_check' -Body $screenBody -ContentType 'application/json; charset=utf-8'); Write-Host '화면 보호기 검사 완료' -ForegroundColor Green; } catch { Write-Host '화면 보호기 검사 실패 - 네트워크 오류' -ForegroundColor Red; }; " ^
            "Write-Host '암호 정책 검사 중...'; " ^
            "$patterns = @{ minimumPasswordLength = 'MinimumPasswordLength'; passwordComplexity = 'PasswordComplexity'; maximumPasswordAge = 'MaximumPasswordAge'; passwordHistorySize = 'PasswordHistorySize'; }; " ^
            "$props = @{}; " ^
            "foreach ($key in $patterns.Keys) { $match = Select-String -Path '%LOG_DIR%\security.inf' -Pattern $patterns[$key] -ErrorAction SilentlyContinue; if ($match) { $props[$key] = $match.Line.Split('=')[1].Trim(); }; }; " ^
            "$itemTypes = @('패스워드 길이의 적정성', '패스워드 복잡도 설정', '패스워드 주기적 변경', '동일 패스워드 설정 제한'); " ^
            "foreach ($itemType in $itemTypes) { $valueKey = switch ($itemType) { '패스워드 길이의 적정성' { 'minimumPasswordLength' } '패스워드 복잡도 설정' { 'passwordComplexity' } '패스워드 주기적 변경' { 'maximumPasswordAge' } '동일 패스워드 설정 제한' { 'passwordHistorySize' } }; $actualValue = @{}; $actualValue[$valueKey] = $props[$valueKey]; $passwordPackages = @{ user_id = $userId; item_type = $itemType; actual_value = $actualValue; }; $passwordBody = ConvertTo-Json $passwordPackages -Depth 3; try { $passwordResponse = Invoke-RestMethod -Method Post -Uri '%SERVER_URL%/api/security-audit/validate_check' -Body $passwordBody -ContentType 'application/json; charset=utf-8'; } catch { Write-Host '[$itemType] 전송 실패' -ForegroundColor Red; } }; " ^
            "Write-Host '암호 정책 검사 완료' -ForegroundColor Green; " ^
            "Write-Host '공유 폴더 검사 진행 중...'; " ^
            "$sharePackages = @{ user_id = $userId; item_type = '공유폴더 확인'; actual_value = @{ folders = @((Get-WmiObject Win32_Share -ErrorAction SilentlyContinue).Name); }; }; " ^
            "$shareBody = ConvertTo-Json $sharePackages -Depth 3; " ^
            "try { $shareResponse = (Invoke-RestMethod -Method Post -Uri '%SERVER_URL%/api/security-audit/validate_check' -Body $shareBody -ContentType 'application/json; charset=utf-8'); Write-Host '공유 폴더 검사 완료' -ForegroundColor Green; } catch { Write-Host '공유 폴더 검사 실패 - 네트워크 오류' -ForegroundColor Red; }; " ^
            "Write-Host '원격 설정 검사 진행 중...'; " ^
            "$remotePackages = @{ user_id = $userId; item_type = '원격데스크톱 제한'; actual_value = @{ fDenyTSConnections = (Get-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -ErrorAction SilentlyContinue).fDenyTSConnections; }; }; " ^
            "$remoteBody = ConvertTo-Json $remotePackages -Depth 3; " ^
            "try { $remoteResponse = (Invoke-RestMethod -Method Post -Uri '%SERVER_URL%/api/security-audit/validate_check' -Body $remoteBody -ContentType 'application/json; charset=utf-8'); Write-Host '원격 설정 검사 완료' -ForegroundColor Green; } catch { Write-Host '원격 설정 검사 실패 - 네트워크 오류' -ForegroundColor Red; }; " ^
        "} catch { Write-Host '[연결 실패] API 서버에 연결할 수 없습니다.' -ForegroundColor Red; exit 1; };"

    if %ERRORLEVEL% EQU 0 (
        echo 통합 보안 검사 완료
    ) else (
        echo 보안 검사 실패. 운영실에 문의해주세요.
        timeout /t 5 /nobreak > nul
        exit
    )
    exit /b