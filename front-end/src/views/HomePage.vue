<!-- views/HomePage.vue 업데이트된 템플릿 -->
<template>
  <div class="dashboard-page">
    <!-- 업무 개요 헤더 -->
    <div class="dashboard-header">
      <div class="welcome-message">
        <h1>종합 보안 관리 시스템</h1>
        <p>
          {{
            authStore.user
              ? `${authStore.user.name}님, 안녕하세요.`
              : '종합 보안 대시보드에 오신 것을 환영합니다.'
          }}
        </p>
      </div>
      <div v-if="authStore.user && dashboardData" class="security-status">
        <div class="status-label">
          종합 보안 점수:
          <span
            class="status-value"
            :class="getScoreClass(dashboardData.overall_score.total_score)"
          >
            {{ dashboardData.overall_score.total_score }}점 ({{
              dashboardData.overall_score.grade
            }})
          </span>
        </div>
        <div class="progress-bar">
          <div
            class="progress-fill"
            :class="getScoreClass(dashboardData.overall_score.total_score)"
            :style="{
              width: `${dashboardData.overall_score.total_score}%`,
            }"
          ></div>
        </div>
      </div>
    </div>

    <!-- 로그인 상태 - 종합 대시보드 표시 -->
    <template v-if="authStore.user">
      <!-- 로딩 상태 -->
      <div v-if="loading" class="dashboard-card status-summary">
        <div class="card-header">
          <h2>종합 보안 현황</h2>
          <span class="date-info">데이터 로딩 중...</span>
        </div>
        <div class="loading-indicator">
          <div class="loading-spinner"></div>
          <p>보안 데이터를 불러오는 중입니다...</p>
        </div>
      </div>

      <!-- 에러 상태 -->
      <div v-else-if="error" class="dashboard-card status-summary">
        <div class="card-header">
          <h2>종합 보안 현황</h2>
          <span class="date-info error">오류 발생</span>
        </div>
        <div class="error-message">
          <p>{{ error }}</p>
          <button @click="fetchDashboardData" class="retry-button">다시 시도</button>
        </div>
      </div>

      <!-- 종합 대시보드 데이터 -->
      <div v-else-if="dashboardData" class="dashboard-main">
        <!-- 주요 지표 카드들 -->
        <div class="metrics-grid">
          <div class="metric-card audit">
            <div class="metric-header">
              <div class="metric-icon">🛡️</div>
              <h3>상시보안감사</h3>
            </div>
            <div class="metric-content">
              <div class="metric-score">{{ dashboardData.score_breakdown.audit.score }}점</div>
              <div class="metric-detail">
                통과율: {{ dashboardData.quick_stats.audit_pass_rate }}%
              </div>
              <div class="metric-status" :class="dashboardData.score_breakdown.audit.status">
                {{ getStatusText(dashboardData.score_breakdown.audit.status) }}
              </div>
            </div>
            <div class="metric-action">
              <RouterLink to="/security-audit/results" class="metric-link">
                상세 보기 →
              </RouterLink>
            </div>
          </div>

          <div class="metric-card education">
            <div class="metric-header">
              <div class="metric-icon">📚</div>
              <h3>정보보호교육</h3>
            </div>
            <div class="metric-content">
              <div class="metric-score penalty">
                -{{ dashboardData.score_breakdown.education.penalty }}점
              </div>
              <div class="metric-detail">
                이수율: {{ dashboardData.quick_stats.education_completion_rate }}%
              </div>
              <div class="metric-status" :class="dashboardData.score_breakdown.education.status">
                미이수 {{ dashboardData.score_breakdown.education.incomplete_count }}회
              </div>
            </div>
            <div class="metric-action">
              <RouterLink to="/security-education" class="metric-link"> 상세 보기 → </RouterLink>
            </div>
          </div>

          <div class="metric-card training">
            <div class="metric-header">
              <div class="metric-icon">📧</div>
              <h3>모의훈련</h3>
            </div>
            <div class="metric-content">
              <div class="metric-score penalty">
                -{{ dashboardData.score_breakdown.training.penalty }}점
              </div>
              <div class="metric-detail">
                통과율: {{ dashboardData.quick_stats.training_pass_rate }}%
              </div>
              <div class="metric-status" :class="dashboardData.score_breakdown.training.status">
                실패 {{ dashboardData.score_breakdown.training.failed_count }}회
              </div>
            </div>
            <div class="metric-action">
              <RouterLink to="/phishing-training" class="metric-link"> 상세 보기 → </RouterLink>
            </div>
          </div>

          <div class="metric-card overall">
            <div class="metric-header">
              <div class="metric-icon">⭐</div>
              <h3>종합점수</h3>
            </div>
            <div class="metric-content">
              <div class="metric-score total">{{ dashboardData.overall_score.total_score }}점</div>
              <div class="metric-detail">등급: {{ dashboardData.overall_score.grade }}</div>
              <div
                class="metric-status"
                :class="getOverallStatus(dashboardData.overall_score.total_score)"
              >
                {{ getOverallStatusText(dashboardData.overall_score.total_score) }}
              </div>
            </div>
            <div class="metric-action">
              <RouterLink to="/security-score" class="metric-link"> 상세 보기 → </RouterLink>
            </div>
          </div>
        </div>

        <!-- 권장사항 섹션 -->
        <div v-if="dashboardData.recommendations.length > 0" class="recommendations-section">
          <h2>개선 권장사항</h2>
          <div class="recommendations-grid">
            <div
              v-for="(rec, index) in dashboardData.recommendations.slice(0, 3)"
              :key="index"
              class="recommendation-card"
              :class="rec.priority"
            >
              <div class="recommendation-header">
                <div class="priority-badge" :class="rec.priority">
                  {{ getPriorityText(rec.priority) }}
                </div>
                <h3>{{ rec.title }}</h3>
              </div>
              <p>{{ rec.description }}</p>
              <div v-if="rec.action_link" class="recommendation-action">
                <RouterLink :to="rec.action_link" class="action-button"> 조치하기 → </RouterLink>
              </div>
            </div>
          </div>
          <div v-if="dashboardData.recommendations.length > 3" class="show-all-recommendations">
            <RouterLink to="/security-score" class="show-all-button">
              모든 권장사항 보기 ({{ dashboardData.recommendations.length }}개)
            </RouterLink>
          </div>
        </div>

        <!-- 빠른 액세스 메뉴 -->
        <div class="quick-access-section">
          <h2>빠른 메뉴</h2>
          <div class="quick-access-grid">
            <RouterLink to="/security-audit" class="quick-access-card">
              <div class="quick-icon">🛡️</div>
              <h3>상시보안감사</h3>
              <p>보안 감사 결과 확인 및 조치방법 안내</p>
            </RouterLink>

            <RouterLink to="/security-education" class="quick-access-card">
              <div class="quick-icon">📚</div>
              <h3>정보보호교육</h3>
              <p>분기별 교육 이수 현황 및 일정</p>
            </RouterLink>

            <RouterLink to="/phishing-training" class="quick-access-card">
              <div class="quick-icon">📧</div>
              <h3>모의훈련</h3>
              <p>악성메일 모의훈련 결과 및 대응방법</p>
            </RouterLink>

            <RouterLink to="/security-score" class="quick-access-card">
              <div class="quick-icon">⭐</div>
              <h3>종합점수</h3>
              <p>보안 평가 점수 및 등급 확인</p>
            </RouterLink>
          </div>
        </div>
      </div>

      <!-- 초기 설정 안내 카드 (기존 코드 유지) -->
      <div v-if="!initialSetupDone" class="dashboard-main">
        <div class="dashboard-card setup-card">
          <div class="card-header">
            <h2>초기 설정 필요</h2>
            <span class="date-info important">최초 1회 필수</span>
          </div>
          <div class="setup-content simple">
            <p>보안 감사를 진행하기 전에 컴퓨터 이름과 작업 그룹(부서명)을 설정해야 합니다.</p>

            <div class="setup-note">
              <ul>
                <li>컴퓨터 이름은 <strong>사용자 본인의 이름</strong>으로 설정하세요.</li>
                <li>작업 그룹은 <strong>소속 부서명</strong>으로 설정하세요.</li>
                <li>설정 후 시스템 재부팅이 필요할 수 있습니다.</li>
              </ul>
            </div>

            <div class="setup-actions simple">
              <button
                class="download-button primary-download"
                @click="downloadHomeScript"
                :disabled="downloadLoading"
              >
                <svg
                  v-if="!downloadLoading"
                  width="16"
                  height="16"
                  fill="currentColor"
                  viewBox="0 0 16 16"
                >
                  <path
                    d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"
                  />
                  <path
                    d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"
                  />
                </svg>
                <div v-else class="loading-spinner-small"></div>
                홈 다운로드
              </button>
              <button class="download-button" @click="downloadScript" :disabled="downloadLoading">
                <svg
                  v-if="!downloadLoading"
                  width="16"
                  height="16"
                  fill="currentColor"
                  viewBox="0 0 16 16"
                >
                  <path
                    d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"
                  />
                  <path
                    d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"
                  />
                </svg>
                <div v-else class="loading-spinner-small"></div>
                스크립트 다운로드
              </button>
              <button class="setup-complete-button" @click="markSetupAsDone">
                <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M13.854 3.646a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 10.293l6.646-6.647a.5.5 0 0 1 .708 0z"
                  />
                </svg>
                초기 설정 완료 표시
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- 로그아웃 상태 - 안내 메시지 표시 -->
    <div v-else class="not-logged-info">
      <div class="info-icon">
        <svg width="40" height="40" fill="currentColor" viewBox="0 0 16 16">
          <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
          <path
            d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"
          />
        </svg>
      </div>
      <h2>로그인이 필요합니다</h2>
      <p>
        종합 보안 관리 시스템을 이용하기 위해서는 로그인이 필요합니다. 로그인 페이지로 이동하여
        로그인해 주세요.
      </p>
      <div class="login-button-container">
        <RouterLink to="/login" class="login-page-button">
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
          로그인 페이지로 이동
        </RouterLink>
      </div>
    </div>

    <!-- 하단 안내 섹션 -->
    <div class="dashboard-main">
      <div class="dashboard-card">
        <div class="help-section">
          <h3>도움이 필요하신가요?</h3>
          <p>
            보안 관련 문의사항은
            <RouterLink to="/security-audit/contact" class="inline-link">
              IT 보안팀에 문의
            </RouterLink>
            하거나 내선 <strong>5678</strong>로 연락해주세요.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Props 정의
defineProps({
  user: {
    type: Object,
    default: null,
  },
})

// Pinia Store
const authStore = useAuthStore()

// 반응형 데이터
const dashboardData = ref(null)
const loading = ref(false)
const error = ref(null)
const initialSetupDone = ref(false)
const downloadLoading = ref(false)

// 메서드
const fetchDashboardData = async () => {
  if (!authStore.user) return

  loading.value = true
  error.value = null

  try {
    const response = await fetch('/api/security-dashboard/overview', {
      credentials: 'include',
    })

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`)
    }

    const data = await response.json()
    dashboardData.value = data
  } catch (err) {
    console.error('Failed to fetch dashboard data:', err)
    error.value = '대시보드 데이터를 불러오는 중 오류가 발생했습니다.'
  } finally {
    loading.value = false
  }
}

const getScoreClass = (score) => {
  if (score >= 90) return 'excellent'
  if (score >= 80) return 'good'
  if (score >= 70) return 'warning'
  return 'poor'
}

const getStatusText = (status) => {
  const statusTexts = {
    good: '양호',
    warning: '주의',
    critical: '위험',
  }
  return statusTexts[status] || '알 수 없음'
}

const getOverallStatus = (score) => {
  if (score >= 90) return 'excellent'
  if (score >= 80) return 'good'
  if (score >= 70) return 'warning'
  return 'critical'
}

const getOverallStatusText = (score) => {
  if (score >= 90) return '우수'
  if (score >= 80) return '양호'
  if (score >= 70) return '보통'
  return '개선필요'
}

const getPriorityText = (priority) => {
  const priorities = {
    high: '긴급',
    medium: '중요',
    low: '권장',
    info: '정보',
  }
  return priorities[priority] || '일반'
}

// 기존 함수들 유지
const checkInitialSetup = () => {
  const setupDone = localStorage.getItem('initialSetupDone')
  if (setupDone === 'true') {
    initialSetupDone.value = true
  }
}

const downloadHomeScript = async () => {
  downloadLoading.value = true
  try {
    await new Promise((resolve) => setTimeout(resolve, 1000))
    console.log('홈 스크립트 다운로드')
  } catch (err) {
    console.error('다운로드 오류:', err)
  } finally {
    downloadLoading.value = false
  }
}

const downloadScript = async () => {
  downloadLoading.value = true
  try {
    await new Promise((resolve) => setTimeout(resolve, 1000))
    console.log('스크립트 다운로드')
  } catch (err) {
    console.error('다운로드 오류:', err)
  } finally {
    downloadLoading.value = false
  }
}

const markSetupAsDone = () => {
  localStorage.setItem('initialSetupDone', 'true')
  initialSetupDone.value = true
}

// 사용자 상태 변화 감지
watch(
  () => authStore.user,
  (newUser) => {
    if (newUser) {
      fetchDashboardData()
    } else {
      dashboardData.value = null
    }
  },
  { immediate: true },
)

// 라이프사이클 훅
onMounted(() => {
  checkInitialSetup()
})
</script>
/* HomePage.vue 업데이트된 스타일 */
<style scoped>
/* 기존 스타일 유지하면서 새로운 스타일 추가 */
.dashboard-page {
  padding: 24px 30px 40px;
  background-color: #ffffff;
  min-height: calc(100vh - 114px);
  width: 100%;
  max-width: 1200px;
  margin: 20px auto;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.05);
  border-left: 1px solid #e0e4e9;
  border-right: 1px solid #e0e4e9;
  border-radius: 8px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e0e4e9;
  width: 100%;
}

.welcome-message h1 {
  font-size: 24px;
  font-weight: 600;
  color: #3949ab;
  margin-bottom: 8px;
}

.welcome-message p {
  font-size: 15px;
  color: #5a6a7e;
}

.security-status {
  text-align: right;
}

.status-label {
  font-size: 14px;
  color: #5a6a7e;
  margin-bottom: 6px;
}

.status-value {
  font-weight: 600;
  margin-left: 8px;
}

.status-value.excellent {
  color: #10b981;
}

.status-value.good {
  color: #3b82f6;
}

.status-value.warning {
  color: #f59e0b;
}

.status-value.poor {
  color: #ef4444;
}

.progress-bar {
  width: 200px;
  height: 8px;
  background-color: #e0e4e9;
  border-radius: 4px;
  overflow: hidden;
  margin-top: 8px;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-fill.excellent {
  background-color: #10b981;
}

.progress-fill.good {
  background-color: #3b82f6;
}

.progress-fill.warning {
  background-color: #f59e0b;
}

.progress-fill.poor {
  background-color: #ef4444;
}

/* 주요 지표 카드들 */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.metric-card {
  background-color: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.metric-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.metric-card.audit {
  border-top-color: #3b82f6;
}

.metric-card.education {
  border-top-color: #10b981;
}

.metric-card.training {
  border-top-color: #f59e0b;
}

.metric-card.overall {
  border-top-color: #8b5cf6;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

.metric-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.metric-icon {
  font-size: 24px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background-color: #f3f4f6;
}

.metric-header h3 {
  margin: 0;
  font-size: 16px;
  color: var(--dark-blue);
  font-weight: 600;
}

.metric-content {
  margin-bottom: 16px;
}

.metric-score {
  font-size: 28px;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 8px;
}

.metric-score.penalty {
  color: #ef4444;
}

.metric-score.total {
  color: #8b5cf6;
}

.metric-detail {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 8px;
}

.metric-status {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 12px;
  display: inline-block;
}

.metric-status.good {
  background-color: #d1fae5;
  color: #065f46;
}

.metric-status.warning {
  background-color: #fef3c7;
  color: #92400e;
}

.metric-status.critical {
  background-color: #fee2e2;
  color: #991b1b;
}

.metric-status.excellent {
  background-color: #ddd6fe;
  color: #5b21b6;
}

.metric-action {
  margin-top: 12px;
}

.metric-link {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
  font-size: 14px;
}

.metric-link:hover {
  text-decoration: underline;
}

/* 권장사항 섹션 */
.recommendations-section {
  margin-bottom: 40px;
}

.recommendations-section h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--dark-blue);
  margin-bottom: 20px;
  border-left: 4px solid var(--primary-color);
  padding-left: 12px;
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.recommendation-card {
  background-color: white;
  border: 1px solid #e5e7eb;
  border-left: 4px solid #6b7280;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s ease;
}

.recommendation-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.recommendation-card.high {
  border-left-color: #ef4444;
  background-color: #fef2f2;
}

.recommendation-card.medium {
  border-left-color: #f59e0b;
  background-color: #fffbeb;
}

.recommendation-card.low {
  border-left-color: #3b82f6;
  background-color: #eff6ff;
}

.recommendation-card.info {
  border-left-color: #10b981;
  background-color: #ecfdf5;
}

.recommendation-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.priority-badge {
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: 600;
  color: white;
}

.priority-badge.high {
  background-color: #ef4444;
}

.priority-badge.medium {
  background-color: #f59e0b;
}

.priority-badge.low {
  background-color: #3b82f6;
}

.priority-badge.info {
  background-color: #10b981;
}

.recommendation-card h3 {
  margin: 0;
  font-size: 14px;
  color: var(--dark-blue);
  font-weight: 600;
}

.recommendation-card p {
  margin: 0 0 12px 0;
  font-size: 13px;
  color: #6b7280;
  line-height: 1.4;
}

.recommendation-action {
  text-align: right;
}

.action-button {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
  font-size: 12px;
}

.action-button:hover {
  text-decoration: underline;
}

.show-all-recommendations {
  text-align: center;
  margin-top: 16px;
}

.show-all-button {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
  padding: 8px 16px;
  border: 1px solid var(--primary-color);
  border-radius: 6px;
  display: inline-block;
  transition: all 0.3s ease;
}

.show-all-button:hover {
  background-color: var(--primary-color);
  color: white;
}

/* 빠른 액세스 메뉴 */
.quick-access-section {
  margin-bottom: 40px;
}

.quick-access-section h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--dark-blue);
  margin-bottom: 20px;
  border-left: 4px solid var(--primary-color);
  padding-left: 12px;
}

.quick-access-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
}

.quick-access-card {
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
  text-decoration: none;
  color: inherit;
  transition: all 0.3s ease;
  text-align: center;
}

.quick-access-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-color: var(--primary-color);
}

.quick-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.quick-access-card h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: var(--dark-blue);
  font-weight: 600;
}

.quick-access-card p {
  margin: 0;
  font-size: 13px;
  color: #6b7280;
  line-height: 1.4;
}

/* 기존 스타일들 유지 */
.dashboard-main {
  margin-bottom: 24px;
  width: 100%;
}

.dashboard-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 24px;
  margin-bottom: 24px;
  width: 100%;
  border: 1px solid #e0e4e9;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.card-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #3949ab;
}

.date-info {
  font-size: 14px;
  color: #7f8c9d;
}

.date-info.important {
  font-weight: 600;
  color: #e74c3c;
}

.loading-indicator {
  padding: 20px;
  text-align: center;
}

.loading-spinner {
  border: 2px solid #f3f3f3;
  border-top: 2px solid var(--primary-color);
  border-radius: 50%;
  width: 20px;
  height: 20px;
  animation: spin 1s linear infinite;
  display: inline-block;
  margin-right: 8px;
}

.loading-spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.error-message {
  padding: 20px;
  color: #f44336;
}

.retry-button {
  padding: 8px 16px;
  margin-top: 10px;
  background-color: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

/* 설정 관련 스타일 (기존 유지) */
.setup-content.simple p {
  font-size: 16px;
  line-height: 1.5;
  color: #3949ab;
  margin-bottom: 16px;
}

.setup-note {
  background-color: #f8f9fa;
  border-radius: 6px;
  padding: 16px 20px;
  margin-bottom: 24px;
}

.setup-note ul {
  margin: 0;
  padding-left: 24px;
}

.setup-note li {
  margin-bottom: 8px;
  color: #5a6a7e;
  line-height: 1.5;
  font-size: 15px;
}

.setup-actions.simple {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 24px;
  justify-content: flex-start;
}

.download-button {
  padding: 12px 20px;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
  background-color: #4056b7;
  color: white;
}

.download-button:hover {
  background-color: #3949ab;
}

.setup-complete-button {
  background-color: transparent;
  border: 1px solid #4056b7;
  color: #4056b7;
  padding: 12px 20px;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.setup-complete-button:hover {
  background-color: #eef1fd;
}

.not-logged-info {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 32px;
  margin-bottom: 24px;
  text-align: center;
  width: 100%;
  border: 1px solid #e0e4e9;
}

.info-icon {
  margin-bottom: 20px;
  color: #4056b7;
}

.not-logged-info h2 {
  font-size: 20px;
  font-weight: 600;
  color: #3949ab;
  margin-bottom: 12px;
}

.not-logged-info p {
  font-size: 15px;
  color: #5a6a7e;
  margin-bottom: 24px;
  line-height: 1.5;
}

.login-page-button {
  background-color: #4056b7;
  color: white;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 500;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.3s;
}

.login-page-button:hover {
  background-color: #3949ab;
}

.help-section {
  text-align: center;
}

.help-section h3 {
  font-size: 18px;
  font-weight: 600;
  color: #3949ab;
  margin-bottom: 12px;
}

.help-section p {
  font-size: 15px;
  color: #6a6057;
  line-height: 1.5;
}

.inline-link {
  color: #4056b7;
  text-decoration: none;
  font-weight: 500;
}

.inline-link:hover {
  text-decoration: underline;
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
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .security-status {
    width: 100%;
    text-align: left;
  }

  .progress-bar {
    width: 100%;
  }

  .metrics-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .recommendations-grid {
    grid-template-columns: 1fr;
  }

  .quick-access-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .setup-actions.simple {
    flex-direction: column;
    width: 100%;
  }

  .download-button,
  .setup-complete-button {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .quick-access-grid {
    grid-template-columns: 1fr;
  }

  .metric-score {
    font-size: 24px;
  }

  .metric-header h3 {
    font-size: 14px;
  }
}
</style>
