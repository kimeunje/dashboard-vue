<!-- views/HomePage.vue -->
<template>
  <div class="dashboard-page">
    <!-- 업무 개요 헤더 -->
    <div class="dashboard-header">
      <div class="welcome-message">
        <h1>상시보안감사 시스템</h1>
        <p>
          {{
            authStore.user
              ? `${authStore.user.name}님, 안녕하세요.`
              : '보안 감사 대시보드에 오신 것을 환영합니다.'
          }}
        </p>
      </div>
      <div v-if="authStore.user && securityStats.totalChecks > 0" class="security-status">
        <div class="status-label">
          보안 준수율:
          <span class="status-value">
            {{ Math.round((securityStats.completedChecks / securityStats.totalChecks) * 100) }}%
          </span>
        </div>
        <div class="progress-bar">
          <div
            class="progress-fill"
            :style="{
              width: `${(securityStats.completedChecks / securityStats.totalChecks) * 100}%`,
            }"
          ></div>
        </div>
      </div>
    </div>

    <!-- 로그인 상태 - 보안 상태 요약 표시 -->
    <template v-if="authStore.user">
      <!-- 보안 상태 요약 카드 -->
      <div class="dashboard-main">
        <div v-if="loading" class="dashboard-card status-summary">
          <div class="card-header">
            <h2>보안 상태 요약</h2>
            <span class="date-info">데이터 로딩 중...</span>
          </div>
          <div class="loading-indicator">
            <div class="loading-spinner"></div>
            <p>보안 데이터를 불러오는 중입니다...</p>
          </div>
        </div>

        <div v-else-if="error" class="dashboard-card status-summary">
          <div class="card-header">
            <h2>보안 상태 요약</h2>
            <span class="date-info error">오류 발생</span>
          </div>
          <div class="error-message">
            <p>{{ error }}</p>
            <button @click="fetchSecurityStats" class="retry-button">다시 시도</button>
          </div>
        </div>

        <div v-else class="dashboard-card status-summary">
          <div class="card-header">
            <h2>보안 상태 요약</h2>
            <span class="date-info"> 마지막 업데이트: {{ securityStats.lastAuditDate }} </span>
          </div>
          <div class="status-metrics">
            <div class="metric-item">
              <div class="metric-value critical">
                {{ securityStats.criticalIssues }}
              </div>
              <div class="metric-label">심각한 문제</div>
            </div>
            <div class="metric-item">
              <div class="metric-value success">
                {{ securityStats.completedChecks }}
              </div>
              <div class="metric-label">완료된 검사</div>
            </div>
            <div class="metric-item">
              <div class="metric-value info">
                {{ securityStats.totalChecks }}
              </div>
              <div class="metric-label">전체 검사 항목</div>
            </div>
            <div class="metric-item">
              <div class="metric-value success">
                {{
                  securityStats.totalChecks > 0
                    ? Math.round((securityStats.completedChecks / securityStats.totalChecks) * 100)
                    : 0
                }}
              </div>
              <div class="metric-label">준수율(%)</div>
            </div>
          </div>
          <div class="card-footer">
            <RouterLink to="/security-audit/results" class="view-details-link">
              <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path
                  d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"
                />
              </svg>
              전체 결과 보기
            </RouterLink>
          </div>
        </div>
      </div>

      <!-- 초기 설정 안내 카드 -->
      <div v-if="!initialSetupDone" class="dashboard-main">
        <div class="dashboard-card setup-card">
          <div class="card-header">
            <h2>초기 설정 필요</h2>
            <span class="date-info important">최초 1회 필수</span>
          </div>
          <div class="setup-content simple">
            <p>보안 감사를 진행하기 전에 컴퓨터 이름과 작업 그룹(부서명)을 설정해야 합니다.</p>

            <div class="setup-note">
              <ul>
                <li>컴퓨터 이름은 <strong>사용자 본인의 이름</strong>으로 설정하세요.</li>
                <li>작업 그룹은 <strong>소속 부서명</strong>으로 설정하세요.</li>
                <li>설정 후 시스템 재부팅이 필요할 수 있습니다.</li>
              </ul>
            </div>

            <div class="setup-actions simple">
              <button
                class="download-button primary-download"
                @click="downloadHomeScript"
                :disabled="downloadLoading"
              >
                <svg
                  v-if="!downloadLoading"
                  width="16"
                  height="16"
                  fill="currentColor"
                  viewBox="0 0 16 16"
                >
                  <path
                    d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"
                  />
                  <path
                    d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"
                  />
                </svg>
                <div v-else class="loading-spinner-small"></div>
                홈 다운로드
              </button>
              <button class="download-button" @click="downloadScript" :disabled="downloadLoading">
                <svg
                  v-if="!downloadLoading"
                  width="16"
                  height="16"
                  fill="currentColor"
                  viewBox="0 0 16 16"
                >
                  <path
                    d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"
                  />
                  <path
                    d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"
                  />
                </svg>
                <div v-else class="loading-spinner-small"></div>
                스크립트 다운로드
              </button>
              <button class="setup-complete-button" @click="markSetupAsDone">
                <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M13.854 3.646a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 10.293l6.646-6.647a.5.5 0 0 1 .708 0z"
                  />
                </svg>
                초기 설정 완료 표시
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- 로그아웃 상태 - 안내 메시지 표시 -->
    <div v-else class="not-logged-info">
      <div class="info-icon">
        <svg width="40" height="40" fill="currentColor" viewBox="0 0 16 16">
          <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
          <path
            d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"
          />
        </svg>
      </div>
      <h2>로그인이 필요합니다</h2>
      <p>
        상시보안감사 시스템을 이용하기 위해서는 로그인이 필요합니다. 로그인 페이지로 이동하여
        로그인해 주세요.
      </p>
      <div class="login-button-container">
        <RouterLink to="/login" class="login-page-button">
          <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path
              fill-rule="evenodd"
              d="M6 12.5a.5.5 0 0 0 .5.5h8a.5.5 0 0 0 .5-.5v-9a.5.5 0 0 0-.5-.5h-8a.5.5 0 0 0-.5.5v2a.5.5 0 0 1-1 0v-2A1.5 1.5 0 0 1 6.5 2h8A1.5 1.5 0 0 1 16 3.5v9a1.5 1.5 0 0 1-1.5 1.5h-8A1.5 1.5 0 0 1 5 12.5v-2a.5.5 0 0 1 1 0v2z"
            />
            <path
              fill-rule="evenodd"
              d="M.146 8.354a.5.5 0 0 1 0-.708l3-3a.5.5 0 1 1 .708.708L1.707 7.5H10.5a.5.5 0 0 1 0 1H1.707l2.147 2.146a.5.5 0 0 1-.708.708l-3-3z"
            />
          </svg>
          로그인 페이지로 이동
        </RouterLink>
      </div>
    </div>

    <!-- 하단 안내 섹션 -->
    <div class="dashboard-main">
      <div class="dashboard-card">
        <div class="help-section">
          <h3>도움이 필요하신가요?</h3>
          <p>
            보안 감사 관련 문의사항은
            <RouterLink to="/security-audit/contact" class="inline-link">
              IT 보안팀에 문의
            </RouterLink>
            하거나 내선 <strong>5678</strong>로 연락해주세요.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Props 정의
defineProps({
  user: {
    type: Object,
    default: null,
  },
})

// Pinia Store
const authStore = useAuthStore()

// 반응형 데이터
const securityStats = ref({
  lastAuditDate: '',
  criticalIssues: 0,
  completedChecks: 0,
  totalChecks: 0,
})

const loading = ref(false)
const error = ref(null)
const initialSetupDone = ref(false)
const downloadLoading = ref(false)

// 초기 설정 완료 여부 확인
const checkInitialSetup = () => {
  const setupDone = localStorage.getItem('initialSetupDone')
  if (setupDone === 'true') {
    initialSetupDone.value = true
  }
}

// 보안 통계 데이터 가져오기
const fetchSecurityStats = async () => {
  if (!authStore.user) return

  loading.value = true
  error.value = null

  try {
    const response = await fetch('/api/security-audit/stats', {
      credentials: 'include',
    })

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`)
    }

    const data = await response.json()
    securityStats.value = {
      lastAuditDate: data.lastAuditDate || '',
      criticalIssues: data.criticalIssues || 0,
      completedChecks: data.completedChecks || 0,
      totalChecks: data.totalChecks || 0,
    }
  } catch (err) {
    console.error('Failed to fetch security stats:', err)
    error.value = '보안 통계 데이터를 불러오는 중 오류가 발생했습니다.'

    // 오류 발생 시 대체 데이터 사용
    securityStats.value = {
      lastAuditDate: '데이터 없음',
      criticalIssues: 0,
      completedChecks: 0,
      totalChecks: 0,
    }
  } finally {
    loading.value = false
  }
}

// 파일 다운로드 처리
const downloadHomeScript = async () => {
  downloadLoading.value = true
  try {
    // TODO: 실제 다운로드 API 구현
    await new Promise((resolve) => setTimeout(resolve, 1000)) // 시뮬레이션
    console.log('홈 스크립트 다운로드')
  } catch (err) {
    console.error('다운로드 오류:', err)
  } finally {
    downloadLoading.value = false
  }
}

const downloadScript = async () => {
  downloadLoading.value = true
  try {
    // TODO: 실제 다운로드 API 구현
    await new Promise((resolve) => setTimeout(resolve, 1000)) // 시뮬레이션
    console.log('스크립트 다운로드')
  } catch (err) {
    console.error('다운로드 오류:', err)
  } finally {
    downloadLoading.value = false
  }
}

// 초기 설정 완료 표시 함수
const markSetupAsDone = () => {
  localStorage.setItem('initialSetupDone', 'true')
  initialSetupDone.value = true
}

// 사용자 상태 변화 감지
watch(
  () => authStore.user,
  (newUser) => {
    if (newUser) {
      fetchSecurityStats()
    } else {
      // 로그아웃 시 데이터 초기화
      securityStats.value = {
        lastAuditDate: '',
        criticalIssues: 0,
        completedChecks: 0,
        totalChecks: 0,
      }
    }
  },
  { immediate: true },
)

// 라이프사이클 훅
onMounted(() => {
  checkInitialSetup()
  // 나중에 사용자 로그인 상태를 확인한 후 데이터를 가져오도록 수정
  // fetchSecurityStats()
})
</script>

<style scoped>
/* 대시보드 페이지 스타일 */
.dashboard-page {
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

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e0e4e9;
  width: 100%;
}

.welcome-message h1 {
  font-size: 24px;
  font-weight: 600;
  color: #3949ab;
  margin-bottom: 8px;
}

.welcome-message p {
  font-size: 15px;
  color: #5a6a7e;
}

.security-status {
  text-align: right;
}

.status-label {
  font-size: 14px;
  color: #5a6a7e;
  margin-bottom: 6px;
}

.status-value {
  font-weight: 600;
  color: #3949ab;
}

.progress-bar {
  width: 150px;
  height: 6px;
  background-color: #e0e4e9;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #4caf50;
  border-radius: 3px;
}

.dashboard-main {
  margin-bottom: 24px;
  width: 100%;
}

.dashboard-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 24px;
  margin-bottom: 24px;
  width: 100%;
  border: 1px solid #e0e4e9;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.card-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #3949ab;
}

.date-info {
  font-size: 14px;
  color: #7f8c9d;
}

.date-info.important {
  font-weight: 600;
  color: #e74c3c;
}

.loading-indicator {
  padding: 20px;
  text-align: center;
}

.error-message {
  padding: 20px;
  color: #f44336;
}

.retry-button {
  padding: 8px 16px;
  margin-top: 10px;
  background-color: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.status-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.metric-item {
  text-align: center;
  padding: 16px;
  background-color: #eef1fd;
  border-radius: 6px;
  transition: transform 0.2s ease;
}

.metric-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.metric-value {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
}

.metric-value.critical {
  color: #e74c3c;
}

.metric-value.success {
  color: #27ae60;
}

.metric-value.info {
  color: #3498db;
}

.metric-label {
  font-size: 14px;
  color: #5a6a7e;
  font-weight: 500;
}

.card-footer {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
  text-align: right;
}

.view-details-link {
  color: #4056b7;
  font-size: 15px;
  font-weight: 500;
  text-decoration: none;
}

.view-details-link:hover {
  text-decoration: underline;
}

.setup-content.simple p {
  font-size: 16px;
  line-height: 1.5;
  color: #3949ab;
  margin-bottom: 16px;
}

.setup-note {
  background-color: #f8f9fa;
  border-radius: 6px;
  padding: 16px 20px;
  margin-bottom: 24px;
}

.setup-note ul {
  margin: 0;
  padding-left: 24px;
}

.setup-note li {
  margin-bottom: 8px;
  color: #5a6a7e;
  line-height: 1.5;
  font-size: 15px;
}

.setup-actions.simple {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 24px;
  justify-content: flex-start;
}

.download-button {
  padding: 12px 20px;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
  background-color: #4056b7;
  color: white;
}

.download-button:hover {
  background-color: #3949ab;
}

.setup-complete-button {
  background-color: transparent;
  border: 1px solid #4056b7;
  color: #4056b7;
  padding: 12px 20px;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.setup-complete-button:hover {
  background-color: #eef1fd;
}

.not-logged-info {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 32px;
  margin-bottom: 24px;
  text-align: center;
  width: 100%;
  border: 1px solid #e0e4e9;
}

.info-icon {
  margin-bottom: 20px;
  color: #4056b7;
}

.not-logged-info h2 {
  font-size: 20px;
  font-weight: 600;
  color: #3949ab;
  margin-bottom: 12px;
}

.not-logged-info p {
  font-size: 15px;
  color: #5a6a7e;
  margin-bottom: 24px;
  line-height: 1.5;
}

.login-page-button {
  background-color: #4056b7;
  color: white;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 500;
  text-decoration: none;
  display: inline-block;
  transition: background-color 0.3s;
}

.login-page-button:hover {
  background-color: #3949ab;
}

.help-section {
  text-align: center;
}

.help-section h3 {
  font-size: 18px;
  font-weight: 600;
  color: #3949ab;
  margin-bottom: 12px;
}

.help-section p {
  font-size: 15px;
  color: #6a6057;
  line-height: 1.5;
}

.inline-link {
  color: #4056b7;
  text-decoration: none;
  font-weight: 500;
}

.inline-link:hover {
  text-decoration: underline;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .security-status {
    width: 100%;
    text-align: left;
    margin-top: 16px;
  }

  .progress-bar {
    width: 100%;
  }

  .status-metrics {
    grid-template-columns: repeat(2, 1fr);
  }

  .setup-actions.simple {
    flex-direction: column;
    width: 100%;
  }

  .download-button,
  .setup-complete-button {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .status-metrics {
    grid-template-columns: 1fr;
  }

  .metric-item {
    padding: 12px;
  }

  .metric-value {
    font-size: 28px;
  }
}
</style>
