<!-- views/admin/AdminDashboard.vue -->
<template>
  <div class="admin-dashboard">
    <div class="admin-header">
      <h1>관리자 대시보드</h1>
      <div class="admin-nav">
        <RouterLink to="/admin" class="nav-item active">대시보드</RouterLink>
        <RouterLink to="/admin/users" class="nav-item">사용자 관리</RouterLink>
        <RouterLink to="/admin/education" class="nav-item">교육 관리</RouterLink>
        <RouterLink to="/admin/training" class="nav-item">훈련 관리</RouterLink>
        <RouterLink to="/admin/scores" class="nav-item">점수 관리</RouterLink>
      </div>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>대시보드 데이터를 불러오는 중...</p>
    </div>

    <!-- 에러 상태 -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">⚠️</div>
      <h3>데이터 로드 실패</h3>
      <p>{{ error }}</p>
      <button @click="fetchDashboardData" class="retry-button">다시 시도</button>
    </div>

    <!-- 대시보드 데이터 -->
    <div v-else-if="dashboardData" class="dashboard-content">
      <!-- 주요 지표 -->
      <div class="overview-section">
        <h2>전체 현황 ({{ dashboardData.overview.evaluation_year }}년)</h2>
        <div class="overview-cards">
          <div class="overview-card users">
            <div class="card-icon">👥</div>
            <div class="card-content">
              <div class="card-value">{{ dashboardData.overview.total_users }}</div>
              <div class="card-label">전체 사용자</div>
            </div>
          </div>

          <div class="overview-card score">
            <div class="card-icon">⭐</div>
            <div class="card-content">
              <div class="card-value">{{ dashboardData.overview.avg_score }}점</div>
              <div class="card-label">평균 보안 점수</div>
            </div>
          </div>

          <div class="overview-card education">
            <div class="card-icon">📚</div>
            <div class="card-content">
              <div class="card-value">{{ dashboardData.education.completion_rate }}%</div>
              <div class="card-label">교육 이수율</div>
            </div>
          </div>

          <div class="overview-card training">
            <div class="card-icon">📧</div>
            <div class="card-content">
              <div class="card-value">{{ dashboardData.training.pass_rate }}%</div>
              <div class="card-label">훈련 통과율</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 상세 통계 -->
      <div class="statistics-section">
        <div class="stat-grid">
          <!-- 교육 통계 -->
          <div class="stat-card">
            <h3>정보보호 교육 현황</h3>
            <div class="stat-details">
              <div class="stat-row">
                <span class="stat-label">총 교육 대상:</span>
                <span class="stat-value">{{ dashboardData.education.total_participants }}명</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">이수 완료:</span>
                <span class="stat-value success">{{ dashboardData.education.completed }}건</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">미이수:</span>
                <span class="stat-value warning">{{ dashboardData.education.incomplete }}건</span>
              </div>
              <div class="progress-container">
                <div class="progress-bar">
                  <div
                    class="progress-fill education-progress"
                    :style="{ width: `${dashboardData.education.completion_rate}%` }"
                  ></div>
                </div>
                <span class="progress-text">{{ dashboardData.education.completion_rate }}%</span>
              </div>
            </div>
            <div class="stat-actions">
              <RouterLink to="/admin/education" class="action-button">교육 관리</RouterLink>
            </div>
          </div>

          <!-- 훈련 통계 -->
          <div class="stat-card">
            <h3>모의훈련 현황</h3>
            <div class="stat-details">
              <div class="stat-row">
                <span class="stat-label">총 훈련 대상:</span>
                <span class="stat-value">{{ dashboardData.training.total_participants }}명</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">통과:</span>
                <span class="stat-value success">{{ dashboardData.training.passed }}건</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">실패:</span>
                <span class="stat-value danger">{{ dashboardData.training.failed }}건</span>
              </div>
              <div class="progress-container">
                <div class="progress-bar">
                  <div
                    class="progress-fill training-progress"
                    :style="{ width: `${dashboardData.training.pass_rate}%` }"
                  ></div>
                </div>
                <span class="progress-text">{{ dashboardData.training.pass_rate }}%</span>
              </div>
            </div>
            <div class="stat-actions">
              <RouterLink to="/admin/training" class="action-button">훈련 관리</RouterLink>
            </div>
          </div>
        </div>
      </div>

      <!-- 빠른 작업 -->
      <div class="quick-actions-section">
        <h2>빠른 작업</h2>
        <div class="quick-actions-grid">
          <div class="quick-action-card" @click="recalculateAllScores">
            <div class="action-icon">🔄</div>
            <h3>전체 점수 재계산</h3>
            <p>모든 사용자의 보안 점수를 다시 계산합니다</p>
            <button class="action-btn" :disabled="recalculating">
              {{ recalculating ? '계산 중...' : '재계산 실행' }}
            </button>
          </div>

          <div class="quick-action-card" @click="exportData">
            <div class="action-icon">📊</div>
            <h3>데이터 내보내기</h3>
            <p>전체 사용자 데이터를 엑셀로 내보냅니다</p>
            <button class="action-btn">내보내기</button>
          </div>

          <div class="quick-action-card" @click="$router.push('/admin/users')">
            <div class="action-icon">👥</div>
            <h3>사용자 관리</h3>
            <p>사용자 정보를 조회하고 관리합니다</p>
            <button class="action-btn">관리하기</button>
          </div>

          <div class="quick-action-card" @click="generateReport">
            <div class="action-icon">📋</div>
            <h3>종합 보고서</h3>
            <p>전체 보안 현황 보고서를 생성합니다</p>
            <button class="action-btn">보고서 생성</button>
          </div>
        </div>
      </div>

      <!-- 최근 활동 -->
      <div class="recent-activity-section">
        <h2>최근 활동</h2>
        <div class="activity-list">
          <div class="activity-item">
            <div class="activity-time">{{ formatDate(new Date()) }}</div>
            <div class="activity-content">
              <div class="activity-title">시스템 점검 완료</div>
              <div class="activity-desc">전체 사용자 보안 점수 업데이트</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 토스트 메시지 -->
    <div v-if="showToast" :class="['toast-message', toastType]">
      {{ toastMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import '@/assets/styles/views/admin/AdminDashboard.css'

// 반응형 데이터
const loading = ref(false)
const error = ref(null)
const dashboardData = ref(null)
const recalculating = ref(false)
const showToast = ref(false)
const toastMessage = ref('')
const toastType = ref('success')

// 메서드
const fetchDashboardData = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await fetch('/api/admin/dashboard', {
      credentials: 'include',
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: 데이터를 불러올 수 없습니다.`)
    }

    dashboardData.value = await response.json()
  } catch (err) {
    console.error('대시보드 데이터 조회 실패:', err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const recalculateAllScores = async () => {
  if (recalculating.value) return

  recalculating.value = true

  try {
    const response = await fetch('/api/admin/scores/recalculate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ year: new Date().getFullYear() }),
    })

    if (!response.ok) {
      throw new Error('점수 재계산에 실패했습니다.')
    }

    const result = await response.json()
    showToastMessage(`${result.success_count}명의 점수가 재계산되었습니다.`, 'success')

    // 대시보드 데이터 새로고침
    await fetchDashboardData()
  } catch (err) {
    console.error('점수 재계산 실패:', err)
    showToastMessage(err.message, 'error')
  } finally {
    recalculating.value = false
  }
}

const exportData = () => {
  // 데이터 내보내기 기능
  showToastMessage('데이터 내보내기 기능이 준비중입니다.', 'info')
}

const generateReport = () => {
  // 보고서 생성 기능
  showToastMessage('보고서 생성 기능이 준비중입니다.', 'info')
}

const formatDate = (date) => {
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const showToastMessage = (message, type = 'success') => {
  toastMessage.value = message
  toastType.value = type
  showToast.value = true

  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

// 라이프사이클 훅
onMounted(() => {
  fetchDashboardData()
})
</script>
