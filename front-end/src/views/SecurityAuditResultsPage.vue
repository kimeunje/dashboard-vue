<!-- views/SecurityAuditResults.vue -->
<template>
  <div>
    <h1 class="page-title">보안 감사 결과</h1>

    <!-- 요약 통계 카드 -->
    <div class="section">
      <h2 class="section-title">요약 통계</h2>
      <div class="stats-grid">
        <StatsCard
          title="총 점검 항목"
          :value="stats.totalChecks"
          :subtitle="`최근 업데이트: ${formatDate(stats.lastCheckedAt)}`"
        />

        <StatsCard
          title="통과"
          :value="stats.passedChecks"
          :subtitle="`통과율: ${
            stats.totalChecks > 0 ? Math.round((stats.passedChecks / stats.totalChecks) * 100) : 0
          }%`"
          value-color="color-green"
        />

        <StatsCard
          title="실패"
          :value="stats.failedChecks"
          :subtitle="`실패율: ${
            stats.totalChecks > 0 ? Math.round((stats.failedChecks / stats.totalChecks) * 100) : 0
          }%`"
          value-color="color-red"
        />

        <StatsCard
          title="보안 점수"
          :value="stats.score"
          subtitle="총점: 100"
          value-color="color-blue"
        />
      </div>
    </div>

    <!-- 일별 통계 시각화 -->
    <div class="section">
      <h2 class="section-title">일별 검사 결과</h2>
      <div v-if="dailyStats.length > 0">
        <!-- 차트 영역 -->
        <div class="chart-container">
          <BarChart :data="dailyStats" :margin="{ top: 20, right: 30, left: 20, bottom: 5 }">
            <CartesianGrid stroke-dasharray="3 3" />
            <XAxis data-key="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar data-key="passed" name="통과" fill="#4caf50" stack-id="a" />
            <Bar data-key="failed" name="실패" fill="#f44336" stack-id="a" />
          </BarChart>
        </div>

        <!-- 일별 통계 테이블 -->
        <div class="table-container">
          <table class="stats-table">
            <thead>
              <tr>
                <th>날짜</th>
                <th>통과</th>
                <th>실패</th>
                <th>통과율</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(day, index) in dailyStats" :key="index">
                <td>{{ day.date }}</td>
                <td class="success">{{ day.passed }}</td>
                <td class="error">{{ day.failed }}</td>
                <td>{{ day.passRate }}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div v-else class="no-data">
        <p>일별 검사 결과 데이터가 없습니다.</p>
      </div>
    </div>

    <!-- 항목별 상세 결과 테이블 -->
    <div class="section">
      <h2 class="section-title">항목별 검사 결과</h2>
      <div v-if="itemStats.length > 0" class="table-container">
        <table class="stats-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>항목명</th>
              <th>카테고리</th>
              <th>통과</th>
              <th>실패</th>
              <th>통과율</th>
              <th>상세</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in itemStats" :key="item.id">
              <td>{{ item.id }}</td>
              <td class="item-name">{{ item.name }}</td>
              <td class="category">{{ item.category }}</td>
              <td class="success">{{ item.passed }}</td>
              <td class="error">{{ item.failed }}</td>
              <td>
                <div class="progress-cell">
                  <div class="progress-bar-container">
                    <div
                      class="progress-bar-fill"
                      :style="{
                        width: `${item.passRate}%`,
                        backgroundColor: getProgressColor(item.passRate),
                      }"
                    ></div>
                  </div>
                  <span class="progress-text">{{ item.passRate }}%</span>
                </div>
              </td>
              <td>
                <button @click="selectItem(item.id)" class="detail-button">상세보기</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="no-data">
        <p>항목별 검사 결과 데이터가 없습니다.</p>
      </div>
    </div>

    <!-- 선택된 항목 상세 정보 -->
    <div v-if="selectedItem" class="section">
      <div class="detail-header">
        <div>
          <h2 class="section-title">{{ selectedItem.name }} 상세 정보</h2>
          <p class="detail-description">{{ selectedItem.description }}</p>
        </div>
        <button @click="closeDetail" class="close-button">닫기</button>
      </div>

      <!-- 항목 상세 로그 -->
      <div v-if="selectedItemLogs.length > 0" class="table-container">
        <table class="stats-table">
          <thead>
            <tr>
              <th>검사 일시</th>
              <th>결과</th>
              <th>실제 값</th>
              <th>메모</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in selectedItemLogs" :key="log.log_id">
              <td>{{ formatDate(log.checked_at) }}</td>
              <td>
                <span :class="['status-badge', log.passed === 1 ? 'success' : 'error']">
                  {{ log.passed === 1 ? '통과' : '실패' }}
                </span>
              </td>
              <td class="actual-value">
                <div
                  v-if="log.actual_value && typeof log.actual_value === 'object'"
                  v-for="[key, value] in Object.entries(log.actual_value)"
                  :key="key"
                >
                  {{ key }}: {{ value }}
                </div>
              </td>
              <td class="notes">
                <pre>{{ log.notes }}</pre>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="no-data">
        <p>이 항목에 대한 상세 로그 데이터가 없습니다.</p>
      </div>
    </div>

    <!-- 관리자 연락처 -->
    <div class="section">
      <h2 class="section-title">관리자 연락처</h2>
      <p>보안 감사 결과에 대한 문의사항이 있는 경우 아래 담당자에게 문의하세요:</p>
      <p>보안 감사팀: 내선 5678 또는 security-audit@example.com</p>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>데이터를 로딩 중입니다...</p>
    </div>

    <!-- 에러 상태 -->
    <div v-if="error" class="error-container">
      <p>{{ error }}</p>
      <button @click="fetchData" class="retry-button">다시 시도</button>
    </div>

    <!-- 공통 페이지 네비게이션 컴포넌트 사용 -->
    <PageNavigation :current-path="route.path" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts'
import StatsCard from '@/components/StatsCard.vue'
import PageNavigation from '@/components/PageNavigation.vue'

// Vue Router
const route = useRoute()

// Pinia Store
const authStore = useAuthStore()

// 반응형 데이터
const stats = ref({
  totalChecks: 0,
  passedChecks: 0,
  failedChecks: 0,
  lastCheckedAt: '',
  score: 0,
})

const checklistItems = ref([])
const auditLogs = ref([])
const selectedItemId = ref(null)
const dailyStats = ref([])
const itemStats = ref([])
const loading = ref(true)
const error = ref(null)

// 계산된 속성
const selectedItem = computed(() => {
  return checklistItems.value.find((item) => item.id === selectedItemId.value)
})

const selectedItemLogs = computed(() => {
  if (!selectedItemId.value) return []

  return auditLogs.value
    .filter((log) => log.item_id === selectedItemId.value)
    .sort((a, b) => new Date(b.checked_at) - new Date(a.checked_at))
})

// 메서드
const fetchData = async () => {
  if (!authStore.user) return

  loading.value = true
  error.value = null

  try {
    // 병렬로 API 요청 보내기
    const [logsResponse, checklistResponse] = await Promise.all([
      fetch('/api/security-audit/logs', {
        credentials: 'include',
      }),
      fetch('/api/security-audit/checklist-items', {
        credentials: 'include',
      }),
    ])

    // 응답 확인
    if (!logsResponse.ok) {
      throw new Error(`Logs API error: ${logsResponse.status}`)
    }

    if (!checklistResponse.ok) {
      throw new Error(`Checklist API error: ${checklistResponse.status}`)
    }

    // 데이터 파싱
    const logsData = await logsResponse.json()
    const checklistData = await checklistResponse.json()

    console.log('로그 데이터:', logsData)
    console.log('체크리스트 데이터:', checklistData)

    // 체크리스트 데이터 변환
    const formattedChecklistItems = checklistData.map((item) => ({
      id: item.item_id,
      name: item.name || item.item_name, // API 응답에 따라 조정
      category: item.category,
      description: item.description,
    }))

    // 상태 업데이트
    auditLogs.value = logsData
    checklistItems.value = formattedChecklistItems
  } catch (err) {
    console.error('Failed to fetch data:', err)
    error.value = '데이터를 불러오는 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.'
  } finally {
    loading.value = false
  }
}

const calculateStats = () => {
  if (auditLogs.value.length === 0 || checklistItems.value.length === 0) return

  // 통계 계산
  const totalChecks = auditLogs.value.length
  const passedChecks = auditLogs.value.filter((log) => log.passed === 1).length
  const failedChecks = auditLogs.value.filter((log) => log.passed === 0).length

  // 가장 최근 검사 날짜
  const sortedLogs = [...auditLogs.value].sort(
    (a, b) => new Date(b.checked_at) - new Date(a.checked_at),
  )
  const lastCheckedAt = sortedLogs.length > 0 ? sortedLogs[0].checked_at : ''

  // 점수 계산 (통과율 * 100)
  const score = totalChecks > 0 ? Math.round((passedChecks / totalChecks) * 100) : 0

  stats.value = {
    totalChecks,
    passedChecks,
    failedChecks,
    lastCheckedAt,
    score,
  }

  // 일별 통계 준비
  prepareDailyStats()

  // 항목별 통계 준비
  prepareItemStats()
}

const prepareDailyStats = () => {
  // 날짜별로 로그를 그룹화
  const groupedByDate = {}

  auditLogs.value.forEach((log) => {
    const dateOnly = log.checked_at.split(' ')[0]
    if (!groupedByDate[dateOnly]) {
      groupedByDate[dateOnly] = { date: dateOnly, passed: 0, failed: 0 }
    }

    if (log.passed === 1) {
      groupedByDate[dateOnly].passed += 1
    } else if (log.passed === 0) {
      groupedByDate[dateOnly].failed += 1
    }
  })

  // 날짜순으로 정렬
  const sortedDates = Object.values(groupedByDate).sort(
    (a, b) => new Date(a.date) - new Date(b.date),
  )

  // 차트 데이터 구조 조정
  const chartData = sortedDates.map((day) => {
    const total = day.passed + day.failed
    const passRate = total > 0 ? Math.round((day.passed / total) * 100) : 0

    return {
      ...day,
      passRate,
      total,
    }
  })

  dailyStats.value = chartData
}

const prepareItemStats = () => {
  const itemStatsData = checklistItems.value.map((item) => {
    const itemLogs = auditLogs.value.filter((log) => log.item_id === item.id)
    const passedCount = itemLogs.filter((log) => log.passed === 1).length
    const failedCount = itemLogs.filter((log) => log.passed === 0).length
    const totalCount = passedCount + failedCount
    const passRate = totalCount > 0 ? (passedCount / totalCount) * 100 : 0

    return {
      id: item.id,
      name: item.name,
      category: item.category,
      description: item.description,
      total: totalCount,
      passed: passedCount,
      failed: failedCount,
      passRate: Math.round(passRate),
    }
  })

  itemStats.value = itemStatsData
}

const formatDate = (dateStr) => {
  if (!dateStr) return '데이터 없음'

  const date = new Date(dateStr)
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const getProgressColor = (passRate) => {
  if (passRate >= 70) return '#4caf50'
  if (passRate >= 40) return '#ff9800'
  return '#f44336'
}

const selectItem = (itemId) => {
  selectedItemId.value = itemId
}

const closeDetail = () => {
  selectedItemId.value = null
}

// 사용자 상태 감지
watch(
  () => authStore.user,
  (newUser) => {
    if (newUser) {
      fetchData()
    }
  },
  { immediate: true },
)

// 데이터 로드 후 통계 계산
watch(
  [auditLogs, checklistItems],
  () => {
    calculateStats()
  },
  { deep: true },
)

// 라이프사이클 훅
onMounted(() => {
  if (authStore.user) {
    fetchData()
  }
})
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 10px;
}

.chart-container {
  height: 300px;
  margin-top: 10px;
}

.table-container {
  margin-top: 20px;
  overflow-x: auto;
}

.stats-table {
  width: 100%;
  border-collapse: collapse;
}

.stats-table thead {
  background-color: #f5f5f5;
}

.stats-table th,
.stats-table td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.stats-table .item-name {
  font-weight: 500;
}

.stats-table .category {
  color: #666;
}

.stats-table .success {
  color: #4caf50;
}

.stats-table .error {
  color: #f44336;
}

.progress-cell {
  display: flex;
  align-items: center;
}

.progress-bar-container {
  width: 100%;
  background-color: #e0e0e0;
  height: 8px;
  border-radius: 4px;
  margin-right: 8px;
}

.progress-bar-fill {
  height: 8px;
  border-radius: 4px;
}

.progress-text {
  font-size: 0.875rem;
}

.detail-button {
  color: #2196f3;
  border: none;
  background: none;
  cursor: pointer;
  padding: 5px;
  text-decoration: underline;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #e3f2fd;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 4px;
}

.detail-description {
  font-size: 0.875rem;
  color: #666;
}

.close-button {
  color: #666;
  border: none;
  background: none;
  cursor: pointer;
  padding: 5px 10px;
  font-size: 0.875rem;
}

.status-badge {
  padding: 2px 8px;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 12px;
}

.status-badge.success {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.status-badge.error {
  background-color: #ffebee;
  color: #c62828;
}

.actual-value {
  color: #666;
}

.notes pre {
  font-size: 0.75rem;
  background-color: #f5f5f5;
  padding: 4px;
  border-radius: 4px;
  font-family: monospace;
  white-space: pre-wrap;
}

.no-data {
  padding: 20px;
  text-align: center;
  color: #666;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.loading-spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4056b7;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

.error-container {
  padding: 20px;
  color: #f44336;
  background-color: #ffebee;
  border-radius: 4px;
  margin: 20px 0;
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

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
