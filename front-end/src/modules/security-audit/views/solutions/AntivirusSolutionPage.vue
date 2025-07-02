<!-- Template 부분 -->
<template>
  <div class="security-audit-layout">
    <!-- 모바일 메뉴 토글 버튼 -->
    <button
      v-if="sidebarRef?.isMobile"
      @click="sidebarRef?.toggleSidebar()"
      class="mobile-menu-toggle"
    >
      <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
        <path
          fill-rule="evenodd"
          d="M2.5 12a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5z"
        />
      </svg>
    </button>

    <!-- 사이드바 -->
    <Sidebar ref="sidebarRef" />

    <!-- 메인 콘텐츠 -->
    <main class="main-content">
      <div v-if="!authStore.user" class="not-authenticated">
        <div class="auth-warning">
          <div class="warning-icon">
            <svg width="48" height="48" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"
              />
            </svg>
          </div>
          <h2>인증이 필요합니다</h2>
          <p>백신 상태 점검 가이드를 확인하려면 로그인이 필요합니다.</p>
          <div class="auth-actions">
            <RouterLink to="/login" class="login-button">
              <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path
                  fill-rule="evenodd"
                  d="M6 12.5a.5.5 0 0 0 .5.5h8a.5.5 0 0 0 .5-.5v-9a.5.5 0 0 0-.5-.5h-8a.5.5 0 0 0-.5.5v2a.5.5 0 0 1-1 0v-2A1.5 1.5 0 0 1 6.5 2h8A1.5 1.5 0 0 1 16 3.5v9a1.5 1.5 0 0 1-1.5 1.5h-8A1.5 1.5 0 0 1 5 12.5v-2a.5.5 0 0 1 1 0v2z"
                />
                <path
                  fill-rule="evenodd"
                  d="M.146 8.354a.5.5 0 0 1 0-.708l3-3a.5.5 0 1 1 .708.708L1.707 7.5H10.5a.5.5 0 0 1 0 1H1.707l2.147 2.146a.5.5 0 0 1-.708.708l-3-3z"
                />
              </svg>
              로그인하기
            </RouterLink>
          </div>
        </div>
      </div>

      <!-- 인증된 사용자용 콘텐츠 -->
      <div v-else>
        <h1 class="page-title">백신 상태 확인</h1>

        <!-- 개요 -->
        <div class="section">
          <h2 class="section-title">개요</h2>
          <p>
            컴퓨터의 보안을 위해서는 안티바이러스 소프트웨어가 설치되어 있고, 실시간 보호 기능이
            활성화되어 있으며, 최신 바이러스 정의 파일로 업데이트되어 있어야 합니다.
          </p>
        </div>

        <!-- 보안 요구사항 -->
        <div class="section">
          <h2 class="section-title">보안 요구사항</h2>
          <div class="requirements-grid">
            <div class="requirement-card">
              <div class="requirement-icon shield">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M5.338 1.59a61.44 61.44 0 0 0-2.837.856.481.481 0 0 0-.328.39c-.554 4.157.726 7.19 2.253 9.188a10.725 10.725 0 0 0 2.287 2.233c.346.244.652.42.893.533.12.057.218.095.293.118a.55.55 0 0 0 .101.025.615.615 0 0 0 .1-.025c.076-.023.174-.061.294-.118.24-.113.547-.29.893-.533a10.726 10.726 0 0 0 2.287-2.233c1.527-1.997 2.807-5.031 2.253-9.188a.48.48 0 0 0-.328-.39c-.651-.213-1.75-.56-2.837-.855C9.552 1.29 8.531 1.067 8 1.067c-.53 0-1.552.223-2.662.524zM5.072.56C6.157.265 7.31 0 8 0s1.843.265 2.928.56c1.11.3 2.229.655 2.887.87a1.54 1.54 0 0 1 1.044 1.262c.596 4.477-.787 7.795-2.465 9.99a11.775 11.775 0 0 1-2.517 2.453 7.159 7.159 0 0 1-1.048.625c-.28.132-.581.24-.829.24s-.548-.108-.829-.24a7.158 7.158 0 0 1-1.048-.625 11.777 11.777 0 0 1-2.517-2.453C1.928 10.487.545 7.169 1.141 2.692A1.54 1.54 0 0 1 2.185 1.43 62.456 62.456 0 0 1 5.072.56z"
                  />
                </svg>
              </div>
              <h3>알약 백신 설치</h3>
              <p>AhnLab 알약 백신이 정상적으로 설치되어 있어야 합니다.</p>
            </div>
            <div class="requirement-card">
              <div class="requirement-icon realtime">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M8 3.5a.5.5 0 0 0-1 0V9a.5.5 0 0 0 .252.434l3.5 2a.5.5 0 0 0 .496-.868L8 8.71V3.5z"
                  />
                  <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm7-8A7 7 0 1 1 1 8a7 7 0 0 1 14 0z" />
                </svg>
              </div>
              <h3>실시간 보호</h3>
              <p>실시간 감시 기능이 활성화되어 악성코드를 즉시 차단해야 합니다.</p>
            </div>
            <div class="requirement-card">
              <div class="requirement-icon update">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    fill-rule="evenodd"
                    d="M10.854 8.146a.5.5 0 0 1 0 .708l-3 3a.5.5 0 0 1-.708 0l-1.5-1.5a.5.5 0 0 1 .708-.708L7.5 10.793l2.646-2.647a.5.5 0 0 1 .708 0z"
                  />
                  <path
                    d="M8 1a2.5 2.5 0 0 1 2.5 2.5V4h-5v-.5A2.5 2.5 0 0 1 8 1zm3.5 3v-.5a3.5 3.5 0 1 0-7 0V4H1v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V4h-3.5zM2 5h12v9a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V5z"
                  />
                </svg>
              </div>
              <h3>최신 업데이트</h3>
              <p>바이러스 정의 파일이 최신 상태로 업데이트되어 있어야 합니다.</p>
            </div>
          </div>
        </div>

        <!-- 페이지 네비게이션 -->
        <PageNavigation :current-path="route.path" />
      </div>
    </main>
  </div>
</template>
<script setup>
// Script 부분
import { ref } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import JSZip from 'jszip'
import Sidebar from '@/components/Sidebar.vue'
import PageNavigation from '@/components/PageNavigation.vue'

const route = useRoute()
const authStore = useAuthStore()
const sidebarRef = ref(null)

// ZIP 파일 다운로드 함수 (JSZip 사용)
const downloadZipWithJSZip = async (files, zipFilename) => {
  try {
    const zip = new JSZip()

    files.forEach((file) => {
      zip.file(file.name, file.content)
    })

    const zipBlob = await zip.generateAsync({ type: 'blob' })
    const url = window.URL.createObjectURL(zipBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = zipFilename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (err) {
    console.error('ZIP 파일 다운로드 실패:', err)
  }
}

// 사용법
const downloadConfigScript = async () => {
  const files = [
    {
      name: '조치 스크립트.bat',
      content: SetupScript,
    },
  ]
  await downloadZipWithJSZip(files, '조치 스크립트.zip')
}

// Windows CRLF 줄바꿈으로 변환하는 함수
const convertToWindowsLineEndings = (content) => {
  return content.replace(/\r?\n/g, '\r\n')
}

// 1. 조치 스크립트.bat 내용을 포함한 변수 추가
const SetupScript = convertToWindowsLineEndings(`@echo off

::  --> 관리자 권한 실행 코드
:-------------------------------------
>nul 2>&1 "%SYSTEMROOT%\\system32\\cacls.exe" "%SYSTEMROOT%\\system32\\config\\system"

if '%errorlevel%' NEQ '0' (
 goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
 echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\\getadmin.vbs"
 echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\\getadmin.vbs"

"%temp%\\getadmin.vbs"
 exit /B

:gotAdmin
 if exist "%temp%\\getadmin.vbs" ( del "%temp%\\getadmin.vbs" )
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

::  --> 특정 IP 설정 (여기에 원격데스크톱을 유지할 IP 주소들을 입력하세요)
:-------------------------------------
set ALLOWED_IPS=10.106.15.100 10.106.15.101 10.106.15.102 10.106.15.103 10.106.15.104 10.106.15.105 10.106.15.114 10.106.15.115 10.106.15.117 10.106.15.125
set SKIP_RDP_DISABLE=0

::  --> 현재 컴퓨터의 IP 주소 확인
:-------------------------------------
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set IP=%%a
    set IP=!IP: =!
    for %%b in (%ALLOWED_IPS%) do (
        if "!IP!"=="%%b" (
            set SKIP_RDP_DISABLE=1
        )
    )
)
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
Reg add "HKEY_CURRENT_USER\\Control Panel\\Desktop" /v SCRNSAVE.EXE /t REG_SZ /d C:\\Windows\\System32\\scrnsave.scr /f | find /v "success"
Reg add "HKEY_CURRENT_USER\\Control Panel\\Desktop" /v ScreenSaveActive /t REG_SZ /d 1 /f | find /v "success"
Reg add "HKEY_CURRENT_USER\\Control Panel\\Desktop" /v ScreenSaverIsSecure /t REG_SZ /d 1 /f | find /v "success"
Reg add "HKEY_CURRENT_USER\\Control Panel\\Desktop" /v ScreenSaveTimeOut /t REG_SZ /d 600 /f | find /v "success"
echo.

echo 2.1 암호 복잡도 설정 완료
secedit /export /cfg "%temp%\\secpol.cfg" > nul
powershell -Command "(Get-Content '%temp%\\secpol.cfg') -replace 'PasswordComplexity = 0', 'PasswordComplexity = 1' | Set-Content '%temp%\\secpol.cfg'"
secedit /configure /db %windir%\\security\\local.sdb /cfg "%temp%\secpol.cfg" /areas SECURITYPOLICY > nul
del "%temp%\\secpol.cfg" > nul
echo.

echo 2.3 최소 암호 길이 8자리로 변경 완료
net accounts /minpwlen:8 | find /v "success"

echo 2.4 암호 복잡도 요구사항 활성화 완료
Reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa" /v NoLMHash /t REG_DWORD /d 0x00000001 /f | find /v "success"

echo 2.5 최대 암호 사용 기간 90일로 변경 완료
net accounts /maxpwage:90 | find /v "success"

echo 2.7 최근 암호 기억 5개로 변경 완료
net accounts /uniquepw:5 | find /v "success"

echo 3.1 불필요한 공유폴더 삭제 완료 ^(IPC$ 제외한 모든 공유폴더 제거^)
:: 모든 공유폴더 목록을 가져와서 IPC$를 제외하고 삭제
for /f "skip=1 tokens=1" %%s in ('net share ^| findstr /v "^$" ^| findstr /v "명령을 잘못" ^| findstr /v "The command completed"') do (
    if /i not "%%s"=="IPC$" (
        net share "%%s" /delete /y > nul 2>&1
    )
)
Reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa" /v restrictanonymous /t REG_DWORD /d 0x00000001 /f | find /v "success"
Reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters" /v AutoShareServer /t REG_DWORD /d 0x00000000 /f | find /v "success"
Reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters" /v AutoShareWks /t REG_DWORD /d 0x00000000 /f | find /v "success"
echo.

:: IP 조건에 따라 원격데스크톱 설정 처리
if %SKIP_RDP_DISABLE%==1 (
    echo 3.3 원격데스크톱 설정 유지 ^(허용된 IP 주소^)
) else (
    echo 3.3 원격데스크톱 해제 완료
    Reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0x00000001 /f | find /v "success"
    Reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server\\WinStations\\RDP-Tcp" /v UserAuthentication /t REG_DWORD /d 0x00000001 /f | find /v "success"
)
echo.

TIMEOUT /t 2 > NUL
echo.
echo ※ 모든 보안 조치가 완료되었습니다. ※
echo.
echo ※ 시스템 재시작을 권장합니다. ※
:-------------------------------------

pause`)
</script>

<style scoped>
.security-audit-layout {
  display: flex;
  background-color: var(--bright-bg);
  min-height: calc(100vh - 114px);
}

.main-content {
  flex: 1;
  padding: 30px;
  background-color: var(--content-bg);
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  margin: 20px;
}

/* 모바일 메뉴 토글 */
.mobile-menu-toggle {
  display: none;
  position: fixed;
  top: 20px;
  left: 20px;
  z-index: 1001;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

@media (max-width: 768px) {
  .mobile-menu-toggle {
    display: block;
  }
}

/* 인증 관련 스타일 */
.not-authenticated {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

.auth-warning {
  text-align: center;
  padding: 40px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border: 1px solid #fee2e2;
}

.warning-icon {
  color: #f59e0b;
  margin-bottom: 20px;
}

.auth-warning h2 {
  color: var(--dark-blue);
  margin-bottom: 12px;
  font-size: 1.5rem;
}

.auth-warning p {
  color: #6b7280;
  margin-bottom: 24px;
  font-size: 1rem;
}

.login-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background-color: var(--primary-color);
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
}

.login-button:hover {
  background-color: var(--dark-blue);
  transform: translateY(-2px);
}

/* 페이지 타이틀 */
.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--dark-blue);
  margin-bottom: 2rem;
  border-bottom: 3px solid var(--primary-blue);
  padding-bottom: 0.5rem;
}

/* 섹션 스타일 */

.section p {
  line-height: 1.6;
  color: #374151;
  margin-bottom: 16px;
}

.section ul {
  margin-left: 20px;
  margin-bottom: 16px;
}

.section li {
  margin-bottom: 8px;
  line-height: 1.5;
  color: #374151;
}

.section ol {
  margin-left: 20px;
  margin-bottom: 16px;
}

.section ol li {
  margin-bottom: 8px;
  line-height: 1.5;
  color: #374151;
}

.section h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--dark-blue);
  margin: 24px 0 12px 0;
}

/* 요구사항 그리드 */
.requirements-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.requirement-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  transition: all 0.3s ease;
}

.requirement-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.requirement-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  color: white;
}

.requirement-icon.shield {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
}

.requirement-icon.realtime {
  background: linear-gradient(135deg, #10b981, #059669);
}

.requirement-icon.update {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.requirement-card h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--dark-blue);
  margin: 0 0 8px 0;
}

.requirement-card p {
  color: #6b7280;
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0;
}

/* 코드 블록 스타일 */
.code-block {
  background-color: #1f2937;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
}

.code-block h3 {
  color: #e5e7eb;
  margin: 0 0 16px 0;
  font-size: 1rem;
  font-weight: 600;
}

.code-container {
  position: relative;
}

.code-container pre {
  background-color: transparent;
  color: #e5e7eb;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0;
  padding: 0;
  overflow-x: auto;
}

.code-container code {
  background-color: transparent;
  color: inherit;
  padding: 0;
}

.copy-button {
  position: absolute;
  top: 8px;
  right: 8px;
  background-color: #374151;
  color: #e5e7eb;
  border: none;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 0.875rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: background-color 0.2s ease;
}

.copy-button:hover {
  background-color: #4b5563;
}

/* 스크립트 다운로드 섹션 */
.script-download-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.script-card {
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
  transition: all 0.3s ease;
}

.script-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.script-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 16px;
}

.script-icon.check {
  background: linear-gradient(135deg, #10b981, #059669);
}

.script-content h3 {
  margin: 0 0 8px 0;
  color: var(--dark-blue);
  font-size: 1.125rem;
  font-weight: 600;
}

.script-content p {
  margin: 0 0 16px 0;
  color: #6b7280;
  font-size: 0.9rem;
  line-height: 1.5;
}

.download-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
}

.download-button.secondary {
  background-color: #10b981;
  color: white;
}

.download-button.secondary:hover {
  background-color: #059669;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
}

/* 사용법 정보 */
.usage-info {
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 20px;
  margin-top: 24px;
}

.usage-info h4 {
  margin: 0 0 12px 0;
  color: var(--dark-blue);
  font-size: 1rem;
  font-weight: 600;
}

.usage-info ol {
  margin: 0;
  padding-left: 20px;
}

.usage-info li {
  margin-bottom: 8px;
  line-height: 1.5;
  color: #374151;
}

.usage-info code {
  background-color: #1f2937;
  color: #e5e7eb;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.875rem;
}

/* 키보드 키 스타일 */
kbd {
  background-color: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 0.875rem;
  font-family: monospace;
  color: #374151;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* 정보 그리드 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.info-card {
  border-radius: 12px;
  padding: 24px;
  border-left: 4px solid;
}

.info-card.warning {
  background-color: #fef3c7;
  border-left-color: #f59e0b;
}

.info-card.tip {
  background-color: #dbeafe;
  border-left-color: #3b82f6;
}

.info-icon {
  margin-bottom: 12px;
}

.info-card.warning .info-icon {
  color: #f59e0b;
}

.info-card.tip .info-icon {
  color: #3b82f6;
}

.info-content h3 {
  margin: 0 0 12px 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--dark-blue);
}

.info-content ul {
  margin: 0;
  padding-left: 20px;
}

.info-content li {
  margin-bottom: 8px;
  line-height: 1.5;
  color: #374151;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .main-content {
    margin: 10px;
    padding: 20px;
  }

  .page-title {
    font-size: 1.5rem;
  }

  .section-title {
    font-size: 1.25rem;
  }

  .requirements-grid {
    grid-template-columns: 1fr;
  }

  .script-download-section {
    grid-template-columns: 1fr;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>
