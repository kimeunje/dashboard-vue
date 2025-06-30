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
          <p>공유폴더 점검 가이드를 확인하려면 로그인이 필요합니다.</p>
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
        <h1 class="page-title">공유폴더 확인</h1>

        <!-- 개요 -->
        <div class="section">
          <h2 class="section-title">개요</h2>
          <p>
            공유폴더는 네트워크상의 다른 사용자들이 파일에 접근할 수 있도록 하는 기능입니다. 하지만
            불필요하거나 잘못 설정된 공유폴더는 심각한 보안 위험을 초래할 수 있으므로, 정기적인
            점검과 관리가 필요합니다.
          </p>
        </div>

        <!-- 보안 위험 요소 -->
        <div class="section">
          <h2 class="section-title">공유폴더 보안 위험 요소</h2>
          <div class="risk-grid">
            <div class="risk-card high">
              <div class="risk-icon">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"
                  />
                </svg>
              </div>
              <h3>무제한 접근 권한</h3>
              <p>Everyone 그룹에 전체 제어 권한이 부여된 공유폴더는 누구나 접근 가능합니다.</p>
            </div>
            <div class="risk-card medium">
              <div class="risk-icon">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M1 2.828c.885-.37 2.154-.769 3.388-.893 1.33-.134 2.458.063 3.112.752v9.746c-.935-.53-2.12-.603-3.213-.493-1.18.12-2.37.461-3.287.811V2.828zm7.5-.141c.654-.689 1.782-.886 3.112-.752 1.234.124 2.503.523 3.388.893v9.923c-.918-.35-2.107-.692-3.287-.81-1.094-.111-2.278-.039-3.213.492V2.687zM8 1.783C7.015.936 5.587.81 4.287.94c-1.514.153-3.042.672-3.994 1.105A.5.5 0 0 0 0 2.5v11a.5.5 0 0 0 .707.455c.882-.4 2.303-.881 3.68-1.02 1.409-.142 2.59.087 3.223.877a.5.5 0 0 0 .78 0c.633-.79 1.814-1.019 3.222-.877 1.378.139 2.8.62 3.681 1.02A.5.5 0 0 0 16 13.5v-11a.5.5 0 0 0-.293-.455c-.952-.433-2.48-.952-3.994-1.105C10.413.809 8.985.936 8 1.783z"
                  />
                </svg>
              </div>
              <h3>중요 데이터 노출</h3>
              <p>개인정보, 기밀문서 등 민감한 데이터가 포함된 폴더가 공유되는 경우입니다.</p>
            </div>
            <div class="risk-card low">
              <div class="risk-icon">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M8 1a2.5 2.5 0 0 1 2.5 2.5V4h-5v-.5A2.5 2.5 0 0 1 8 1zm3.5 3v-.5a3.5 3.5 0 1 0-7 0V4H1v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V4h-3.5zM2 5h12v9a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V5z"
                  />
                </svg>
              </div>
              <h3>불필요한 공유</h3>
              <p>더 이상 사용하지 않거나 임시로 생성했던 공유폴더가 방치된 경우입니다.</p>
            </div>
          </div>
        </div>

        <!-- 수동 확인 방법 -->
        <div class="section">
          <h2 class="section-title">수동 확인 방법</h2>

          <h3>1. 컴퓨터 관리를 통한 확인</h3>
          <ol>
            <li><kbd>Windows</kbd> + <kbd>X</kbd> 키를 눌러 관리자 메뉴 열기</li>
            <li><strong>컴퓨터 관리</strong> 선택</li>
            <li>
              좌측 트리에서 <strong>[시스템 도구]</strong> → <strong>[공유 폴더]</strong> →
              <strong>[공유]</strong> 선택
            </li>
            <li>현재 공유되고 있는 모든 폴더 목록 확인</li>
            <li>각 공유폴더를 우클릭하여 <strong>[속성]</strong> 선택 후 권한 확인</li>
          </ol>

          <h3>2. 네트워크 공유 센터 확인</h3>
          <ol>
            <li>
              <strong>제어판</strong> → <strong>네트워크 및 인터넷</strong> →
              <strong>네트워크 및 공유 센터</strong> 열기
            </li>
            <li>좌측 메뉴에서 <strong>[고급 공유 설정 변경]</strong> 클릭</li>
            <li>현재 네트워크 프로필의 공유 설정 상태 확인</li>
            <li>불필요한 공유 기능 비활성화</li>
          </ol>

          <h3>3. 명령어를 통한 확인</h3>
          <ol>
            <li><kbd>Windows</kbd> + <kbd>R</kbd> 키를 눌러 실행 창 열기</li>
            <li><code>cmd</code> 입력 후 <kbd>Enter</kbd></li>
            <li><code>net share</code> 명령어로 공유폴더 목록 확인</li>
            <li><code>net share [공유이름] /delete</code> 명령어로 불필요한 공유 제거</li>
          </ol>
        </div>

        <!-- 기본 공유폴더 설명 -->
        <div class="section">
          <h2 class="section-title">Windows 기본 공유폴더</h2>
          <div class="default-shares-table">
            <table>
              <thead>
                <tr>
                  <th>공유 이름</th>
                  <th>실제 경로</th>
                  <th>용도</th>
                  <th>권장 조치</th>
                </tr>
              </thead>
              <tbody>
                <tr class="safe">
                  <td><code>ADMIN$</code></td>
                  <td>C:\Windows</td>
                  <td>시스템 관리용</td>
                  <td><span class="action-keep">유지</span></td>
                </tr>
                <tr class="safe">
                  <td><code>C$</code></td>
                  <td>C:\</td>
                  <td>시스템 드라이브 관리용</td>
                  <td><span class="action-keep">유지</span></td>
                </tr>
                <tr class="safe">
                  <td><code>IPC$</code></td>
                  <td>-</td>
                  <td>프로세스 간 통신</td>
                  <td><span class="action-keep">유지</span></td>
                </tr>
                <tr class="warning">
                  <td><code>Users</code></td>
                  <td>C:\Users</td>
                  <td>사용자 폴더</td>
                  <td><span class="action-check">권한 확인</span></td>
                </tr>
                <tr class="danger">
                  <td>사용자 생성 공유</td>
                  <td>다양함</td>
                  <td>개인/업무용</td>
                  <td><span class="action-review">검토 필요</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- PowerShell 확인 -->
        <div class="section">
          <h2 class="section-title">PowerShell을 이용한 확인</h2>
          <div class="code-block">
            <h3>공유폴더 확인 명령어</h3>
            <div class="code-container">
              <pre><code># 모든 공유폴더 목록 확인
Get-SmbShare | Select-Object Name, Path, Description

# 세부 공유 정보 확인
Get-SmbShare | Format-Table Name, Path, ShareType, CurrentUsers -AutoSize

# 공유폴더 권한 확인
Get-SmbShareAccess -Name "*" | Format-Table ShareName, AccountName, AccessControlType, AccessRight

# 특정 공유폴더의 상세 정보
Get-SmbShare -Name "공유이름" | Get-SmbShareAccess</code></pre>
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

        <!-- 보안 설정 가이드 -->
        <div class="section">
          <h2 class="section-title">안전한 공유폴더 설정 가이드</h2>

          <h3>1. 최소 권한 원칙 적용</h3>
          <ul>
            <li>필요한 사용자에게만 최소한의 권한 부여</li>
            <li>"Everyone" 그룹 사용 지양</li>
            <li>읽기 전용 권한을 우선적으로 고려</li>
            <li>관리자 권한은 신중하게 부여</li>
          </ul>

          <h3>2. 정기적인 권한 검토</h3>
          <ul>
            <li>분기별 공유폴더 및 권한 점검</li>
            <li>퇴사자 계정의 공유폴더 접근 권한 즉시 제거</li>
            <li>프로젝트 완료 후 임시 공유폴더 정리</li>
            <li>사용하지 않는 공유폴더 비활성화</li>
          </ul>

          <h3>3. 공유폴더 명명 규칙</h3>
          <ul>
            <li>명확하고 이해하기 쉬운 이름 사용</li>
            <li>용도를 알 수 있는 설명 추가</li>
            <li>임시 공유폴더에는 날짜 포함</li>
            <li>중요도에 따른 분류 체계 구축</li>
          </ul>
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
                <h3>공유폴더 점검 스크립트</h3>
                <p>현재 시스템의 모든 공유폴더와 권한을 상세히 분석하여 보안 위험을 식별합니다.</p>
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
            <div class="script-card">
              <div class="script-icon cleanup">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M6.5 1h3a.5.5 0 0 1 .5.5v1H6v-1a.5.5 0 0 1 .5-.5ZM11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3A1.5 1.5 0 0 0 5 1.5v1H2.506a.58.58 0 0 0-.01 0H1.5a.5.5 0 0 0 0 1h.538l.853 10.66A2 2 0 0 0 4.885 16h6.23a2 2 0 0 0 1.994-1.84l.853-10.66h.538a.5.5 0 0 0 0-1h-.995a.59.59 0 0 0-.01 0H11Zm1.958 1-.846 10.58a1 1 0 0 1-.997.92h-6.23a1 1 0 0 1-.997-.92L3.042 3.5h9.916Zm-7.487 1a.5.5 0 0 1 .528.47l.5 8.5a.5.5 0 0 1-.998.06L5 5.03a.5.5 0 0 1 .47-.53Zm5.058 0a.5.5 0 0 1 .47.53l-.5 8.5a.5.5 0 1 1-.998-.06l.5-8.5a.5.5 0 0 1 .528-.47ZM8 4.5a.5.5 0 0 1 .5.5v8.5a.5.5 0 0 1-1 0V5a.5.5 0 0 1 .5-.5Z"
                  />
                </svg>
              </div>
              <div class="script-content">
                <h3>불필요한 공유 정리 스크립트</h3>
                <p>사용하지 않는 공유폴더를 식별하고 안전하게 제거하는 스크립트입니다.</p>
                <button @click="downloadCleanupScript" class="download-button warning">
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
              <li>스크립트 실행 전 중요 데이터 백업 권장</li>
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
                  <li>기본 시스템 공유(ADMIN$, C$, IPC$)는 함부로 제거하지 마세요</li>
                  <li>공유 제거 전 현재 사용자가 있는지 확인하세요</li>
                  <li>중요한 업무용 공유는 백업 후 변경하세요</li>
                  <li>공유폴더 변경 후 네트워크 연결 테스트를 수행하세요</li>
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
                  <li>정기적으로 공유폴더 사용 현황을 모니터링하세요</li>
                  <li>파일 서버 로그를 통해 접근 기록을 확인하세요</li>
                  <li>DLP(Data Loss Prevention) 솔루션 도입을 검토하세요</li>
                  <li>직원들에게 공유폴더 보안 교육을 실시하세요</li>
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

// 공유폴더 점검 스크립트
const sharedFolderCheckScript = `# 공유폴더 점검 스크립트
# 현재 시스템의 공유폴더와 권한을 상세히 분석합니다.

Write-Host "=== 공유폴더 보안 점검 스크립트 ===" -ForegroundColor Cyan
Write-Host "시스템의 모든 공유폴더를 분석하여 보안 위험을 식별합니다." -ForegroundColor Yellow
Write-Host ""

# 관리자 권한 확인
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "이 스크립트는 관리자 권한이 필요합니다." -ForegroundColor Red
    Write-Host "PowerShell을 관리자 권한으로 실행해주세요." -ForegroundColor Red
    Read-Host "아무 키나 누르면 종료됩니다"
    exit 1
}

try {
    Write-Host "1. 전체 공유폴더 목록 확인" -ForegroundColor Yellow
    $shares = Get-SmbShare

    Write-Host "발견된 공유폴더: $($shares.Count)개" -ForegroundColor White
    Write-Host ""

    # 기본 시스템 공유
    $systemShares = @("ADMIN$", "C$", "D$", "E$", "F$", "IPC$")
    $userShares = $shares | Where-Object { $_.Name -notin $systemShares }
    $suspiciousShares = @()

    Write-Host "2. 공유폴더 상세 분석" -ForegroundColor Yellow
    Write-Host "=" * 60 -ForegroundColor Gray

    foreach ($share in $shares) {
        $isSystemShare = $share.Name -in $systemShares
        $shareType = if ($isSystemShare) { "시스템" } else { "사용자" }

        Write-Host "공유명: $($share.Name) [$shareType]" -ForegroundColor $(if($isSystemShare) {'Green'} else {'Yellow'})
        Write-Host "경로: $($share.Path)" -ForegroundColor White
        Write-Host "설명: $($share.Description)" -ForegroundColor Gray
        Write-Host "공유 타입: $($share.ShareType)" -ForegroundColor White

        # 현재 연결된 사용자 확인
        try {
            $sessions = Get-SmbConnection -ShareName $share.Name -ErrorAction SilentlyContinue
            if ($sessions) {
                Write-Host "현재 연결: $($sessions.Count)명" -ForegroundColor Cyan
            } else {
                Write-Host "현재 연결: 없음" -ForegroundColor Gray
            }
        } catch {
            Write-Host "현재 연결: 확인 불가" -ForegroundColor Gray
        }

        # 권한 확인
        try {
            $permissions = Get-SmbShareAccess -Name $share.Name
            Write-Host "접근 권한:" -ForegroundColor White

            $hasEveryoneAccess = $false
            $hasFullControl = $false

            foreach ($perm in $permissions) {
                $accessType = switch ($perm.AccessControlType) {
                    "Allow" { "허용" }
                    "Deny" { "거부" }
                    default { $perm.AccessControlType }
                }

                $accessRight = switch ($perm.AccessRight) {
                    "Full" { "전체 제어" }
                    "Change" { "변경" }
                    "Read" { "읽기" }
                    default { $perm.AccessRight }
                }

                $color = "White"
                if ($perm.AccountName -eq "Everyone" -and $perm.AccessControlType -eq "Allow") {
                    $hasEveryoneAccess = $true
                    $color = "Red"
                }
                if ($perm.AccessRight -eq "Full") {
                    $hasFullControl = $true
                    if ($perm.AccountName -eq "Everyone") {
                        $color = "Red"
                    } else {
                        $color = "Yellow"
                    }
                }

                Write-Host "  - $($perm.AccountName): $accessType/$accessRight" -ForegroundColor $color
            }

            # 보안 위험 평가
            $riskLevel = "낮음"
            $riskReasons = @()

            if ($hasEveryoneAccess) {
                $riskLevel = "높음"
                $riskReasons += "Everyone 그룹 접근 허용"
            }

            if ($hasFullControl -and -not $isSystemShare) {
                if ($riskLevel -eq "낮음") { $riskLevel = "중간" }
                $riskReasons += "전체 제어 권한 존재"
            }

            if ($share.Path -and (Test-Path $share.Path)) {
                $folderItems = Get-ChildItem $share.Path -ErrorAction SilentlyContinue
                if ($folderItems -and $folderItems.Count -gt 100) {
                    if ($riskLevel -eq "낮음") { $riskLevel = "중간" }
                    $riskReasons += "많은 파일 포함 ($($folderItems.Count)개)"
                }
            }

            $riskColor = switch ($riskLevel) {
                "높음" { "Red" }
                "중간" { "Yellow" }
                default { "Green" }
            }

            Write-Host "보안 위험도: $riskLevel" -ForegroundColor $riskColor
            if ($riskReasons.Count -gt 0) {
                Write-Host "위험 요소: $($riskReasons -join ', ')" -ForegroundColor $riskColor
            }

            if ($riskLevel -ne "낮음" -and -not $isSystemShare) {
                $suspiciousShares += [PSCustomObject]@{
                    Name = $share.Name
                    Path = $share.Path
                    RiskLevel = $riskLevel
                    Reasons = $riskReasons -join ', '
                }
            }

        } catch {
            Write-Host "권한 확인 실패: $($_.Exception.Message)" -ForegroundColor Red
        }

        Write-Host "-" * 60 -ForegroundColor Gray
    }

    Write-Host ""
    Write-Host "3. 보안 위험 요약" -ForegroundColor Yellow

    if ($suspiciousShares.Count -eq 0) {
        Write-Host "✓ 특별한 보안 위험이 발견되지 않았습니다." -ForegroundColor Green
    } else {
        Write-Host "⚠ 주의가 필요한 공유폴더: $($suspiciousShares.Count)개" -ForegroundColor Red
        Write-Host ""

        foreach ($suspicious in $suspiciousShares) {
            Write-Host "공유명: $($suspicious.Name)" -ForegroundColor Red
            Write-Host "경로: $($suspicious.Path)" -ForegroundColor White
            Write-Host "위험도: $($suspicious.RiskLevel)" -ForegroundColor Red
            Write-Host "이유: $($suspicious.Reasons)" -ForegroundColor Yellow
            Write-Host ""
        }
    }

    Write-Host "4. 네트워크 공유 설정 확인" -ForegroundColor Yellow
    try {
        $networkSharing = Get-SmbServerConfiguration | Select-Object EnableSMB1Protocol, EnableSMB2Protocol, RequireSecuritySignature
        Write-Host "SMB1 프로토콜: $($networkSharing.EnableSMB1Protocol ? '활성화' : '비활성화')" -ForegroundColor $(if($networkSharing.EnableSMB1Protocol) {'Red'} else {'Green'})
        Write-Host "SMB2 프로토콜: $($networkSharing.EnableSMB2Protocol ? '활성화' : '비활성화')" -ForegroundColor $(if($networkSharing.EnableSMB2Protocol) {'Green'} else {'Red'})
        Write-Host "보안 서명 필요: $($networkSharing.RequireSecuritySignature ? '활성화' : '비활성화')" -ForegroundColor $(if($networkSharing.RequireSecuritySignature) {'Green'} else {'Yellow'})
    } catch {
        Write-Host "네트워크 공유 설정 확인 실패" -ForegroundColor Red
    }

    Write-Host ""
    Write-Host "=== 권장사항 ===" -ForegroundColor Cyan
    Write-Host "✓ Everyone 그룹 접근 권한을 구체적인 사용자/그룹으로 변경" -ForegroundColor Green
    Write-Host "✓ 불필요한 공유폴더 제거" -ForegroundColor Green
    Write-Host "✓ 최소 권한 원칙 적용 (읽기 전용 우선)" -ForegroundColor Green
    Write-Host "✓ 정기적인 공유폴더 및 권한 점검" -ForegroundColor Green
    Write-Host "✓ SMB1 프로토콜 비활성화 (보안상 취약)" -ForegroundColor Green

} catch {
    Write-Host "공유폴더 점검 중 오류가 발생했습니다: $($_.Exception.Message)" -ForegroundColor Red
}

Read-Host "아무 키나 누르면 종료됩니다"`

// 공유폴더 정리 스크립트
const sharedFolderCleanupScript = `# 공유폴더 정리 스크립트
# 사용하지 않는 공유폴더를 식별하고 안전하게 제거합니다.

Write-Host "=== 공유폴더 정리 스크립트 ===" -ForegroundColor Cyan
Write-Host "주의: 이 스크립트는 공유폴더를 제거할 수 있습니다." -ForegroundColor Red
Write-Host "중요한 데이터의 백업을 먼저 수행하세요." -ForegroundColor Red
Write-Host ""

# 관리자 권한 확인
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "이 스크립트는 관리자 권한이 필요합니다." -ForegroundColor Red
    Write-Host "PowerShell을 관리자 권한으로 실행해주세요." -ForegroundColor Red
    Read-Host "아무 키나 누르면 종료됩니다"
    exit 1
}

$confirmation = Read-Host "정말로 공유폴더 정리를 진행하시겠습니까? (Y/N)"
if ($confirmation -ne "Y" -and $confirmation -ne "y") {
    Write-Host "작업이 취소되었습니다." -ForegroundColor Yellow
    Read-Host "아무 키나 누르면 종료됩니다"
    exit 0
}

try {
    Write-Host ""
    Write-Host "1. 현재 공유폴더 분석" -ForegroundColor Yellow

    $shares = Get-SmbShare
    $systemShares = @("ADMIN$", "C$", "D$", "E$", "F$", "IPC$", "print$")
    $userShares = $shares | Where-Object { $_.Name -notin $systemShares }

    Write-Host "사용자 생성 공유폴더: $($userShares.Count)개" -ForegroundColor White

    if ($userShares.Count -eq 0) {
        Write-Host "정리할 사용자 공유폴더가 없습니다." -ForegroundColor Green
        Read-Host "아무 키나 누르면 종료됩니다"
        exit 0
    }

    $toRemove = @()
    $toKeep = @()

    Write-Host ""
    Write-Host "2. 각 공유폴더 상태 확인" -ForegroundColor Yellow
    Write-Host "=" * 60 -ForegroundColor Gray

    foreach ($share in $userShares) {
        Write-Host "공유명: $($share.Name)" -ForegroundColor Cyan
        Write-Host "경로: $($share.Path)" -ForegroundColor White
        Write-Host "설명: $($share.Description)" -ForegroundColor Gray

        # 현재 연결 확인
        $hasConnections = $false
        try {
            $sessions = Get-SmbConnection -ShareName $share.Name -ErrorAction SilentlyContinue
            if ($sessions -and $sessions.Count -gt 0) {
                $hasConnections = $true
                Write-Host "현재 연결: $($sessions.Count)명 (활성 사용 중)" -ForegroundColor Red
            } else {
                Write-Host "현재 연결: 없음" -ForegroundColor Green
            }
        } catch {
            Write-Host "현재 연결: 확인 불가" -ForegroundColor Gray
        }

        # 폴더 존재 및 사용 현황 확인
        $folderExists = Test-Path $share.Path -ErrorAction SilentlyContinue
        $isEmpty = $false
        $isOld = $false

        if ($folderExists) {
            Write-Host "폴더 상태: 존재함" -ForegroundColor Green
            try {
                $items = Get-ChildItem $share.Path -ErrorAction SilentlyContinue
                if (-not $items -or $items.Count -eq 0) {
                    $isEmpty = $true
                    Write-Host "폴더 내용: 비어있음" -ForegroundColor Yellow
                } else {
                    Write-Host "폴더 내용: $($items.Count)개 파일/폴더" -ForegroundColor White

                    # 최근 수정일 확인
                    $latestModified = $items | Sort-Object LastWriteTime -Descending | Select-Object -First 1
                    if ($latestModified) {
                        $daysSinceModified = (Get-Date) - $latestModified.LastWriteTime
                        Write-Host "최근 수정: $($daysSinceModified.Days)일 전" -ForegroundColor $(if($daysSinceModified.Days -gt 90) {'Yellow'} else {'White'})
                        if ($daysSinceModified.Days -gt 90) {
                            $isOld = $true
                        }
                    }
                }
            } catch {
                Write-Host "폴더 내용 확인 실패" -ForegroundColor Red
            }
        } else {
            Write-Host "폴더 상태: 존재하지 않음 (경로 오류)" -ForegroundColor Red
        }

        # 권한 위험도 확인
        $hasRisk = $false
        try {
            $permissions = Get-SmbShareAccess -Name $share.Name
            $everyoneAccess = $permissions | Where-Object { $_.AccountName -eq "Everyone" -and $_.AccessControlType -eq "Allow" }
            if ($everyoneAccess) {
                $hasRisk = $true
                Write-Host "보안 위험: Everyone 그룹 접근 허용" -ForegroundColor Red
            }
        } catch {
            Write-Host "권한 확인 실패" -ForegroundColor Red
        }

        # 제거 권장 여부 결정
        $shouldRemove = $false
        $removeReasons = @()

        if (-not $folderExists) {
            $shouldRemove = $true
            $removeReasons += "폴더가 존재하지 않음"
        } elseif ($isEmpty -and -not $hasConnections) {
            $shouldRemove = $true
            $removeReasons += "빈 폴더이며 사용되지 않음"
        } elseif ($isOld -and -not $hasConnections) {
            $shouldRemove = $true
            $removeReasons += "오래된 파일(90일 이상)이며 사용되지 않음"
        }

        if ($hasConnections) {
            $removeReasons = @("현재 사용 중이므로 제거 불가")
            $shouldRemove = $false
        }

        if ($shouldRemove) {
            Write-Host "권장: 제거" -ForegroundColor Red
            Write-Host "이유: $($removeReasons -join ', ')" -ForegroundColor Yellow
            $toRemove += [PSCustomObject]@{
                Name = $share.Name
                Path = $share.Path
                Reasons = $removeReasons -join ', '
                HasConnections = $hasConnections
            }
        } else {
            Write-Host "권장: 유지" -ForegroundColor Green
            if ($removeReasons.Count -gt 0) {
                Write-Host "이유: $($removeReasons -join ', ')" -ForegroundColor White
            }
            $toKeep += $share
        }

        Write-Host "-" * 60 -ForegroundColor Gray
    }

    Write-Host ""
    Write-Host "3. 정리 권장 요약" -ForegroundColor Yellow

    if ($toRemove.Count -eq 0) {
        Write-Host "제거를 권장하는 공유폴더가 없습니다." -ForegroundColor Green
    } else {
        Write-Host "제거 권장: $($toRemove.Count)개" -ForegroundColor Red
        Write-Host "유지 권장: $($toKeep.Count)개" -ForegroundColor Green
        Write-Host ""

        Write-Host "제거 권장 공유폴더:" -ForegroundColor Red
        foreach ($item in $toRemove) {
            Write-Host "- $($item.Name): $($item.Reasons)" -ForegroundColor Yellow
        }

        Write-Host ""
        $proceedRemoval = Read-Host "위의 공유폴더들을 제거하시겠습니까? (Y/N)"

        if ($proceedRemoval -eq "Y" -or $proceedRemoval -eq "y") {
            Write-Host ""
            Write-Host "4. 공유폴더 제거 실행" -ForegroundColor Yellow

            foreach ($item in $toRemove) {
                if ($item.HasConnections) {
                    Write-Host "건너뜀: $($item.Name) (연결된 사용자 있음)" -ForegroundColor Yellow
                    continue
                }

                try {
                    Remove-SmbShare -Name $item.Name -Force
                    Write-Host "✓ 제거 완료: $($item.Name)" -ForegroundColor Green
                } catch {
                    Write-Host "✗ 제거 실패: $($item.Name) - $($_.Exception.Message)" -ForegroundColor Red
                }
            }
        } else {
            Write-Host "공유폴더 제거가 취소되었습니다." -ForegroundColor Yellow
        }
    }

    Write-Host ""
    Write-Host "=== 정리 완료 ===" -ForegroundColor Cyan
    Write-Host "정기적인 공유폴더 점검을 권장합니다." -ForegroundColor Green

} catch {
    Write-Host "공유폴더 정리 중 오류가 발생했습니다: $($_.Exception.Message)" -ForegroundColor Red
}

Read-Host "아무 키나 누르면 종료됩니다"`

// 메서드
const copyToClipboard = async () => {
  const codeText = `# 모든 공유폴더 목록 확인
Get-SmbShare | Select-Object Name, Path, Description

# 세부 공유 정보 확인
Get-SmbShare | Format-Table Name, Path, ShareType, CurrentUsers -AutoSize

# 공유폴더 권한 확인
Get-SmbShareAccess -Name "*" | Format-Table ShareName, AccountName, AccessControlType, AccessRight

# 특정 공유폴더의 상세 정보
Get-SmbShare -Name "공유이름" | Get-SmbShareAccess`

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

// 공유폴더 점검 스크립트 다운로드
const downloadCheckScript = () => {
  downloadScript(sharedFolderCheckScript, 'SharedFolder_Check.ps1')
}

// 공유폴더 정리 스크립트 다운로드
const downloadCleanupScript = () => {
  downloadScript(sharedFolderCleanupScript, 'SharedFolder_Cleanup.ps1')
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

/* 위험 요소 그리드 */
.risk-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.risk-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  transition: all 0.3s ease;
  border-left: 4px solid;
}

.risk-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.risk-card.high {
  border-left-color: #ef4444;
  background: linear-gradient(135deg, #fef2f2, #ffffff);
}

.risk-card.medium {
  border-left-color: #f59e0b;
  background: linear-gradient(135deg, #fefbf2, #ffffff);
}

.risk-card.low {
  border-left-color: #3b82f6;
  background: linear-gradient(135deg, #eff6ff, #ffffff);
}

.risk-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  color: white;
}

.risk-card.high .risk-icon {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.risk-card.medium .risk-icon {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.risk-card.low .risk-icon {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
}

.risk-card h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--dark-blue);
  margin: 0 0 8px 0;
}

.risk-card p {
  color: #6b7280;
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0;
}

/* 기본 공유폴더 테이블 */
.default-shares-table {
  margin: 20px 0;
  overflow-x: auto;
}

.default-shares-table table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.default-shares-table th {
  background: var(--primary-color);
  color: white;
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
}

.default-shares-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
}

.default-shares-table tr:last-child td {
  border-bottom: none;
}

.default-shares-table tr.safe {
  background: #f0fdf4;
}

.default-shares-table tr.warning {
  background: #fefbf2;
}

.default-shares-table tr.danger {
  background: #fef2f2;
}

.default-shares-table code {
  background: #f3f4f6;
  color: #1f2937;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.875rem;
}

.action-keep {
  background: #dcfce7;
  color: #166534;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.875rem;
}

.action-check {
  background: #fef3c7;
  color: #92400e;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.875rem;
}

.action-review {
  background: #fee2e2;
  color: #991b1b;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.875rem;
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

.script-icon.cleanup {
  background: linear-gradient(135deg, #f59e0b, #d97706);
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

.download-button.warning {
  background-color: #f59e0b;
  color: white;
}

.download-button.warning:hover {
  background-color: #d97706;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(245, 158, 11, 0.3);
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

  .risk-grid {
    grid-template-columns: 1fr;
  }

  .script-download-section {
    grid-template-columns: 1fr;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .default-shares-table {
    font-size: 0.875rem;
  }

  .default-shares-table th,
  .default-shares-table td {
    padding: 8px 12px;
  }
}

@media (max-width: 480px) {
  .default-shares-table th,
  .default-shares-table td {
    padding: 6px 8px;
    font-size: 0.8rem;
  }

  .risk-icon {
    width: 50px;
    height: 50px;
  }

  .action-keep,
  .action-check,
  .action-review {
    font-size: 0.75rem;
    padding: 2px 6px;
  }
}
</style>
