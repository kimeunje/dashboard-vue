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
            활성화되어 있으며, 최신 바이러스 정의 파일로 업데이트되어 있어야 합니다. 특히
            알약(AhnLab V3) 백신 사용을 권장합니다.
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

        <!-- 수동 설정 방법 -->
        <div class="section">
          <h2 class="section-title">수동 설정 방법</h2>

          <h3>1. 알약 백신 설치 방법</h3>
          <ol>
            <li>AhnLab 공식 웹사이트 (www.ahnlab.com)에 접속</li>
            <li>[제품] → [개인용 제품] → [알약] 메뉴 선택</li>
            <li>[다운로드] 버튼을 클릭하여 설치 파일 다운로드</li>
            <li>다운로드한 설치 파일을 관리자 권한으로 실행</li>
            <li>설치 마법사의 안내에 따라 설치 진행</li>
            <li>설치 완료 후 제품 등록 및 라이선스 활성화</li>
          </ol>

          <h3>2. 실시간 보호 활성화</h3>
          <ol>
            <li>알약 백신 프로그램 실행</li>
            <li>메인 화면에서 [설정] 메뉴 클릭</li>
            <li>[실시간 감시] 탭 선택</li>
            <li>[실시간 감시 사용] 옵션을 체크하여 활성화</li>
            <li>세부 감시 옵션들(파일 감시, 웹 보호, 메일 보호 등) 활성화</li>
            <li>[적용] 버튼을 클릭하여 설정 저장</li>
          </ol>

          <h3>3. 백신 업데이트 방법</h3>
          <ol>
            <li>알약 백신 메인 화면에서 [업데이트] 버튼 클릭</li>
            <li>[엔진 업데이트] 및 [패턴 업데이트] 실행</li>
            <li>업데이트 완료까지 대기</li>
            <li>[자동 업데이트] 설정을 활성화하여 항상 최신 상태 유지</li>
            <li>필요시 시스템 재부팅</li>
          </ol>
        </div>

        <!-- PowerShell 확인 -->
        <div class="section">
          <h2 class="section-title">PowerShell을 이용한 확인</h2>
          <div class="code-block">
            <h3>백신 상태 확인 명령어</h3>
            <div class="code-container">
              <pre><code># 설치된 백신 소프트웨어 확인
Get-WmiObject -Namespace "root\SecurityCenter2" -Class AntiVirusProduct | Select-Object displayName, productState

# 알약 백신 설치 확인
Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | Where-Object {$_.DisplayName -like "*AhnLab*" -or $_.DisplayName -like "*알약*"} | Select-Object DisplayName, DisplayVersion

# Windows Defender 상태 확인 (보조 확인용)
Get-MpComputerStatus | Select-Object AntivirusEnabled, RealTimeProtectionEnabled, AntivirusSignatureLastUpdated</code></pre>
              <button @click="copyToClipboard" class="copy-button">
                <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M4 1.5H3a2 2 0 0 0-2 2V14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V3.5a2 2 0 0 0-2-2h-1v1h1a1 1 0 0 1 1 1V14a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V3.5a1 1 0 0 1 1-1h1v-1z"
                  />
                  <path
                    d="M9.5 1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-3a.5.5 0 0 1-.5-.5v-1a.5.5 0 0 1 .5-.5h3zm-3-1A1.5 1.5 0 0 0 5 1.5v1A1.5 1.5 0 0 0 6.5 4h3A1.5 1.5 0 0 0 11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3z"
                  />
                </svg>
                복사
              </button>
            </div>
          </div>
        </div>

        <!-- 스크립트 다운로드 섹션 -->
        <div class="section">
          <h2 class="section-title">자동화 스크립트</h2>
          <div class="script-download-section">
            <div class="script-card">
              <div class="script-icon check">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M10.97 4.97a.235.235 0 0 0-.02.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.061L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"
                  />
                </svg>
              </div>
              <div class="script-content">
                <h3>백신 상태 확인 스크립트</h3>
                <p>
                  설치된 백신의 상태, 실시간 보호 활성화 여부, 업데이트 상태를 자동으로 확인합니다.
                </p>
                <button @click="downloadCheckScript" class="download-button secondary">
                  <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path
                      d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"
                    />
                    <path
                      d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"
                    />
                  </svg>
                  다운로드
                </button>
              </div>
            </div>
          </div>

          <div class="usage-info">
            <h4>스크립트 사용 방법</h4>
            <ol>
              <li><kbd>Windows</kbd> + <kbd>X</kbd> 키를 눌러 관리자 메뉴 열기</li>
              <li><strong>Windows PowerShell(관리자)</strong> 선택</li>
              <li>다운로드한 스크립트 파일의 경로로 이동</li>
              <li>
                <code>Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser</code>
                실행
              </li>
              <li><code>.\Antivirus_Check.ps1</code> 명령어로 스크립트 실행</li>
            </ol>
          </div>
        </div>

        <!-- 추가 보안 팁 -->
        <div class="section">
          <h2 class="section-title">추가 보안 팁</h2>
          <div class="info-grid">
            <div class="info-card warning">
              <div class="info-icon">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"
                  />
                </svg>
              </div>
              <div class="info-content">
                <h3>주의사항</h3>
                <ul>
                  <li>여러 백신 프로그램을 동시에 설치하면 충돌이 발생할 수 있습니다</li>
                  <li>백신 업데이트는 정기적으로 실행해야 합니다</li>
                  <li>실시간 보호 기능을 임의로 비활성화하지 마세요</li>
                  <li>의심스러운 파일은 백신 검사 후 실행하세요</li>
                </ul>
              </div>
            </div>
            <div class="info-card tip">
              <div class="info-icon">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412-1 4.705c-.07.34.029.533.304.533.194 0 .487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381 2.29-.287zM8 5.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"
                  />
                </svg>
              </div>
              <div class="info-content">
                <h3>권장사항</h3>
                <ul>
                  <li>알약 백신의 정기 검사 일정을 설정하세요</li>
                  <li>백신 로그를 정기적으로 확인하세요</li>
                  <li>의심스러운 이메일 첨부파일은 열지 마세요</li>
                  <li>정품 소프트웨어만 설치하고 사용하세요</li>
                </ul>
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
<script setup>
// Script 부분
import { ref } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Sidebar from '@/components/Sidebar.vue'
import PageNavigation from '@/components/PageNavigation.vue'

const route = useRoute()
const authStore = useAuthStore()
const sidebarRef = ref(null)

// 백신 확인 스크립트
const antivirusCheckScript = `# 백신 상태 확인 스크립트
# AhnLab V3(알약) 백신 상태를 확인합니다.

Write-Host "=== 백신 상태 확인 스크립트 ===" -ForegroundColor Cyan
Write-Host ""

try {
    Write-Host "1. 설치된 백신 소프트웨어 확인" -ForegroundColor Yellow
    $antivirusProducts = Get-WmiObject -Namespace "root\\SecurityCenter2" -Class AntiVirusProduct -ErrorAction SilentlyContinue

    if ($antivirusProducts) {
        foreach ($av in $antivirusProducts) {
            $displayName = $av.displayName
            $productState = $av.productState

            # productState 해석 (간단한 버전)
            $isEnabled = ($productState -band 0x1000) -ne 0
            $isUpToDate = ($productState -band 0x10) -eq 0

            Write-Host "- 백신명: $displayName" -ForegroundColor White
            Write-Host "- 상태: $($isEnabled ? '활성화됨' : '비활성화됨')" -ForegroundColor $($isEnabled ? 'Green' : 'Red')
            Write-Host "- 업데이트: $($isUpToDate ? '최신' : '구버전')" -ForegroundColor $($isUpToDate ? 'Green' : 'Yellow')

            # 알약 백신 확인
            if ($displayName -like "*AhnLab*" -or $displayName -like "*알약*" -or $displayName -like "*V3*") {
                Write-Host "✓ 알약(AhnLab) 백신이 설치되어 있습니다!" -ForegroundColor Green
            }
            Write-Host ""
        }
    } else {
        Write-Host "⚠ 백신 정보를 찾을 수 없습니다." -ForegroundColor Yellow
    }

    Write-Host "2. 설치된 프로그램에서 알약 확인" -ForegroundColor Yellow
    $ahnlabPrograms = Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* |
                     Where-Object {$_.DisplayName -like "*AhnLab*" -or $_.DisplayName -like "*알약*" -or $_.DisplayName -like "*V3*"}

    if ($ahnlabPrograms) {
        foreach ($program in $ahnlabPrograms) {
            Write-Host "- 프로그램: $($program.DisplayName)" -ForegroundColor Green
            Write-Host "- 버전: $($program.DisplayVersion)" -ForegroundColor White
            Write-Host "- 설치일: $($program.InstallDate)" -ForegroundColor White
            Write-Host ""
        }
    } else {
        Write-Host "⚠ 알약 백신이 설치되어 있지 않습니다." -ForegroundColor Red
    }

    Write-Host "3. Windows Defender 상태 (참고용)" -ForegroundColor Yellow
    $defenderStatus = Get-MpComputerStatus -ErrorAction SilentlyContinue
    if ($defenderStatus) {
        Write-Host "- Windows Defender 활성화: $($defenderStatus.AntivirusEnabled)" -ForegroundColor White
        Write-Host "- 실시간 보호: $($defenderStatus.RealTimeProtectionEnabled)" -ForegroundColor White
        Write-Host "- 시그니처 업데이트: $($defenderStatus.AntivirusSignatureLastUpdated)" -ForegroundColor White
    }

    Write-Host ""
    Write-Host "=== 권장사항 ===" -ForegroundColor Cyan
    Write-Host "✓ 알약(AhnLab) 백신이 설치되어 있어야 합니다" -ForegroundColor Green
    Write-Host "✓ 실시간 보호 기능이 활성화되어 있어야 합니다" -ForegroundColor Green
    Write-Host "✓ 백신 정의 파일이 최신 상태여야 합니다" -ForegroundColor Green
    Write-Host "✓ 정기적인 시스템 검사를 실행하세요" -ForegroundColor Green

} catch {
    Write-Host "백신 상태 확인 중 오류가 발생했습니다: $($_.Exception.Message)" -ForegroundColor Red
}

Read-Host "아무 키나 누르면 종료됩니다"`

// 메서드
const copyToClipboard = async () => {
  const codeText = `# 설치된 백신 소프트웨어 확인
Get-WmiObject -Namespace "root\\SecurityCenter2" -Class AntiVirusProduct | Select-Object displayName, productState

# 알약 백신 설치 확인
Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Where-Object {$_.DisplayName -like "*AhnLab*" -or $_.DisplayName -like "*알약*"} | Select-Object DisplayName, DisplayVersion

# Windows Defender 상태 확인 (보조 확인용)
Get-MpComputerStatus | Select-Object AntivirusEnabled, RealTimeProtectionEnabled, AntivirusSignatureLastUpdated`

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

// 백신 확인 스크립트 다운로드
const downloadCheckScript = () => {
  downloadScript(antivirusCheckScript, 'Antivirus_Check.ps1')
}
</script>

/* Style 부분 */
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
