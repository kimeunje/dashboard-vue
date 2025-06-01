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
        <div class="page-header">
          <h1 class="page-title">정보보안 감사 현황</h1>
        </div>
        <!-- 로딩 상태 -->
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>데이터를 불러오는 중...</p>
        </div>

        <!-- 점검 상태 대시보드 -->
        <div class="section" v-if="dashboardStats">
          <div class="dashboard-grid">
            <!-- 정기 점검 카드 -->
            <div class="dashboard-card daily-check">
              <div class="card-header">
                <div class="card-icon daily">
                  <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                    <path
                      d="M8 3.5a.5.5 0 0 0-1 0V9a.5.5 0 0 0 .252.434l3.5 2a.5.5 0 0 0 .496-.868L8 8.71V3.5z"
                    />
                    <path
                      d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm7-8A7 7 0 1 1 1 8a7 7 0 0 1 14 0z"
                    />
                  </svg>
                </div>
                <h3>정기 점검</h3>
                <span class="card-frequency">매일 자동 실행</span>
              </div>
              <div class="card-stats">
                <div class="stat-row">
                  <span class="stat-label">전체 항목</span>
                  <span class="stat-value">{{ dashboardStats.daily.totalChecks }}</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">통과 항목</span>
                  <span class="stat-value success">{{ dashboardStats.daily.completedChecks }}</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">실패 항목</span>
                  <span class="stat-value danger">{{ dashboardStats.daily.criticalIssues }}</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">최근 점검</span>
                  <span class="stat-value">{{
                    formatDate(dashboardStats.daily.lastAuditDate)
                  }}</span>
                </div>
              </div>
              <div class="card-progress">
                <div class="progress-bar">
                  <div
                    class="progress-fill daily"
                    :style="{ width: `${getDailyPassRate()}%` }"
                  ></div>
                </div>
                <span class="progress-text">통과율 {{ getDailyPassRate() }}%</span>
              </div>
            </div>

            <!-- 수시 점검 카드 -->
            <div class="dashboard-card manual-check">
              <div class="card-header">
                <div class="card-icon manual">
                  <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                    <path
                      d="M9.405 1.05c-.413-1.4-2.397-1.4-2.81 0l-.1.34a1.464 1.464 0 0 1-2.105.872l-.31-.17c-1.283-.698-2.686.705-1.987 1.987l.169.311c.446.82.023 1.841-.872 2.105l-.34.1c-1.4.413-1.4 2.397 0 2.81l.34.1a1.464 1.464 0 0 1 .872 2.105l-.17.31c-.698 1.283.705 2.686 1.987 1.987l.311-.169a1.464 1.464 0 0 1 2.105.872l.1.34c.413 1.4 2.397 1.4 2.81 0l.1-.34a1.464 1.464 0 0 1 2.105-.872l.31.17c1.283.698 2.686-.705 1.987-1.987l-.169-.311a1.464 1.464 0 0 1 .872-2.105l.34-.1c1.4-.413 1.4-2.397 0-2.81l-.34-.1a1.464 1.464 0 0 1-.872-2.105l.17-.31c.698-1.283-.705-2.686-1.987-1.987l-.311.169a1.464 1.464 0 0 1-2.105-.872l-.1-.34zM8 10.93a2.929 2.929 0 1 1 0-5.86 2.929 2.929 0 0 1 0 5.858z"
                    />
                  </svg>
                </div>
                <h3>수시 점검</h3>
                <span class="card-frequency">관리자 수동 실행</span>
              </div>
              <div class="card-stats">
                <div class="stat-row">
                  <span class="stat-label">전체 항목</span>
                  <span class="stat-value">{{ dashboardStats.manual.totalChecks }}</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">통과 항목</span>
                  <span class="stat-value success">{{
                    dashboardStats.manual.completedChecks
                  }}</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">실패 항목</span>
                  <span class="stat-value danger">{{ dashboardStats.manual.criticalIssues }}</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">최근 점검</span>
                  <span class="stat-value">{{
                    formatDate(dashboardStats.manual.lastAuditDate)
                  }}</span>
                </div>
              </div>
              <div class="card-progress">
                <div class="progress-bar">
                  <div
                    class="progress-fill manual"
                    :style="{ width: `${getManualPassRate()}%` }"
                  ></div>
                </div>
                <span class="progress-text">통과율 {{ getManualPassRate() }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 빠른 실행 패널 -->
        <!-- <div class="section">
          <h2 class="section-title">빠른 실행</h2>
          <div class="quick-actions">
            <div class="action-card">
              <div class="action-icon daily">
                <svg width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M11 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h6zM5 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H5z"
                  />
                  <path d="M8 14a1 1 0 1 0 0-2 1 1 0 0 0 0 2z" />
                </svg>
              </div>
              <div class="action-content">
                <h4>정기 점검 실행</h4>
                <p>시스템에서 자동으로 실행되는 8개 항목의 정기 보안 점검</p>
                <span class="action-status">{{
                  dashboardStats?.daily?.lastAuditDate ? '자동 실행됨' : '아직 실행되지 않음'
                }}</span>
              </div>
            </div>

            <div class="action-card">
              <div class="action-icon manual">
                <svg width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M1 2.5A1.5 1.5 0 0 1 2.5 1h3A1.5 1.5 0 0 1 7 2.5v3A1.5 1.5 0 0 1 5.5 7h-3A1.5 1.5 0 0 1 1 5.5v-3zM2.5 2a.5.5 0 0 0-.5.5v3a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5-.5v-3a.5.5 0 0 0-.5-.5h-3zm6.5.5A1.5 1.5 0 0 1 10.5 1h3A1.5 1.5 0 0 1 15 2.5v3A1.5 1.5 0 0 1 13.5 7h-3A1.5 1.5 0 0 1 9 5.5v-3zm1.5-.5a.5.5 0 0 0-.5.5v3a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5-.5v-3a.5.5 0 0 0-.5-.5h-3zM1 10.5A1.5 1.5 0 0 1 2.5 9h3A1.5 1.5 0 0 1 7 10.5v3A1.5 1.5 0 0 1 5.5 15h-3A1.5 1.5 0 0 1 1 13.5v-3zm1.5-.5a.5.5 0 0 0-.5.5v3a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5-.5v-3a.5.5 0 0 0-.5-.5h-3zm6.5.5A1.5 1.5 0 0 1 10.5 9h3a1.5 1.5 0 0 1 1.5 1.5v3a1.5 1.5 0 0 1-1.5 1.5h-3A1.5 1.5 0 0 1 9 13.5v-3zm1.5-.5a.5.5 0 0 0-.5.5v3a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5-.5v-3a.5.5 0 0 0-.5-.5h-3z"
                  />
                </svg>
              </div>
              <div class="action-content">
                <h4>수시 점검 실행</h4>
                <p>PC 봉인씰, 악성코드 탐지, 개인정보 암호화 등 수동 점검 항목</p>
                <button @click="showManualCheckModal = true" class="execute-button">
                  점검 실행
                </button>
              </div>
            </div>
          </div>
        </div> -->

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
          </div>
        </div>

        <!-- 수시 점검 모달 -->
        <ManualCheckModal
          v-if="showManualCheckModal"
          @close="showManualCheckModal = false"
          @check-completed="handleManualCheckCompleted"
        />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Sidebar from '@/components/Sidebar.vue'
import ManualCheckModal from '@/components/ManualCheckModal.vue'

// Pinia Store
const authStore = useAuthStore()

// 반응형 데이터
const dashboardStats = ref(null)
const loading = ref(false)
const showManualCheckModal = ref(false)

// Sidebar ref
const sidebarRef = ref(null)

// 계산된 속성
const isAuthenticated = computed(() => !!authStore.user)

const getDailyPassRate = () => {
  if (!dashboardStats.value?.daily) return 0
  const stats = dashboardStats.value.daily
  if (stats.totalChecks === 0) return 0
  return Math.round((stats.completedChecks / stats.totalChecks) * 100)
}

const getManualPassRate = () => {
  if (!dashboardStats.value?.manual) return 0
  const stats = dashboardStats.value.manual
  if (stats.totalChecks === 0) return 0
  return Math.round((stats.completedChecks / stats.totalChecks) * 100)
}

// 메서드
const fetchDashboardStats = async () => {
  if (!authStore.user) return

  loading.value = true
  try {
    const response = await fetch('/api/security-audit/dashboard-stats', {
      credentials: 'include',
    })

    if (response.ok) {
      const data = await response.json()
      dashboardStats.value = data
    } else {
      console.error('대시보드 데이터 로드 실패:', response.status)
    }
  } catch (error) {
    console.error('대시보드 데이터 로드 실패:', error)
  } finally {
    loading.value = false
  }
}

const handleManualCheckCompleted = () => {
  // 수시 점검 완료 후 데이터 새로고침
  fetchDashboardStats()
}

const formatDate = (dateStr) => {
  if (!dateStr) return '아직 없음'

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
    fetchDashboardStats()
  }
})
</script>

<style scoped>
/* SecurityAuditPage.vue 스타일 */
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

/* 로딩 상태 */
.loading-container {
  text-align: center;
  padding: 60px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
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

/* 환영 섹션 */
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

/* 대시보드 그리드 */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
  margin-top: 20px;
}

.dashboard-card {
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.dashboard-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.dashboard-card.daily-check {
  border-left: 4px solid #3b82f6;
}

.dashboard-card.manual-check {
  border-left: 4px solid #10b981;
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.card-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  color: white;
}

.card-icon.daily {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
}

.card-icon.manual {
  background: linear-gradient(135deg, #10b981, #059669);
}

.card-header h3 {
  margin: 0 0 4px 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--dark-blue);
}

.card-frequency {
  padding-left: 10px;
  font-size: 0.875rem;
  color: #6b7280;
}

.card-stats {
  margin-bottom: 20px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f3f4f6;
}

.stat-row:last-child {
  border-bottom: none;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
}

.stat-value {
  font-weight: 600;
  color: var(--dark-blue);
}

.stat-value.success {
  color: #10b981;
}

.stat-value.danger {
  color: #ef4444;
}

.card-progress {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background-color: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-fill.daily {
  background: linear-gradient(90deg, #3b82f6, #1d4ed8);
}

.progress-fill.manual {
  background: linear-gradient(90deg, #10b981, #059669);
}

.progress-text {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--dark-blue);
  min-width: 60px;
}

/* 빠른 실행 패널 */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.action-card {
  display: flex;
  align-items: flex-start;
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.3s ease;
}

.action-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.action-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  flex-shrink: 0;
  color: white;
}

.action-icon.daily {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
}

.action-icon.manual {
  background: linear-gradient(135deg, #10b981, #059669);
}

.action-content {
  flex: 1;
}

.action-content h4 {
  margin: 0 0 8px 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--dark-blue);
}

.action-content p {
  margin: 0 0 12px 0;
  font-size: 0.875rem;
  color: #6b7280;
  line-height: 1.5;
}

.action-status {
  font-size: 0.75rem;
  color: #10b981;
  font-weight: 500;
}

.execute-button {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.execute-button:hover {
  background-color: var(--dark-blue);
  transform: translateY(-1px);
}

/* 기능 그리드 */
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

/* 섹션 공통 스타일 */
/* .section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--dark-blue);
  margin-bottom: 20px;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--light-blue);
} */

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 2px solid #e5e7eb;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--dark-blue);
  margin: 0;
}

/* 반응형 디자인 */
@media (max-width: 1024px) {
  .security-audit-layout {
    flex-direction: column;
  }

  .main-content {
    margin: 20px;
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
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

  .quick-actions {
    grid-template-columns: 1fr;
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    text-align: center;
  }

  .card-icon {
    margin-right: 0;
    margin-bottom: 12px;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.5rem;
  }

  .section-title {
    font-size: 1.25rem;
  }

  .dashboard-card {
    padding: 16px;
  }

  .action-card {
    flex-direction: column;
    text-align: center;
  }

  .action-icon {
    margin-right: 0;
    margin-bottom: 12px;
  }
}

@media (min-width: 769px) {
  .mobile-menu-toggle {
    display: none;
  }
}
</style>
