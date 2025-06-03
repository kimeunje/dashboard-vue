<!-- views/SecurityScorePage.vue 템플릿 부분 -->
<template>
  <div class="score-page">
    <div class="page-header">
      <h1 class="page-title">종합 보안 점수</h1>
      <div class="year-selector">
        <label for="year">평가연도:</label>
        <select id="year" v-model="selectedYear" @change="fetchSecurityScore">
          <option v-for="year in availableYears" :key="year" :value="year">{{ year }}년</option>
        </select>
      </div>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>보안 점수를 계산하는 중...</p>
    </div>

    <!-- 에러 상태 -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">⚠️</div>
      <h3>점수 계산 실패</h3>
      <p>{{ error }}</p>
      <button @click="fetchSecurityScore" class="retry-button">다시 계산</button>
    </div>

    <!-- 보안 점수 데이터 -->
    <div v-else-if="scoreData" class="score-content">
      <!-- 종합 점수 카드 -->
      <div class="overall-score-card">
        <div class="score-circle">
          <div class="circle-chart" :class="getGradeClass(scoreData.grade)">
            <div class="circle-score">
              <span class="score-number">{{ scoreData.total_score }}</span>
              <span class="score-unit">점</span>
            </div>
            <div class="circle-grade">{{ scoreData.grade }}</div>
          </div>
        </div>
        <div class="score-summary">
          <h2>{{ selectedYear }}년 종합 보안 점수</h2>
          <p class="score-description">
            {{ getScoreDescription(scoreData.grade, scoreData.total_score) }}
          </p>
          <div class="score-details">
            <div class="detail-item">
              <span class="detail-label">상시감사 점수:</span>
              <span class="detail-value">{{ scoreData.audit_score }}점</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">교육 미이수 감점:</span>
              <span class="detail-value penalty">-{{ scoreData.education_penalty }}점</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">모의훈련 감점:</span>
              <span class="detail-value penalty">-{{ scoreData.training_penalty }}점</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 점수 구성 요소 -->
      <div class="score-breakdown">
        <h2>점수 구성 요소</h2>
        <div class="breakdown-grid">
          <!-- 정보보안 감사 -->
          <div class="breakdown-card audit">
            <div class="card-header">
              <div class="card-icon">🛡️</div>
              <h3>정보보안 감사 현황</h3>
            </div>
            <div class="card-content">
              <div class="main-score">{{ scoreData.audit_score }}점</div>
              <div class="score-detail">
                <p>
                  통과 항목: {{ scoreData.details.passed_audit_items }}/{{
                    scoreData.details.total_audit_items
                  }}
                </p>
                <p>통과율: {{ scoreData.details.audit_pass_rate }}%</p>
              </div>
              <div class="progress-bar">
                <div
                  class="progress-fill audit-progress"
                  :style="{ width: `${scoreData.details.audit_pass_rate}%` }"
                ></div>
              </div>
            </div>
            <div class="card-footer">
              <RouterLink to="/security-audit/results" class="detail-link">
                상세 보기 →
              </RouterLink>
            </div>
          </div>

          <!-- 정보보호교육 -->
          <div class="breakdown-card education">
            <div class="card-header">
              <div class="card-icon">📚</div>
              <h3>정보보호교육</h3>
            </div>
            <div class="card-content">
              <div class="main-score penalty">-{{ scoreData.education_penalty }}점</div>
              <div class="score-detail">
                <p>미이수 횟수: {{ scoreData.education_incomplete }}회</p>
                <p>
                  연간 이수율: {{ Math.round(((4 - scoreData.education_incomplete) / 4) * 100) }}%
                </p>
              </div>
              <div class="penalty-info">
                <small>분기당 0.5점 감점</small>
              </div>
            </div>
            <div class="card-footer">
              <RouterLink to="/security-education" class="detail-link"> 상세 보기 → </RouterLink>
            </div>
          </div>

          <!-- 악성메일 모의훈련 -->
          <div class="breakdown-card training">
            <div class="card-header">
              <div class="card-icon">📧</div>
              <h3>악성메일 모의훈련</h3>
            </div>
            <div class="card-content">
              <div class="main-score penalty">-{{ scoreData.training_penalty }}점</div>
              <div class="score-detail">
                <p>실패 횟수: {{ scoreData.training_failed }}회</p>
                <p>연간 통과율: {{ Math.round(((4 - scoreData.training_failed) / 4) * 100) }}%</p>
              </div>
              <div class="penalty-info">
                <small>실패시 0.5점 감점</small>
              </div>
            </div>
            <div class="card-footer">
              <RouterLink to="/phishing-training" class="detail-link"> 상세 보기 → </RouterLink>
            </div>
          </div>
        </div>
      </div>

      <!-- 등급별 기준 -->
      <div class="grade-criteria">
        <h2>등급 평가 기준</h2>
        <div class="criteria-grid">
          <div class="criteria-item grade-a-plus">
            <div class="grade-label">A+</div>
            <div class="grade-range">95점 이상</div>
            <div class="grade-desc">최우수</div>
          </div>
          <div class="criteria-item grade-a">
            <div class="grade-label">A</div>
            <div class="grade-range">90-94점</div>
            <div class="grade-desc">우수</div>
          </div>
          <div class="criteria-item grade-b-plus">
            <div class="grade-label">B+</div>
            <div class="grade-range">85-89점</div>
            <div class="grade-desc">양호</div>
          </div>
          <div class="criteria-item grade-b">
            <div class="grade-label">B</div>
            <div class="grade-range">80-84점</div>
            <div class="grade-desc">보통</div>
          </div>
          <div class="criteria-item grade-c-plus">
            <div class="grade-label">C+</div>
            <div class="grade-range">75-79점</div>
            <div class="grade-desc">미흡</div>
          </div>
          <div class="criteria-item grade-c">
            <div class="grade-label">C</div>
            <div class="grade-range">70-74점</div>
            <div class="grade-desc">부족</div>
          </div>
          <div class="criteria-item grade-d">
            <div class="grade-label">D</div>
            <div class="grade-range">60-69점</div>
            <div class="grade-desc">불량</div>
          </div>
          <div class="criteria-item grade-f">
            <div class="grade-label">F</div>
            <div class="grade-range">60점 미만</div>
            <div class="grade-desc">매우불량</div>
          </div>
        </div>
      </div>

      <!-- 개선 권장사항 -->
      <div v-if="recommendations.length > 0" class="recommendations">
        <h2>개선 권장사항</h2>
        <div class="recommendations-list">
          <div
            v-for="(rec, index) in recommendations"
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
      </div>

      <!-- 연도별 점수 추이 -->
      <div class="score-trend">
        <h2>연도별 점수 추이</h2>
        <div class="trend-chart">
          <div class="chart-placeholder">
            <p>점수 추이 차트가 여기에 표시됩니다.</p>
            <small>* 향후 업데이트 예정</small>
          </div>
        </div>
      </div>

      <!-- 액션 버튼 -->
      <div class="action-section">
        <div class="action-buttons">
          <button @click="downloadReport" class="primary-button">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"
              />
              <path
                d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"
              />
            </svg>
            평가 보고서 다운로드
          </button>

          <button @click="requestImprovement" class="secondary-button">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M3 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1H3zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"
              />
            </svg>
            개선 컨설팅 요청
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { RouterLink } from 'vue-router'

// Pinia Store
const authStore = useAuthStore()

// 반응형 데이터
const loading = ref(false)
const error = ref(null)
const scoreData = ref(null)
const recommendations = ref([])
const selectedYear = ref(new Date().getFullYear())

// 계산된 속성
const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  return [currentYear - 1, currentYear, currentYear + 1]
})

// 메서드
const fetchSecurityScore = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await fetch(`/api/security-score/summary?year=${selectedYear.value}`, {
      credentials: 'include',
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: 데이터를 불러올 수 없습니다.`)
    }

    const data = await response.json()
    scoreData.value = data

    // 권장사항 가져오기
    await fetchRecommendations()
  } catch (err) {
    console.error('보안 점수 조회 실패:', err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const fetchRecommendations = async () => {
  try {
    const response = await fetch(`/api/security-dashboard/overview?year=${selectedYear.value}`, {
      credentials: 'include',
    })

    if (response.ok) {
      const data = await response.json()
      recommendations.value = data.recommendations || []
    }
  } catch (err) {
    console.error('권장사항 조회 실패:', err)
  }
}

const getGradeClass = (grade) => {
  const gradeClasses = {
    'A+': 'grade-a-plus',
    A: 'grade-a',
    'B+': 'grade-b-plus',
    B: 'grade-b',
    'C+': 'grade-c-plus',
    C: 'grade-c',
    D: 'grade-d',
    F: 'grade-f',
  }
  return gradeClasses[grade] || 'grade-f'
}

const getScoreDescription = (grade, score) => {
  if (score >= 95) {
    return '탁월한 보안 관리 상태입니다. 현재 수준을 유지해주세요.'
  } else if (score >= 90) {
    return '우수한 보안 의식을 보유하고 있습니다.'
  } else if (score >= 80) {
    return '양호한 상태이나 일부 개선이 필요합니다.'
  } else if (score >= 70) {
    return '보안 의식 향상이 필요합니다.'
  } else {
    return '즉시 보안 교육 및 개선 조치가 필요합니다.'
  }
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

const downloadReport = () => {
  // 평가 보고서 다운로드 기능
  alert('평가 보고서 다운로드 기능이 준비중입니다.')
}

const requestImprovement = () => {
  // 개선 컨설팅 요청 기능
  alert('개선 컨설팅 요청이 접수되었습니다. IT 보안팀에서 연락드리겠습니다.')
}

// 라이프사이클 훅
onMounted(() => {
  if (authStore.user) {
    fetchSecurityScore()
  }
})
</script>

/* SecurityScorePage.vue 스타일 */
<style scoped>
.score-page {
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

.overall-score-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 20px;
  padding: 40px;
  margin-bottom: 40px;
  display: flex;
  align-items: center;
  gap: 40px;
}

.score-circle {
  flex-shrink: 0;
}

.circle-chart {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  border: 8px solid rgba(255, 255, 255, 0.3);
}

.circle-chart.grade-a-plus,
.circle-chart.grade-a {
  border-color: #10b981;
  background: linear-gradient(135deg, #10b981, #059669);
}

.circle-chart.grade-b-plus,
.circle-chart.grade-b {
  border-color: #3b82f6;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}

.circle-chart.grade-c-plus,
.circle-chart.grade-c {
  border-color: #f59e0b;
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.circle-chart.grade-d,
.circle-chart.grade-f {
  border-color: #ef4444;
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.circle-score {
  text-align: center;
}

.score-number {
  font-size: 48px;
  font-weight: 700;
  display: block;
  line-height: 1;
}

.score-unit {
  font-size: 16px;
  opacity: 0.9;
}

.circle-grade {
  font-size: 24px;
  font-weight: 700;
  margin-top: 8px;
}

.score-summary {
  flex: 1;
}

.score-summary h2 {
  margin: 0 0 16px 0;
  font-size: 32px;
  font-weight: 700;
}

.score-description {
  font-size: 18px;
  margin: 0 0 24px 0;
  opacity: 0.9;
  line-height: 1.5;
}

.score-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.detail-label {
  font-size: 16px;
  opacity: 0.9;
}

.detail-value {
  font-size: 16px;
  font-weight: 600;
}

.detail-value.penalty {
  color: #fecaca;
}

.score-breakdown {
  margin-bottom: 40px;
}

.score-breakdown h2 {
  margin-bottom: 24px;
  color: var(--dark-blue);
  font-size: 24px;
}

.breakdown-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.breakdown-card {
  background-color: white;
  border-radius: 12px;
  border: 2px solid #e5e7eb;
  overflow: hidden;
  transition: all 0.3s ease;
}

.breakdown-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.breakdown-card.audit {
  border-top-color: #3b82f6;
}

.breakdown-card.education {
  border-top-color: #10b981;
}

.breakdown-card.training {
  border-top-color: #f59e0b;
}

.card-header {
  padding: 20px 20px 0 20px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.card-icon {
  font-size: 24px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background-color: #f3f4f6;
}

.card-header h3 {
  margin: 0;
  color: var(--dark-blue);
  font-size: 18px;
}

.card-content {
  padding: 16px 20px;
}

.main-score {
  font-size: 32px;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 12px;
}

.main-score.penalty {
  color: #ef4444;
}

.score-detail p {
  margin: 4px 0;
  color: #6b7280;
  font-size: 14px;
}

.progress-bar {
  height: 8px;
  background-color: #f3f4f6;
  border-radius: 4px;
  overflow: hidden;
  margin-top: 12px;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.audit-progress {
  background-color: #3b82f6;
}

.penalty-info {
  margin-top: 8px;
}

.penalty-info small {
  color: #ef4444;
  font-style: italic;
}

.card-footer {
  padding: 0 20px 20px 20px;
}

.detail-link {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
  font-size: 14px;
}

.detail-link:hover {
  text-decoration: underline;
}

.grade-criteria {
  margin-bottom: 40px;
}

.grade-criteria h2 {
  margin-bottom: 20px;
  color: var(--dark-blue);
  font-size: 24px;
}

.criteria-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
}

.criteria-item {
  background-color: white;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
  transition: all 0.3s ease;
}

.criteria-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.criteria-item.grade-a-plus,
.criteria-item.grade-a {
  border-color: #10b981;
  background-color: #ecfdf5;
}

.criteria-item.grade-b-plus,
.criteria-item.grade-b {
  border-color: #3b82f6;
  background-color: #eff6ff;
}

.criteria-item.grade-c-plus,
.criteria-item.grade-c {
  border-color: #f59e0b;
  background-color: #fffbeb;
}

.criteria-item.grade-d,
.criteria-item.grade-f {
  border-color: #ef4444;
  background-color: #fef2f2;
}

.grade-label {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 4px;
  color: var(--dark-blue);
}

.grade-range {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 4px;
}

.grade-desc {
  font-size: 12px;
  color: #9ca3af;
}

.recommendations {
  margin-bottom: 40px;
}

.recommendations h2 {
  margin-bottom: 20px;
  color: var(--dark-blue);
  font-size: 24px;
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.recommendation-card {
  background-color: white;
  border: 1px solid #e5e7eb;
  border-left: 4px solid #6b7280;
  border-radius: 8px;
  padding: 20px;
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
  gap: 12px;
  margin-bottom: 12px;
}

.priority-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
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
  color: var(--dark-blue);
  font-size: 16px;
}

.recommendation-card p {
  margin: 0 0 16px 0;
  color: #6b7280;
  line-height: 1.5;
}

.recommendation-action {
  text-align: right;
}

.action-button {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
  font-size: 14px;
}

.action-button:hover {
  text-decoration: underline;
}

.score-trend {
  margin-bottom: 40px;
}

.score-trend h2 {
  margin-bottom: 20px;
  color: var(--dark-blue);
  font-size: 24px;
}

.trend-chart {
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 40px;
}

.chart-placeholder {
  text-align: center;
  color: #6b7280;
  padding: 40px;
}

.chart-placeholder p {
  margin: 0 0 8px 0;
  font-size: 16px;
}

.action-section {
  text-align: center;
  padding: 40px 0;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

.primary-button,
.secondary-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  font-size: 16px;
}

.primary-button {
  background-color: var(--primary-color);
  color: white;
}

.primary-button:hover {
  background-color: var(--dark-blue);
  transform: translateY(-2px);
}

.secondary-button {
  background-color: white;
  color: var(--primary-color);
  border: 2px solid var(--primary-color);
}

.secondary-button:hover {
  background-color: var(--primary-color);
  color: white;
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

  .overall-score-card {
    flex-direction: column;
    text-align: center;
    gap: 20px;
    padding: 30px 20px;
  }

  .score-summary h2 {
    font-size: 24px;
  }

  .score-description {
    font-size: 16px;
  }

  .circle-chart {
    width: 150px;
    height: 150px;
  }

  .score-number {
    font-size: 36px;
  }

  .circle-grade {
    font-size: 20px;
  }

  .breakdown-grid {
    grid-template-columns: 1fr;
  }

  .criteria-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
  }

  .criteria-item {
    padding: 12px 8px;
  }

  .grade-label {
    font-size: 20px;
  }

  .action-buttons {
    flex-direction: column;
  }
}

@media (max-width: 480px) {
  .criteria-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .detail-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
}
</style>
