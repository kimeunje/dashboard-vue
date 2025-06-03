<!-- SecurityScorePage.vue - Template 부분 -->
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
              <span class="score-number">{{ Math.round(scoreData.total_score) }}</span>
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
              <span class="detail-value">{{ Math.round(scoreData.audit_score) }}점</span>
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
              <div class="main-score">{{ Math.round(scoreData.audit_score) }}점</div>
              <div class="score-detail">
                <p>
                  통과 항목: {{ scoreData.education_stats?.completed_count || 0 }}/{{
                    scoreData.education_stats?.total_count || 0
                  }}
                </p>
                <p>통과율: {{ getAuditPassRate() }}%</p>
              </div>
              <div class="progress-bar">
                <div
                  class="progress-fill audit-progress"
                  :style="{ width: `${getAuditPassRate()}%` }"
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
                <p>미이수 횟수: {{ getEducationIncompleteCount() }}회</p>
                <p>연간 이수율: {{ getEducationCompletionRate() }}%</p>
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
              <div class="main-score penalty">-{{ scoreData.training_penalty }}점</div>
              <div class="score-detail">
                <p>실패 횟수: {{ getTrainingFailedCount() }}회</p>
                <p>연간 통과율: {{ getTrainingPassRate() }}%</p>
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
          <div v-if="yearlyTrend.length > 0" class="chart-container">
            <div class="trend-bars">
              <div v-for="yearData in yearlyTrend" :key="yearData.year" class="trend-bar-group">
                <div class="trend-bar-container">
                  <div
                    class="trend-bar"
                    :style="{ height: `${(yearData.score / 100) * 100}%` }"
                    :class="getScoreBarClass(yearData.score)"
                  ></div>
                </div>
                <div class="trend-label">{{ yearData.year }}</div>
                <div class="trend-score">{{ Math.round(yearData.score) }}점</div>
                <div class="trend-grade">{{ yearData.grade }}</div>
              </div>
            </div>
          </div>
          <div v-else class="chart-placeholder">
            <p>점수 추이 데이터를 불러오는 중...</p>
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
    console.error('보안 점수 조회 실패:', err)
    error.value = err.message || '점수 데이터를 불러오는 중 오류가 발생했습니다.'
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
            score: data.total_score,
            grade: data.grade,
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

  // 감사 점수에 따른 권장사항
  if (scoreData.value.audit_score < 90) {
    recs.push({
      priority: 'medium',
      title: '보안 설정 개선',
      description: '일부 보안 설정이 정책에 맞지 않습니다. 감사 결과를 확인하고 조치하세요.',
      action_link: '/security-audit/results',
    })
  }

  // 총 점수에 따른 일반적인 권장사항
  if (scoreData.value.total_score < 80) {
    recs.push({
      priority: 'info',
      title: '종합적인 보안 의식 개선',
      description: '보안 점수가 낮습니다. 정기적인 보안 교육 참여와 정책 준수를 권장합니다.',
      action_link: '/security-audit/solutions',
    })
  }

  recommendations.value = recs
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

const getAuditPassRate = () => {
  if (!scoreData.value?.audit_score) return 0
  return Math.round(scoreData.value.audit_score)
}

const getEducationIncompleteCount = () => {
  if (!scoreData.value?.education_stats) return 0
  return (
    (scoreData.value.education_stats.total_count || 0) -
    (scoreData.value.education_stats.completed_count || 0)
  )
}

const getEducationCompletionRate = () => {
  if (!scoreData.value?.education_stats) return 0
  const stats = scoreData.value.education_stats
  if (stats.total_count === 0) return 0
  return Math.round((stats.completed_count / stats.total_count) * 100)
}

const getTrainingFailedCount = () => {
  if (!scoreData.value?.training_stats) return 0
  return (
    (scoreData.value.training_stats.total_count || 0) -
    (scoreData.value.training_stats.passed_count || 0)
  )
}

const getTrainingPassRate = () => {
  if (!scoreData.value?.training_stats) return 0
  const stats = scoreData.value.training_stats
  if (stats.total_count === 0) return 0
  return Math.round((stats.passed_count / stats.total_count) * 100)
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

const getScoreBarClass = (score) => {
  if (score >= 90) return 'excellent'
  if (score >= 80) return 'good'
  if (score >= 70) return 'warning'
  return 'poor'
}

const downloadReport = () => {
  if (!scoreData.value) return

  // 간단한 보고서 텍스트 생성
  const reportContent = `
정보보안 평가 보고서
=====================

평가 연도: ${selectedYear.value}년
평가 대상: ${authStore.user?.name || '사용자'}

종합 점수: ${Math.round(scoreData.value.total_score)}점 (${scoreData.value.grade})

점수 구성:
- 상시감사 점수: ${Math.round(scoreData.value.audit_score)}점
- 교육 미이수 감점: -${scoreData.value.education_penalty}점
- 모의훈련 감점: -${scoreData.value.training_penalty}점

세부 내용:
- 교육 이수율: ${getEducationCompletionRate()}%
- 모의훈련 통과율: ${getTrainingPassRate()}%
- 감사 항목 통과율: ${getAuditPassRate()}%

평가 결과: ${getScoreDescription(scoreData.value.grade, scoreData.value.total_score)}

개선 권장사항:
${recommendations.value.map((rec) => `- [${getPriorityText(rec.priority)}] ${rec.title}: ${rec.description}`).join('\n')}

생성일: ${new Date().toLocaleDateString('ko-KR')}
  `

  // 파일 다운로드
  const blob = new Blob([reportContent], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `보안평가보고서_${selectedYear.value}_${authStore.user?.username || 'user'}.txt`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

const requestImprovement = () => {
  const currentScore = Math.round(scoreData.value?.total_score || 0)
  const improvements = []

  if (scoreData.value?.education_penalty > 0) {
    improvements.push('정보보호 교육 이수')
  }
  if (scoreData.value?.training_penalty > 0) {
    improvements.push('악성메일 대응 능력 향상')
  }
  if (scoreData.value?.audit_score < 90) {
    improvements.push('보안 설정 개선')
  }

  const improvementText =
    improvements.length > 0
      ? `\n\n주요 개선 필요 사항:\n${improvements.map((item) => `- ${item}`).join('\n')}`
      : ''

  alert(`개선 컨설팅 요청이 접수되었습니다.

현재 보안 점수: ${currentScore}점 (${scoreData.value?.grade || 'N/A'})${improvementText}

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
