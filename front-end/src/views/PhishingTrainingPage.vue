<!-- views/PhishingTrainingPage.vue -->
<template>
  <main class="">
    <div class="training-page">
      <!-- 연도 선택기 -->
      <div class="page-header">
        <h1 class="page-title">악성메일 모의훈련 현황</h1>
        <div class="year-selector">
          <label for="year">연도:</label>
          <select id="year" v-model="selectedYear" @change="fetchTrainingStatus">
            <option v-for="year in availableYears" :key="year" :value="year">{{ year }}년</option>
          </select>
        </div>
      </div>

      <!-- 로딩 상태 -->
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>모의훈련 현황을 불러오는 중...</p>
      </div>

      <!-- 에러 상태 -->
      <div v-else-if="error" class="error-container">
        <div class="error-icon">⚠️</div>
        <h3>데이터 로드 실패</h3>
        <p>{{ error }}</p>
        <button @click="fetchTrainingStatus" class="retry-button">다시 시도</button>
      </div>

      <!-- 모의훈련 현황 데이터 -->
      <div v-else-if="trainingData" class="training-content">
        <!-- 훈련 상태 대시보드 -->
        <div class="section">
          <div class="dashboard-grid">
            <!-- 모의훈련 카드 -->
            <div class="dashboard-card phishing-training">
              <div class="card-header">
                <div class="card-icon phishing">
                  <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                    <path
                      d="M8 1a2.5 2.5 0 0 1 2.5 2.5V4h-5v-.5A2.5 2.5 0 0 1 8 1zm3.5 3v-.5a3.5 3.5 0 1 0-7 0V4H1v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V4h-3.5zM2 5h12v9a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V5z"
                    />
                  </svg>
                </div>
                <h3>악성메일 모의훈련</h3>
                <span class="card-frequency">{{ selectedYear }}년 연 2회 실시</span>
              </div>
              <div class="card-stats">
                <div class="stat-row">
                  <span class="stat-label">실시 횟수</span>
                  <span class="stat-value">{{ trainingData.summary.conducted }}</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">통과</span>
                  <span class="stat-value success">{{ trainingData.summary.passed }}</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">실패</span>
                  <span class="stat-value danger">{{ trainingData.summary.failed }}</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">클릭/열람</span>
                  <span class="stat-value warning">{{
                    trainingData.summary.clicked_or_opened_count
                  }}</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">감점</span>
                  <span class="stat-value danger">-{{ trainingData.summary.penalty_score }}</span>
                </div>
              </div>
              <div class="card-progress">
                <div class="progress-bar">
                  <div
                    class="progress-fill phishing"
                    :style="{ width: `${trainingData.summary.pass_rate}%` }"
                    :class="getProgressClass(trainingData.summary.pass_rate)"
                  ></div>
                </div>
                <span class="progress-text">통과율 {{ trainingData.summary.pass_rate }}%</span>
              </div>

              <!-- 제외된 기록이 있을 경우 표시 -->
              <div v-if="trainingData.summary.excluded_count > 0" class="card-notice">
                <div class="notice-icon">ℹ️</div>
                <span>{{ trainingData.summary.excluded_count }}건 점수 제외</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 상반기/하반기별 상세 현황 -->
        <div class="section">
          <h2 class="section-title">상반기/하반기별 모의훈련 결과</h2>
          <div class="periods-grid">
            <div
              v-for="period in trainingData.period_status"
              :key="period.period"
              class="period-card"
              :class="getPeriodCardClass(period)"
            >
              <div class="period-header">
                <h3>{{ period.period_name }}</h3>
                <div class="status-badge" :class="getStatusBadgeClass(period.result)">
                  {{ getResultText(period.result) }}
                </div>
                <div v-if="period.exclude_from_scoring" class="excluded-badge">점수 제외</div>
              </div>

              <div class="period-details">
                <div class="detail-row">
                  <span class="label">메일 발송시각:</span>
                  <span class="value">{{ period.email_sent_time || '미발송' }}</span>
                </div>
                <div class="detail-row" v-if="period.action_time">
                  <span class="label">수행시간:</span>
                  <span class="value">{{ period.action_time }}</span>
                </div>
                <div class="detail-row" v-if="period.log_type">
                  <span class="label">로그유형:</span>
                  <span class="value danger-text">{{ period.log_type }}</span>
                </div>
                <div class="detail-row" v-if="period.mail_type">
                  <span class="label">메일유형:</span>
                  <span class="value">{{ period.mail_type }}</span>
                </div>
                <div class="detail-row" v-if="period.user_email">
                  <span class="label">이메일:</span>
                  <span class="value">{{ period.user_email }}</span>
                </div>
                <div class="detail-row" v-if="period.ip_address">
                  <span class="label">IP주소:</span>
                  <span class="value">{{ period.ip_address }}</span>
                </div>
                <div class="detail-row" v-if="period.response_time_minutes">
                  <span class="label">응답시간:</span>
                  <span class="value">{{ period.response_time_minutes }}분</span>
                </div>
                <div class="detail-row">
                  <span class="label">비고:</span>
                  <span class="value notes">{{ period.notes || '-' }}</span>
                </div>
              </div>

              <!-- 결과별 알림 -->
              <div v-if="period.result === 'fail'" class="result-notice fail">
                <div class="notice-icon">⚠️</div>
                <p>모의훈련에서 {{ period.log_type || '피싱 활동' }}을 했습니다.</p>
                <small v-if="!period.exclude_from_scoring">감점: -0.5점</small>
                <small v-else>점수 계산에서 제외됨</small>
              </div>

              <div v-else-if="period.result === 'pass'" class="result-notice pass">
                <div class="notice-icon">✅</div>
                <p>모의훈련을 성공적으로 통과했습니다.</p>
                <small v-if="period.response_time_minutes">
                  {{ period.response_time_minutes }}분 경과 후 액션 없음
                </small>
              </div>

              <div v-else="period.result === 'pending'" class="result-notice pending">
                <div class="notice-icon">⏳</div>
                <p>이 기간 모의훈련이 아직 실시되지 않았습니다.</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 훈련 안내 -->
        <div class="section">
          <h2 class="section-title">악성메일 모의훈련 안내</h2>
          <div class="info-grid">
            <div class="info-card">
              <div class="info-icon">📧</div>
              <h3>훈련 방식</h3>
              <ul>
                <li>상반기/하반기 각 1회 실시</li>
                <li>무작위 시점에 발송</li>
                <li>실제 업무메일과 유사한 형태</li>
                <li>클릭/열람 여부 및 시간 추적</li>
              </ul>
            </div>

            <div class="info-card">
              <div class="info-icon">🎯</div>
              <h3>평가 기준</h3>
              <ul>
                <li>피싱메일에 액션 없음: 통과</li>
                <li>첨부파일 열람/링크 클릭: 실패</li>
                <li>실패시 0.5점 감점</li>
              </ul>
            </div>

            <div class="info-card">
              <div class="info-icon">🛡️</div>
              <h3>대응 방법</h3>
              <ul>
                <li>의심스러운 메일은 즉시 신고</li>
                <li>첨부파일 다운로드 주의</li>
                <li>링크 클릭 전 URL 확인</li>
                <li>발신자 정보 검증</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

// Pinia Store
const authStore = useAuthStore()

// 반응형 데이터
const loading = ref(false)
const error = ref(null)
const trainingData = ref(null)
const selectedYear = ref(new Date().getFullYear())

// 계산된 속성
const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  return [currentYear - 1, currentYear, currentYear + 1]
})

// 메서드
const fetchTrainingStatus = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await fetch(`/api/phishing-training/status?year=${selectedYear.value}`, {
      credentials: 'include',
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: 데이터를 불러올 수 없습니다.`)
    }

    trainingData.value = await response.json()
  } catch (err) {
    console.error('모의훈련 현황 조회 실패:', err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const getProgressClass = (rate) => {
  if (rate >= 75) return 'excellent'
  if (rate >= 50) return 'good'
  if (rate >= 25) return 'warning'
  return 'poor'
}

const getPeriodCardClass = (period) => {
  if (period.exclude_from_scoring) return 'excluded'
  if (period.result === 'pass') return 'passed'
  if (period.result === 'fail') return 'failed'
  return 'pending'
}

const getStatusBadgeClass = (result) => {
  if (result === 'pass') return 'success'
  if (result === 'fail') return 'danger'
  return 'warning'
}

const getResultText = (result) => {
  const texts = {
    pass: '통과',
    fail: '실패',
    pending: '미실시',
  }
  return texts[result] || '알 수 없음'
}

// 라이프사이클 훅
onMounted(() => {
  if (authStore.user) {
    fetchTrainingStatus()
  }
})
</script>

<style scoped>
.training-page {
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

.year-selector {
  display: flex;
  align-items: center;
  gap: 10px;
}

.year-selector label {
  font-weight: 500;
  color: #374151;
}

.year-selector select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.loading-container,
.error-container {
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
}

/* 대시보드 카드 스타일 (security-audit와 통일) */
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

.dashboard-card.phishing-training {
  border-left: 4px solid #f59e0b;
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

.card-icon.phishing {
  background: linear-gradient(135deg, #f59e0b, #d97706);
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

.stat-value.warning {
  color: #f59e0b;
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

.progress-fill.phishing {
  background: linear-gradient(90deg, #f59e0b, #d97706);
}

.progress-fill.excellent {
  background: linear-gradient(90deg, #10b981, #059669);
}

.progress-fill.good {
  background: linear-gradient(90deg, #3b82f6, #1d4ed8);
}

.progress-fill.warning {
  background: linear-gradient(90deg, #f59e0b, #d97706);
}

.progress-fill.poor {
  background: linear-gradient(90deg, #ef4444, #dc2626);
}

.progress-text {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--dark-blue);
  min-width: 70px;
}

.card-notice {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 8px 12px;
  background-color: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #1e40af;
}

.notice-icon {
  font-size: 16px;
}

/* 기존 스타일들 유지 */
.periods-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.period-card {
  background-color: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
}

.period-card.passed {
  border-color: #10b981;
  background-color: #ecfdf5;
}

.period-card.failed {
  border-color: #ef4444;
  background-color: #fef2f2;
}

.period-card.pending {
  border-color: #f59e0b;
  background-color: #fffbeb;
}

.period-card.excluded {
  border-color: #6b7280;
  background-color: #f9fafb;
}

.period-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  flex-wrap: wrap;
  gap: 8px;
}

.period-header h3 {
  margin: 0;
  color: var(--dark-blue);
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.success {
  background-color: #10b981;
  color: white;
}

.status-badge.danger {
  background-color: #ef4444;
  color: white;
}

.status-badge.warning {
  background-color: #f59e0b;
  color: white;
}

.excluded-badge {
  padding: 4px 8px;
  background-color: #6b7280;
  color: white;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 600;
}

.period-details {
  margin-bottom: 15px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  flex-wrap: wrap;
  gap: 4px;
}

.detail-row .label {
  font-weight: 500;
  color: #6b7280;
  min-width: 120px;
}

.detail-row .value {
  color: #374151;
  flex: 1;
  text-align: right;
}

.detail-row .danger-text {
  color: #ef4444;
  font-weight: 600;
}

.detail-row .safe-text {
  color: #10b981;
  font-weight: 600;
}

.detail-row .notes {
  font-style: italic;
  color: #6b7280;
}

.result-notice {
  border-radius: 8px;
  padding: 12px;
  text-align: center;
}

.result-notice.pass {
  background-color: #d1fae5;
  border: 1px solid #10b981;
}

.result-notice.fail {
  background-color: #fee2e2;
  border: 1px solid #ef4444;
}

.result-notice.pending {
  background-color: #fef3c7;
  border: 1px solid #f59e0b;
}

.result-notice p {
  margin: 0 0 4px 0;
  font-weight: 500;
}

.result-notice.pass p {
  color: #065f46;
}

.result-notice.fail p {
  color: #991b1b;
}

.result-notice.pending p {
  color: #92400e;
}

.result-notice small {
  font-size: 12px;
  opacity: 0.8;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.info-card {
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
}

.info-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.info-card h3 {
  margin: 0 0 12px 0;
  color: var(--dark-blue);
}

.info-card ul {
  margin: 0;
  padding-left: 16px;
  color: #6b7280;
}

.info-card li {
  margin-bottom: 4px;
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
  .training-page {
    padding: 15px;
  }

  .page-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .periods-grid {
    grid-template-columns: 1fr;
  }

  .detail-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .detail-row .value {
    text-align: left;
  }
}

@media (max-width: 480px) {
  .training-page {
    padding: 15px;
  }

  .page-title {
    font-size: 24px;
  }

  .info-grid {
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
</style>
