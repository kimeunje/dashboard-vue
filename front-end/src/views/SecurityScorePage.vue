<!-- SecurityScorePage.vue - KPI 감점 시스템으로 수정 -->
<template>
  <div class="score-page">
    <div class="page-header">
      <h1 class="page-title">KPI 보안 감점 현황</h1>
      <!-- 수정: 종합 보안 점수 -> KPI 보안 감점 현황 -->
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
      <p>KPI 감점을 계산하는 중...</p>
      <!-- 수정 -->
    </div>

    <!-- 에러 상태 -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">⚠️</div>
      <h3>감점 계산 실패</h3>
      <!-- 수정 -->
      <p>{{ error }}</p>
      <button @click="fetchSecurityScore" class="retry-button">다시 계산</button>
    </div>

    <!-- KPI 감점 데이터 -->
    <!-- 수정 -->
    <div v-else-if="scoreData" class="score-content">
      <!-- 총 감점 카드 -->
      <!-- 수정: 종합 점수 카드 -> 총 감점 카드 -->
      <div class="overall-score-card">
        <div class="score-circle">
          <div class="circle-chart penalty-display">
            <!-- 수정: grade 클래스 제거 -->
            <div class="circle-score">
              <span class="score-number">-{{ scoreData.total_penalty || 0 }}</span>
              <!-- 수정: total_score -> total_penalty -->
              <span class="score-unit">점</span>
            </div>
            <div class="circle-grade">감점</div>
            <!-- 수정: grade -> '감점' 고정 -->
          </div>
        </div>
        <div class="score-summary">
          <h2>{{ selectedYear }}년 KPI 보안 감점</h2>
          <!-- 수정 -->
          <p class="score-description">
            {{ getPenaltyDescription(scoreData.total_penalty) }}
            <!-- 수정: 감점 기준 설명 -->
          </p>
          <div class="score-details">
            <div class="detail-item">
              <span class="detail-label">상시감사 감점:</span>
              <!-- 수정 -->
              <span class="detail-value penalty">-{{ scoreData.audit_penalty || 0 }}점</span>
              <!-- 수정 -->
            </div>
            <div class="detail-item">
              <span class="detail-label">교육 미이수 감점:</span>
              <span class="detail-value penalty">-{{ scoreData.education_penalty || 0 }}점</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">모의훈련 감점:</span>
              <span class="detail-value penalty">-{{ scoreData.training_penalty || 0 }}점</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 감점 구성 요소 -->
      <!-- 수정: 점수 구성 요소 -> 감점 구성 요소 -->
      <div class="score-breakdown">
        <h2>감점 구성 요소</h2>
        <!-- 수정 -->
        <div class="breakdown-grid">
          <!-- 정보보안 감사 -->
          <div class="breakdown-card audit">
            <div class="card-header">
              <div class="card-icon">🛡️</div>
              <h3>정보보안 감사 현황</h3>
            </div>
            <div class="card-content">
              <div class="main-score penalty">-{{ scoreData.audit_penalty || 0 }}점</div>
              <div class="score-detail">
                <p>
                  실패 항목: {{ scoreData.audit_stats?.failed_count || 0 }}/{{
                    scoreData.audit_stats?.total_count || 0
                  }}
                </p>
                <p>감점: {{ scoreData.audit_stats?.failed_count || 0 }} × 0.5점</p>
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
              <div class="main-score penalty">-{{ scoreData.education_penalty || 0 }}점</div>
              <div class="score-detail">
                <p>미이수 횟수: {{ getEducationIncompleteCount() }}회</p>
                <p>감점: {{ getEducationIncompleteCount() }} × 0.5점</p>
                <!-- 수정: 이수율 -> 감점 계산 -->
              </div>
              <div class="penalty-info">
                <small>미이수시 0.5점 감점</small>
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
              <div class="main-score penalty">-{{ scoreData.training_penalty || 0 }}점</div>
              <div class="score-detail">
                <p>실패 횟수: {{ getTrainingFailedCount() }}회</p>
                <p>감점: {{ getTrainingFailedCount() }} × 0.5점</p>
                <!-- 수정: 통과율 -> 감점 계산 -->
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

      <!-- 수정: 등급별 기준 섹션 완전 제거 (KPI에서 등급 불필요) -->

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

      <!-- 연도별 감점 추이 -->
      <!-- 수정: 점수 추이 -> 감점 추이 -->
      <div class="score-trend">
        <h2>연도별 감점 추이</h2>
        <!-- 수정 -->
        <div class="trend-chart">
          <div v-if="yearlyTrend.length > 0" class="chart-container">
            <div class="trend-bars">
              <div v-for="yearData in yearlyTrend" :key="yearData.year" class="trend-bar-group">
                <div class="trend-bar-container">
                  <div
                    class="trend-bar penalty-bar"
                    :style="{ height: `${(yearData.penalty / 5.0) * 100}%` }"
                  ></div>
                </div>
                <div class="trend-label">{{ yearData.year }}</div>
                <div class="trend-score">-{{ yearData.penalty }}점</div>
                <!-- 수정: score -> penalty -->
                <!-- 수정: trend-grade 제거 -->
              </div>
            </div>
          </div>
          <div v-else class="chart-placeholder">
            <p>감점 추이 데이터를 불러오는 중...</p>
            <!-- 수정 -->
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
            KPI 감점 보고서 다운로드
            <!-- 수정 -->
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
import '@/assets/styles/views/SecurityScorePage.css'

// Pinia Store
const authStore = useAuthStore()

// 반응형 데이터
const loading = ref(false)
const error = ref(null)
const scoreData = ref(null)
const recommendations = ref([])
const yearlyTrend = ref([])
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

    // 권장사항 생성
    generateRecommendations()

    // 연도별 추이 데이터 가져오기
    await fetchYearlyTrend()
  } catch (err) {
    console.error('KPI 감점 조회 실패:', err) // 수정
    error.value = err.message || '감점 데이터를 불러오는 중 오류가 발생했습니다.' // 수정
  } finally {
    loading.value = false
  }
}

const fetchYearlyTrend = async () => {
  try {
    const years = [selectedYear.value - 2, selectedYear.value - 1, selectedYear.value]
    const trendData = []

    for (const year of years) {
      try {
        const response = await fetch(`/api/security-score/summary?year=${year}`, {
          credentials: 'include',
        })

        if (response.ok) {
          const data = await response.json()
          trendData.push({
            year: year,
            penalty: data.total_penalty || 0, // 수정: score -> penalty
          })
        }
      } catch (err) {
        console.warn(`${year}년 데이터 조회 실패:`, err)
      }
    }

    yearlyTrend.value = trendData
  } catch (err) {
    console.error('연도별 추이 데이터 조회 실패:', err)
  }
}

const generateRecommendations = () => {
  const recs = []

  if (!scoreData.value) return

  // 교육 미이수에 따른 권장사항
  if (scoreData.value.education_penalty > 0) {
    recs.push({
      priority: 'high',
      title: '정보보호 교육 이수',
      description: `미이수된 교육이 ${getEducationIncompleteCount()}회 있습니다. 교육을 완료하여 감점을 해소하세요.`,
      action_link: '/security-education',
    })
  }

  // 모의훈련 실패에 따른 권장사항
  if (scoreData.value.training_penalty > 0) {
    recs.push({
      priority: 'high',
      title: '악성메일 대응 능력 향상',
      description: `모의훈련에서 ${getTrainingFailedCount()}회 실패했습니다. 악성메일 식별 능력을 향상시키세요.`,
      action_link: '/phishing-training',
    })
  }

  // 감사 감점에 따른 권장사항 // 수정
  if (scoreData.value.audit_penalty > 0) {
    recs.push({
      priority: 'medium',
      title: '보안 설정 개선',
      description: '일부 보안 설정이 정책에 맞지 않습니다. 감사 결과를 확인하고 조치하세요.',
      action_link: '/security-audit/results',
    })
  }

  // 총 감점에 따른 일반적인 권장사항 // 수정
  if (scoreData.value.total_penalty >= 2.0) {
    // 수정: 80점 기준 -> 2점 이상 감점
    recs.push({
      priority: 'info',
      title: '종합적인 보안 의식 개선',
      description: '감점이 많습니다. 정기적인 보안 교육 참여와 정책 준수를 권장합니다.', // 수정
      action_link: '/security-audit/solutions',
    })
  }

  recommendations.value = recs
}

// 수정: getGradeClass 메서드 제거 (등급 불필요)

const getPenaltyDescription = (penalty) => {
  // 수정: 감점 기준 설명
  if (penalty === 0) {
    return '우수한 보안 관리 상태입니다. 현재 수준을 유지해주세요.'
  } else if (penalty <= 1.0) {
    return '양호한 상태이나 일부 개선이 필요합니다.'
  } else if (penalty <= 2.5) {
    return '보안 의식 향상이 필요합니다.'
  } else {
    return '즉시 보안 교육 및 개선 조치가 필요합니다.'
  }
}

const getEducationIncompleteCount = () => {
  if (!scoreData.value?.education_stats) return 0
  return scoreData.value.education_stats.incomplete_count || 0 // 수정: 직접 계산 제거
}

const getTrainingFailedCount = () => {
  if (!scoreData.value?.training_stats) return 0
  return scoreData.value.training_stats.failed_count || 0 // 수정: 직접 계산 제거
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

// 수정: getScoreBarClass 메서드 제거 (등급별 스타일 불필요)

const downloadReport = () => {
  if (!scoreData.value) return

  // KPI 감점 보고서 텍스트 생성 // 수정
  const reportContent = `
KPI 보안 감점 보고서
==================

평가 연도: ${selectedYear.value}년
평가 대상: ${authStore.user?.name || '사용자'}

총 감점: -${scoreData.value.total_penalty || 0}점

감점 구성:
- 상시감사 감점: -${scoreData.value.audit_penalty || 0}점
- 교육 미이수 감점: -${scoreData.value.education_penalty || 0}점
- 모의훈련 감점: -${scoreData.value.training_penalty || 0}점

세부 내용:
- 감사 실패 항목: ${scoreData.value.audit_stats?.failed_count || 0}개
- 교육 미이수: ${getEducationIncompleteCount()}회
- 모의훈련 실패: ${getTrainingFailedCount()}회

평가 결과: ${getPenaltyDescription(scoreData.value.total_penalty)}

개선 권장사항:
${recommendations.value.map((rec) => `- [${getPriorityText(rec.priority)}] ${rec.title}: ${rec.description}`).join('\n')}

생성일: ${new Date().toLocaleDateString('ko-KR')}
  `

  // 파일 다운로드
  const blob = new Blob([reportContent], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `KPI감점보고서_${selectedYear.value}_${authStore.user?.username || 'user'}.txt` // 수정
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

const requestImprovement = () => {
  const currentPenalty = scoreData.value?.total_penalty || 0 // 수정
  const improvements = []

  if (scoreData.value?.education_penalty > 0) {
    improvements.push('정보보호 교육 이수')
  }
  if (scoreData.value?.training_penalty > 0) {
    improvements.push('악성메일 대응 능력 향상')
  }
  if (scoreData.value?.audit_penalty > 0) {
    // 수정
    improvements.push('보안 설정 개선')
  }

  const improvementText =
    improvements.length > 0
      ? `\n\n주요 개선 필요 사항:\n${improvements.map((item) => `- ${item}`).join('\n')}`
      : ''

  alert(`개선 컨설팅 요청이 접수되었습니다.

현재 KPI 감점: -${currentPenalty}점${improvementText}

담당자: IT 보안팀
연락처: 내선 1234
이메일: security@company.com

2-3일 내에 담당자가 연락드려 맞춤형 개선 방안을 제시해드리겠습니다.`)
}

// 라이프사이클 훅
onMounted(() => {
  if (authStore.user) {
    fetchSecurityScore()
  }
})
</script>
