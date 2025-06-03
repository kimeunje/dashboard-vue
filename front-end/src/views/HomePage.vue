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
          <p>정보보안 감사 시스템에 접근하려면 로그인이 필요합니다.</p>
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
              <h2>정보보안 감사 시스템에 오신 것을 환영합니다</h2>
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
import '@/assets/styles/views/HomePage.css'

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
