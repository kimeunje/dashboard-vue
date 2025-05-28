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
          <p>공통 정보보안 시스템에 접근하려면 로그인이 필요합니다.</p>
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

        <!-- 로딩 상태 -->
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>데이터를 불러오는 중...</p>
        </div>

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
              <h2>공통 정보보안 시스템에 오신 것을 환영합니다</h2>
              <p>
                {{ authStore.user.name }}님, 조직의 보안 정책 준수를 위한 체계적인 감사 도구를
                활용하여 시스템의 보안 상태를 점검하고 개선하세요.
              </p>
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
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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
.section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--dark-blue);
  margin-bottom: 20px;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--light-blue);
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--dark-blue);
  margin-bottom: 32px;
  text-align: center;
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
