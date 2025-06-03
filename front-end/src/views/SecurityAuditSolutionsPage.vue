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
          <p>보안 감사 조치방법을 확인하려면 로그인이 필요합니다.</p>
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
        <h1 class="page-title">보안 감사 조치방법</h1>

        <!-- 조치방법 개요 -->
        <div class="section">
          <h2 class="section-title">조치방법 개요</h2>
          <div class="overview-card">
            <!-- <div class="overview-icon">
              <svg width="32" height="32" fill="currentColor" viewBox="0 0 16 16">
                <path
                  d="M8 4.754a3.246 3.246 0 1 0 0 6.492 3.246 3.246 0 0 0 0-6.492zM5.754 8a2.246 2.246 0 1 1 4.492 0 2.246 2.246 0 0 1-4.492 0z"
                />
                <path
                  d="M9.796 1.343c-.527-1.79-3.065-1.79-3.592 0l-.094.319a.873.873 0 0 1-1.255.52l-.292-.16c-1.64-.892-3.433.902-2.54 2.541l.159.292a.873.873 0 0 1-.52 1.255l-.319.094c-1.79.527-1.79 3.065 0 3.592l.319.094a.873.873 0 0 1 .52 1.255l-.16.292c-.892 1.64.901 3.434 2.541 2.54l.292-.159a.873.873 0 0 1 1.255.52l.094.319c.527 1.79 3.065 1.79 3.592 0l.094-.319a.873.873 0 0 1 1.255-.52l.292.16c1.64.893 3.434-.902 2.54-2.541l-.159-.292a.873.873 0 0 1 .52-1.255l.319-.094c1.79-.527 1.79-3.065 0-3.592l-.319-.094a.873.873 0 0 1-.52-1.255l.16-.292c.893-1.64-.902-3.433-2.541-2.54l-.292.159a.873.873 0 0 1-1.255-.52l-.094-.319z"
                />
              </svg>
            </div> -->
            <div class="overview-content">
              <p>
                이 페이지에서는 정보보안 감사에서 확인해야 할 주요 항목에 대한 조치방법을
                안내합니다. 모든 가이드는 조직의 보안 정책을 준수하기 위한 기본적인 설정 방법과 점검
                사항을 제공합니다.
              </p>
            </div>
          </div>
        </div>

        <!-- 항목별 상세 가이드 -->
        <div class="section">
          <h2 class="section-title">항목별 상세 가이드</h2>
          <div class="solutions-grid">
            <RouterLink
              v-for="(item, index) in solutionItems"
              :key="index"
              :to="item.path"
              class="solution-card-link"
            >
              <div class="solution-card">
                <!-- <div class="solution-icon" :class="getIconClass(item.id)">
                  <component :is="getIconComponent(item.id)" />
                </div> -->
                <div class="solution-content">
                  <h3 class="solution-title">{{ item.title }}</h3>
                  <p class="solution-description">{{ item.description }}</p>
                  <div class="solution-meta">
                    <span class="solution-category">{{ item.category }}</span>
                    <!-- <span class="solution-difficulty" :class="getDifficultyClass(item.difficulty)">
                      {{ item.difficulty }}
                    </span> -->
                  </div>
                </div>
                <div class="solution-arrow">
                  <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path
                      fill-rule="evenodd"
                      d="M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z"
                    />
                  </svg>
                </div>
              </div>
            </RouterLink>
          </div>
        </div>

        <!-- 추가 도움말 섹션 -->
        <!-- <div class="section">
          <h2 class="section-title">추가 도움말</h2>
          <div class="help-grid">
            <div class="help-card info">
              <div class="help-icon">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
                  <path
                    d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"
                  />
                </svg>
              </div>
              <div class="help-content">
                <h3>일반적인 문제 해결</h3>
                <p>자주 발생하는 보안 설정 문제와 해결 방법을 안내합니다.</p>
                <ul>
                  <li>설정 적용 후 시스템 재시작이 필요한 경우</li>
                  <li>관리자 권한이 필요한 설정 변경</li>
                  <li>그룹 정책으로 인한 설정 제한</li>
                </ul>
              </div>
            </div>

            <div class="help-card contact">
              <div class="help-icon">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M3 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1H3zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"
                  />
                </svg>
              </div>
              <div class="help-content">
                <h3>관리자 문의</h3>
                <p>추가적인 도움이 필요한 경우 IT 보안팀에 문의하세요.</p>
                <div class="contact-details">
                  <div class="contact-item">
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                      <path
                        d="M3.654 1.328a.678.678 0 0 0-1.015-.063L1.605 2.3c-.483.484-.661 1.169-.45 1.77a17.568 17.568 0 0 0 4.168 6.608 17.569 17.569 0 0 0 6.608 4.168c.601.211 1.286.033 1.77-.45l1.034-1.034a.678.678 0 0 0-.063-1.015l-2.307-1.794a.678.678 0 0 0-.58-.122L9.98 10.4a.678.678 0 0 1-.615-.04L7.6 9.39a.678.678 0 0 1-.215-.176L6.417 8.246a.678.678 0 0 1-.176-.215L5.27 6.266a.678.678 0 0 1-.04-.615l.969-1.805a.678.678 0 0 0-.122-.58L3.654 1.328z"
                      />
                    </svg>
                    <span>내선 5678</span>
                  </div>
                  <div class="contact-item">
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                      <path
                        d="M2 2a2 2 0 0 0-2 2v8.01A2 2 0 0 0 2 14h5.5a.5.5 0 0 0 0-1H2a1 1 0 0 1-.966-.741l5.64-3.471L8 9.583l7-4.2V8.5a.5.5 0 0 0 1 0V4a2 2 0 0 0-2-2H2Zm3.708 6.208L1 11.105V5.383l4.708 2.825ZM1 4.217V4a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v.217l-7 4.2-7-4.2Z"
                      />
                    </svg>
                    <span>security@example.com</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="help-card policy">
              <div class="help-icon">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M14 1a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H4.414A2 2 0 0 0 3 11.586l-2 2V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v12.793a.5.5 0 0 0 .854.353l2.853-2.853A1 1 0 0 1 4.414 12H14a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z"
                  />
                  <path
                    d="M3 3.5a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9a.5.5 0 0 1-.5-.5zM3 6a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9A.5.5 0 0 1 3 6zm0 2.5a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5z"
                  />
                </svg>
              </div>
              <div class="help-content">
                <h3>정책 문서</h3>
                <p>회사의 보안 정책 및 가이드라인을 확인하세요.</p>
                <ul>
                  <li>정보보안 정책 문서</li>
                  <li>IT 자산 관리 가이드라인</li>
                  <li>보안 사고 대응 절차</li>
                </ul>
              </div>
            </div>
          </div>
        </div> -->

        <!-- 보안 정책 요약 -->
        <!-- <div class="section">
          <h2 class="section-title">보안 정책 요약</h2>
          <div class="policy-summary">
            <div class="policy-item">
              <div class="policy-icon critical">
                <svg width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"
                  />
                </svg>
              </div>
              <div class="policy-content">
                <h4>필수 준수 사항</h4>
                <p>
                  모든 직원은 보안 정책을 반드시 준수해야 하며, 위반 시 징계 조치가 있을 수
                  있습니다.
                </p>
              </div>
            </div>

            <div class="policy-item">
              <div class="policy-icon important">
                <svg width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
                  <path
                    d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"
                  />
                </svg>
              </div>
              <div class="policy-content">
                <h4>정기 감사</h4>
                <p>매월 첫째 주에 정기 보안 감사가 실시되며, 미준수 항목은 즉시 조치해야 합니다.</p>
              </div>
            </div>

            <div class="policy-item">
              <div class="policy-icon update">
                <svg width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M11.534 7h3.932a.25.25 0 0 1 .192.41l-1.966 2.36a.25.25 0 0 1-.384 0l-1.966-2.36a.25.25 0 0 1 .192-.41zm-11 2h3.932a.25.25 0 0 0 .192-.41L2.692 6.23a.25.25 0 0 0-.384 0L.342 8.59A.25.25 0 0 0 .534 9z"
                  />
                  <path
                    fill-rule="evenodd"
                    d="M8 3c-1.552 0-2.94.707-3.857 1.818a.5.5 0 1 1-.771-.636A6.002 6.002 0 0 1 13.917 7H12.9A5.002 5.002 0 0 0 8 3zM3.1 9a5.002 5.002 0 0 0 8.757 2.182.5.5 0 1 1 .771.636A6.002 6.002 0 0 1 2.083 9H3.1z"
                  />
                </svg>
              </div>
              <div class="policy-content">
                <h4>지속적 개선</h4>
                <p>보안 정책은 지속적으로 업데이트되며, 변경사항은 즉시 공지됩니다.</p>
              </div>
            </div>
          </div>
        </div> -->

        <!-- 페이지 네비게이션 -->
        <PageNavigation :current-path="route.path" />
      </div>
    </main>
  </div>
</template>
<script setup>
import { ref, computed } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Sidebar from '@/components/Sidebar.vue'
import PageNavigation from '@/components/PageNavigation.vue'
import '@/assets/styles/views/SecurityAuditSolutionsPage.css'

// Vue Router
const route = useRoute()

// Pinia Store
const authStore = useAuthStore()

// Sidebar ref
const sidebarRef = ref(null)

// 솔루션 항목 데이터
const solutionItems = [
  {
    id: 'screen-saver',
    title: '화면보호기 사용',
    path: '/security-audit/solutions/screen-saver',
    description: '화면보호기 10분 이내 설정 및 암호화 적용',
    category: '시스템 보안',
    difficulty: '쉬움',
  },

  {
    id: 'antivirus',
    title: '백신 상태 확인',
    path: '/security-audit/solutions/antivirus',
    description: '바이러스 백신 설치, 실시간 보호, 최신 업데이트 확인',
    category: '악성코드 방지',
    difficulty: '쉬움',
  },
  {
    id: 'password-policy',
    title: '패스워드 길이 및 복잡도',
    path: '/security-audit/solutions/password-policy',
    description: '8자 이상 강력한 패스워드 정책 적용 및 정기적 변경',
    category: '인증 보안',
    difficulty: '보통',
  },
  {
    id: 'shared-folder',
    title: '공유폴더 확인',
    path: '/security-audit/solutions/shared-folder',
    description: '불필요한 공유폴더 제거 및 접근 권한 관리',
    category: '접근 통제',
    difficulty: '어려움',
  },
  {
    id: 'remote-desktop',
    title: '원격데스크톱 제한',
    path: '/security-audit/solutions/remote-desktop',
    description: '원격 접속 비활성화 또는 승인된 사용자로 제한',
    category: '네트워크 보안',
    difficulty: '보통',
  },
]

// 계산된 속성
const isAuthenticated = computed(() => !!authStore.user)

// 메서드
const getIconComponent = (itemId) => {
  // SVG 아이콘을 직접 반환하는 함수형 컴포넌트들
  const icons = {
    'screen-saver': () => ({
      template: `
        <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
          <path d="M0 1.5A1.5 1.5 0 0 1 1.5 0h13A1.5 1.5 0 0 1 16 1.5v8A1.5 1.5 0 0 1 14.5 11H1.5A1.5 1.5 0 0 1 0 9.5v-8zM1.5 1a.5.5 0 0 0-.5.5v8a.5.5 0 0 0 .5.5h13a.5.5 0 0 0 .5-.5v-8a.5.5 0 0 0-.5-.5h-13z"/>
          <path d="M8 5.5a2 2 0 1 1-4 0 2 2 0 0 1 4 0zm-2.5-1.5a.5.5 0 1 0 0 1 .5.5 0 0 0 0-1zm7 .5a.5.5 0 0 0-1 0v3a.5.5 0 0 0 1 0v-3z"/>
        </svg>
      `,
    }),
    'auto-run': () => ({
      template: `
        <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
          <path d="M.5 9.9a.5.5 0 0 1 .5.5v1.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-1.5a.5.5 0 0 1 1 0v1.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-1.5a.5.5 0 0 1 .5-.5z"/>
          <path d="M7.646 1.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 2.707V11.5a.5.5 0 0 1-1 0V2.707L5.354 4.854a.5.5 0 1 1-.708-.708l3-3z"/>
        </svg>
      `,
    }),
    antivirus: () => ({
      template: `
        <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
          <path d="M5.338 1.59a61.44 61.44 0 0 0-2.837.856.481.481 0 0 0-.328.39c-.554 4.157.726 7.19 2.253 9.188a10.725 10.725 0 0 0 2.287 2.233c.346.244.652.42.893.533.12.057.218.095.293.118a.55.55 0 0 0 .101.025.615.615 0 0 0 .1-.025c.076-.023.174-.061.294-.118.24-.113.547-.29.893-.533a10.726 10.726 0 0 0 2.287-2.233c1.527-1.997 2.807-5.031 2.253-9.188a.48.48 0 0 0-.328-.39c-.651-.213-1.75-.56-2.837-.855C9.552 1.29 8.531 1.067 8 1.067c-.53 0-1.552.223-2.662.524zM5.072.56C6.157.265 7.31 0 8 0s1.843.265 2.928.56c1.11.3 2.229.655 2.887.87a1.54 1.54 0 0 1 1.044 1.262c.596 4.477-.787 7.795-2.465 9.99a11.775 11.775 0 0 1-2.517 2.453 7.159 7.159 0 0 1-1.048.625c-.28.132-.581.24-.829.24s-.548-.108-.829-.24a7.158 7.158 0 0 1-1.048-.625 11.777 11.777 0 0 1-2.517-2.453C1.928 10.487.545 7.169 1.141 2.692A1.54 1.54 0 0 1 2.185 1.43 62.456 62.456 0 0 1 5.072.56z"/>
          <path d="M10.854 5.146a.5.5 0 0 1 0 .708l-3 3a.5.5 0 0 1-.708 0l-1.5-1.5a.5.5 0 1 1 .708-.708L7.5 7.793l2.646-2.647a.5.5 0 0 1 .708 0z"/>
        </svg>
      `,
    }),
    'password-policy': () => ({
      template: `
        <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
          <path d="M8 1a2 2 0 0 1 2 2v4H6V3a2 2 0 0 1 2-2zm3 6V3a3 3 0 0 0-6 0v4a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2zM5 8h6a1 1 0 0 1 1 1v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1z"/>
        </svg>
      `,
    }),
    'shared-folder': () => ({
      template: `
        <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
          <path d="M1.5 1a.5.5 0 0 0-.5.5v3a.5.5 0 0 1-1 0v-3A1.5 1.5 0 0 1 1.5 0h3a.5.5 0 0 1 0 1h-3zM11 .5a.5.5 0 0 1 .5-.5h3A1.5 1.5 0 0 1 16 1.5v3a.5.5 0 0 1-1 0v-3a.5.5 0 0 0-.5-.5h-3a.5.5 0 0 1-.5-.5zM.5 11a.5.5 0 0 1 .5.5v3a.5.5 0 0 0 .5.5h3a.5.5 0 0 1 0 1h-3A1.5 1.5 0 0 1 0 14.5v-3a.5.5 0 0 1 .5-.5zm15 0a.5.5 0 0 1 .5.5v3a1.5 1.5 0 0 1-1.5 1.5h-3a.5.5 0 0 1 0-1h3a.5.5 0 0 0 .5-.5v-3a.5.5 0 0 1 .5-.5z"/>
          <path d="M3 4.5a.5.5 0 0 1 1 0v7a.5.5 0 0 1-1 0v-7zm2 0a.5.5 0 0 1 1 0v7a.5.5 0 0 1-1 0v-7zm2 0a.5.5 0 0 1 1 0v7a.5.5 0 0 1-1 0v-7zm2 0a.5.5 0 0 1 1 0v7a.5.5 0 0 1-1 0v-7zm4-1a.5.5 0 0 0-.5.5v7a.5.5 0 0 0 1 0v-7a.5.5 0 0 0-.5-.5z"/>
        </svg>
      `,
    }),
    'remote-desktop': () => ({
      template: `
        <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
          <path d="M0 4s0-2 2-2h12s2 0 2 2v6s0 2-2 2h-4c0 .667.083 1.167.25 1.5H11a.5.5 0 0 1 0 1H5a.5.5 0 0 1 0-1h.75c.167-.333.25-.833.25-1.5H2s-2 0-2-2V4zm1.398-.855a.758.758 0 0 0-.254.302A1.46 1.46 0 0 0 1 4.01V10c0 .325.078.502.145.602.07.105.17.188.302.254a1.464 1.464 0 0 0 .538.143L2.01 11H14c.325 0 .502-.078.602-.145a.758.758 0 0 0 .254-.302 1.464 1.464 0 0 0 .143-.538L15 9.99V4c0-.325-.078-.502-.145-.602a.757.757 0 0 0-.302-.254A1.46 1.46 0 0 0 13.99 3H2c-.325 0-.502.078-.602.145z"/>
        </svg>
      `,
    }),
    firewall: () => ({
      template: `
        <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
          <path d="M5.338 1.59a61.44 61.44 0 0 0-2.837.856.481.481 0 0 0-.328.39c-.554 4.157.726 7.19 2.253 9.188a10.725 10.725 0 0 0 2.287 2.233c.346.244.652.42.893.533.12.057.218.095.293.118a.55.55 0 0 0 .101.025.615.615 0 0 0 .1-.025c.076-.023.174-.061.294-.118.24-.113.547-.29.893-.533a10.726 10.726 0 0 0 2.287-2.233c1.527-1.997 2.807-5.031 2.253-9.188a.48.48 0 0 0-.328-.39c-.651-.213-1.75-.56-2.837-.855C9.552 1.29 8.531 1.067 8 1.067c-.53 0-1.552.223-2.662.524zM5.072.56C6.157.265 7.31 0 8 0s1.843.265 2.928.56c1.11.3 2.229.655 2.887.87a1.54 1.54 0 0 1 1.044 1.262c.596 4.477-.787 7.795-2.465 9.99a11.775 11.775 0 0 1-2.517 2.453 7.159 7.159 0 0 1-1.048.625c-.28.132-.581.24-.829.24s-.548-.108-.829-.24a7.158 7.158 0 0 1-1.048-.625 11.777 11.777 0 0 1-2.517-2.453C1.928 10.487.545 7.169 1.141 2.692A1.54 1.54 0 0 1 2.185 1.43 62.456 62.456 0 0 1 5.072.56z"/>
          <path d="M9.5 6.5a1.5 1.5 0 0 1-1 1.415l.385 1.99a.5.5 0 0 1-.491.595h-.788a.5.5 0 0 1-.49-.595L7.5 7.915A1.5 1.5 0 1 1 9.5 6.5z"/>
        </svg>
      `,
    }),
  }

  return (
    icons[itemId] ||
    (() => ({
      template: `
      <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
        <path d="M8 4.754a3.246 3.246 0 1 0 0 6.492 3.246 3.246 0 0 0 0-6.492zM5.754 8a2.246 2.246 0 1 1 4.492 0 2.246 2.246 0 0 1-4.492 0z"/>
        <path d="M9.796 1.343c-.527-1.79-3.065-1.79-3.592 0l-.094.319a.873.873 0 0 1-1.255.52l-.292-.16c-1.64-.892-3.433.902-2.54 2.541l.159.292a.873.873 0 0 1-.52 1.255l-.319.094c-1.79.527-1.79 3.065 0 3.592l.319.094a.873.873 0 0 1 .52 1.255l-.16.292c-.892 1.64.901 3.434 2.541 2.54l.292-.159a.873.873 0 0 1 1.255.52l.094.319c.527 1.79 3.065 1.79 3.592 0l.094-.319a.873.873 0 0 1 1.255-.52l.292.16c1.64.893 3.434-.902 2.54-2.541l-.159-.292a.873.873 0 0 1 .52-1.255l.319-.094c1.79-.527 1.79-3.065 0-3.592l-.319-.094a.873.873 0 0 1-.52-1.255l.16-.292c.893-1.64-.902-3.433-2.541-2.54l-.292.159a.873.873 0 0 1-1.255-.52l-.094-.319z"/>
      </svg>
    `,
    }))
  )
}

const getIconClass = (itemId) => {
  const iconClasses = {
    'screen-saver': 'screen-saver',
    'auto-run': 'auto-run',
    antivirus: 'antivirus',
    'password-policy': 'password-policy',
    'shared-folder': 'shared-folder',
    'remote-desktop': 'remote-desktop',
    firewall: 'firewall',
  }
  return iconClasses[itemId] || 'default'
}

const getDifficultyClass = (difficulty) => {
  switch (difficulty) {
    case '쉬움':
      return 'easy'
    case '보통':
      return 'medium'
    case '어려움':
      return 'hard'
    default:
      return 'medium'
  }
}
</script>
