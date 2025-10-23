<template>
  <div class="score-page">

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
      <!-- 2. 종합 점수 카드 -->
      <div class="overall-score-card">
        <div class="score-circle">
          <div class="circle-chart" :class="getRiskLevel()">
            <div class="circle-score">
              <span class="score-number">{{ getTotalCount() }}</span>
              <span class="score-unit">건</span>
            </div>
            <div class="circle-grade">총 미흡 건수</div>
          </div>
        </div>

        <div class="score-summary">
          <h2>{{ selectedYear }}년 보안 미흡 현황</h2>
          <p class="score-description">
            총 <strong>{{ getTotalCount() }}건</strong>의 보안 미흡 사항이 있습니다.
          </p>

          <div class="score-details">
            <div class="detail-item">
              <span class="detail-label">정보보안 감사</span>
              <span class="detail-value penalty">{{ getAuditTotalCount() }}건</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">정보보호 교육</span>
              <span class="detail-value penalty">
                {{ scoreData.education_stats?.periods_with_incomplete ||
                   scoreData.education_stats?.incomplete_count || 0 }}건
              </span>
            </div>
            <div class="detail-item">
              <span class="detail-label">악성메일 모의훈련</span>
              <span class="detail-value penalty">
                {{ scoreData.training_stats?.failed_count || 0 }}건
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 3. 감점 상세 내역 -->
      <div class="score-breakdown">
        <h2>감점 상세 내역</h2>

        <div class="breakdown-grid">
          <!-- 보안 감사 (상시 + 수시 통합) -->
          <div class="breakdown-card audit">
            <div class="card-header">
              <div class="card-icon audit">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M8 1a2 2 0 0 1 2 2v4H6V3a2 2 0 0 1 2-2zm3 6V3a3 3 0 0 0-6 0v4a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2z"/>
                </svg>
              </div>
              <h3>정보보안 감사</h3>
            </div>

            <div class="card-content">
              <div class="main-score penalty">{{ getAuditTotalCount() }}건</div>
              <div class="score-detail">
                <p>총 미흡 항목: {{ getAuditTotalCount() }}개</p>
                <p>정기 점검: {{ scoreData.audit_stats?.failed_count || 0 }}개 / {{ scoreData.audit_stats?.total_count || 0 }}개</p>
                <p v-if="scoreData.manual_check_stats">
                  수시 점검: {{ scoreData.manual_check_stats.failed_count || 0 }}개 / {{ scoreData.manual_check_stats.total_count || 0 }}개
                </p>
              </div>

              <!-- 상시 감사 항목 -->
              <div v-if="scoreData.audit_stats && scoreData.audit_stats.items?.length > 0" class="penalty-items">
                <h4>📋 정기 점검 항목</h4>
                <div class="penalty-list">
                  <div
                    v-for="item in scoreData.audit_stats.items"
                    :key="item.item_name"
                    class="penalty-item"
                    :class="item.result === 'pass' ? 'pass' : 'fail'"
                  >
                    <div class="item-info">
                      <div class="item-name">{{ item.item_name }}</div>
                      <div class="item-status">
                        {{ item.result === 'pass' ? '✓ 양호' : '✗ 미흡' }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- items가 없고 failed_items만 있는 경우 (하위 호환성) -->
              <div v-else-if="scoreData.audit_stats?.failed_items?.length > 0" class="penalty-items">
                <h4>📋 수시 점검 항목</h4>
                <div class="penalty-list">
                  <div
                    v-for="item in scoreData.audit_stats.failed_items"
                    :key="item.item_name"
                    class="penalty-item fail"
                  >
                    <div class="item-info">
                      <div class="item-name">{{ item.item_name }}</div>
                      <div class="item-status">✗ 양호</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 수시 점검 항목 -->
              <div v-if="scoreData.manual_check_stats?.items?.length > 0" class="penalty-items">
                <h4>🔍 수시 점검 항목</h4>
                <div class="penalty-list">
                  <div
                    v-for="(item, index) in scoreData.manual_check_stats.items"
                    :key="index"
                    class="penalty-item"
                    :class="item.result"
                  >
                    <div class="item-info">
                      <div class="item-name">{{ item.check_type }}</div>
                      <div class="item-status">{{ item.result === 'pass' ? '✓ 양호' : '✗ 미흡' }}</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 모두 통과한 경우 -->
              <div v-if="getAuditTotalCount() === 0" class="no-penalty-items">
                모든 보안 감사 항목을 통과했습니다 ✓
              </div>
            </div>

            <div class="card-footer">
              <router-link to="/security-audit/results" class="detail-link">
                정기 점검 상세 보기 →
              </router-link>
              <router-link 
                v-if="scoreData.manual_check_stats" 
                to="/security-audit/results" 
                class="detail-link"
                style="margin-left: 1rem;"
              >
                수시 점검 상세 보기 →
              </router-link>
            </div>
          </div>

          <!-- 정보보호 교육 -->
          <div class="breakdown-card education">
            <div class="card-header">
              <div class="card-icon education">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M8.211 2.047a.5.5 0 0 0-.422 0l-7.5 3.5a.5.5 0 0 0 .025.917l7.5 3a.5.5 0 0 0 .372 0L14.5 7.14V13a1 1 0 0 0-1 1v2h3v-2a1 1 0 0 0-1-1V6.739l.686-.275a.5.5 0 0 0 .025-.917l-7.5-3.5Z"/>
                </svg>
              </div>
              <h3>정보보호 교육</h3>
            </div>

            <div class="card-content">
              <div class="main-score penalty">
                {{ scoreData.education_stats?.periods_with_incomplete ||
                   scoreData.education_stats?.incomplete_count || 0 }}건
              </div>
              <div class="score-detail">
                <p>미완료 기간: {{ scoreData.education_stats?.incomplete_count || 0 }}개</p>
                <p>총 교육 기간: {{ scoreData.education_stats?.total_count || 0 }}개</p>
              </div>

              <div v-if="scoreData.education_stats?.incomplete_periods?.length > 0" class="penalty-items">
                <h4>미완료 교육 목록</h4>
                <div class="penalty-list">
                  <div
                    v-for="(period, index) in scoreData.education_stats.incomplete_periods"
                    :key="index"
                    class="penalty-item fail"
                  >
                    <div class="item-info">
                      <div class="item-name">{{ period }}</div>
                      <div class="item-status">✗ 미완료</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="card-footer">
              <router-link to="/security-education" class="detail-link">
                상세 보기 →
              </router-link>
            </div>
          </div>

          <!-- 악성메일 모의훈련 -->
          <div class="breakdown-card training">
            <div class="card-header">
              <div class="card-icon training">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M0 4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V4Zm2-1a1 1 0 0 0-1 1v.217l7 4.2 7-4.2V4a1 1 0 0 0-1-1H2Zm13 2.383-4.708 2.825L15 11.105V5.383Zm-.034 6.876-5.64-3.471L8 9.583l-1.326-.795-5.64 3.47A1 1 0 0 0 2 13h12a1 1 0 0 0 .966-.741ZM1 11.105l4.708-2.897L1 5.383v5.722Z"/>
                </svg>
              </div>
              <h3>악성메일 모의훈련</h3>
            </div>

            <div class="card-content">
              <div class="main-score penalty">
                {{ scoreData.training_stats?.failed_count || 0 }}건
              </div>
              <div class="score-detail">
                <p>실패 횟수: {{ scoreData.training_stats?.failed_count || 0 }}회</p>
                <p>총 훈련: {{ scoreData.training_stats?.total_count || 0 }}회</p>
              </div>

              <div v-if="scoreData.training_stats?.failed_periods?.length > 0" class="penalty-items">
                <h4>실패한 훈련 목록</h4>
                <div class="penalty-list">
                  <div
                    v-for="(period, index) in scoreData.training_stats.failed_periods"
                    :key="index"
                    class="penalty-item fail"
                  >
                    <div class="item-info">
                      <div class="item-name">{{ period }}</div>
                      <div class="item-status">✗ 실패</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="card-footer">
              <router-link to="/phishing-training" class="detail-link">
                상세 보기 →
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Router와 Store 사용
const router = useRouter()
const authStore = useAuthStore()

// 반응형 데이터
const loading = ref(false)
const error = ref(null)
const scoreData = ref(null)
const recommendations = ref([])
const selectedYear = ref(2025)

// 계산된 속성
const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  return [currentYear - 1, currentYear, currentYear + 1]
})

// 점수 계산 함수들
const getTotalCount = () => {
  const auditCount = getAuditTotalCount()
  const educationCount = scoreData.value?.education_stats?.periods_with_incomplete ||
                        scoreData.value?.education_stats?.incomplete_count || 0
  const trainingCount = scoreData.value?.training_stats?.failed_count || 0
  return auditCount + educationCount + trainingCount
}

const getAuditTotalCount = () => {
  const failed = scoreData.value?.audit_stats?.failed_count || 0
  const manualFailed = scoreData.value?.manual_check_stats?.failed_count || 0
  return failed + manualFailed
}

const getPassRate = (stats) => {
  if (!stats || !stats.total_count) return 0
  const passCount = stats.total_count - (stats.failed_count || 0)
  return Math.round((passCount / stats.total_count) * 100)
}

const getRiskLevel = () => {
  const totalCount = getTotalCount()
  if (totalCount === 0) return 'low'
  if (totalCount <= 3) return 'medium'
  if (totalCount <= 6) return 'high'
  return 'critical'
}

const getRiskLevelLabel = () => {
  const level = getRiskLevel()
  const labels = {
    low: '우수',
    medium: '주의',
    high: '위험',
    critical: '매우 위험'
  }
  return labels[level] || '미평가'
}

const getPriorityText = (priority) => {
  const texts = {
    high: '긴급',
    medium: '보통',
    low: '낮음',
    info: '정보'
  }
  return texts[priority] || priority
}

const getActionButtonText = (category) => {
  const texts = {
    audit: '감사 결과 보기',
    education: '교육 이수하기',
    training: '훈련 결과 보기'
  }
  return texts[category] || '자세히 보기'
}

// 날짜 포맷 함수
const formatDateTime = (date) => {
  if (!date) return '-'
  try {
    return new Date(date).toLocaleString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return '-'
  }
}

// API 호출 함수
const callSecurityScoreAPI = async (year) => {
  const response = await fetch(`/api/personal-dashboard/summary?year=${year}`, {
    method: 'GET',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    if (response.status === 401) {
      router.push('/login')
      throw new Error('인증이 필요합니다. 로그인 페이지로 이동합니다.')
    }
    const errorData = await response.json()
    throw new Error(errorData.error || '데이터 조회 중 오류가 발생했습니다.')
  }

  return await response.json()
}

const callRecommendationsAPI = async (year) => {
  const response = await fetch(`/api/personal-dashboard/recommendations?year=${year}`, {
    method: 'GET',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    if (response.status === 401) {
      router.push('/login')
      throw new Error('인증이 필요합니다. 로그인 페이지로 이동합니다.')
    }
    const errorData = await response.json()
    throw new Error(errorData.error || '권장사항 조회 중 오류가 발생했습니다.')
  }

  return await response.json()
}

// 데이터 로드
const fetchSecurityScore = async () => {
  loading.value = true
  error.value = null

  try {
    const data = await callSecurityScoreAPI(selectedYear.value)
    scoreData.value = data

    try {
      const recommendationsData = await callRecommendationsAPI(selectedYear.value)
      recommendations.value = recommendationsData.recommendations || []
    } catch (err) {
      console.error('권장사항 로드 실패:', err)
      recommendations.value = []
    }
  } catch (err) {
    console.error('보안 점수 로드 실패:', err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// 라이프사이클
onMounted(() => {
  fetchSecurityScore()
})
</script>

<style scoped>
@import '../styles/TotalScorePage.css';
</style>