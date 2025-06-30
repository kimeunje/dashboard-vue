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
          <p>원격 데스크톱 제한 가이드를 확인하려면 로그인이 필요합니다.</p>
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
        <h1 class="page-title">원격 데스크톱 제한</h1>

        <!-- 개요 -->
        <div class="section">
          <h2 class="section-title">개요</h2>
          <p>
            원격 데스크톱 연결(RDP)은 네트워크를 통해 컴퓨터에 원격으로 접근할 수 있는 기능입니다.
            편리한 기능이지만 보안상 큰 위험을 초래할 수 있으므로, 불필요한 경우 비활성화하거나
            엄격한 접근 제한을 적용해야 합니다.
          </p>
        </div>

        <!-- 보안 위험 요소 -->
        <div class="section">
          <h2 class="section-title">원격 데스크톱 보안 위험</h2>
          <div class="risk-grid">
            <div class="risk-card critical">
              <div class="risk-icon">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M6 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm-5 6s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1H1zM11 3.5a.5.5 0 0 1 .5-.5h4a.5.5 0 0 1 0 1h-4a.5.5 0 0 1-.5-.5zm.5 2.5a.5.5 0 0 0 0 1h4a.5.5 0 0 0 0-1h-4zm2 3a.5.5 0 0 0 0 1h2a.5.5 0 0 0 0-1h-2zm0 3a.5.5 0 0 0 0 1h2a.5.5 0 0 0 0-1h-2z"
                  />
                </svg>
              </div>
              <h3>무단 접근</h3>
              <p>약한 패스워드나 설정 오류로 인해 악의적인 사용자가 시스템에 침입할 수 있습니다.</p>
            </div>
            <div class="risk-card high">
              <div class="risk-icon">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M11.251.068a.5.5 0 0 1 .227.58L9.677 6.5H13a.5.5 0 0 1 .364.843l-8 8.5a.5.5 0 0 1-.842-.49L6.323 9.5H3a.5.5 0 0 1-.364-.843l8-8.5a.5.5 0 0 1 .615-.09z"
                  />
                </svg>
              </div>
              <h3>브루트포스 공격</h3>
              <p>자동화된 도구를 사용하여 패스워드를 무차별 대입으로 시도하는 공격에 취약합니다.</p>
            </div>
            <div class="risk-card medium">
              <div class="risk-icon">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M8 1a2.5 2.5 0 0 1 2.5 2.5V4h-5v-.5A2.5 2.5 0 0 1 8 1zm3.5 3v-.5a3.5 3.5 0 1 0-7 0V4H1v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V4h-3.5zM2 5h12v9a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V5z"
                  />
                </svg>
              </div>
              <h3>데이터 유출</h3>
              <p>원격 접속을 통해 중요한 데이터가 외부로 유출될 가능성이 있습니다.</p>
            </div>
          </div>
        </div>

        <!-- 보안 설정 단계 -->
        <div class="section">
          <h2 class="section-title">보안 설정 단계</h2>
          <div class="security-levels">
            <div class="level-card recommended">
              <div class="level-header">
                <div class="level-icon">
                  <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                    <path
                      d="M10.97 4.97a.235.235 0 0 0-.02.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.061L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"
                    />
                  </svg>
                </div>
                <h3>권장: 완전 비활성화</h3>
                <span class="level-badge safe">가장 안전</span>
              </div>
              <p>원격 데스크톱을 완전히 비활성화하여 외부 접근을 차단합니다.</p>
              <ul>
                <li>시스템 보안 최대화</li>
                <li>네트워크 공격 차단</li>
                <li>자원 절약</li>
              </ul>
            </div>
            <div class="level-card conditional">
              <div class="level-header">
                <div class="level-icon">
                  <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                    <path
                      d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"
                    />
                  </svg>
                </div>
                <h3>조건부: 제한적 허용</h3>
                <span class="level-badge warning">주의 필요</span>
              </div>
              <p>업무상 필요한 경우에만 엄격한 조건 하에 허용합니다.</p>
              <ul>
                <li>특정 IP 주소만 허용</li>
                <li>강력한 인증 요구</li>
                <li>접속 로그 모니터링</li>
                <li>VPN 연결 필수</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- 수동 비활성화 방법 -->
        <div class="section">
          <h2 class="section-title">수동 비활성화 방법</h2>

          <h3>방법 1: 시스템 속성을 통한 비활성화</h3>
          <ol>
            <li>
              <kbd>Windows</kbd> + <kbd>Pause</kbd> 키를 누르거나 <strong>내 컴퓨터</strong> 우클릭
              → <strong>속성</strong>
            </li>
            <li>좌측 메뉴에서 <strong>고급 시스템 설정</strong> 클릭</li>
            <li><strong>원격</strong> 탭 선택</li>
            <li><strong>"이 컴퓨터에 대한 원격 데스크톱을 사용하지 않음"</strong> 선택</li>
            <li><strong>확인</strong> 버튼 클릭하여 적용</li>
          </ol>

          <h3>방법 2: 레지스트리를 통한 비활성화</h3>
          <ol>
            <li><kbd>Windows</kbd> + <kbd>R</kbd> 키를 눌러 실행 창 열기</li>
            <li><code>regedit</code> 입력 후 <kbd>Enter</kbd></li>
            <li>
              다음 경로로 이동:
              <code>HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Terminal Server</code>
            </li>
            <li><code>fDenyTSConnections</code> 값을 <strong>1</strong>로 설정</li>
            <li>시스템 재부팅</li>
          </ol>

          <h3>방법 3: 서비스 비활성화</h3>
          <ol>
            <li><kbd>Windows</kbd> + <kbd>R</kbd> 키를 눌러 실행 창 열기</li>
            <li><code>services.msc</code> 입력 후 <kbd>Enter</kbd></li>
            <li><strong>Remote Desktop Services</strong> 서비스 찾기</li>
            <li>서비스를 우클릭하여 <strong>속성</strong> 선택</li>
            <li>시작 유형을 <strong>사용 안 함</strong>으로 변경</li>
            <li>서비스가 실행 중이면 <strong>중지</strong> 버튼 클릭</li>
          </ol>
        </div>

        <!-- 방화벽 설정 -->
        <div class="section">
          <h2 class="section-title">방화벽 규칙 설정</h2>

          <h3>Windows 방화벽에서 RDP 차단</h3>
          <ol>
            <li><kbd>Windows</kbd> + <kbd>R</kbd> 키를 눌러 실행 창 열기</li>
            <li>
              <code>wf.msc</code> 입력 후 <kbd>Enter</kbd> (고급 보안이 포함된 Windows Defender
              방화벽)
            </li>
            <li>좌측에서 <strong>인바운드 규칙</strong> 선택</li>
            <li>
              <strong>원격 데스크톱</strong> 관련 규칙들을 찾아서 모두
              <strong>사용 안 함</strong>으로 설정
            </li>
            <li>또는 규칙을 삭제하여 완전히 차단</li>
          </ol>

          <div class="firewall-rules-table">
            <table>
              <thead>
                <tr>
                  <th>규칙 이름</th>
                  <th>포트</th>
                  <th>프로토콜</th>
                  <th>권장 조치</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>원격 데스크톱 - 사용자 모드(TCP-In)</td>
                  <td>3389</td>
                  <td>TCP</td>
                  <td><span class="action-disable">비활성화</span></td>
                </tr>
                <tr>
                  <td>원격 데스크톱 - 사용자 모드(UDP-In)</td>
                  <td>3389</td>
                  <td>UDP</td>
                  <td><span class="action-disable">비활성화</span></td>
                </tr>
                <tr>
                  <td>원격 데스크톱 - 섀도우(TCP-In)</td>
                  <td>다양함</td>
                  <td>TCP</td>
                  <td><span class="action-disable">비활성화</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- PowerShell 확인 -->
        <div class="section">
          <h2 class="section-title">PowerShell을 이용한 확인</h2>
          <div class="code-block">
            <h3>원격 데스크톱 상태 확인 명령어</h3>
            <div class="code-container">
              <pre><code># 원격 데스크톱 설정 상태 확인
Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server" -Name "fDenyTSConnections"

# 원격 데스크톱 서비스 상태 확인
Get-Service -Name "TermService" | Select-Object Name, Status, StartType

# 방화벽 규칙 확인
Get-NetFirewallRule -DisplayGroup "원격 데스크톱" | Select-Object DisplayName, Enabled, Direction

# 현재 RDP 연결 확인
qwinsta

# 네트워크 포트 3389 사용 확인
netstat -an | findstr :3389</code></pre>
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

        <!-- 안전한 원격 접속 대안 -->
        <div class="section">
          <h2 class="section-title">안전한 원격 접속 대안</h2>

          <div class="alternatives-grid">
            <div class="alternative-card">
              <div class="alternative-icon vpn">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M6 10.5a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1h-3a.5.5 0 0 1-.5-.5zm-2-3a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7a.5.5 0 0 1-.5-.5zm-2-3a.5.5 0 0 1 .5-.5h11a.5.5 0 0 1 0 1h-11a.5.5 0 0 1-.5-.5z"
                  />
                </svg>
              </div>
              <h3>VPN 연결</h3>
              <p>가상 사설망을 통한 안전한 원격 접속</p>
              <ul>
                <li>암호화된 통신</li>
                <li>접근 통제</li>
                <li>중앙 관리</li>
              </ul>
            </div>
            <div class="alternative-card">
              <div class="alternative-icon ssh">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M13.5 3a.5.5 0 0 1 .5.5V11H2V3.5a.5.5 0 0 1 .5-.5h11zm-11-1A1.5 1.5 0 0 0 1 3.5V12h14V3.5A1.5 1.5 0 0 0 13.5 2h-11zM5 4a.5.5 0 0 0 0 1h6a.5.5 0 0 0 0-1H5zM4.5 7a.5.5 0 0 0 0 1h7a.5.5 0 0 0 0-1h-7z"
                  />
                </svg>
              </div>
              <h3>SSH 터널링</h3>
              <p>SSH를 통한 보안 터널 구성</p>
              <ul>
                <li>강력한 암호화</li>
                <li>키 기반 인증</li>
                <li>포트 포워딩</li>
              </ul>
            </div>
            <div class="alternative-card">
              <div class="alternative-icon cloud">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M4.406 3.342A5.53 5.53 0 0 1 8 2c2.69 0 4.923 2 5.166 4.579C14.758 6.804 16 8.137 16 9.773 16 11.569 14.502 13 12.687 13H3.781C1.708 13 0 11.366 0 9.318c0-1.763 1.266-3.223 2.942-3.593.143-.863.698-1.723 1.464-2.383z"
                  />
                </svg>
              </div>
              <h3>클라우드 솔루션</h3>
              <p>클라우드 기반 원격 데스크톱 서비스</p>
              <ul>
                <li>전문 보안 관리</li>
                <li>확장성</li>
                <li>중앙 모니터링</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- 스크립트 다운로드 섹션 -->
        <div class="section">
          <h2 class="section-title">자동화 스크립트</h2>
          <div class="script-download-section">
            <div class="script-card">
              <div class="script-icon disable">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M6.146 8.146a.5.5 0 0 1 .708 0L8 9.293l1.146-1.147a.5.5 0 1 1 .708.708L8.707 10l1.147 1.146a.5.5 0 0 1-.708.708L8 10.707l-1.146 1.147a.5.5 0 0 1-.708-.708L7.293 10 6.146 8.854a.5.5 0 0 1 0-.708z"
                  />
                  <path
                    d="M4 1.5H3a2 2 0 0 0-2 2V14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V3.5a2 2 0 0 0-2-2h-1v1A2.5 2.5 0 0 1 9.5 5h-3A2.5 2.5 0 0 1 4 2.5v-1zM6 2.5v1a1.5 1.5 0 0 0 1.5 1.5h3A1.5 1.5 0 0 0 12 3.5v-1a0.5 0.5 0 0 0-0.5-0.5h-5A0.5 0.5 0 0 0 6 2.5z"
                  />
                </svg>
              </div>
              <div class="script-content">
                <h3>원격 데스크톱 비활성화 스크립트</h3>
                <p>
                  원격 데스크톱을 안전하게 비활성화하고 관련 서비스 및 방화벽 규칙을 설정합니다.
                </p>
                <button @click="downloadDisableScript" class="download-button danger">
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
              <div class="script-icon check">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M10.97 4.97a.235.235 0 0 0-.02.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.061L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"
                  />
                </svg>
              </div>
              <div class="script-content">
                <h3>원격 데스크톱 상태 확인 스크립트</h3>
                <p>현재 원격 데스크톱 설정 상태와 보안 취약점을 상세히 분석합니다.</p>
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
              <li>비활성화 스크립트 실행 전 현재 연결된 사용자가 있는지 확인</li>
            </ol>
          </div>
        </div>

        <!-- 모니터링 및 로그 -->
        <div class="section">
          <h2 class="section-title">모니터링 및 로그 관리</h2>

          <h3>RDP 접속 로그 확인</h3>
          <p>원격 데스크톱 접속 시도 및 성공/실패 기록을 확인할 수 있습니다:</p>
          <ul>
            <li>
              <strong>이벤트 뷰어</strong> → <strong>Windows 로그</strong> → <strong>보안</strong>
            </li>
            <li>이벤트 ID 4624: 성공적인 로그온</li>
            <li>이벤트 ID 4625: 실패한 로그온 시도</li>
            <li>이벤트 ID 4634: 계정 로그오프</li>
            <li>이벤트 ID 4647: 사용자가 시작한 로그오프</li>
          </ul>

          <h3>정기적인 보안 점검</h3>
          <ul>
            <li>월별 RDP 설정 상태 확인</li>
            <li>접속 로그 분석 및 이상 징후 탐지</li>
            <li>네트워크 방화벽 규칙 검토</li>
            <li>사용자 계정 및 권한 점검</li>
          </ul>
        </div>

        <!-- 추가 보안 팁 -->
        <div class="section">
          <h2 class="section-title">추가 보안 팁</h2>
          <div class="info-grid">
            <div class="info-card critical">
              <div class="info-icon">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"
                  />
                </svg>
              </div>
              <div class="info-content">
                <h3>중요 주의사항</h3>
                <ul>
                  <li>RDP 비활성화 전 현재 원격 작업 중인 사용자가 있는지 확인</li>
                  <li>서버 환경에서는 신중하게 결정 (원격 관리 필요성 고려)</li>
                  <li>설정 변경 후 로컬 접근이 가능한지 확인</li>
                  <li>방화벽 변경 시 다른 서비스에 영향 없는지 검토</li>
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
                  <li>정말 필요한 경우가 아니면 RDP를 비활성화하세요</li>
                  <li>대안적인 원격 접속 방법을 검토하세요</li>
                  <li>네트워크 레벨에서 접근 제한을 적용하세요</li>
                  <li>정기적으로 시스템 보안 상태를 점검하세요</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 복구 방법 -->
        <div class="section">
          <h2 class="section-title">설정 복구 방법</h2>
          <div class="recovery-info">
            <h3>RDP를 다시 활성화해야 하는 경우</h3>
            <p>비상 상황이나 업무상 필요에 의해 원격 데스크톱을 다시 활성화해야 하는 경우:</p>

            <h4>레지스트리를 통한 복구</h4>
            <div class="recovery-code">
              <pre><code># PowerShell을 관리자 권한으로 실행
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server" -Name "fDenyTSConnections" -Value 0

# 방화벽 규칙 활성화
Enable-NetFirewallRule -DisplayGroup "원격 데스크톱"

# 서비스 시작
Set-Service -Name "TermService" -StartupType Automatic
Start-Service -Name "TermService"</code></pre>
            </div>

            <div class="warning-box">
              <h4>⚠️ 보안 경고</h4>
              <p>RDP를 다시 활성화하는 경우 반드시 다음 보안 조치를 함께 적용하세요:</p>
              <ul>
                <li>강력한 패스워드 정책 적용</li>
                <li>특정 IP 주소만 허용하는 방화벽 규칙 설정</li>
                <li>2단계 인증 활성화 (가능한 경우)</li>
                <li>접속 로그 모니터링 강화</li>
              </ul>
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

// 원격 데스크톱 비활성화 스크립트
const remoteDesktopDisableScript = `# 원격 데스크톱 비활성화 스크립트
# 시스템의 원격 데스크톱을 안전하게 비활성화합니다.

Write-Host "=== 원격 데스크톱 비활성화 스크립트 ===" -ForegroundColor Cyan
Write-Host "시스템 보안을 위해 원격 데스크톱을 비활성화합니다." -ForegroundColor Yellow
Write-Host ""

# 관리자 권한 확인
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "이 스크립트는 관리자 권한이 필요합니다." -ForegroundColor Red
    Write-Host "PowerShell을 관리자 권한으로 실행해주세요." -ForegroundColor Red
    Read-Host "아무 키나 누르면 종료됩니다"
    exit 1
}

try {
    Write-Host "1. 현재 원격 데스크톱 상태 확인" -ForegroundColor Yellow

    # 현재 RDP 설정 확인
    $rdpSetting = Get-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" -Name "fDenyTSConnections" -ErrorAction SilentlyContinue
    $currentStatus = if ($rdpSetting.fDenyTSConnections -eq 0) { "활성화" } else { "비활성화" }
    Write-Host "현재 원격 데스크톱 상태: $currentStatus" -ForegroundColor $(if($currentStatus -eq "활성화") {'Red'} else {'Green'})

    # 현재 연결된 사용자 확인
    Write-Host ""
    Write-Host "현재 원격 연결 확인 중..." -ForegroundColor Yellow
    try {
        $sessions = qwinsta | Where-Object { $_ -match "rdp" -and $_ -match "Active" }
        if ($sessions) {
            Write-Host "⚠️ 경고: 현재 활성화된 RDP 세션이 있습니다!" -ForegroundColor Red
            $sessions | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
            Write-Host ""
            $confirmation = Read-Host "활성화된 세션이 있어도 계속 진행하시겠습니까? (Y/N)"
            if ($confirmation -ne "Y" -and $confirmation -ne "y") {
                Write-Host "작업이 취소되었습니다." -ForegroundColor Yellow
                Read-Host "아무 키나 누르면 종료됩니다"
                exit 0
            }
        } else {
            Write-Host "✓ 현재 활성화된 RDP 세션이 없습니다." -ForegroundColor Green
        }
    } catch {
        Write-Host "RDP 세션 확인 중 오류 발생: $($_.Exception.Message)" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "2. 원격 데스크톱 비활성화 진행" -ForegroundColor Yellow

    # 레지스트리 설정 변경
    Write-Host "레지스트리 설정 변경 중..." -ForegroundColor White
    Set-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" -Name "fDenyTSConnections" -Value 1
    Write-Host "✓ 레지스트리 설정 완료" -ForegroundColor Green

    # Terminal Services 서비스 중지 및 비활성화
    Write-Host "Terminal Services 서비스 설정 중..." -ForegroundColor White
    try {
        $service = Get-Service -Name "TermService" -ErrorAction SilentlyContinue
        if ($service) {
            if ($service.Status -eq "Running") {
                Stop-Service -Name "TermService" -Force
                Write-Host "✓ Terminal Services 서비스 중지 완료" -ForegroundColor Green
            }
            Set-Service -Name "TermService" -StartupType Disabled
            Write-Host "✓ Terminal Services 서비스 비활성화 완료" -ForegroundColor Green
        } else {
            Write-Host "Terminal Services 서비스를 찾을 수 없습니다." -ForegroundColor Yellow
        }
    } catch {
        Write-Host "서비스 설정 중 오류: $($_.Exception.Message)" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "3. 방화벽 규칙 비활성화" -ForegroundColor Yellow

    # 방화벽 규칙 비활성화
    try {
        $firewallRules = Get-NetFirewallRule -DisplayGroup "원격 데스크톱" -ErrorAction SilentlyContinue
        if ($firewallRules) {
            foreach ($rule in $firewallRules) {
                if ($rule.Enabled -eq "True") {
                    Disable-NetFirewallRule -DisplayName $rule.DisplayName
                    Write-Host "✓ 방화벽 규칙 비활성화: $($rule.DisplayName)" -ForegroundColor Green
                }
            }
        } else {
            Write-Host "원격 데스크톱 방화벽 규칙을 찾을 수 없습니다." -ForegroundColor Yellow
        }

        # 영어 시스템용 규칙도 확인
        $englishRules = Get-NetFirewallRule -DisplayGroup "Remote Desktop" -ErrorAction SilentlyContinue
        if ($englishRules) {
            foreach ($rule in $englishRules) {
                if ($rule.Enabled -eq "True") {
                    Disable-NetFirewallRule -DisplayName $rule.DisplayName
                    Write-Host "✓ 방화벽 규칙 비활성화: $($rule.DisplayName)" -ForegroundColor Green
                }
            }
        }
    } catch {
        Write-Host "방화벽 설정 중 오류: $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host "수동으로 방화벽 설정을 확인해주세요." -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "4. 추가 보안 설정" -ForegroundColor Yellow

    # NLA (Network Level Authentication) 강화 (재활성화 시를 대비)
    try {
        Set-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server\\WinStations\\RDP-Tcp" -Name "UserAuthentication" -Value 1
        Write-Host "✓ 네트워크 수준 인증 강화 설정 완료" -ForegroundColor Green
    } catch {
        Write-Host "NLA 설정 중 오류: $($_.Exception.Message)" -ForegroundColor Yellow
    }

    # 기본 포트 변경 설정 (재활성화 시를 대비)
    try {
        $currentPort = Get-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server\\Wds\\rdpwd\\Tds\\tcp" -Name "PortNumber" -ErrorAction SilentlyContinue
        if ($currentPort -and $currentPort.PortNumber -eq 3389) {
            Write-Host "권장: 재활성화 시 기본 포트(3389) 변경을 고려하세요." -ForegroundColor Yellow
        }
    } catch {
        Write-Host "포트 설정 확인 중 오류: $($_.Exception.Message)" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "5. 설정 완료 확인" -ForegroundColor Yellow

    # 최종 상태 확인
    $finalStatus = Get-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" -Name "fDenyTSConnections"
    $statusText = if ($finalStatus.fDenyTSConnections -eq 1) { "비활성화됨" } else { "활성화됨" }
    Write-Host "원격 데스크톱 상태: $statusText" -ForegroundColor $(if($statusText -eq "비활성화됨") {'Green'} else {'Red'})

    $serviceStatus = Get-Service -Name "TermService" -ErrorAction SilentlyContinue
    if ($serviceStatus) {
        Write-Host "Terminal Services 서비스: $($serviceStatus.Status) / $($serviceStatus.StartType)" -ForegroundColor $(if($serviceStatus.Status -eq "Stopped") {'Green'} else {'Yellow'})
    }

    # 포트 3389 사용 확인
    $portCheck = netstat -an | Select-String ":3389"
    if (-not $portCheck) {
        Write-Host "✓ 포트 3389가 사용되지 않습니다." -ForegroundColor Green
    } else {
        Write-Host "⚠️ 포트 3389가 여전히 사용 중입니다." -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "=== 비활성화 완료 ===" -ForegroundColor Cyan
    Write-Host "원격 데스크톱이 성공적으로 비활성화되었습니다." -ForegroundColor Green
    Write-Host ""
    Write-Host "중요 안내사항:" -ForegroundColor Yellow
    Write-Host "- 시스템 재부팅을 권장합니다" -ForegroundColor White
    Write-Host "- 설정이 완전히 적용되려면 재부팅이 필요할 수 있습니다" -ForegroundColor White
    Write-Host "- 원격 접속이 필요한 경우 VPN 등 대안 방법을 사용하세요" -ForegroundColor White

    $reboot = Read-Host "지금 시스템을 재부팅하시겠습니까? (Y/N)"
    if ($reboot -eq "Y" -or $reboot -eq "y") {
        Write-Host "5초 후 시스템이 재부팅됩니다..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
        Restart-Computer -Force
    }

} catch {
    Write-Host "원격 데스크톱 비활성화 중 오류가 발생했습니다: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "수동으로 설정을 확인해주세요." -ForegroundColor Yellow
}

Read-Host "아무 키나 누르면 종료됩니다"`

// 원격 데스크톱 상태 확인 스크립트
const remoteDesktopCheckScript = `# 원격 데스크톱 상태 확인 스크립트
# 현재 시스템의 원격 데스크톱 설정과 보안 상태를 확인합니다.

Write-Host "=== 원격 데스크톱 보안 점검 스크립트 ===" -ForegroundColor Cyan
Write-Host "시스템의 RDP 설정과 보안 위험을 분석합니다." -ForegroundColor Yellow
Write-Host ""

try {
    Write-Host "1. 기본 RDP 설정 확인" -ForegroundColor Yellow
    Write-Host "=" * 50 -ForegroundColor Gray

    # RDP 활성화 상태 확인
    $rdpSetting = Get-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" -Name "fDenyTSConnections" -ErrorAction SilentlyContinue
    if ($rdpSetting) {
        $isEnabled = $rdpSetting.fDenyTSConnections -eq 0
        Write-Host "원격 데스크톱 상태: $($isEnabled ? '활성화됨' : '비활성화됨')" -ForegroundColor $(if($isEnabled) {'Red'} else {'Green'})

        if ($isEnabled) {
            Write-Host "⚠️ 보안 위험: 원격 데스크톱이 활성화되어 있습니다!" -ForegroundColor Red
        } else {
            Write-Host "✓ 보안 양호: 원격 데스크톱이 비활성화되어 있습니다." -ForegroundColor Green
        }
    } else {
        Write-Host "RDP 설정을 확인할 수 없습니다." -ForegroundColor Yellow
    }

    # RDP 포트 확인
    try {
        $rdpPort = Get-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server\\Wds\\rdpwd\\Tds\\tcp" -Name "PortNumber" -ErrorAction SilentlyContinue
        if ($rdpPort) {
            $port = $rdpPort.PortNumber
            Write-Host "RDP 포트: $port" -ForegroundColor $(if($port -eq 3389) {'Yellow'} else {'Green'})
            if ($port -eq 3389) {
                Write-Host "권장: 기본 포트(3389) 사용으로 인한 보안 위험" -ForegroundColor Yellow
            }
        }
    } catch {
        Write-Host "RDP 포트 확인 실패" -ForegroundColor Red
    }

    # NLA (Network Level Authentication) 확인
    try {
        $nla = Get-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server\\WinStations\\RDP-Tcp" -Name "UserAuthentication" -ErrorAction SilentlyContinue
        if ($nla) {
            $nlaEnabled = $nla.UserAuthentication -eq 1
            Write-Host "네트워크 수준 인증(NLA): $($nlaEnabled ? '활성화됨' : '비활성화됨')" -ForegroundColor $(if($nlaEnabled) {'Green'} else {'Red'})
            if (-not $nlaEnabled) {
                Write-Host "⚠️ 보안 위험: NLA가 비활성화되어 있습니다!" -ForegroundColor Red
            }
        }
    } catch {
        Write-Host "NLA 설정 확인 실패" -ForegroundColor Red
    }

    Write-Host ""
    Write-Host "2. 서비스 상태 확인" -ForegroundColor Yellow
    Write-Host "=" * 50 -ForegroundColor Gray

    # Terminal Services 상태 확인
    $termService = Get-Service -Name "TermService" -ErrorAction SilentlyContinue
    if ($termService) {
        Write-Host "Terminal Services 서비스:" -ForegroundColor White
        Write-Host "  상태: $($termService.Status)" -ForegroundColor $(if($termService.Status -eq "Running") {'Red'} else {'Green'})
        Write-Host "  시작 유형: $($termService.StartType)" -ForegroundColor $(if($termService.StartType -eq "Automatic") {'Red'} else {'Green'})

        if ($termService.Status -eq "Running") {
            Write-Host "⚠️ 보안 위험: Terminal Services가 실행 중입니다!" -ForegroundColor Red
        }
    } else {
        Write-Host "Terminal Services 서비스를 찾을 수 없습니다." -ForegroundColor Yellow
    }

    # Remote Desktop Configuration 서비스 확인
    $rdcService = Get-Service -Name "SessionEnv" -ErrorAction SilentlyContinue
    if ($rdcService) {
        Write-Host "Remote Desktop Configuration 서비스:" -ForegroundColor White
        Write-Host "  상태: $($rdcService.Status)" -ForegroundColor $(if($rdcService.Status -eq "Running") {'Yellow'} else {'Green'})
        Write-Host "  시작 유형: $($rdcService.StartType)" -ForegroundColor White
    }

    Write-Host ""
    Write-Host "3. 방화벽 규칙 확인" -ForegroundColor Yellow
    Write-Host "=" * 50 -ForegroundColor Gray

    # 방화벽 규칙 확인
    $rdpRules = Get-NetFirewallRule -DisplayGroup "원격 데스크톱" -ErrorAction SilentlyContinue
    if (-not $rdpRules) {
        $rdpRules = Get-NetFirewallRule -DisplayGroup "Remote Desktop" -ErrorAction SilentlyContinue
    }

    if ($rdpRules) {
        Write-Host "원격 데스크톱 방화벽 규칙:" -ForegroundColor White
        foreach ($rule in $rdpRules) {
            $color = if ($rule.Enabled -eq "True") { "Red" } else { "Green" }
            Write-Host "  - $($rule.DisplayName): $($rule.Enabled)" -ForegroundColor $color
            if ($rule.Enabled -eq "True") {
                Write-Host "    ⚠️ 위험: 이 규칙이 활성화되어 있습니다!" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "원격 데스크톱 방화벽 규칙을 찾을 수 없습니다." -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "4. 현재 연결 상태 확인" -ForegroundColor Yellow
    Write-Host "=" * 50 -ForegroundColor Gray

    # 현재 RDP 세션 확인
    try {
        $sessions = qwinsta
        $rdpSessions = $sessions | Where-Object { $_ -match "rdp" }

        if ($rdpSessions) {
            Write-Host "현재 RDP 세션:" -ForegroundColor White
            foreach ($session in $rdpSessions) {
                $isActive = $session -match "Active"
                Write-Host "  $session" -ForegroundColor $(if($isActive) {'Red'} else {'Gray'})
                if ($isActive) {
                    Write-Host "    ⚠️ 활성 세션이 발견되었습니다!" -ForegroundColor Red
                }
            }
        } else {
            Write-Host "✓ 현재 활성화된 RDP 세션이 없습니다." -ForegroundColor Green
        }
    } catch {
        Write-Host "세션 정보 확인 실패: $($_.Exception.Message)" -ForegroundColor Yellow
    }

    # 포트 3389 사용 확인
    $portUsage = netstat -an | Select-String ":3389"
    if ($portUsage) {
        Write-Host "포트 3389 사용 상태:" -ForegroundColor Red
        $portUsage | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
        Write-Host "⚠️ 포트 3389가 사용 중입니다!" -ForegroundColor Red
    } else {
        Write-Host "✓ 포트 3389가 사용되지 않습니다." -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "5. 보안 이벤트 로그 확인" -ForegroundColor Yellow
    Write-Host "=" * 50 -ForegroundColor Gray

    # 최근 RDP 로그인 시도 확인
    try {
        $startTime = (Get-Date).AddDays(-7)
        $rdpEvents = Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4624,4625; StartTime=$startTime} -MaxEvents 10 -ErrorAction SilentlyContinue |
                     Where-Object { $_.Message -match "터미널 서비스|Terminal Services|Remote Desktop" }

        if ($rdpEvents) {
            Write-Host "최근 7일간 RDP 관련 이벤트 ($($rdpEvents.Count)개):" -ForegroundColor White
            $rdpEvents | ForEach-Object {
                $eventType = if ($_.Id -eq 4624) { "성공적인 로그인" } else { "실패한 로그인" }
                $color = if ($_.Id -eq 4624) { "Yellow" } else { "Red" }
                Write-Host "  [$($_.TimeCreated)] $eventType" -ForegroundColor $color
            }
            Write-Host "⚠️ RDP 접속 시도가 감지되었습니다!" -ForegroundColor Red
        } else {
            Write-Host "✓ 최근 RDP 관련 이벤트가 없습니다." -ForegroundColor Green
        }
    } catch {
        Write-Host "이벤트 로그 확인 실패: $($_.Exception.Message)" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "6. 보안 위험 평가" -ForegroundColor Yellow
    Write-Host "=" * 50 -ForegroundColor Gray

    $riskScore = 0
    $risks = @()

    # 위험 점수 계산
    if ($rdpSetting -and $rdpSetting.fDenyTSConnections -eq 0) {
        $riskScore += 40
        $risks += "원격 데스크톱이 활성화되어 있음"
    }

    if ($termService -and $termService.Status -eq "Running") {
        $riskScore += 30
        $risks += "Terminal Services가 실행 중"
    }

    if ($rdpRules -and ($rdpRules | Where-Object { $_.Enabled -eq "True" })) {
        $riskScore += 20
        $risks += "방화벽에서 RDP 규칙이 활성화되어 있음"
    }

    if ($rdpPort -and $rdpPort.PortNumber -eq 3389) {
        $riskScore += 10
        $risks += "기본 포트(3389) 사용"
    }

    if ($portUsage) {
        $riskScore += 15
        $risks += "포트 3389가 사용 중"
    }

    if ($rdpEvents) {
        $riskScore += 10
        $risks += "최근 RDP 접속 시도 감지"
    }

    # 위험 등급 결정
    $riskLevel = if ($riskScore -ge 70) { "높음" }
                 elseif ($riskScore -ge 40) { "중간" }
                 elseif ($riskScore -ge 10) { "낮음" }
                 else { "없음" }

    $riskColor = switch ($riskLevel) {
        "높음" { "Red" }
        "중간" { "Yellow" }
        "낮음" { "Cyan" }
        default { "Green" }
    }

    Write-Host "전체 보안 위험도: $riskLevel (점수: $riskScore/100)" -ForegroundColor $riskColor

    if ($risks.Count -gt 0) {
        Write-Host ""
        Write-Host "발견된 위험 요소:" -ForegroundColor Red
        $risks | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
    }

    Write-Host ""
    Write-Host "=== 권장사항 ===" -ForegroundColor Cyan

    if ($riskScore -gt 0) {
        Write-Host "✓ 원격 데스크톱을 완전히 비활성화하세요" -ForegroundColor Green
        Write-Host "✓ Terminal Services 서비스를 중지하고 비활성화하세요" -ForegroundColor Green
        Write-Host "✓ 방화벽에서 RDP 관련 규칙을 비활성화하세요" -ForegroundColor Green
        Write-Host "✓ 대안적인 원격 접속 방법(VPN, SSH 터널링)을 고려하세요" -ForegroundColor Green
        Write-Host "✓ 정기적으로 보안 이벤트 로그를 모니터링하세요" -ForegroundColor Green
    } else {
        Write-Host "✓ 현재 시스템의 RDP 보안 상태가 양호합니다" -ForegroundColor Green
        Write-Host "✓ 정기적인 보안 점검을 계속 수행하세요" -ForegroundColor Green
    }

} catch {
    Write-Host "RDP 보안 점검 중 오류가 발생했습니다: $($_.Exception.Message)" -ForegroundColor Red
}

Read-Host "아무 키나 누르면 종료됩니다"`

// 메서드
const copyToClipboard = async () => {
  const codeText = `# 원격 데스크톱 설정 상태 확인
Get-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" -Name "fDenyTSConnections"

# 원격 데스크톱 서비스 상태 확인
Get-Service -Name "TermService" | Select-Object Name, Status, StartType

# 방화벽 규칙 확인
Get-NetFirewallRule -DisplayGroup "원격 데스크톱" | Select-Object DisplayName, Enabled, Direction

# 현재 RDP 연결 확인
qwinsta

# 네트워크 포트 3389 사용 확인
netstat -an | findstr :3389`

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

// 원격 데스크톱 비활성화 스크립트 다운로드
const downloadDisableScript = () => {
  downloadScript(remoteDesktopDisableScript, 'RemoteDesktop_Disable.ps1')
}

// 원격 데스크톱 상태 확인 스크립트 다운로드
const downloadCheckScript = () => {
  downloadScript(remoteDesktopCheckScript, 'RemoteDesktop_Check.ps1')
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

.section h4 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--dark-blue);
  margin: 16px 0 8px 0;
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

.risk-card.critical {
  border-left-color: #dc2626;
  background: linear-gradient(135deg, #fef2f2, #ffffff);
}

.risk-card.high {
  border-left-color: #ef4444;
  background: linear-gradient(135deg, #fef2f2, #ffffff);
}

.risk-card.medium {
  border-left-color: #f59e0b;
  background: linear-gradient(135deg, #fefbf2, #ffffff);
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

.risk-card.critical .risk-icon {
  background: linear-gradient(135deg, #dc2626, #b91c1c);
}

.risk-card.high .risk-icon {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.risk-card.medium .risk-icon {
  background: linear-gradient(135deg, #f59e0b, #d97706);
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

/* 보안 설정 단계 */
.security-levels {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
  margin: 20px 0;
}

.level-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
  transition: all 0.3s ease;
}

.level-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.level-card.recommended {
  border-left: 4px solid #10b981;
  background: linear-gradient(135deg, #ecfdf5, #ffffff);
}

.level-card.conditional {
  border-left: 4px solid #f59e0b;
  background: linear-gradient(135deg, #fefbf2, #ffffff);
}

.level-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.level-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.level-card.recommended .level-icon {
  background: linear-gradient(135deg, #10b981, #059669);
}

.level-card.conditional .level-icon {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.level-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--dark-blue);
  margin: 0;
  flex: 1;
}

.level-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.level-badge.safe {
  background: #dcfce7;
  color: #166534;
}

.level-badge.warning {
  background: #fef3c7;
  color: #92400e;
}

.level-card p {
  color: #6b7280;
  line-height: 1.5;
  margin-bottom: 16px;
}

.level-card ul {
  margin: 0;
  padding-left: 20px;
}

.level-card li {
  color: #374151;
  line-height: 1.5;
  margin-bottom: 4px;
}

/* 방화벽 규칙 테이블 */
.firewall-rules-table {
  margin: 20px 0;
  overflow-x: auto;
}

.firewall-rules-table table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.firewall-rules-table th {
  background: var(--primary-color);
  color: white;
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
}

.firewall-rules-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
}

.firewall-rules-table tr:last-child td {
  border-bottom: none;
}

.firewall-rules-table tr:nth-child(even) {
  background: #f9fafb;
}

.action-disable {
  background: #fee2e2;
  color: #991b1b;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.875rem;
}

/* 대안 솔루션 그리드 */
.alternatives-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.alternative-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  transition: all 0.3s ease;
}

.alternative-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.alternative-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  color: white;
}

.alternative-icon.vpn {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
}

.alternative-icon.ssh {
  background: linear-gradient(135deg, #10b981, #059669);
}

.alternative-icon.cloud {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
}

.alternative-card h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--dark-blue);
  margin: 0 0 8px 0;
}

.alternative-card p {
  color: #6b7280;
  font-size: 0.9rem;
  line-height: 1.5;
  margin-bottom: 12px;
}

.alternative-card ul {
  margin: 0;
  padding-left: 20px;
  text-align: left;
}

.alternative-card li {
  color: #374151;
  font-size: 0.875rem;
  line-height: 1.4;
  margin-bottom: 4px;
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

.script-icon.disable {
  background: linear-gradient(135deg, #ef4444, #dc2626);
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

.download-button.danger {
  background-color: #ef4444;
  color: white;
}

.download-button.danger:hover {
  background-color: #dc2626;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(239, 68, 68, 0.3);
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

/* 복구 정보 */
.recovery-info {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
}

.recovery-code {
  background: #1f2937;
  border-radius: 6px;
  padding: 16px;
  margin: 12px 0;
}

.recovery-code pre {
  color: #e5e7eb;
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
  line-height: 1.5;
  margin: 0;
}

.warning-box {
  background: #fef3c7;
  border: 1px solid #fcd34d;
  border-radius: 8px;
  padding: 16px;
  margin: 16px 0;
}

.warning-box h4 {
  color: #92400e;
  margin: 0 0 8px 0;
  font-size: 1rem;
  font-weight: 600;
}

.warning-box p {
  color: #92400e;
  margin: 0 0 8px 0;
  line-height: 1.5;
}

.warning-box ul {
  margin: 0;
  padding-left: 20px;
}

.warning-box li {
  color: #92400e;
  line-height: 1.4;
  margin-bottom: 4px;
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

.info-card.critical {
  background-color: #fef2f2;
  border-left-color: #ef4444;
}

.info-card.tip {
  background-color: #dbeafe;
  border-left-color: #3b82f6;
}

.info-icon {
  margin-bottom: 12px;
}

.info-card.critical .info-icon {
  color: #ef4444;
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

  .risk-grid,
  .security-levels,
  .alternatives-grid {
    grid-template-columns: 1fr;
  }

  .script-download-section {
    grid-template-columns: 1fr;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .firewall-rules-table {
    font-size: 0.875rem;
  }

  .firewall-rules-table th,
  .firewall-rules-table td {
    padding: 8px 12px;
  }
}

@media (max-width: 480px) {
  .firewall-rules-table th,
  .firewall-rules-table td {
    padding: 6px 8px;
    font-size: 0.8rem;
  }

  .risk-icon,
  .alternative-icon {
    width: 50px;
    height: 50px;
  }

  .level-icon {
    width: 35px;
    height: 35px;
  }

  .action-disable {
    font-size: 0.75rem;
    padding: 2px 6px;
  }
}
</style>
