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

      <div v-else-if="isEmptyData" class="error-container">
        <div class="no-data-icon">📚</div>
        <h3>{{ selectedYear }}년 교육 데이터 없음</h3>
        <p>해당 연도에 등록된 교육 과정이 없습니다.</p>
        <div class="no-data-actions">
          <button @click="fetchEducationStatus" class="retry-button">다시 조회</button>
        </div>
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

                <!-- ✅ 새로운 통계 정보 추가 -->
                <div v-if="educationData.summary.unique_courses" class="stat-row">
                  <span class="stat-label">교육 과정 종류</span>
                  <span class="stat-value info">{{ educationData.summary.unique_courses }}</span>
                </div>
                <div
                  v-if="educationData.summary.avg_completion_rate !== undefined"
                  class="stat-row"
                >
                  <span class="stat-label">평균 수료율</span>
                  <span class="stat-value info"
                    >{{ educationData.summary.avg_completion_rate }}%</span
                  >
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
              :key="education.course_name || education.type"
              class="period-card"
              :class="getPeriodCardClass(education)"
            >
              <div class="period-header">
                <!-- ✅ 과정명 우선 표시, 없으면 기존 방식 -->
                <h3>{{ education.course_name || education.type_name }}</h3>
                <div class="status-badge" :class="getStatusBadgeClass(education.status)">
                  {{ getStatusText(education.status) }}
                </div>
                <div v-if="education.exclude_from_scoring" class="excluded-badge">점수 제외</div>
              </div>

              <div class="period-details">
                <div class="detail-row">
                  <span class="label">수료 횟수:</span>
                  <span class="value success">{{
                    education.completed_count || education.completed_courses || 0
                  }}</span>
                </div>

                <div class="detail-row">
                  <span class="label">미수료 횟수:</span>
                  <span class="value danger">{{
                    education.incomplete_count || education.incomplete_courses || 0
                  }}</span>
                </div>

                <div v-if="education.total_courses" class="detail-row">
                  <span class="label">총 과정 수:</span>
                  <span class="value info">{{ education.total_courses }}</span>
                </div>

                <!-- ✅ 수료율 표시 (새로운 정보) -->
                <div v-if="education.completion_rate !== undefined" class="detail-row">
                  <span class="label">수료율:</span>
                  <span class="value" :class="getCompletionRateClass(education.completion_rate)">
                    {{ education.completion_rate }}%
                  </span>
                </div>

                <!-- 기존 교육일 표시 유지 -->
                <div v-if="education.education_date" class="detail-row">
                  <span class="label">교육일:</span>
                  <span class="value">{{ formatDate(education.education_date) }}</span>
                </div>

                <!-- ✅ 기간 정보 표시 (새로운 정보) -->
                <div v-if="education.period_name" class="detail-row">
                  <span class="label">교육 기간:</span>
                  <span class="value info">{{ education.period_name }}</span>
                </div>
              </div>

              <div v-if="education.notes" class="detail-row">
                <div class="notes-icon">📝</div>
                <span>{{ education.notes }}</span>
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
                <li>온라인: 미수료율 기준 평가(0% 초과 감점)</li>
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

// ✅ 기존 getMockEducationData도 새로운 필드 지원하도록 수정
const getMockEducationData = () => {
  if (selectedYear.value === 2025) {
    return {
      year: 2025,
      education_status: [
        {
          type: 'online',
          type_name: '온라인',
          course_name: '온라인교육',
          completed_count: 2,
          incomplete_count: 0,
          total_courses: 2,
          completion_rate: 100.0,
          // 기존 호환성 필드
          completed_courses: 2,
          incomplete_courses: 0,
          not_started_courses: 0,
          status: 'completed',
          education_date: '2025-03-15',
          exclude_from_scoring: false,
          notes: null,
          period_name: '2025년 온라인 교육',
        },
        {
          type: 'offline',
          type_name: '오프라인',
          course_name: '종합교육',
          completed_count: 1,
          incomplete_count: 1,
          total_courses: 2,
          completion_rate: 50.0,
          // 기존 호환성 필드
          completed_courses: 1,
          incomplete_courses: 1,
          not_started_courses: 0,
          status: 'incomplete',
          education_date: '2025-06-10',
          exclude_from_scoring: false,
          notes: '일부 과정 미완료',
          period_name: '2025년 오프라인 교육',
        },
      ],
      summary: {
        total_courses: 4,
        completed: 3,
        incomplete: 1,
        not_started: 0,
        completion_rate: 75,
        penalty_score: 0.5,
        excluded_count: 0,
        unique_courses: 2,
        avg_completion_rate: 75.0,
      },
    }
  }

  // 2024년 또는 기타 연도는 기존 형식 유지
  return {
    year: selectedYear.value,
    education_status: [],
    summary: {
      total_courses: 0,
      completed: 0,
      incomplete: 0,
      not_started: 0,
      completion_rate: 0,
      penalty_score: 0.0,
      excluded_count: 0,
    },
  }
}

const fetchEducationStatus = async () => {
  loading.value = true
  error.value = null

  try {
    console.log('[DEBUG] 사용자 교육 요약 조회 시작:', selectedYear.value)

    // ✅ 새로운 엔드포인트 사용
    const response = await fetch(
      `/api/security-education/user-summary?year=${selectedYear.value}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authStore.token}`,
        },
      },
    )

    // 응답 처리 로직은 동일하게 유지...
    if (!response.ok) {
      if (response.status === 401) {
        authStore.logout()
        throw new Error('로그인이 만료되었습니다. 다시 로그인 페이지로 이동합니다.')
      }

      try {
        const errorData = await response.json()
        throw new Error(errorData.error || `HTTP ${response.status}: 데이터를 불러올 수 없습니다.`)
      } catch (parseError) {
        throw new Error(`HTTP ${response.status}: 데이터를 불러올 수 없습니다.`)
      }
    }

    const responseData = await response.json()
    console.log('[DEBUG] 사용자 교육 요약 API 응답:', responseData)

    // ✅ 응답 데이터 검증 및 기본값 보장
    if (!responseData || typeof responseData !== 'object') {
      throw new Error('서버에서 올바르지 않은 응답을 받았습니다.')
    }

    // ✅ 레거시 관련 코드 제거, 새로운 스키마만 지원
    educationData.value = {
      year: responseData.year || selectedYear.value,
      education_status: responseData.education_status || [],
      summary: {
        total_courses: responseData.summary?.total_courses || 0,
        completed: responseData.summary?.completed || 0,
        incomplete: responseData.summary?.incomplete || 0,
        not_started: responseData.summary?.not_started || 0,
        completion_rate: responseData.summary?.completion_rate || 0,
        penalty_score: responseData.summary?.penalty_score || 0.0,
        excluded_count: responseData.summary?.excluded_count || 0,
        unique_courses: responseData.summary?.unique_courses || 0,
        avg_completion_rate: responseData.summary?.avg_completion_rate || 0.0,
      },
    }

    console.log('[DEBUG] 교육 현황 데이터 설정 완료:', {
      year: educationData.value.year,
      totalCourses: educationData.value.summary.total_courses,
      completed: educationData.value.summary.completed,
      incomplete: educationData.value.summary.incomplete,
      statusCount: educationData.value.education_status.length,
    })

    // ✅ 서버에서 오류 메시지가 있는 경우 경고 표시
    if (responseData.error_message) {
      console.warn('[WARNING]', responseData.error_message)
    }
  } catch (err) {
    console.error('[ERROR] 사용자 교육 요약 조회 실패:', err)
    error.value = err.message || '교육 현황을 불러오는 중 오류가 발생했습니다.'

    // ✅ 에러 발생 시에도 기본 구조로 초기화
    educationData.value = {
      year: selectedYear.value,
      education_status: [],
      summary: {
        total_courses: 0,
        completed: 0,
        incomplete: 0,
        not_started: 0,
        completion_rate: 0,
        penalty_score: 0.0,
        excluded_count: 0,
        unique_courses: 0,
        avg_completion_rate: 0.0,
      },
    }
  } finally {
    loading.value = false
  }
}

// ✅ 데이터 상태 확인 헬퍼 함수들 추가
const hasEducationData = computed(() => {
  return (
    educationData.value &&
    educationData.value.summary &&
    educationData.value.summary.total_courses > 0
  )
})

const isEmptyData = computed(() => {
  return (
    educationData.value &&
    educationData.value.summary &&
    educationData.value.summary.total_courses === 0 &&
    educationData.value.education_status.length === 0
  )
})

const getProgressClass = (rate) => {
  if (rate >= 75) return 'excellent'
  if (rate >= 50) return 'good'
  if (rate >= 25) return 'warning'
  return 'poor'
}

const getCompletionRateClass = (rate) => {
  if (rate === undefined || rate === null) return 'warning-text'
  if (rate >= 80) return 'excellent-text'
  if (rate >= 60) return 'good-text'
  if (rate >= 40) return 'warning-text'
  return 'danger-text'
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  try {
    return new Date(dateString).toLocaleDateString('ko-KR')
  } catch {
    return dateString
  }
}

// ✅ 레거시 관련 헬퍼 함수들 정리 (completion_rate 기반으로 통일)
const getPeriodCardClass = (education) => {
  if (!education) return 'pending'
  if (education.exclude_from_scoring) return 'excluded'

  // ✅ 새로운 스키마만 지원 (completion_rate 기반)
  if (education.completion_rate !== undefined) {
    if (education.completion_rate >= 80) return 'passed'
    if (education.completion_rate > 0) return 'partial'
    return 'failed'
  }

  // ✅ 폴백 제거 (레거시 지원 중단)
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

const getStatusText = (education) => {
  // ✅ 서버에서 제공하는 status 텍스트를 우선 사용
  if (education.status) {
    return education.status
  }

  // ✅ 클라이언트 사이드 폴백 (새로운 스키마만)
  if (education.exclude_from_scoring) return '제외'

  if (education.completion_rate !== undefined) {
    const rate = education.completion_rate
    if (rate >= 100) return '완료'
    if (rate >= 80) return '수료'
    if (rate > 0) return `부분완료(${rate.toFixed(0)}%)`
    return '미실시'
  }

  return '알 수 없음'
}

// 라이프사이클 훅
onMounted(() => {
  if (authStore.user) {
    fetchEducationStatus()
  }
})
</script>

<!-- CSS는 외부 파일에서 import -->
<style scoped>
@import '../styles/SecurityEducationPage.css';
</style>
