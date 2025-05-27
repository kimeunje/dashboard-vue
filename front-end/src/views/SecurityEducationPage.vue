<!-- views/SecurityEducationPage.vue -->
<template>
  <div class="education-page">
    <div class="page-header">
      <h1 class="page-title">정보보호 교육 현황</h1>
      <div class="year-selector">
        <label for="year">연도:</label>
        <select id="year" v-model="selectedYear" @change="fetchEducationStatus">
          <option v-for="year in availableYears" :key="year" :value="year">{{ year }}년</option>
        </select>
      </div>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>교육 현황을 불러오는 중...</p>
    </div>

    <!-- 에러 상태 -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">⚠️</div>
      <h3>데이터 로드 실패</h3>
      <p>{{ error }}</p>
      <button @click="fetchEducationStatus" class="retry-button">다시 시도</button>
    </div>

    <!-- 교육 현황 데이터 -->
    <div v-else-if="educationData" class="education-content">
      <!-- 요약 카드 -->
      <div class="summary-card">
        <h2>{{ selectedYear }}년 교육 이수 현황</h2>
        <div class="summary-stats">
          <div class="stat-item">
            <div class="stat-value completed">{{ educationData.summary.completed }}</div>
            <div class="stat-label">이수 완료</div>
          </div>
          <div class="stat-item">
            <div class="stat-value incomplete">{{ educationData.summary.incomplete }}</div>
            <div class="stat-label">미이수</div>
          </div>
          <div class="stat-item">
            <div class="stat-value rate">{{ educationData.summary.completion_rate }}%</div>
            <div class="stat-label">이수율</div>
          </div>
          <div class="stat-item">
            <div class="stat-value penalty">-{{ educationData.summary.penalty_score }}</div>
            <div class="stat-label">감점</div>
          </div>
        </div>

        <!-- 진행률 바 -->
        <div class="progress-container">
          <div class="progress-label">전체 이수율</div>
          <div class="progress-bar">
            <div
              class="progress-fill"
              :style="{ width: `${educationData.summary.completion_rate}%` }"
              :class="getProgressClass(educationData.summary.completion_rate)"
            ></div>
          </div>
          <div class="progress-text">{{ educationData.summary.completion_rate }}%</div>
        </div>
      </div>

      <!-- 분기별 상세 현황 -->
      <div class="quarterly-section">
        <h2>분기별 교육 현황</h2>
        <div class="quarters-grid">
          <div
            v-for="quarter in educationData.quarterly_status"
            :key="quarter.quarter"
            class="quarter-card"
            :class="{ completed: quarter.completed, incomplete: !quarter.completed }"
          >
            <div class="quarter-header">
              <h3>{{ quarter.quarter }}분기</h3>
              <div class="status-badge" :class="quarter.completed ? 'success' : 'danger'">
                {{ quarter.completed ? '이수완료' : '미이수' }}
              </div>
            </div>

            <div class="quarter-details">
              <div class="detail-row">
                <span class="label">교육일:</span>
                <span class="value">{{ quarter.education_date || '미이수' }}</span>
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

            <!-- 미이수인 경우 알림 -->
            <div v-if="!quarter.completed" class="incomplete-notice">
              <div class="notice-icon">📚</div>
              <p>이 분기 교육을 아직 이수하지 않았습니다.</p>
              <small>감점: -0.5점</small>
            </div>
          </div>
        </div>
      </div>

      <!-- 교육 안내 -->
      <div class="education-info">
        <h2>정보보호 교육 안내</h2>
        <div class="info-grid">
          <div class="info-card">
            <div class="info-icon">📖</div>
            <h3>교육 일정</h3>
            <ul>
              <li>1분기: 1월 ~ 3월</li>
              <li>2분기: 4월 ~ 6월</li>
              <li>3분기: 7월 ~ 9월</li>
              <li>4분기: 10월 ~ 12월</li>
            </ul>
          </div>

          <div class="info-card">
            <div class="info-icon">⚠️</div>
            <h3>미이수시 패널티</h3>
            <ul>
              <li>분기당 0.5점 감점</li>
              <li>연간 최대 2점 감점</li>
              <li>평가 등급에 반영</li>
            </ul>
          </div>

          <div class="info-card">
            <div class="info-icon">🎯</div>
            <h3>교육 신청 방법</h3>
            <ul>
              <li>사내 교육 시스템 접속</li>
              <li>분기별 교육 과정 선택</li>
              <li>온라인 수강 완료</li>
              <li>수료증 발급</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- 액션 버튼 -->
      <div class="action-section">
        <div class="action-buttons">
          <button @click="openEducationSystem" class="primary-button">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M8.5 2.687c.654-.689 1.782-.886 3.112-.752 1.234.124 2.503.523 3.388.893v9.923c-.918-.35-2.107-.692-3.287-.81-1.094-.111-2.278-.039-3.213.492V2.687zM8 1.783C7.015.936 5.587.81 4.287.94c-1.514.153-3.042.672-3.994 1.105A.5.5 0 0 0 0 2.5v11a.5.5 0 0 0 .707.455c.882-.4 2.303-.881 3.68-1.02 1.409-.142 2.59.087 3.223.877a.5.5 0 0 0 .78 0c.633-.79 1.814-1.019 3.222-.877 1.378.139 2.8.62 3.681 1.02A.5.5 0 0 0 16 13.5v-11a.5.5 0 0 0-.293-.455c-.952-.433-2.48-.952-3.994-1.105C10.413.809 8.985.936 8 1.783z"
              />
            </svg>
            교육 시스템 바로가기
          </button>

          <button
            @click="downloadCertificate"
            class="secondary-button"
            :disabled="!hasCompletedEducation"
          >
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"
              />
              <path
                d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"
              />
            </svg>
            수료증 다운로드
          </button>
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
const educationData = ref(null)
const selectedYear = ref(new Date().getFullYear())

// 계산된 속성
const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  return [currentYear - 1, currentYear, currentYear + 1]
})

const hasCompletedEducation = computed(() => {
  if (!educationData.value) return false
  return educationData.value.summary.completed > 0
})

// 메서드
const fetchEducationStatus = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await fetch(`/api/security-education/status?year=${selectedYear.value}`, {
      credentials: 'include',
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: 데이터를 불러올 수 없습니다.`)
    }

    educationData.value = await response.json()
  } catch (err) {
    console.error('교육 현황 조회 실패:', err)
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

const openEducationSystem = () => {
  // 실제 교육 시스템 URL로 이동
  window.open('https://education.company.com', '_blank')
}

const downloadCertificate = () => {
  // 수료증 다운로드 기능
  alert('수료증 다운로드 기능이 준비중입니다.')
}

// 라이프사이클 훅
onMounted(() => {
  if (authStore.user) {
    fetchEducationStatus()
  }
})
</script>

<style scoped>
.education-page {
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
  display: block;
}

.stat-value.completed {
  color: #10b981;
}

.stat-value.incomplete {
  color: #f59e0b;
}

.stat-value.penalty {
  color: #ef4444;
}

.stat-label {
  font-size: 14px;
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

.quarter-card.completed {
  border-color: #10b981;
  background-color: #ecfdf5;
}

.quarter-card.incomplete {
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

.detail-row .notes {
  font-style: italic;
  color: #6b7280;
}

.incomplete-notice {
  background-color: #fef3c7;
  border: 1px solid #f59e0b;
  border-radius: 8px;
  padding: 12px;
  text-align: center;
}

.notice-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.incomplete-notice p {
  margin: 0 0 4px 0;
  font-weight: 500;
  color: #92400e;
}

.incomplete-notice small {
  color: #b45309;
}

.education-info {
  margin-bottom: 30px;
}

.education-info h2 {
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

.action-section {
  text-align: center;
  padding: 30px 0;
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

.secondary-button:hover:not(:disabled) {
  background-color: var(--primary-color);
  color: white;
}

.secondary-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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
    grid-template-columns: repeat(2, 1fr);
  }

  .progress-container {
    flex-direction: column;
    gap: 10px;
  }

  .action-buttons {
    flex-direction: column;
  }
}
</style>
