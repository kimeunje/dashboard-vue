<template>
  <div class="score-page">
    <!-- 헤더 -->
    <div class="page-header">
      <h1 class="page-title">개인 보안 점수 현황</h1>
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
      <!-- 총 감점 카드 -->
      <div class="overall-score-card">
        <div class="score-circle">
          <div class="circle-chart penalty-display">
            <div class="circle-score">
              <span class="score-number">-{{ scoreData.total_penalty }}</span>
              <span class="score-unit">점</span>
            </div>
            <div class="circle-grade">총 감점</div>
          </div>
        </div>
        <div class="score-summary">
          <h2>{{ selectedYear }}년 보안 점수 현황</h2>
          <!-- <p class="score-description">
            {{ getPenaltyDescription(scoreData.total_penalty) }}
          </p> -->
          <div class="score-details">
            <div class="detail-item">
              <span class="detail-label">상시감사 감점:</span>
              <span class="detail-value penalty">-{{ scoreData.audit_penalty }}점</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">수시감사 감점:</span>
              <span class="detail-value penalty">-{{ scoreData.manual_check_penalty || 0 }}점</span>
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

      <!-- 감점 구성 요소 -->
      <!-- <div class="score-breakdown">
        <h2>감점 구성 요소</h2>
        <div class="breakdown-grid">

          <div class="breakdown-card audit">
            <div class="card-header">
              <div class="card-icon">🛡️</div>
              <h3>상시감사 현황</h3>
            </div>
            <div class="card-content">
              <div class="main-score penalty">-{{ scoreData.audit_penalty }}점</div>
              <div class="score-detail">
                <p>실패 항목: {{ scoreData.audit_stats?.failed_count || 0 }}/{{ scoreData.audit_stats?.total_count || 0 }}</p>
                <p>감점: {{ scoreData.audit_stats?.failed_count || 0 }} × 0.5점</p>
              </div>
              <div v-if="scoreData.audit_stats?.failed_items?.length > 0" class="failed-items">
                <h4>실패한 항목:</h4>
                <ul>
                  <li v-for="(item, index) in scoreData.audit_stats.failed_items" :key="index">
                    {{ item.item_name }} ({{ item.category }})
                  </li>
                </ul>
              </div>
            </div>
            <div class="card-footer">
              <router-link to="/security-audit/results" class="detail-link">
                상세 보기 →
              </router-link>
            </div>
          </div>

          <div class="breakdown-card manual-audit">
            <div class="card-header">
              <div class="card-icon">🔍</div>
              <h3>수시감사 현황</h3>
            </div>
            <div class="card-content">
              <div class="main-score penalty">-{{ scoreData.manual_check_stats?.total_penalty || 0 }}점</div>
              <div class="score-detail">
                <p>실패 항목: {{ scoreData.manual_check_stats?.failed_count || 0 }}/{{ scoreData.manual_check_stats?.total_count || 0 }}</p>
                <p>통과율: {{ getPassRate(scoreData.manual_check_stats) }}%</p>
              </div>
              <div v-if="scoreData.manual_check_stats?.items?.length > 0" class="check-items">
                <h4>점검 항목:</h4>
                <ul>
                  <li
                    v-for="(item, index) in scoreData.manual_check_stats.items"
                    :key="index"
                    :class="item.result"
                  >
                    {{ item.check_type }}: {{ item.result === 'pass' ? '통과' : '실패' }}
                  </li>
                </ul>
              </div>
            </div>
            <div class="card-footer">
              <router-link to="/security-audit/manual-results" class="detail-link">
                상세 보기 →
              </router-link>
            </div>
          </div>

          <div class="breakdown-card education">
            <div class="card-header">
              <div class="card-icon">📚</div>
              <h3>정보보호교육</h3>
            </div>
            <div class="card-content">
              <div class="main-score penalty">-{{ scoreData.education_penalty }}점</div>
              <div class="score-detail">
                <p>미이수: {{ scoreData.education_stats?.incomplete_count || 0 }}/{{ scoreData.education_stats?.total_count || 0 }}</p>
                <p>감점: {{ scoreData.education_stats?.incomplete_count || 0 }} × 0.5점</p>
              </div>
              <div v-if="scoreData.education_stats?.incomplete_periods?.length > 0" class="incomplete-periods">
                <h4>미이수 기간:</h4>
                <ul>
                  <li v-for="(period, index) in scoreData.education_stats.incomplete_periods" :key="index">
                    {{ period }}
                  </li>
                </ul>
              </div>
            </div>
            <div class="card-footer">
              <router-link to="/security-education" class="detail-link">
                상세 보기 →
              </router-link>
            </div>
          </div>

          <div class="breakdown-card training">
            <div class="card-header">
              <div class="card-icon">🎯</div>
              <h3>악성메일 모의훈련</h3>
            </div>
            <div class="card-content">
              <div class="main-score penalty">-{{ scoreData.training_penalty }}점</div>
              <div class="score-detail">
                <p>실패: {{ scoreData.training_stats?.failed_count || 0 }}/{{ scoreData.training_stats?.total_count || 0 }}</p>
                <p>감점: {{ scoreData.training_stats?.failed_count || 0 }} × 0.5점</p>
              </div>
              <div v-if="scoreData.training_stats?.failed_periods?.length > 0" class="failed-periods">
                <h4>실패한 기간:</h4>
                <ul>
                  <li v-for="(period, index) in scoreData.training_stats.failed_periods" :key="index">
                    {{ period }}
                  </li>
                </ul>
              </div>
            </div>
            <div class="card-footer">
              <router-link to="/phishing-training" class="detail-link">
                상세 보기 →
              </router-link>
            </div>
          </div>
        </div>
      </div> -->

      <!-- 개선 권장사항 -->
      <!-- <div class="recommendations">
        <h2>개선 권장사항</h2>
        <div v-if="recommendations.length === 0" class="no-recommendations">
          <div class="success-icon">🎉</div>
          <h3>축하합니다!</h3>
          <p>현재 모든 보안 요구사항을 완벽히 준수하고 있습니다.</p>
        </div>
        <div v-else class="recommendation-cards">

          <div
            v-for="(recommendation, index) in recommendations"
            :key="index"
            :class="['recommendation-card', `${recommendation.priority}-priority`]"
          >
            <div class="priority-badge">{{ getPriorityText(recommendation.priority) }}</div>
            <h3>{{ recommendation.title }}</h3>
            <p>{{ recommendation.description }}</p>
            <router-link
              :to="recommendation.action_url"
              class="action-button"
            >
              {{ getActionButtonText(recommendation.category) }}
            </router-link>
          </div>

        </div>
      </div> -->
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

// API 호출 함수
const callSecurityScoreAPI = async (year) => {
  const response = await fetch(`/api/personal-dashboard/summary?year=${year}`, {
    method: 'GET',
    credentials: 'include', // 쿠키 기반 인증 사용
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    if (response.status === 401) {
      // 인증 실패 시 로그인 페이지로 리다이렉트
      router.push('/login')
      throw new Error('인증이 필요합니다. 로그인 페이지로 이동합니다.')
    }
    const errorData = await response.json()
    throw new Error(errorData.error || '데이터 조회 중 오류가 발생했습니다.')
  }

  return await response.json()
}

// 권장사항 API 호출 함수
const callRecommendationsAPI = async (year) => {
  const response = await fetch(`/api/personal-dashboard/recommendations?year=${year}`, {
    method: 'GET',
    credentials: 'include', // 쿠키 기반 인증 사용
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    if (response.status === 401) {
      // 인증 실패 시 로그인 페이지로 리다이렉트
      router.push('/login')
      throw new Error('인증이 필요합니다. 로그인 페이지로 이동합니다.')
    }
    const errorData = await response.json()
    throw new Error(errorData.error || '권장사항 조회 중 오류가 발생했습니다.')
  }

  return await response.json()
}

// 메서드
const fetchSecurityScore = async () => {
  loading.value = true
  error.value = null

  try {
    console.log(`API 호출: 개인 보안 점수 조회 (연도: ${selectedYear.value})`)

    // 점수 데이터와 권장사항을 병렬로 호출
    const [scoreResponse, recommendationsResponse] = await Promise.all([
      callSecurityScoreAPI(selectedYear.value),
      callRecommendationsAPI(selectedYear.value),
    ])

    console.log('점수 API 응답:', scoreResponse)
    console.log('권장사항 API 응답:', recommendationsResponse)

    scoreData.value = scoreResponse
    recommendations.value = recommendationsResponse.recommendations || []
  } catch (err) {
    console.error('API 호출 오류:', err)
    error.value = err.message || '데이터를 불러오는 중 오류가 발생했습니다.'
  } finally {
    loading.value = false
  }
}

const getPenaltyDescription = (penalty) => {
  if (penalty === 0) return '감점 없음! 모든 보안 요구사항을 완벽히 준수하고 있습니다.'
  if (penalty <= 1) return '경미한 감점이 있습니다. 일부 항목 개선이 필요합니다.'
  if (penalty <= 2) return '보통 수준의 감점입니다. 보안 정책 준수 강화가 필요합니다.'
  if (penalty <= 3) return '상당한 감점이 있습니다. 즉시 보안 조치가 필요합니다.'
  return '높은 수준의 감점입니다. 긴급히 보안 개선이 필요합니다.'
}

const getPassRate = (stats) => {
  if (!stats || stats.total_count === 0) return 0
  return Math.round((stats.passed_count / stats.total_count) * 100)
}

const getPriorityText = (priority) => {
  const priorityMap = {
    high: '높음',
    medium: '보통',
    low: '낮음',
    info: '정보',
  }
  return priorityMap[priority] || priority
}

const getActionButtonText = (category) => {
  const actionMap = {
    education: '교육 현황 확인',
    training: '훈련 현황 확인',
    audit: '감사 결과 확인',
    manual: '수시감사 결과 확인',
    general: '조치 방법 보기',
  }
  return actionMap[category] || '상세 보기'
}

// 라이프사이클 훅
onMounted(() => {
  // 인증된 사용자만 데이터 로드
  if (authStore.user) {
    fetchSecurityScore()
  } else {
    // 인증되지 않은 경우 로그인 페이지로 리다이렉트
    router.push('/login')
  }
})
</script>

<style scoped>
.score-page {
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
  background-color: white;
}

.overall-score-card {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border-radius: 20px;
  padding: 40px;
  margin-bottom: 40px;
  display: flex;
  align-items: center;
  gap: 40px;
  box-shadow: 0 8px 32px rgba(239, 68, 68, 0.3);
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
  border: 8px solid rgba(255, 255, 255, 0.3);
  background-color: rgba(255, 255, 255, 0.1);
}

.circle-score {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.score-number {
  font-size: 2.5rem;
  font-weight: 800;
  line-height: 1;
}

.score-unit {
  font-size: 1.2rem;
  font-weight: 600;
  opacity: 0.9;
}

.circle-grade {
  font-size: 1rem;
  opacity: 0.9;
  margin-top: 8px;
}

.score-summary h2 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 16px 0;
}

.score-description {
  font-size: 1.125rem;
  opacity: 0.9;
  margin-bottom: 24px;
  line-height: 1.5;
}

.score-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-label {
  font-size: 0.9rem;
  opacity: 0.8;
}

.detail-value {
  font-weight: 600;
  font-size: 1.1rem;
}

.detail-value.penalty {
  color: #fecaca;
}

.score-breakdown {
  margin-bottom: 40px;
}

.score-breakdown h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 24px;
}

.breakdown-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.breakdown-card {
  background-color: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
}

.breakdown-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.breakdown-card.audit {
  border-left: 4px solid #ef4444;
}

.breakdown-card.manual-audit {
  border-left: 4px solid #f59e0b;
}

.breakdown-card.education {
  border-left: 4px solid #8b5cf6;
}

.breakdown-card.training {
  border-left: 4px solid #06b6d4;
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.card-icon {
  font-size: 1.5rem;
  margin-right: 12px;
}

.card-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
}

.card-content {
  margin-bottom: 16px;
}

.main-score {
  font-size: 2rem;
  font-weight: 700;
  color: #ef4444;
  margin-bottom: 8px;
}

.score-detail {
  color: #6b7280;
  font-size: 0.875rem;
}

.score-detail p {
  margin: 4px 0;
}

.failed-items,
.incomplete-periods,
.failed-periods,
.check-items {
  margin-top: 12px;
  font-size: 0.875rem;
}

.failed-items h4,
.incomplete-periods h4,
.failed-periods h4,
.check-items h4 {
  margin: 0 0 8px 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
}

.failed-items ul,
.incomplete-periods ul,
.failed-periods ul,
.check-items ul {
  margin: 0;
  padding-left: 16px;
  color: #6b7280;
}

.check-items li.pass {
  color: #10b981;
}

.check-items li.fail {
  color: #ef4444;
}

.card-footer {
  border-top: 1px solid #f3f4f6;
  padding-top: 16px;
}

.detail-link {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.875rem;
}

.detail-link:hover {
  text-decoration: underline;
}

.recommendations h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 24px;
}

.no-recommendations {
  text-align: center;
  padding: 60px 20px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
}

.success-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.no-recommendations h3 {
  margin: 0 0 12px 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #10b981;
}

.no-recommendations p {
  margin: 0;
  color: #6b7280;
  font-size: 1rem;
}

.recommendation-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
}

.recommendation-card {
  background-color: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
  position: relative;
}

.recommendation-card.high-priority {
  border-left: 4px solid #ef4444;
  background-color: #fef2f2;
}

.recommendation-card.medium-priority {
  border-left: 4px solid #f59e0b;
  background-color: #fffbeb;
}

.recommendation-card.low-priority {
  border-left: 4px solid #10b981;
  background-color: #f0fdf4;
}

.recommendation-card.info {
  border-left: 4px solid #3b82f6;
  background-color: #eff6ff;
}

.priority-badge {
  position: absolute;
  top: 16px;
  right: 16px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  background-color: #ef4444;
  color: white;
}

.recommendation-card.medium-priority .priority-badge {
  background-color: #f59e0b;
}

.recommendation-card.low-priority .priority-badge {
  background-color: #10b981;
}

.recommendation-card.info .priority-badge {
  background-color: #3b82f6;
}

.recommendation-card h3 {
  margin: 0 0 12px 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  padding-right: 60px;
}

.recommendation-card p {
  margin: 0 0 16px 0;
  color: #6b7280;
  line-height: 1.5;
}

.action-button {
  display: inline-block;
  background-color: #3b82f6;
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.875rem;
  transition: background-color 0.3s ease;
}

.action-button:hover {
  background-color: #2563eb;
}

.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.retry-button {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  margin-top: 20px;
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
@media (max-width: 1024px) {
  .overall-score-card {
    flex-direction: column;
    text-align: center;
    gap: 24px;
  }

  .score-details {
    grid-template-columns: 1fr;
  }

  .breakdown-grid {
    grid-template-columns: 1fr;
  }

  .recommendation-cards {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .score-page {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .page-title {
    font-size: 24px;
  }

  .overall-score-card {
    padding: 24px;
  }

  .circle-chart {
    width: 150px;
    height: 150px;
  }

  .score-number {
    font-size: 2rem;
  }

  .score-summary h2 {
    font-size: 1.5rem;
  }

  .breakdown-card {
    padding: 20px;
  }

  .main-score {
    font-size: 1.5rem;
  }

  .priority-badge {
    position: static;
    margin-bottom: 8px;
    display: inline-block;
  }

  .recommendation-card h3 {
    padding-right: 0;
  }
}
</style>
