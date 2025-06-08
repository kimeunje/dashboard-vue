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
                  <span class="stat-label">미실시</span>
                  <span class="stat-value warning">{{
                    trainingData.summary.not_started || 0
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
                <div class="detail-row" v-if="period.email_sent_time || period.result !== 'pass'">
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

<!-- CSS는 외부 파일에서 import -->
<style scoped>
@import '../styles/PhishingTrainingPage.css';
</style>
