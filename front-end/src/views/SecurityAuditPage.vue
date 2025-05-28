<!-- views/SecurityAuditPage.vue -->
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
          <p>상시보안감사 페이지에 접근하려면 로그인이 필요합니다.</p>
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
        <h1 class="page-title">상시보안감사</h1>

        <!-- 환영 메시지 -->
        <div class="section welcome-section">
          <div class="welcome-card">
            <div class="welcome-icon">
              <svg width="32" height="32" fill="currentColor" viewBox="0 0 16 16">
                <path
                  d="M5.338 1.59a61.44 61.44 0 0 0-2.837.856.481.481 0 0 0-.328.39c-.554 4.157.726 7.19 2.253 9.188a10.725 10.725 0 0 0 2.287 2.233c.346.244.652.42.893.533.12.057.218.095.293.118a.55.55 0 0 0 .101.025.615.615 0 0 0 .1-.025c.076-.023.174-.061.294-.118.24-.113.547-.29.893-.533a10.726 10.726 0 0 0 2.287-2.233c1.527-1.997 2.807-5.031 2.253-9.188a.48.48 0 0 0-.328-.39c-.651-.213-1.75-.56-2.837-.855C9.552 1.29 8.531 1.067 8 1.067c-.53 0-1.552.223-2.662.524zM5.072.56C6.157.265 7.31 0 8 0s1.843.265 2.928.56c1.11.3 2.229.655 2.887.87a1.54 1.54 0 0 1 1.044 1.262c.596 4.477-.787 7.795-2.465 9.99a11.775 11.775 0 0 1-2.517 2.453 7.159 7.159 0 0 1-1.048.625c-.28.132-.581.24-.829.24s-.548-.108-.829-.24a7.158 7.158 0 0 1-1.048-.625 11.777 11.777 0 0 1-2.517-2.453C1.928 10.487.545 7.169 1.141 2.692A1.54 1.54 0 0 1 2.185 1.43 62.456 62.456 0 0 1 5.072.56z"
                />
                <path
                  d="M9.5 6.5a1.5 1.5 0 0 1-1 1.415l.385 1.99a.5.5 0 0 1-.491.595h-.788a.5.5 0 0 1-.49-.595L7.5 7.915A1.5 1.5 0 1 1 9.5 6.5z"
                />
              </svg>
            </div>
            <div class="welcome-content">
              <h2>상시보안감사 시스템에 오신 것을 환영합니다</h2>
              <p>
                {{ authStore.user.name }}님, 조직의 보안 정책 준수를 위한 체계적인 감사 도구를
                활용하여 시스템의 보안 상태를 점검하고 개선하세요.
              </p>
            </div>
          </div>
        </div>

        <!-- 주요 기능 소개 -->
        <div class="section">
          <h2 class="section-title">주요 기능</h2>
          <div class="features-grid">
            <div class="feature-card">
              <div class="feature-icon results">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M1.5 1.5A.5.5 0 0 1 2 1h12a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-.128.334L10 8.692V13.5a.5.5 0 0 1-.342.474l-3 1A.5.5 0 0 1 6 14.5V8.692L1.628 3.834A.5.5 0 0 1 1.5 3.5v-2z"
                  />
                </svg>
              </div>
              <div class="feature-content">
                <h3>검사결과</h3>
                <p>실시간 보안 감사 결과와 통계를 확인하고 분석할 수 있습니다.</p>
                <RouterLink to="/security-audit/results" class="feature-link">
                  결과 보기
                  <svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                    <path
                      fill-rule="evenodd"
                      d="M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z"
                    />
                  </svg>
                </RouterLink>
              </div>
            </div>

            <div class="feature-card">
              <div class="feature-icon solutions">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M8 4.754a3.246 3.246 0 1 0 0 6.492 3.246 3.246 0 0 0 0-6.492zM5.754 8a2.246 2.246 0 1 1 4.492 0 2.246 2.246 0 0 1-4.492 0z"
                  />
                  <path
                    d="M9.796 1.343c-.527-1.79-3.065-1.79-3.592 0l-.094.319a.873.873 0 0 1-1.255.52l-.292-.16c-1.64-.892-3.433.902-2.54 2.541l.159.292a.873.873 0 0 1-.52 1.255l-.319.094c-1.79.527-1.79 3.065 0 3.592l.319.094a.873.873 0 0 1 .52 1.255l-.16.292c-.892 1.64.901 3.434 2.541 2.54l.292-.159a.873.873 0 0 1 1.255.52l.094.319c.527 1.79 3.065 1.79 3.592 0l.094-.319a.873.873 0 0 1 1.255-.52l.292.16c1.64.893 3.434-.902 2.54-2.541l-.159-.292a.873.873 0 0 1 .52-1.255l.319-.094c1.79-.527 1.79-3.065 0-3.592l-.319-.094a.873.873 0 0 1-.52-1.255l.16-.292c.893-1.64-.902-3.433-2.541-2.54l-.292.159a.873.873 0 0 1-1.255-.52l-.094-.319z"
                  />
                </svg>
              </div>
              <div class="feature-content">
                <h3>조치방법</h3>
                <p>보안 문제에 대한 상세한 해결 방법과 가이드를 제공합니다.</p>
                <RouterLink to="/security-audit/solutions" class="feature-link">
                  조치방법 보기
                  <svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                    <path
                      fill-rule="evenodd"
                      d="M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z"
                    />
                  </svg>
                </RouterLink>
              </div>
            </div>

            <!-- <div class="feature-card">
              <div class="feature-icon contact">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M3 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1H3zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"
                  />
                </svg>
              </div>
              <div class="feature-content">
                <h3>문의하기</h3>
                <p>보안 관련 문의사항이나 기술 지원이 필요한 경우 연락하세요.</p>
                <RouterLink to="/security-audit/contact" class="feature-link">
                  문의하기
                  <svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                    <path
                      fill-rule="evenodd"
                      d="M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z"
                    />
                  </svg>
                </RouterLink>
              </div>
            </div> -->
          </div>
        </div>

        <!-- 최근 감사 현황 -->
        <!-- <div class="section" v-if="recentStats">
          <h2 class="section-title">최근 감사 현황</h2>
          <div class="recent-stats">
            <div class="stats-summary">
              <div class="stat-item">
                <span class="stat-label">마지막 감사</span>
                <span class="stat-value">{{ formatDate(recentStats.lastAuditDate) }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">전체 항목</span>
                <span class="stat-value">{{ recentStats.totalChecks }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">통과율</span>
                <span class="stat-value success">
                  {{
                    recentStats.totalChecks > 0
                      ? Math.round((recentStats.completedChecks / recentStats.totalChecks) * 100)
                      : 0
                  }}%
                </span>
              </div>
              <div class="stat-item">
                <span class="stat-label">개선 필요</span>
                <span class="stat-value warning">{{ recentStats.criticalIssues }}</span>
              </div>
            </div>
            <div class="quick-action">
              <RouterLink to="/security-audit/results" class="quick-action-button">
                전체 결과 확인하기
              </RouterLink>
            </div>
          </div>
        </div> -->

        <!-- 안내 사항 -->
        <!-- <div class="section">
          <h2 class="section-title">안내 사항</h2>
          <div class="notice-cards">
            <div class="notice-card info">
              <div class="notice-icon">
                <svg width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
                  <path
                    d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"
                  />
                </svg>
              </div>
              <div class="notice-content">
                <h3>정기 감사 일정</h3>
                <p>매월 첫째 주에 정기 보안 감사가 실시됩니다. 사전에 시스템을 점검해 주세요.</p>
              </div>
            </div>

            <div class="notice-card warning">
              <div class="notice-icon">
                <svg width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"
                  />
                </svg>
              </div>
              <div class="notice-content">
                <h3>보안 정책 업데이트</h3>
                <p>새로운 보안 정책이 적용되었습니다. 조치방법 페이지에서 변경사항을 확인하세요.</p>
              </div>
            </div>
          </div>
        </div> -->
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Sidebar from '@/components/Sidebar.vue'

// Pinia Store
const authStore = useAuthStore()

// 반응형 데이터
const recentStats = ref(null)
const loading = ref(false)
// Sidebar ref
const sidebarRef = ref(null)

// 계산된 속성
const isAuthenticated = computed(() => !!authStore.user)

// 메서드
const fetchRecentStats = async () => {
  if (!authStore.user) return

  loading.value = true
  try {
    const response = await fetch('/api/security-audit/stats', {
      credentials: 'include',
    })

    if (response.ok) {
      const data = await response.json()
      recentStats.value = data
    }
  } catch (error) {
    console.error('최근 통계 데이터 로드 실패:', error)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '데이터 없음'

  const date = new Date(dateStr)
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

// 라이프사이클 훅
onMounted(() => {
  if (authStore.user) {
    fetchRecentStats()
  }
})
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

.welcome-section {
  margin-bottom: 32px;
}

.welcome-card {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, var(--primary-color), var(--dark-blue));
  color: white;
  padding: 32px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(64, 86, 183, 0.2);
}

.welcome-icon {
  margin-right: 24px;
  flex-shrink: 0;
}

.welcome-content h2 {
  margin: 0 0 12px 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.welcome-content p {
  margin: 0;
  font-size: 1rem;
  line-height: 1.6;
  opacity: 0.9;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
  margin-top: 20px;
}

.feature-card {
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.feature-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  transform: translateY(-4px);
}

.feature-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  color: white;
}

.feature-icon.results {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
}

.feature-icon.solutions {
  background: linear-gradient(135deg, #10b981, #059669);
}

.feature-icon.contact {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.feature-content h3 {
  margin: 0 0 12px 0;
  color: var(--dark-blue);
  font-size: 1.25rem;
  font-weight: 600;
}

.feature-content p {
  margin: 0 0 16px 0;
  color: #6b7280;
  line-height: 1.5;
}

.feature-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.875rem;
}

.feature-link:hover {
  text-decoration: underline;
}

.recent-stats {
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
  margin-top: 20px;
}

.stats-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 4px;
}

.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--dark-blue);
}

.stat-value.success {
  color: #10b981;
}

.stat-value.warning {
  color: #f59e0b;
}

.quick-action {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.quick-action-button {
  display: inline-flex;
  align-items: center;
  background-color: var(--primary-color);
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
}

.quick-action-button:hover {
  background-color: var(--dark-blue);
}

.notice-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.notice-card {
  display: flex;
  align-items: flex-start;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid;
}

.notice-card.info {
  background-color: #eff6ff;
  border-left-color: #3b82f6;
}

.notice-card.warning {
  background-color: #fffbeb;
  border-left-color: #f59e0b;
}

.notice-icon {
  margin-right: 16px;
  flex-shrink: 0;
}

.notice-card.info .notice-icon {
  color: #3b82f6;
}

.notice-card.warning .notice-icon {
  color: #f59e0b;
}

.notice-content h3 {
  margin: 0 0 8px 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--dark-blue);
}

.notice-content p {
  margin: 0;
  font-size: 0.875rem;
  color: #6b7280;
  line-height: 1.5;
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
  .main-content {
    padding: 20px;
    margin: 10px;
  }

  .welcome-card {
    flex-direction: column;
    text-align: center;
    padding: 24px;
  }

  .welcome-icon {
    margin-right: 0;
    margin-bottom: 16px;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .stats-summary {
    grid-template-columns: repeat(2, 1fr);
  }

  .notice-cards {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .stats-summary {
    grid-template-columns: 1fr;
  }
}

/* 기존 스타일은 그대로 두고 추가 */

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

@media (min-width: 769px) {
  .mobile-menu-toggle {
    display: none;
  }
}
</style>
