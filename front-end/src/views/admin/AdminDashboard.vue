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
/* AdminDashboard.vue 스타일 */
<style scoped>
.admin-dashboard {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f8fafc;
  min-height: calc(100vh - 114px);
}

.admin-header {
  background-color: white;
  border-radius: 12px;
  padding: 20px 30px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
}

.admin-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 20px 0;
}

.admin-nav {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.nav-item {
  padding: 8px 16px;
  border-radius: 8px;
  text-decoration: none;
  color: #6b7280;
  font-weight: 500;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.nav-item:hover {
  background-color: #f3f4f6;
  color: #374151;
}

.nav-item.active {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.loading-container,
.error-container {
  background-color: white;
  border-radius: 12px;
  padding: 60px 20px;
  text-align: center;
  margin: 20px 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
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

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.retry-button {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 16px;
  font-weight: 500;
}

.retry-button:hover {
  background-color: var(--dark-blue);
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

/* 주요 지표 섹션 */
.overview-section h2 {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 20px;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
}

.overview-card {
  background-color: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
}

.overview-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.overview-card.users {
  border-left: 4px solid #3b82f6;
}

.overview-card.score {
  border-left: 4px solid #8b5cf6;
}

.overview-card.education {
  border-left: 4px solid #10b981;
}

.overview-card.training {
  border-left: 4px solid #f59e0b;
}

.card-icon {
  font-size: 36px;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8fafc;
  border-radius: 12px;
  flex-shrink: 0;
}

.card-content {
  flex: 1;
}

.card-value {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 4px;
  line-height: 1;
}

.card-label {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

/* 통계 섹션 */
.statistics-section h2 {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 20px;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
}

.stat-card {
  background-color: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
}

.stat-card h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 20px 0;
  padding-bottom: 12px;
  border-bottom: 1px solid #f3f4f6;
}

.stat-details {
  margin-bottom: 20px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.stat-value.success {
  color: #10b981;
}

.stat-value.warning {
  color: #f59e0b;
}

.stat-value.danger {
  color: #ef4444;
}

.progress-container {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background-color: #f3f4f6;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.education-progress {
  background-color: #10b981;
}

.training-progress {
  background-color: #f59e0b;
}

.progress-text {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  min-width: 40px;
}

.stat-actions {
  text-align: right;
}

.action-button {
  background-color: var(--primary-color);
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s ease;
}

.action-button:hover {
  background-color: var(--dark-blue);
}

/* 빠른 작업 섹션 */
.quick-actions-section h2 {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 20px;
}

.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.quick-action-card {
  background-color: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.quick-action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  border-color: var(--primary-color);
}

.action-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.quick-action-card h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.quick-action-card p {
  font-size: 14px;
  color: #6b7280;
  margin: 0 0 20px 0;
  line-height: 1.5;
}

.action-btn {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
  width: 100%;
}

.action-btn:hover:not(:disabled) {
  background-color: var(--dark-blue);
}

.action-btn:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

/* 최근 활동 섹션 */
.recent-activity-section h2 {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 20px;
}

.activity-list {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 24px;
  border-bottom: 1px solid #f3f4f6;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-time {
  font-size: 12px;
  color: #9ca3af;
  min-width: 120px;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 2px;
}

.activity-desc {
  font-size: 13px;
  color: #6b7280;
}

/* 토스트 메시지 */
.toast-message {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 8px;
  color: white;
  font-size: 14px;
  font-weight: 500;
  z-index: 1000;
  animation: slideIn 0.3s ease;
  max-width: 400px;
}

.toast-message.success {
  background-color: #10b981;
}

.toast-message.error {
  background-color: #ef4444;
}

.toast-message.info {
  background-color: #3b82f6;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .admin-dashboard {
    padding: 15px;
  }

  .admin-header {
    padding: 20px;
  }

  .admin-header h1 {
    font-size: 24px;
  }

  .admin-nav {
    flex-direction: column;
    gap: 8px;
  }

  .nav-item {
    text-align: center;
    padding: 12px;
  }

  .overview-cards {
    grid-template-columns: 1fr;
  }

  .stat-grid {
    grid-template-columns: 1fr;
  }

  .quick-actions-grid {
    grid-template-columns: 1fr;
  }

  .card-value {
    font-size: 28px;
  }

  .card-icon {
    font-size: 32px;
    width: 50px;
    height: 50px;
  }
}

@media (max-width: 480px) {
  .overview-card {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }

  .activity-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .activity-time {
    min-width: auto;
  }
}
</style>
