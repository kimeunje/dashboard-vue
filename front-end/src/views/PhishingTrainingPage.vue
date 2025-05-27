<!-- views/PhishingTrainingPage.vue -->
<template>
  <div class="training-page">
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
      <!-- 요약 카드 -->
      <div class="summary-card">
        <h2>{{ selectedYear }}년 모의훈련 결과</h2>
        <div class="summary-stats">
          <div class="stat-item">
            <div class="stat-value conducted">{{ trainingData.summary.conducted }}</div>
            <div class="stat-label">실시횟수</div>
          </div>
          <div class="stat-item">
            <div class="stat-value passed">{{ trainingData.summary.passed }}</div>
            <div class="stat-label">통과</div>
          </div>
          <div class="stat-item">
            <div class="stat-value failed">{{ trainingData.summary.failed }}</div>
            <div class="stat-label">실패</div>
          </div>
          <div class="stat-item">
            <div class="stat-value clicked">{{ trainingData.summary.clicked_phishing_count }}</div>
            <div class="stat-label">피싱클릭</div>
          </div>
          <div class="stat-item">
            <div class="stat-value rate">{{ trainingData.summary.pass_rate }}%</div>
            <div class="stat-label">통과율</div>
          </div>
          <div class="stat-item">
            <div class="stat-value penalty">-{{ trainingData.summary.penalty_score }}</div>
            <div class="stat-label">감점</div>
          </div>
        </div>

        <!-- 진행률 바 -->
        <div class="progress-container">
          <div class="progress-label">전체 통과율</div>
          <div class="progress-bar">
            <div
              class="progress-fill"
              :style="{ width: `${trainingData.summary.pass_rate}%` }"
              :class="getProgressClass(trainingData.summary.pass_rate)"
            ></div>
          </div>
          <div class="progress-text">{{ trainingData.summary.pass_rate }}%</div>
        </div>
      </div>

      <!-- 분기별 상세 현황 -->
      <div class="quarterly-section">
        <h2>분기별 모의훈련 결과</h2>
        <div class="quarters-grid">
          <div
            v-for="quarter in trainingData.quarterly_status"
            :key="quarter.quarter"
            class="quarter-card"
            :class="getQuarterCardClass(quarter)"
          >
            <div class="quarter-header">
              <h3>{{ quarter.quarter }}분기</h3>
              <div class="status-badge" :class="getStatusBadgeClass(quarter.result)">
                {{ getResultText(quarter.result) }}
              </div>
            </div>

            <div class="quarter-details">
              <div class="detail-row">
                <span class="label">훈련일:</span>
                <span class="value">{{ quarter.training_date || '미실시' }}</span>
              </div>
              <div class="detail-row">
                <span class="label">피싱메일 클릭:</span>
                <span class="value" :class="quarter.clicked_phishing ? 'danger-text' : 'safe-text'">
                  {{
                    quarter.clicked_phishing === null
                      ? '-'
                      : quarter.clicked_phishing
                        ? '예'
                        : '아니오'
                  }}
                </span>
              </div>
              <div class="detail-row" v-if="quarter.response_time">
                <span class="label">신고시간:</span>
                <span class="value">{{ quarter.response_time }}분</span>
              </div>
              <div class="detail-row">
                <span class="label">점수:</span>
                <span class="value">{{ quarter.score ? `${quarter.score}점` : '-' }}</span>
              </div>
              <div class="detail-row">
                <span class="label">비고:</span>
                <span class="value notes">{{ quarter.notes || '-' }}</span>
              </div>
            </div>

            <!-- 결과별 알림 -->
            <div v-if="quarter.result === 'fail'" class="result-notice fail">
              <div class="notice-icon">⚠️</div>
              <p>모의훈련에서 피싱메일을 클릭했습니다.</p>
              <small>감점: -0.5점</small>
            </div>

            <div v-else-if="quarter.result === 'pass'" class="result-notice pass">
              <div class="notice-icon">✅</div>
              <p>모의훈련을 성공적으로 통과했습니다.</p>
              <small v-if="quarter.response_time">{{ quarter.response_time }}분 만에 신고</small>
            </div>

            <div v-else="quarter.result === 'pending'" class="result-notice pending">
              <div class="notice-icon">⏳</div>
              <p>이 분기 모의훈련이 아직 실시되지 않았습니다.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 훈련 안내 -->
      <div class="training-info">
        <h2>악성메일 모의훈련 안내</h2>
        <div class="info-grid">
          <div class="info-card">
            <div class="info-icon">📧</div>
            <h3>훈련 방식</h3>
            <ul>
              <li>분기별 1회 실시</li>
              <li>무작위 시점에 발송</li>
              <li>실제 업무메일과 유사한 형태</li>
              <li>클릭 여부 및 신고 여부 추적</li>
            </ul>
          </div>

          <div class="info-card">
            <div class="info-icon">🎯</div>
            <h3>평가 기준</h3>
            <ul>
              <li>피싱메일 미클릭: 통과</li>
              <li>빠른 신고: 가산점</li>
              <li>피싱메일 클릭: 실패</li>
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

      <!-- 훈련 통계 차트 -->
      <div class="chart-section">
        <h2>연간 훈련 성과 추이</h2>
        <div class="chart-container">
          <div class="chart-placeholder">
            <div class="quarter-chart">
              <div
                v-for="quarter in trainingData.quarterly_status"
                :key="quarter.quarter"
                class="chart-bar"
              >
                <div
                  class="bar-fill"
                  :class="
                    quarter.passed ? 'success' : quarter.result === 'fail' ? 'danger' : 'pending'
                  "
                  :style="{ height: `${getChartBarHeight(quarter)}%` }"
                ></div>
                <div class="bar-label">{{ quarter.quarter }}Q</div>
              </div>
            </div>
            <div class="chart-legend">
              <div class="legend-item">
                <div class="legend-color success"></div>
                <span>통과</span>
              </div>
              <div class="legend-item">
                <div class="legend-color danger"></div>
                <span>실패</span>
              </div>
              <div class="legend-item">
                <div class="legend-color pending"></div>
                <span>미실시</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 추가 리소스 -->
      <div class="resources-section">
        <h2>보안 의식 향상 자료</h2>
        <div class="resources-grid">
          <div class="resource-card">
            <div class="resource-icon">📖</div>
            <h3>피싱메일 식별 가이드</h3>
            <p>악성메일의 특징과 식별 방법을 학습하세요.</p>
            <button class="resource-button">가이드 보기</button>
          </div>

          <div class="resource-card">
            <div class="resource-icon">🎓</div>
            <h3>보안 교육 자료</h3>
            <p>정보보안 관련 교육 자료와 동영상을 확인하세요.</p>
            <button class="resource-button">교육 자료</button>
          </div>

          <div class="resource-card">
            <div class="resource-icon">📞</div>
            <h3>신고 및 문의</h3>
            <p>의심스러운 메일 발견시 즉시 신고해주세요.</p>
            <button class="resource-button">신고하기</button>
          </div>
        </div>
      </div>
    </div>
  </div>
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

const getQuarterCardClass = (quarter) => {
  if (quarter.result === 'pass') return 'passed'
  if (quarter.result === 'fail') return 'failed'
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

const getChartBarHeight = (quarter) => {
  if (quarter.result === 'pass') return 100
  if (quarter.result === 'fail') return 30
  return 10
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
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
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

.summary-card {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 30px;
}

.summary-card h2 {
  margin: 0 0 20px 0;
  font-size: 24px;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
  display: block;
}

.stat-value.passed {
  color: #10b981;
}

.stat-value.failed {
  color: #ef4444;
}

.stat-value.clicked {
  color: #f59e0b;
}

.stat-value.penalty {
  color: #dc2626;
}

.stat-label {
  font-size: 12px;
  opacity: 0.9;
}

.progress-container {
  display: flex;
  align-items: center;
  gap: 15px;
}

.progress-label {
  min-width: 80px;
  font-weight: 500;
}

.progress-bar {
  flex: 1;
  height: 12px;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  transition: width 0.3s ease;
  border-radius: 6px;
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

.progress-text {
  min-width: 50px;
  font-weight: 600;
}

.quarterly-section {
  margin-bottom: 40px;
}

.quarterly-section h2 {
  margin-bottom: 20px;
  color: var(--dark-blue);
}

.quarters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.quarter-card {
  background-color: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
}

.quarter-card.passed {
  border-color: #10b981;
  background-color: #ecfdf5;
}

.quarter-card.failed {
  border-color: #ef4444;
  background-color: #fef2f2;
}

.quarter-card.pending {
  border-color: #f59e0b;
  background-color: #fffbeb;
}

.quarter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.quarter-header h3 {
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

.quarter-details {
  margin-bottom: 15px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.detail-row .label {
  font-weight: 500;
  color: #6b7280;
}

.detail-row .value {
  color: #374151;
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

.notice-icon {
  font-size: 24px;
  margin-bottom: 8px;
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

.training-info {
  margin-bottom: 40px;
}

.training-info h2 {
  margin-bottom: 20px;
  color: var(--dark-blue);
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

.chart-section {
  margin-bottom: 40px;
}

.chart-section h2 {
  margin-bottom: 20px;
  color: var(--dark-blue);
}

.chart-container {
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
}

.quarter-chart {
  display: flex;
  align-items: end;
  justify-content: space-around;
  height: 200px;
  margin-bottom: 20px;
}

.chart-bar {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 60px;
}

.bar-fill {
  width: 40px;
  transition: height 0.3s ease;
  border-radius: 4px 4px 0 0;
  margin-bottom: 10px;
}

.bar-fill.success {
  background-color: #10b981;
}

.bar-fill.danger {
  background-color: #ef4444;
}

.bar-fill.pending {
  background-color: #f59e0b;
}

.bar-label {
  font-size: 14px;
  font-weight: 500;
  color: #6b7280;
}

.chart-legend {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.legend-color.success {
  background-color: #10b981;
}

.legend-color.danger {
  background-color: #ef4444;
}

.legend-color.pending {
  background-color: #f59e0b;
}

.resources-section {
  margin-bottom: 30px;
}

.resources-section h2 {
  margin-bottom: 20px;
  color: var(--dark-blue);
}

.resources-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.resource-card {
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
}

.resource-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.resource-card h3 {
  margin: 0 0 8px 0;
  color: var(--dark-blue);
}

.resource-card p {
  margin: 0 0 16px 0;
  color: #6b7280;
  font-size: 14px;
}

.resource-button {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
}

.resource-button:hover {
  background-color: var(--dark-blue);
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
  .page-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }

  .summary-stats {
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
  }

  .stat-value {
    font-size: 24px;
  }

  .progress-container {
    flex-direction: column;
    gap: 10px;
  }
}
</style>
