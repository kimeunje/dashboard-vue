<!-- views/SecurityEducationPage.vue -->
<template>
  <main class="">
    <div class="education-page">
      <!-- 연도 선택기 -->
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
        <!-- 교육 상태 대시보드 -->
        <div class="section">
          <!-- <h2 class="section-title">교육 상태 대시보드</h2> -->
          <div class="dashboard-grid">
            <!-- 정보보호 교육 카드 -->
            <div class="dashboard-card education-check">
              <div class="card-header">
                <div class="card-icon education">
                  <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                    <path
                      d="M8.211 2.047a.5.5 0 0 0-.422 0l-7.5 3.5a.5.5 0 0 0 .025.917l7.5 3a.5.5 0 0 0 .372 0L14.5 7.14V13a1 1 0 0 0-1 1v2h3v-2a1 1 0 0 0-1-1V6.739l.686-.275a.5.5 0 0 0 .025-.917l-7.5-3.5ZM8 8.46 1.758 5.965 8 3.052l6.242 2.913L8 8.46Z"
                    />
                    <path
                      d="M4.176 9.032a.5.5 0 0 0-.656.327l-.5 1.7a.5.5 0 0 0 .294.605l4.5 1.8a.5.5 0 0 0 .372 0l4.5-1.8a.5.5 0 0 0 .294-.605l-.5-1.7a.5.5 0 0 0-.656-.327L8 10.466 4.176 9.032Z"
                    />
                  </svg>
                </div>
                <h3>정보보호 교육</h3>
                <span class="card-frequency">{{ selectedYear }}년 온/오프라인 교육</span>
              </div>
              <div class="card-stats">
                <div class="stat-row">
                  <span class="stat-label">총 과정수</span>
                  <span class="stat-value">{{ educationData.summary.total_courses }}</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">이수완료</span>
                  <span class="stat-value success">{{ educationData.summary.completed }}</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">미이수</span>
                  <span class="stat-value danger">{{ educationData.summary.incomplete }}</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">미실시</span>
                  <span class="stat-value warning">{{ educationData.summary.not_started }}</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">감점</span>
                  <span class="stat-value danger">-{{ educationData.summary.penalty_score }}</span>
                </div>
              </div>
              <div class="card-progress">
                <div class="progress-bar">
                  <div
                    class="progress-fill education"
                    :style="{ width: `${educationData.summary.completion_rate}%` }"
                    :class="getProgressClass(educationData.summary.completion_rate)"
                  ></div>
                </div>
                <span class="progress-text"
                  >이수율 {{ educationData.summary.completion_rate }}%</span
                >
              </div>

              <!-- 제외된 기록이 있을 경우 표시 -->
              <div v-if="educationData.summary.excluded_count > 0" class="card-notice">
                <div class="notice-icon">ℹ️</div>
                <span>{{ educationData.summary.excluded_count }}건 점수 제외</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 온라인/오프라인별 상세 현황 -->
        <div class="section">
          <h2 class="section-title">온라인/오프라인별 교육 현황</h2>
          <div class="periods-grid">
            <div
              v-for="education in educationData.education_status"
              :key="education.type"
              class="period-card"
              :class="getPeriodCardClass(education)"
            >
              <div class="period-header">
                <h3>{{ education.type_name }} 교육</h3>
                <div class="status-badge" :class="getStatusBadgeClass(education.status)">
                  {{ getStatusText(education.status) }}
                </div>
                <div v-if="education.exclude_from_scoring" class="excluded-badge">점수 제외</div>
              </div>

              <div class="period-details">
                <div class="detail-row">
                  <span class="label">총 과정수:</span>
                  <span class="value">{{ education.total_courses }}개</span>
                </div>
                <div class="detail-row">
                  <span class="label">수료 과정:</span>
                  <span class="value">{{ education.completed_courses }}개</span>
                </div>
                <div class="detail-row">
                  <span class="label">미수료 과정:</span>
                  <span class="value">{{ education.incomplete_courses }}개</span>
                </div>
                <div class="detail-row" v-if="education.type === 'online'">
                  <span class="label">미수료율:</span>
                  <span class="value" :class="getIncompleteRateClass(education.incomplete_rate)">
                    {{ education.incomplete_rate }}%
                  </span>
                </div>
                <div class="detail-row">
                  <span class="label">비고:</span>
                  <span class="value notes">{{ education.notes || '-' }}</span>
                </div>
              </div>

              <!-- 결과별 알림 -->
              <div v-if="education.status === 'incomplete'" class="result-notice fail">
                <div class="notice-icon">⚠️</div>
                <p>{{ education.type_name }} 교육이 완료되지 않았습니다.</p>
                <small v-if="!education.exclude_from_scoring">
                  {{
                    education.type === 'online'
                      ? `미수료율: ${education.incomplete_rate}%`
                      : '감점: -0.5점'
                  }}
                </small>
                <small v-else>점수 계산에서 제외됨</small>
              </div>

              <div v-else-if="education.status === 'completed'" class="result-notice pass">
                <div class="notice-icon">✅</div>
                <p>{{ education.type_name }} 교육을 성공적으로 완료했습니다.</p>
                <small v-if="education.education_date">{{ education.education_date }}에 완료</small>
              </div>

              <div v-else="education.status === 'not_started'" class="result-notice pending">
                <div class="notice-icon">⏳</div>
                <p>{{ education.type_name }} 교육이 아직 시작되지 않았습니다.</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 교육 안내 -->
        <div class="section">
          <h2 class="section-title">정보보호 교육 안내</h2>
          <div class="info-grid">
            <div class="info-card">
              <div class="info-icon">💻</div>
              <h3>온라인 교육</h3>
              <ul>
                <li>온라인 수강 형태(상시)</li>
                <li>필수 수료 과정</li>
                <li>미수료시 0.5점 감점</li>
              </ul>
            </div>

            <div class="info-card">
              <div class="info-icon">🏢</div>
              <h3>오프라인 교육</h3>
              <ul>
                <li>집합 교육 형태</li>
                <li>필수 참석 과정</li>
                <li>미참석시 0.5점 감점</li>
              </ul>
            </div>

            <div class="info-card">
              <div class="info-icon">🎯</div>
              <h3>평가 기준</h3>
              <ul>
                <li>온라인: 미수료율 기준 평가</li>
                <li>오프라인: 참석 여부 평가</li>
                <li>미이수시 감점 적용</li>
                <li>제외 대상자는 감점 면제</li>
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
const educationData = ref(null)
const selectedYear = ref(new Date().getFullYear())

// 계산된 속성
const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  return [currentYear - 1, currentYear, currentYear + 1]
})

// 임시 데이터 (프로토타입용) - 엑셀 데이터 구조 반영
const getMockEducationData = () => {
  // 2025년 데이터 (미완료 상태)
  if (selectedYear.value === 2025) {
    const onlineEducationData = {
      total_courses: 2, // 수강과정 수
      completed_courses: 0, // 수료 과정
      incomplete_courses: 2, // 미수료 과정
      incomplete_rate: 100, // 미수료율 (3/8 * 100)
      status: 'incomplete', // 미수료율이 20% 초과이므로 미이수
      education_date: '2025-05-20',
      exclude_from_scoring: false,
      notes: '온라인 교육 2개 과정 중 2개 미수료 (미수료율 100%)',
    }

    const offlineEducationData = {
      total_courses: 1, // 오프라인 필수 교육 과정
      completed_courses: 0, // 참석한 과정
      incomplete_courses: 0, // 미참석하여 미수료된 과정
      not_started_courses: 1, // 아직 시작되지 않은 과정
      status: 'not_started', // 아직 시작되지 않음
      education_date: null,
      exclude_from_scoring: false,
      notes: '집합교육 아직 미실시 상태',
    }

    return {
      year: selectedYear.value,
      education_status: [
        {
          type: 'online',
          type_name: '온라인',
          total_courses: onlineEducationData.total_courses,
          completed_courses: onlineEducationData.completed_courses,
          incomplete_courses: onlineEducationData.incomplete_courses,
          incomplete_rate: onlineEducationData.incomplete_rate,
          status: onlineEducationData.status,
          education_date: onlineEducationData.education_date,
          exclude_from_scoring: onlineEducationData.exclude_from_scoring,
          notes: onlineEducationData.notes,
        },
        {
          type: 'offline',
          type_name: '오프라인',
          total_courses: offlineEducationData.total_courses,
          completed_courses: offlineEducationData.completed_courses,
          incomplete_courses: offlineEducationData.incomplete_courses,
          not_started_courses: offlineEducationData.not_started_courses,
          status: offlineEducationData.status,
          education_date: offlineEducationData.education_date,
          exclude_from_scoring: offlineEducationData.exclude_from_scoring,
          notes: offlineEducationData.notes,
        },
      ],
      summary: {
        total_courses: onlineEducationData.total_courses + offlineEducationData.total_courses, // 10개
        completed: onlineEducationData.completed_courses + offlineEducationData.completed_courses, // 5개
        incomplete:
          onlineEducationData.incomplete_courses + offlineEducationData.incomplete_courses, // 3개
        not_started: offlineEducationData.not_started_courses, // 2개
        completion_rate: Math.round(
          ((onlineEducationData.completed_courses + offlineEducationData.completed_courses) /
            (onlineEducationData.total_courses + offlineEducationData.total_courses)) *
            100,
        ), // 50%
        penalty_score: 0.5, // 온라인 미수료율 초과로 인한 감점
        excluded_count: 0,
      },
    }
  }

  // 2024년 데이터 (성공 상태)
  if (selectedYear.value === 2024) {
    const onlineEducationData = {
      total_courses: 4, // 수강과정 수
      completed_courses: 4, // 수료 과정
      incomplete_courses: 0, // 미수료 과정
      incomplete_rate: 0, // 미수료율 (1/10 * 100) - 20% 이하로 성공
      status: 'completed', // 미수료율이 20% 이하이므로 이수완료
      education_date: '2024-11-25',
      exclude_from_scoring: false,
      notes: '온라인 교육 4개 과정 중 4개 수료 완료 (미수료율 0%)',
    }

    const offlineEducationData = {
      total_courses: 1, // 오프라인 필수 교육 과정
      completed_courses: 1, // 참석한 과정
      incomplete_courses: 0, // 미참석하여 미수료된 과정
      not_started_courses: 0, // 아직 시작되지 않은 과정
      status: 'completed', // 모든 과정 완료
      education_date: '2024-12-10',
      exclude_from_scoring: false,
      notes: '집합교육 1회 모두 참석 완료',
    }

    return {
      year: selectedYear.value,
      education_status: [
        {
          type: 'online',
          type_name: '온라인',
          total_courses: onlineEducationData.total_courses,
          completed_courses: onlineEducationData.completed_courses,
          incomplete_courses: onlineEducationData.incomplete_courses,
          incomplete_rate: onlineEducationData.incomplete_rate,
          status: onlineEducationData.status,
          education_date: onlineEducationData.education_date,
          exclude_from_scoring: onlineEducationData.exclude_from_scoring,
          notes: onlineEducationData.notes,
        },
        {
          type: 'offline',
          type_name: '오프라인',
          total_courses: offlineEducationData.total_courses,
          completed_courses: offlineEducationData.completed_courses,
          incomplete_courses: offlineEducationData.incomplete_courses,
          not_started_courses: offlineEducationData.not_started_courses,
          status: offlineEducationData.status,
          education_date: offlineEducationData.education_date,
          exclude_from_scoring: offlineEducationData.exclude_from_scoring,
          notes: offlineEducationData.notes,
        },
      ],
      summary: {
        total_courses: onlineEducationData.total_courses + offlineEducationData.total_courses, // 12개
        completed: onlineEducationData.completed_courses + offlineEducationData.completed_courses, // 11개
        incomplete:
          onlineEducationData.incomplete_courses + offlineEducationData.incomplete_courses, // 1개
        not_started: offlineEducationData.not_started_courses, // 0개
        completion_rate: Math.round(
          ((onlineEducationData.completed_courses + offlineEducationData.completed_courses) /
            (onlineEducationData.total_courses + offlineEducationData.total_courses)) *
            100,
        ), // 92%
        penalty_score: 0.0, // 모든 교육 완료로 감점 없음
        excluded_count: 0,
      },
    }
  }

  // 기본 반환값 (다른 연도)
  return null
}

// 메서드
const fetchEducationStatus = async () => {
  loading.value = true
  error.value = null

  try {
    // 2025년 또는 2024년인 경우 임시 데이터 사용
    if (selectedYear.value === 2025 || selectedYear.value === 2024) {
      // 임시 데이터 로딩 시뮬레이션
      await new Promise((resolve) => setTimeout(resolve, 1000))
      educationData.value = getMockEducationData()
      return
    }

    // 실제 API 호출
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

const getPeriodCardClass = (education) => {
  if (education.exclude_from_scoring) return 'excluded'
  if (education.status === 'completed') return 'passed'
  if (education.status === 'incomplete') return 'failed'
  return 'pending'
}

const getStatusBadgeClass = (status) => {
  if (status === 'completed') return 'success'
  if (status === 'incomplete') return 'danger'
  return 'warning'
}

const getIncompleteRateClass = (rate) => {
  if (rate === 0) return 'perfect-text'
  return 'danger-text'
}

const getStatusText = (status) => {
  const statusMap = {
    completed: '이수완료',
    incomplete: '미이수',
    not_started: '미실시',
  }
  return statusMap[status] || '알 수 없음'
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

.dashboard-card.education-check {
  border-left: 4px solid #8b5cf6;
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

.card-icon.education {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
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

.progress-fill.education {
  background: linear-gradient(90deg, #8b5cf6, #7c3aed);
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

.detail-row .perfect-text {
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
  .education-page {
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
  .education-page {
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
