<!-- views/ScreenSaverSolutionPage.vue - Template -->
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
          <p>화면보호기 설정 가이드를 확인하려면 로그인이 필요합니다.</p>
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
        <h1 class="page-title">화면보호기 사용</h1>

        <!-- 개요 -->
        <div class="section">
          <h2 class="section-title">개요</h2>
          <p>
            화면보호기는 컴퓨터를 사용하지 않는 동안 화면을 보호하고 무단 접근을 방지하는 중요한
            보안 기능입니다. 화면보호기가 10분 이내에 활성화되고 암호로 보호되도록 설정해야 합니다.
          </p>
        </div>

        <!-- 화면보호기 요구사항 -->
        <div class="section">
          <h2 class="section-title">화면보호기 요구사항</h2>
          <p>다음 화면보호기 요구사항이 반드시 충족되어야 합니다:</p>
          <ul>
            <li><strong>대기 시간:</strong> 10분 이내로 화면보호기가 자동 실행되도록 설정</li>
            <li>
              <strong>암호 보호:</strong> 화면보호기 해제 시 로그인 암호 입력이 필요하도록 설정
            </li>
            <li>
              <strong>화면보호기 선택:</strong> 시스템 리소스를 적게 사용하는 단순한 화면보호기 사용
            </li>
          </ul>
        </div>

        <!-- Windows 설정 방법 -->
        <!-- <div class="section">
          <h2 class="section-title">Windows 화면보호기 설정 방법</h2>

          <h3>방법 1: 설정 앱 사용 (Windows 10/11)</h3>
          <ol>
            <li><kbd>Windows</kbd> + <kbd>I</kbd> 키를 눌러 설정을 엽니다.</li>
            <li>"개인 설정" → "잠금 화면"을 클릭합니다.</li>
            <li>하단의 "화면 보호기 설정"을 클릭합니다.</li>
            <li>화면보호기를 선택하고 대기 시간을 <strong>10분 이하</strong>로 설정합니다.</li>
            <li><strong>"다시 시작할 때 로그온 화면 표시"</strong> 체크박스를 선택합니다.</li>
            <li>"확인"을 클릭하여 설정을 저장합니다.</li>
          </ol>

          <h3>방법 2: 제어판 사용</h3>
          <ol>
            <li>
              <kbd>Windows</kbd> + <kbd>R</kbd> 키를 누르고 <code>control</code>을 입력 후 엔터를
              누릅니다.
            </li>
            <li>"모양 및 개인 설정" → "디스플레이" → "화면 보호기 변경"을 클릭합니다.</li>
            <li>드롭다운 메뉴에서 적절한 화면보호기를 선택합니다.</li>
            <li>
              대기 시간을 10분 이하로 설정하고 "다시 시작할 때 로그온 화면 표시"를 체크합니다.
            </li>
            <li>"확인"을 클릭하여 설정을 저장합니다.</li>
          </ol>
        </div> -->

        <!-- 자동화 스크립트 -->
        <div class="section">
          <h2 class="section-title">자동화 스크립트 다운로드</h2>
          <p>
            PowerShell 스크립트를 사용하여 화면보호기를 자동으로 설정하거나 현재 설정을 확인할 수
            있습니다:
          </p>

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
                <h3>화면보호기 자동 설정</h3>
                <p>화면보호기를 10분 이내로 설정하고 암호 보호를 자동으로 활성화합니다.</p>
                <button @click="downloadConfigScript" class="download-button primary">
                  <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path
                      d="M.5 9.9a.5.5 0 0 1 .5.5v1.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-1.5a.5.5 0 0 1 1 0v1.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-1.5a.5.5 0 0 1 .5-.5z"
                    />
                    <path
                      d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"
                    />
                  </svg>
                  다운로드 (ScreenSaver_Setup.ps1)
                </button>
              </div>
            </div>

            <div class="script-card">
              <div class="script-icon check">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M2.5 3A1.5 1.5 0 0 0 1 4.5v.793c.026.009.051.02.076.032L7.674 8.51c.206.1.446.1.652 0l6.598-3.185A.755.755 0 0 1 15 5.293V4.5A1.5 1.5 0 0 0 13.5 3h-11Z"
                  />
                  <path
                    d="M15 6.954 8.978 9.86a2.25 2.25 0 0 1-1.956 0L1 6.954V11.5A1.5 1.5 0 0 0 2.5 13h11a1.5 1.5 0 0 0 1.5-1.5V6.954Z"
                  />
                </svg>
              </div>
              <div class="script-content">
                <h3>설정 상태 확인</h3>
                <p>현재 화면보호기 설정이 보안 요구사항을 충족하는지 확인합니다.</p>
                <button @click="downloadCheckScript" class="download-button secondary">
                  <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path
                      d="M.5 9.9a.5.5 0 0 1 .5.5v1.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-1.5a.5.5 0 0 1 1 0v1.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-1.5a.5.5 0 0 1 .5-.5z"
                    />
                    <path
                      d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"
                    />
                  </svg>
                  다운로드 (ScreenSaver_Check.ps1)
                </button>
              </div>
            </div>
          </div>

          <div class="usage-info">
            <h4>사용 방법:</h4>
            <ol>
              <li>스크립트 파일을 다운로드합니다.</li>
              <li>PowerShell을 <strong>관리자 권한</strong>으로 실행합니다.</li>
              <li>다운로드한 스크립트 파일이 있는 폴더로 이동합니다.</li>
              <li>
                <code>Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser</code>
                명령으로 실행 정책을 설정합니다.
              </li>
              <li>
                <code>.\ScreenSaver_Setup.ps1</code> 또는
                <code>.\ScreenSaver_Check.ps1</code> 명령으로 스크립트를 실행합니다.
              </li>
            </ol>
          </div>
        </div>

        <!-- 명령줄 확인 -->
        <!-- <div class="section">
          <h2 class="section-title">수동 설정 확인</h2>
          <p>PowerShell을 사용하여 현재 화면보호기 설정을 수동으로 확인할 수 있습니다:</p>

          <div class="code-block">
            <pre><code># 화면보호기 활성화 상태 확인
Get-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name "ScreenSaveActive"

# 화면보호기 대기 시간 확인 (초 단위)
Get-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name "ScreenSaveTimeOut"

# 암호 보호 설정 확인
Get-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name "ScreenSaverIsSecure"</code></pre>
          </div>

          <p><strong>설정값 해석:</strong></p>
          <ul>
            <li><strong>ScreenSaveActive</strong>: 1 = 활성화, 0 = 비활성화</li>
            <li><strong>ScreenSaveTimeOut</strong>: 초 단위 (600 = 10분)</li>
            <li><strong>ScreenSaverIsSecure</strong>: 1 = 암호 보호, 0 = 보호 없음</li>
          </ul>
        </div> -->

        <!-- 문제 해결 -->
        <!-- <div class="section">
          <h2 class="section-title">문제 해결 방법</h2>

          <h3>화면보호기가 실행되지 않는 경우</h3>
          <ul>
            <li>전원 관리 설정에서 "절전 모드" 시간이 화면보호기 시간보다 짧지 않은지 확인</li>
            <li>멀티미디어 프로그램이나 게임이 실행 중이면 화면보호기가 작동하지 않을 수 있음</li>
            <li>마우스나 키보드의 미세한 움직임이 있는지 확인</li>
          </ul>

          <h3>암호 보호가 작동하지 않는 경우</h3>
          <ul>
            <li>그룹 정책에서 화면보호기 설정이 제한되어 있는지 IT 부서에 문의</li>
            <li>Windows 업데이트 후 설정이 초기화되었을 가능성 확인</li>
            <li>사용자 계정에 암호가 설정되어 있는지 확인</li>
          </ul>
        </div> -->

        <!-- 보안 모범 사례 -->
        <!-- <div class="section">
          <h2 class="section-title">보안 모범 사례</h2>
          <ul>
            <li>자리를 비울 때는 <kbd>Windows</kbd> + <kbd>L</kbd> 키로 즉시 화면 잠금</li>
            <li>화면보호기 시간은 5-10분 사이로 설정하여 보안과 편의성의 균형 유지</li>
            <li>정기적으로 화면보호기 설정이 유지되고 있는지 확인</li>
            <li>복잡한 화면보호기보다는 단순한 것을 선택하여 시스템 성능 보호</li>
          </ul>
        </div> -->

        <!-- 관리자 연락처 -->
        <!-- <div class="section">
          <h2 class="section-title">관리자 연락처</h2>
          <p>화면보호기 설정에 문제가 있는 경우 아래 담당자에게 문의하세요:</p>
          <p>보안관리팀: 내선 5678 또는 security@example.com</p>
        </div> -->

        <!-- 페이지 네비게이션 -->
        <PageNavigation :current-path="route.path" />
      </div>
    </main>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Sidebar from '@/components/Sidebar.vue'
import PageNavigation from '@/components/PageNavigation.vue'

// Vue Router
const route = useRoute()

// Pinia Store
const authStore = useAuthStore()

// Sidebar ref
const sidebarRef = ref(null)

// PowerShell 스크립트 내용
const screenSaverScript = `# 화면보호기 자동 설정 스크립트
# 작성일: ${new Date().toLocaleDateString('ko-KR')}
# 설명: 화면보호기를 10분 이내로 설정하고 암호 보호를 활성화합니다.

Write-Host "화면보호기 설정을 시작합니다..." -ForegroundColor Green

try {
    # 레지스트리 경로 설정
    $registryPath = "HKCU:\\Control Panel\\Desktop"

    # 화면보호기 활성화 (1 = 활성화)
    Set-ItemProperty -Path $registryPath -Name "ScreenSaveActive" -Value "1"
    Write-Host "✓ 화면보호기가 활성화되었습니다." -ForegroundColor Green

    # 화면보호기 대기 시간을 600초(10분)로 설정
    Set-ItemProperty -Path $registryPath -Name "ScreenSaveTimeOut" -Value "600"
    Write-Host "✓ 화면보호기 대기 시간이 10분으로 설정되었습니다." -ForegroundColor Green

    # 암호 보호 활성화 (1 = 활성화)
    Set-ItemProperty -Path $registryPath -Name "ScreenSaverIsSecure" -Value "1"
    Write-Host "✓ 화면보호기 암호 보호가 활성화되었습니다." -ForegroundColor Green

    # 기본 화면보호기를 'scrnsave.scr' (빈 화면)으로 설정
    Set-ItemProperty -Path $registryPath -Name "SCRNSAVE.EXE" -Value "scrnsave.scr"
    Write-Host "✓ 기본 화면보호기가 설정되었습니다." -ForegroundColor Green

    Write-Host ""
    Write-Host "화면보호기 설정이 완료되었습니다!" -ForegroundColor Yellow
    Write-Host "변경사항이 즉시 적용됩니다." -ForegroundColor Yellow

    # 현재 설정 확인
    Write-Host ""
    Write-Host "현재 설정 확인:" -ForegroundColor Cyan

    $isActive = Get-ItemProperty -Path $registryPath -Name "ScreenSaveActive" | Select-Object -ExpandProperty ScreenSaveActive
    $timeout = Get-ItemProperty -Path $registryPath -Name "ScreenSaveTimeOut" | Select-Object -ExpandProperty ScreenSaveTimeOut
    $isSecure = Get-ItemProperty -Path $registryPath -Name "ScreenSaverIsSecure" | Select-Object -ExpandProperty ScreenSaverIsSecure

    Write-Host "- 화면보호기 활성화: $($isActive -eq 1 ? '예' : '아니오')" -ForegroundColor White
    Write-Host "- 대기 시간: $([math]::Round($timeout / 60, 1))분" -ForegroundColor White
    Write-Host "- 암호 보호: $($isSecure -eq 1 ? '예' : '아니오')" -ForegroundColor White

}
catch {
    Write-Host "오류가 발생했습니다: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "관리자 권한으로 PowerShell을 실행해보세요." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "스크립트 실행이 완료되었습니다. 아무 키나 누르면 종료됩니다." -ForegroundColor Gray
Read-Host`

// 설정 확인용 스크립트
const checkScript = `# 화면보호기 설정 확인 스크립트
Write-Host "현재 화면보호기 설정을 확인합니다..." -ForegroundColor Green
Write-Host ""

$registryPath = "HKCU:\\Control Panel\\Desktop"

try {
    $isActive = Get-ItemProperty -Path $registryPath -Name "ScreenSaveActive" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty ScreenSaveActive
    $timeout = Get-ItemProperty -Path $registryPath -Name "ScreenSaveTimeOut" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty ScreenSaveTimeOut
    $isSecure = Get-ItemProperty -Path $registryPath -Name "ScreenSaverIsSecure" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty ScreenSaverIsSecure

    Write-Host "화면보호기 설정 현황:" -ForegroundColor Cyan
    Write-Host "- 활성화 상태: $($isActive -eq 1 ? '활성화됨' : '비활성화됨')" -ForegroundColor $(if($isActive -eq 1) {'Green'} else {'Red'})
    Write-Host "- 대기 시간: $([math]::Round($timeout / 60, 1))분 ($timeout초)" -ForegroundColor $(if($timeout -le 600) {'Green'} else {'Yellow'})
    Write-Host "- 암호 보호: $($isSecure -eq 1 ? '활성화됨' : '비활성화됨')" -ForegroundColor $(if($isSecure -eq 1) {'Green'} else {'Red'})

    Write-Host ""
    if($isActive -eq 1 -and $timeout -le 600 -and $isSecure -eq 1) {
        Write-Host "✓ 모든 보안 요구사항을 충족합니다!" -ForegroundColor Green
    } else {
        Write-Host "⚠ 일부 보안 요구사항을 충족하지 않습니다." -ForegroundColor Yellow
        Write-Host "화면보호기 자동 설정 스크립트를 실행하세요." -ForegroundColor Yellow
    }
}
catch {
    Write-Host "설정을 읽는 중 오류가 발생했습니다: $($_.Exception.Message)" -ForegroundColor Red
}

Read-Host "아무 키나 누르면 종료됩니다"`

// 메서드
const copyToClipboard = async () => {
  const codeText = `# 화면보호기 활성화 상태 확인
Get-ItemProperty -Path "HKCU:\\Control Panel\\Desktop" -Name "ScreenSaveActive"

# 화면보호기 대기 시간 확인 (초 단위)
Get-ItemProperty -Path "HKCU:\\Control Panel\\Desktop" -Name "ScreenSaveTimeOut"

# 암호 보호 설정 확인
Get-ItemProperty -Path "HKCU:\\Control Panel\\Desktop" -Name "ScreenSaverIsSecure"`

  try {
    await navigator.clipboard.writeText(codeText)
    console.log('코드가 클립보드에 복사되었습니다.')
  } catch (err) {
    console.error('클립보드 복사 실패:', err)
  }
}

// 스크립트 다운로드 함수
const downloadScript = (scriptContent, filename) => {
  try {
    const blob = new Blob([scriptContent], { type: 'text/plain;charset=utf-8' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (err) {
    console.error('파일 다운로드 실패:', err)
  }
}

// 화면보호기 설정 스크립트 다운로드
const downloadConfigScript = () => {
  downloadScript(screenSaverScript, 'ScreenSaver_Setup.ps1')
}

// 설정 확인 스크립트 다운로드
const downloadCheckScript = () => {
  downloadScript(checkScript, 'ScreenSaver_Check.ps1')
}
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

/* 섹션 스타일 */
.section {
  margin-bottom: 32px;
}

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

.script-icon.setup {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
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

.download-button.primary {
  background-color: var(--primary-color);
  color: white;
}

.download-button.primary:hover {
  background-color: var(--dark-blue);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(64, 86, 183, 0.3);
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

/* 코드 블록 스타일 */
.code-block {
  background-color: #1f2937;
  border-radius: 8px;
  padding: 20px;
  margin: 16px 0;
  overflow-x: auto;
}

.code-block pre {
  margin: 0;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.875rem;
  line-height: 1.5;
}

.code-block code {
  color: #e5e7eb;
  background: none;
  padding: 0;
  border-radius: 0;
}

/* 인라인 코드 스타일 */
code {
  background-color: #f3f4f6;
  color: #dc2626;
  padding: 2px 4px;
  border-radius: 4px;
  font-size: 0.875rem;
  font-family: monospace;
}

/* 강조 텍스트 */
strong {
  color: var(--primary-color);
  font-weight: 600;
}

/* 모바일 메뉴 토글 버튼 */
.mobile-menu-toggle {
  position: fixed;
  bottom: 20px;
  left: 20px;
  z-index: 1001;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.2s ease;
}

.mobile-menu-toggle:hover {
  background-color: var(--dark-blue);
  transform: scale(1.05);
}

/* 반응형 디자인 */
@media (max-width: 1024px) {
  .security-audit-layout {
    flex-direction: column;
  }

  .main-content {
    margin: 20px;
  }
}

@media (max-width: 768px) {
  .mobile-menu-toggle {
    display: block;
  }

  .main-content {
    padding: 20px;
    margin: 10px;
  }

  .section h3 {
    font-size: 1rem;
  }

  .code-block {
    padding: 16px;
    font-size: 0.8rem;
  }

  kbd {
    font-size: 0.8rem;
    padding: 1px 4px;
  }
}

@media (max-width: 480px) {
  .main-content {
    padding: 16px;
  }

  .section {
    margin-bottom: 24px;
  }

  .section ul,
  .section ol {
    margin-left: 16px;
  }

  .code-block {
    padding: 12px;
    margin: 12px 0;
  }
}

@media (min-width: 769px) {
  .mobile-menu-toggle {
    display: none;
  }
}
</style>
