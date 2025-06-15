<!-- views/SecurityAuditSolutionsPage.vue - Template -->
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
      <div>
        <div class="page-header">
          <h1 class="page-title">보안 감사 조치방법</h1>
        </div>
        <!-- 조치방법 개요 -->
        <div class="section">
          <h2 class="section-title">조치방법 개요</h2>
          <div class="overview-card">
            <div class="overview-content">
              <p>
                이 페이지에서는 정보보안 감사에서 확인해야 할 주요 항목에 대한 조치방법을
                안내합니다. 모든 가이드는 조직의 보안 정책을 준수하기 위한 기본적인 설정 방법과 점검
                사항을 제공합니다.
              </p>
            </div>
          </div>
        </div>

        <!-- 자동화 스크립트 -->
        <div class="section">
          <h2 class="section-title">자동화 스크립트 다운로드</h2>
          <p>배치 스크립트를 사용하여 자동으로 조치할 수 있습니다.</p>

          <div class="script-download-section">
            <div class="script-card">
              <div class="script-icon setup">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M8 4.754a3.246 3.246 0 1 0 0 6.492 3.246 3.246 0 0 0 0-6.492zM5.754 8a2.246 2.246 0 1 1 4.492 0 2.246 2.246 0 0 1-4.492 0z"
                  />
                  <path
                    d="M9.796 1.343c-.527-1.79-3.065-1.79-3.592 0l-.094.319a.873.873 0 0 1-1.255.52l-.292-.16c-1.64-.892-3.433.902-2.54 2.541l.159.292a.873.873 0 0 1-.52 1.255l-.319.094c-1.79.527-1.79 3.065 0 3.592l.319.094a.873.873 0 0 1 .52 1.255l-.16.292c-.892 1.64.901 3.434 2.541 2.54l.292-.159a.873.873 0 0 1 1.255.52l.094.319c.527 1.79 3.065 1.79 3.592 0l.094-.319a.873.873 0 0 1 1.255-.52l.292.16c1.64.893 3.434-.902 2.54-2.541l-.159-.292a.873.873 0 0 1 .52-1.255l.319-.094c1.79-.527 1.79-3.065 0-3.592l-.319-.094a.873.873 0 0 1-.52-1.255l.16-.292c.893-1.64-.902-3.433-2.541-2.54l-.292.159a.873.873 0 0 1-1.255-.52l-.094-.319z"
                  />
                </svg>
              </div>
              <div class="script-content">
                <h3>조치 자동화 스크립트</h3>
                <p>자동화 스크립트를 통해 자동으로 조치를 받을 수 있습니다.</p>
                <button @click="downloadConfigScript" class="download-button primary">
                  <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path
                      d="M.5 9.9a.5.5 0 0 1 .5.5v1.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-1.5a.5.5 0 0 1 1 0v1.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-1.5a.5.5 0 0 1 .5-.5z"
                    />
                    <path
                      d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"
                    />
                  </svg>
                  다운로드 (조치 스크립트.bat)
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 페이지 네비게이션 -->
        <PageNavigation :current-path="route.path" />
      </div>
    </main>
  </div>
</template>
<!-- views/SecurityAuditSolutionsPage.vue - script -->
<script setup>
import { ref } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import Sidebar from '@/components/Sidebar.vue'
import PageNavigation from '@/components/PageNavigation.vue'

import JSZip from 'jszip' // 또는 CDN 사용
import { useAuthStore } from '@/stores/auth'

// Vue Router
const route = useRoute()

// Pinia Store
const authStore = useAuthStore()

// Sidebar ref
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
Reg add "HKEY_CURRENT_USER\\Control Panel\\Desktop" /v SCRNSAVE.EXE /t REG_SZ /d C:\\\\Windows\\\\System32\\\\scrnsave.scr /f | find /v "success"
Reg add "HKEY_CURRENT_USER\\Control Panel\\Desktop" /v ScreenSaveActive /t REG_SZ /d 1 /f | find /v "success"
Reg add "HKEY_CURRENT_USER\\Control Panel\\Desktop" /v ScreenSaverIsSecure /t REG_SZ /d 1 /f | find /v "success"
Reg add "HKEY_CURRENT_USER\\Control Panel\\Desktop" /v ScreenSaveTimeOut /t REG_SZ /d 600 /f | find /v "success"
echo.

echo 2.1 암호 복잡도 설정 완료
secedit /export /cfg "%temp%\\secpol.cfg" > nul
powershell -Command "(Get-Content '%temp%\\secpol.cfg') -replace 'PasswordComplexity = 0', 'PasswordComplexity = 1' | Set-Content '%temp%\\secpol.cfg'"
secedit /configure /db %windir%\\security\\local.sdb /cfg "%temp%\\secpol.cfg" /areas SECURITYPOLICY > nul
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
echo.

echo 3.1 불필요한 공유폴더 삭제 완료 (C$, D$, E$, F$, ADMIN$ 제거, IPC$ 유지)
net share C$ /delete /y > nul 2>&1
net share D$ /delete /y > nul 2>&1
net share E$ /delete /y > nul 2>&1
net share F$ /delete /y > nul 2>&1
net share ADMIN$ /delete /y > nul 2>&1
Reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa" /v restrictanonymous /t REG_DWORD /d 0x00000001 /f | find /v "success"
Reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters" /v AutoShareServer /t REG_DWORD /d 0x00000000 /f | find /v "success"
Reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters" /v AutoShareWks /t REG_DWORD /d 0x00000000 /f | find /v "success"
echo.

echo 3.3 원격데스크톱 해제 완료
Reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0x00000001 /f | find /v "success"
Reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server\\WinStations\\RDP-Tcp" /v UserAuthentication /t REG_DWORD /d 0x00000001 /f | find /v "success"
echo.

TIMEOUT /t 2 > NUL
echo.
echo ※ 모든 보안 조치가 완료되었습니다. ※
echo.
echo ※ 시스템 재시작을 권장합니다. ※
:-------------------------------------

pause`)
</script>

<!-- CSS는 외부 파일에서 import -->
<style scoped>
@import '../styles/SecurityAuditSolutionsPage.css';
</style>
