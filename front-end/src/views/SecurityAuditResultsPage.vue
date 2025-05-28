<!-- views/SecurityAuditResultsPage.vue - Template -->
<template>
  <div class="security-audit-layout">
    <!-- 모바일 메뉴 토글 버튼 -->
    <button
      v-if="sidebarRef?.isMobile"
      @click="sidebarRef?.toggleSidebar()"
      class="mobile-menu-toggle"
    >
      <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
        <path
          fill-rule="evenodd"
          d="M2.5 12a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5z"
        />
      </svg>
    </button>

    <!-- 사이드바 -->
    <Sidebar ref="sidebarRef" />

    <!-- 메인 콘텐츠 -->
    <main class="main-content">
      <div v-if="!authStore.user" class="not-authenticated">
        <div class="auth-warning">
          <div class="warning-icon">
            <svg width="48" height="48" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"
              />
            </svg>
          </div>
          <h2>인증이 필요합니다</h2>
          <p>보안 감사 결과를 확인하려면 로그인이 필요합니다.</p>
          <div class="auth-actions">
            <RouterLink to="/login" class="login-button">
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
              로그인하기
            </RouterLink>
          </div>
        </div>
      </div>

      <!-- 인증된 사용자용 콘텐츠 -->
      <div v-else>
        <h1 class="page-title">보안 감사 결과</h1>

        <!-- 로딩 상태 -->
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>데이터를 불러오는 중...</p>
        </div>

        <!-- 에러 상태 -->
        <div v-else-if="error" class="error-container">
          <div class="error-icon">⚠️</div>
          <h3>데이터 로드 실패</h3>
          <p>{{ error }}</p>
          <button @click="fetchData" class="retry-button">다시 시도</button>
        </div>

        <!-- 데이터 표시 -->
        <div v-else>
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
                :subtitle="`통과율: ${getPassRate()}%`"
                value-color="green"
              />

              <StatsCard
                title="실패"
                :value="stats.failedChecks"
                :subtitle="`실패율: ${getFailRate()}%`"
                value-color="red"
              />

              <StatsCard
                title="보안 점수"
                :value="stats.score"
                subtitle="총점: 3"
                value-color="blue"
              />
            </div>
          </div>

          <!-- 일별 통계 시각화 -->
          <div class="section">
            <h2 class="section-title">일별 검사 결과</h2>
            <div v-if="dailyStats.length > 0" class="daily-stats-container">
              <!-- 차트 영역 -->
              <div class="chart-container">
                <div class="chart-area">
                  <div class="chart-bars">
                    <div
                      v-for="(day, index) in dailyStats"
                      :key="index"
                      class="chart-bar-group"
                    >
                      <div class="chart-bars-container">
                        <div
                          class="chart-bar passed"
                          :style="{ height: `${(day.passed / getMaxValue()) * 100}%` }"
                        ></div>
                        <div
                          class="chart-bar failed"
                          :style="{ height: `${(day.failed / getMaxValue()) * 100}%` }"
                        ></div>
                      </div>
                      <div class="chart-label">{{ formatChartDate(day.date) }}</div>
                    </div>
                  </div>
                </div>

                <!-- 범례 -->
                <div class="chart-legend">
                  <div class="legend-item">
                    <div class="legend-color passed"></div>
                    <span>통과</span>
                  </div>
                  <div class="legend-item">
                    <div class="legend-color failed"></div>
                    <span>실패</span>
                  </div>
                </div>
              </div>

              <!-- 일별 통계 테이블 -->
              <div class="daily-stats-table">
                <table>
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
                      <td class="passed-count">{{ day.passed }}</td>
                      <td class="failed-count">{{ day.failed }}</td>
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
            <div v-if="itemStats.length > 0" class="items-container">
              <!-- 테이블 헤더 -->
              <div class="items-header">
                <div class="header-cell">ID</div>
                <div class="header-cell">항목명</div>
                <div class="header-cell">카테고리</div>
                <div class="header-cell">통과</div>
                <div class="header-cell">실패</div>
                <div class="header-cell">통과율</div>
                <div class="header-cell">상세</div>
              </div>

              <div v-for="item in itemStats" :key="item.id" class="item-row-container">
                <!-- 항목 정보 행 -->
                <div class="item-row" :class="{ 'expanded': selectedItemId === item.id }">
                  <div class="item-cell item-id">{{ item.id }}</div>
                  <div class="item-cell item-name">{{ item.name }}</div>
                  <div class="item-cell item-category">{{ item.category }}</div>
                  <div class="item-cell passed-count">{{ item.passed }}</div>
                  <div class="item-cell failed-count">{{ item.failed }}</div>
                  <div class="item-cell">
                    <div class="progress-container">
                      <div class="progress-bar">
                        <div
                          class="progress-fill"
                          :style="{ width: `${item.passRate}%` }"
                          :class="getProgressClass(item.passRate)"
                        ></div>
                      </div>
                      <span class="progress-text">{{ item.passRate }}%</span>
                    </div>
                  </div>
                  <div class="item-cell">
                    <button
                      @click="toggleItemDetail(item.id)"
                      class="detail-button"
                      :class="{ 'active': selectedItemId === item.id }"
                    >
                      {{ selectedItemId === item.id ? '닫기' : '상세보기' }}
                    </button>
                  </div>
                </div>

                <!-- 선택된 항목의 상세 정보 (바로 아래 표시) -->
                <div v-if="selectedItemId === item.id" class="item-detail-container">
                  <div class="detail-header-inline">
                    <div class="detail-info">
                      <h3 class="detail-title">{{ item.name }} 상세 정보</h3>
                      <p class="detail-description">{{ item.description }}</p>
                    </div>
                  </div>

                  <!-- 항목 상세 로그 -->
                  <div v-if="getItemLogs(item.id).length > 0" class="logs-table-container-inline">
                    <table class="logs-table">
                      <thead>
                        <tr>
                          <th>검사 일시</th>
                          <th>결과</th>
                          <th>실제 값</th>
                          <th>메모</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="log in getItemLogs(item.id)" :key="log.log_id">
                          <td>{{ formatDate(log.checked_at) }}</td>
                          <td>
                            <span
                              class="result-badge"
                              :class="log.passed === 1 ? 'passed' : 'failed'"
                            >
                              {{ log.passed === 1 ? '통과' : '실패' }}
                            </span>
                          </td>
                          <td class="actual-value">
                            <div v-if="log.actual_value && typeof log.actual_value === 'object'">
                              <div v-for="(value, key) in log.actual_value" :key="key">
                                {{ key }}: {{ value }}
                              </div>
                            </div>
                            <span v-else>{{ log.actual_value || '-' }}</span>
                          </td>
                          <td>
                            <pre class="log-notes">{{ log.notes || '-' }}</pre>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  <div v-else class="no-data-inline">
                    <p>이 항목에 대한 상세 로그 데이터가 없습니다.</p>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="no-data">
              <p>항목별 검사 결과 데이터가 없습니다.</p>
            </div>
          </div>

          <!-- 관리자 연락처 -->
          <!-- <div class="section">
            <h2 class="section-title">관리자 연락처</h2>
            <div class="contact-info">
              <p>보안 감사 결과에 대한 문의사항이 있는 경우 아래 담당자에게 문의하세요:</p>
              <div class="contact-details">
                <div class="contact-item">
                  <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M3.654 1.328a.678.678 0 0 0-1.015-.063L1.605 2.3c-.483.484-.661 1.169-.45 1.77a17.568 17.568 0 0 0 4.168 6.608 17.569 17.569 0 0 0 6.608 4.168c.601.211 1.286.033 1.77-.45l1.034-1.034a.678.678 0 0 0-.063-1.015l-2.307-1.794a.678.678 0 0 0-.58-.122L9.98 10.4a.678.678 0 0 1-.615-.04L7.6 9.39a.678.678 0 0 1-.215-.176L6.417 8.246a.678.678 0 0 1-.176-.215L5.27 6.266a.678.678 0 0 1-.04-.615l.969-1.805a.678.678 0 0 0-.122-.58L3.654 1.328z"/>
                  </svg>
                  <span>보안 감사팀: 내선 5678</span>
                </div>
                <div class="contact-item">
                  <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M2 2a2 2 0 0 0-2 2v8.01A2 2 0 0 0 2 14h5.5a.5.5 0 0 0 0-1H2a1 1 0 0 1-.966-.741l5.64-3.471L8 9.583l7-4.2V8.5a.5.5 0 0 0 1 0V4a2 2 0 0 0-2-2H2Zm3.708 6.208L1 11.105V5.383l4.708 2.825ZM1 4.217V4a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v.217l-7 4.2-7-4.2Z"/>
                    <path d="M14.247 14.269c1.01 0 1.587-.857 1.587-2.025v-.21C15.834 10.43 14.64 9 12.52 9h-.035C10.42 9 9 10.36 9 12.432v.214C9 14.82 10.438 16 12.358 16h.044c.594 0 1.018-.074 1.237-.175v-.73c-.245.11-.673.18-1.18.18h-.044c-1.334 0-2.571-.788-2.571-2.655v-.157c0-1.657 1.058-2.724 2.64-2.724h.04c1.535 0 2.484 1.05 2.484 2.326v.118c0 .975-.324 1.39-.639 1.39-.232 0-.41-.148-.41-.42v-2.19h-.906v.569h-.03c-.084-.298-.368-.61-.954-.61-.778 0-1.259.555-1.259 1.4v.528c0 .892.49 1.434 1.26 1.434.471 0 .896-.227 1.014-.643h.043c.118.42.617.648 1.12.648Zm-2.453-1.588v-.227c0-.546.227-.791.573-.791.297 0 .572.192.572.708v.367c0 .573-.253.744-.564.744-.354 0-.581-.215-.581-.8Z"/>
                  </svg>
                  <span>security-audit@example.com</span>
                </div>
              </div>
            </div>
          </div> -->
        </div>

        <!-- 페이지 네비게이션 -->
        <PageNavigation current-path="/security-audit/results" />
      </div>
    </main>
  </div>
</template>
<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Sidebar from '@/components/Sidebar.vue'
import StatsCard from '@/components/StatsCard.vue'
import PageNavigation from '@/components/PageNavigation.vue'

// Pinia Store
const authStore = useAuthStore()

// 반응형 데이터
const loading = ref(false)
const error = ref(null)

// 통계 데이터
const stats = ref({
  totalChecks: 0,
  passedChecks: 0,
  failedChecks: 0,
  lastCheckedAt: '',
  score: 0
})

// 보안 점검 항목 데이터
const checklistItems = ref([])

// 로그 데이터
const auditLogs = ref([])

// 선택된 항목 ID
const selectedItemId = ref(null)

// 시간별로 그룹화된 로그 (최근 7일)
const dailyStats = ref([])

// 항목별 통과/실패 통계
const itemStats = ref([])

// Sidebar ref
const sidebarRef = ref(null)

// 계산된 속성
const isAuthenticated = computed(() => !!authStore.user)

const getPassRate = () => {
  if (stats.value.totalChecks === 0) return 0
  return Math.round((stats.value.passedChecks / stats.value.totalChecks) * 100)
}

const getFailRate = () => {
  if (stats.value.totalChecks === 0) return 0
  return Math.round((stats.value.failedChecks / stats.value.totalChecks) * 100)
}

const getMaxValue = () => {
  if (dailyStats.value.length === 0) return 1
  return Math.max(...dailyStats.value.map(day => Math.max(day.passed, day.failed)))
}

const selectedItem = computed(() => {
  return checklistItems.value.find(item => item.id === selectedItemId.value)
})

const selectedItemLogs = computed(() => {
  if (!selectedItemId.value) return []
  return auditLogs.value
    .filter(log => log.item_id === selectedItemId.value)
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
        credentials: 'include'
      }),
      fetch('/api/security-audit/checklist-items', {
        credentials: 'include'
      })
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

    // 체크리스트 데이터 변환 (API 응답 형식에 맞게 조정)
    const formattedChecklistItems = checklistData.map(item => ({
      id: item.item_id,
      name: item.name || item.item_name,
      category: item.category,
      description: item.description
    }))

    // 상태 업데이트
    auditLogs.value = logsData
    checklistItems.value = formattedChecklistItems

    // 통계 계산
    calculateStats()
    prepareDailyStats()
    prepareItemStats()

  } catch (err) {
    console.error('Failed to fetch data:', err)
    error.value = '데이터를 불러오는 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.'
  } finally {
    loading.value = false
  }
}

const calculateStats = () => {
  const totalChecks = auditLogs.value.length
  const passedChecks = auditLogs.value.filter(log => log.passed === 1).length
  const failedChecks = auditLogs.value.filter(log => log.passed === 0).length

  // 가장 최근 검사 날짜
  const sortedLogs = [...auditLogs.value].sort(
    (a, b) => new Date(b.checked_at) - new Date(a.checked_at)
  )
  const lastCheckedAt = sortedLogs.length > 0 ? sortedLogs[0].checked_at : ''

  // 점수 계산 (통과율 * 100)
  // const score = totalChecks > 0 ? Math.round((passedChecks / totalChecks) * 100) : 0
   const score = Math.max(0, 3 - (failedChecks * 0.5))

  stats.value = {
    totalChecks,
    passedChecks,
    failedChecks,
    lastCheckedAt,
    score
  }
}

const prepareDailyStats = () => {
  // 날짜별로 로그를 그룹화
  const groupedByDate = {}

  auditLogs.value.forEach(log => {
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
    (a, b) => new Date(a.date) - new Date(b.date)
  )

  // 차트에서 사용하기 쉽게 데이터 구조 조정
  const chartData = sortedDates.map(day => {
    const total = day.passed + day.failed
    const passRate = total > 0 ? Math.round((day.passed / total) * 100) : 0

    return {
      ...day,
      passRate,
      total
    }
  })

  dailyStats.value = chartData
}

const prepareItemStats = () => {
  const itemStatsData = checklistItems.value.map(item => {
    const itemLogs = auditLogs.value.filter(log => log.item_id === item.id)
    const passedCount = itemLogs.filter(log => log.passed === 1).length
    const failedCount = itemLogs.filter(log => log.passed === 0).length
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
      passRate: Math.round(passRate)
    }
  })

  itemStats.value = itemStatsData
}

const setSelectedItemId = (itemId) => {
  selectedItemId.value = itemId
}

const toggleItemDetail = (itemId) => {
  if (selectedItemId.value === itemId) {
    selectedItemId.value = null
  } else {
    selectedItemId.value = itemId
  }
}

const getItemLogs = (itemId) => {
  return auditLogs.value
    .filter(log => log.item_id === itemId)
    .sort((a, b) => new Date(b.checked_at) - new Date(a.checked_at))
}

const getProgressClass = (rate) => {
  if (rate >= 70) return 'excellent'
  if (rate >= 40) return 'good'
  return 'poor'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '데이터 없음'

  const date = new Date(dateStr)
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatChartDate = (dateStr) => {
  if (!dateStr) return ''

  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

// 라이프사이클 훅
onMounted(() => {
  if (authStore.user) {
    fetchData()
  }
})

// 인증 상태 변경 감지
watch(() => authStore.user, (newUser) => {
  if (newUser) {
    fetchData()
  } else {
    // 로그아웃 시 데이터 초기화
    stats.value = {
      totalChecks: 0,
      passedChecks: 0,
      failedChecks: 0,
      lastCheckedAt: '',
      score: 0
    }
    checklistItems.value = []
    auditLogs.value = []
    dailyStats.value = []
    itemStats.value = []
    selectedItemId.value = null
  }
})
</script>
<style scoped>
.security-audit-layout {
  display: flex;
  background-color: var(--bright-bg);
  min-height: calc(100vh - 114px);
}

.main-content {
  flex: 1;
  padding: 30px;
  background-color: var(--content-bg);
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  margin: 20px;
}

/* 인증 관련 스타일 */
.not-authenticated {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

.auth-warning {
  text-align: center;
  padding: 40px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border: 1px solid #fee2e2;
}

.warning-icon {
  color: #f59e0b;
  margin-bottom: 20px;
}

.auth-warning h2 {
  color: var(--dark-blue);
  margin-bottom: 12px;
  font-size: 1.5rem;
}

.auth-warning p {
  color: #6b7280;
  margin-bottom: 24px;
  font-size: 1rem;
}

.login-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background-color: var(--primary-color);
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
}

.login-button:hover {
  background-color: var(--dark-blue);
  transform: translateY(-2px);
}

/* 로딩 및 에러 상태 */
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
  transition: background-color 0.3s ease;
}

.retry-button:hover {
  background-color: var(--dark-blue);
}

/* 통계 카드 그리드 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

/* 일별 통계 컨테이너 */
.daily-stats-container {
  margin-top: 20px;
}

.chart-container {
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
}

.chart-area {
  height: 300px;
  margin-bottom: 20px;
}

.chart-bars {
  display: flex;
  align-items: end;
  justify-content: space-around;
  height: 250px;
  padding: 20px 0;
}

.chart-bar-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 60px;
}

.chart-bars-container {
  display: flex;
  align-items: end;
  gap: 4px;
  height: 200px;
  margin-bottom: 10px;
}

.chart-bar {
  width: 20px;
  min-height: 4px;
  border-radius: 4px 4px 0 0;
  transition: height 0.3s ease;
}

.chart-bar.passed {
  background-color: #10b981;
}

.chart-bar.failed {
  background-color: #ef4444;
}

.chart-label {
  font-size: 12px;
  font-weight: 500;
  color: #6b7280;
  text-align: center;
}

.chart-legend {
  display: flex;
  justify-content: center;
  gap: 24px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #374151;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.legend-color.passed {
  background-color: #10b981;
}

.legend-color.failed {
  background-color: #ef4444;
}

/* 일별 통계 테이블 */
.daily-stats-table {
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.daily-stats-table table {
  width: 100%;
  border-collapse: collapse;
}

.daily-stats-table th {
  background-color: #f9fafb;
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.daily-stats-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #f3f4f6;
}

.daily-stats-table tbody tr:hover {
  background-color: #f9fafb;
}

.passed-count {
  color: #10b981;
  font-weight: 600;
}

.failed-count {
  color: #ef4444;
  font-weight: 600;
}

/* 항목별 테이블 - 새로운 구조 */
.items-container {
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  margin-top: 20px;
}

.item-row-container {
  border-bottom: 1px solid #f3f4f6;
}

.item-row-container:last-child {
  border-bottom: none;
}

.item-row {
  display: grid;
  grid-template-columns: 80px 1fr 120px 80px 80px 150px 100px;
  align-items: center;
  padding: 12px 16px;
  transition: all 0.2s ease;
  cursor: pointer;
  background-color: white;
}

.item-row:hover {
  background-color: #f9fafb;
}

.item-row.expanded {
  background-color: #f0f9ff;
  border-bottom: 1px solid #e0f2fe;
}

.item-cell {
  padding: 4px 8px;
  display: flex;
  align-items: center;
}

.item-id {
  font-weight: 500;
  color: #6b7280;
  font-size: 0.875rem;
}

.item-name {
  font-weight: 500;
  color: var(--dark-blue);
}

.item-category {
  color: #6b7280;
  font-size: 0.875rem;
}

.passed-count {
  color: #10b981;
  font-weight: 600;
}

.failed-count {
  color: #ef4444;
  font-weight: 600;
}

.detail-button {
  color: var(--primary-color);
  background: none;
  border: 1px solid transparent;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  width: 100%;
}

.detail-button:hover {
  background-color: var(--light-blue);
  border-color: var(--primary-color);
}

.detail-button.active {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

/* 인라인 상세 정보 */
.item-detail-container {
  background-color: #f8fafc;
  border-top: 1px solid #e2e8f0;
  padding: 20px;
  animation: slideDown 0.3s ease-out;
}

.detail-header-inline {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.detail-title {
  margin: 0 0 8px 0;
  color: var(--dark-blue);
  font-size: 1.1rem;
  font-weight: 600;
}

.detail-description {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
  line-height: 1.5;
}

.logs-table-container-inline {
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
}

.no-data-inline {
  text-align: center;
  padding: 20px;
  color: #6b7280;
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
}

.no-data-inline p {
  margin: 0;
  font-size: 0.875rem;
}

/* 테이블 헤더 추가 */
.items-container::before {
  content: '';
  display: block;
  background-color: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.items-header {
  display: grid;
  grid-template-columns: 80px 1fr 120px 80px 80px 150px 100px;
  background-color: #f9fafb;
  padding: 12px 16px;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.header-cell {
  padding: 4px 8px;
  font-size: 0.875rem;
}

/* 애니메이션 */
@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
    padding: 0 20px;
  }
  to {
    opacity: 1;
    max-height: 500px;
    padding: 20px;
  }
}

.progress-container {
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
  min-width: 80px;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-fill.excellent {
  background-color: #10b981;
}

.progress-fill.good {
  background-color: #f59e0b;
}

.progress-fill.poor {
  background-color: #ef4444;
}

.progress-text {
  font-size: 0.875rem;
  font-weight: 500;
  min-width: 40px;
}

.detail-button {
  color: var(--primary-color);
  background: none;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  text-decoration: underline;
  transition: all 0.2s ease;
}

.detail-button:hover {
  background-color: var(--light-blue);
  text-decoration: none;
}

/* 상세 정보 섹션 */
.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background-color: #e3f2fd;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.detail-info {
  flex: 1;
}

.detail-description {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 8px 0 0 0;
  line-height: 1.5;
}

.close-button {
  color: #6b7280;
  background: none;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.close-button:hover {
  background-color: rgba(0, 0, 0, 0.05);
  color: #374151;
}

/* 로그 테이블 */
.logs-table-container {
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.logs-table {
  width: 100%;
  border-collapse: collapse;
}

.logs-table th {
  background-color: #f9fafb;
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.logs-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #f3f4f6;
  vertical-align: top;
}

.logs-table tbody tr:hover {
  background-color: #f9fafb;
}

.result-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.result-badge.passed {
  background-color: #d1fae5;
  color: #065f46;
}

.result-badge.failed {
  background-color: #fee2e2;
  color: #991b1b;
}

.actual-value {
  color: #6b7280;
  font-size: 0.875rem;
  max-width: 200px;
}

.log-notes {
  font-size: 0.75rem;
  background-color: #f5f5f5;
  padding: 8px;
  border-radius: 4px;
  font-family: monospace;
  white-space: pre-wrap;
  max-width: 250px;
  overflow-wrap: break-word;
}

/* 연락처 정보 */
.contact-info {
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 24px;
  margin-top: 20px;
}

.contact-info p {
  margin-bottom: 16px;
  color: #374151;
  line-height: 1.6;
}

.contact-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--primary-color);
  font-weight: 500;
}

.contact-item svg {
  flex-shrink: 0;
}

/* 데이터 없음 상태 */
.no-data {
  text-align: center;
  padding: 40px 20px;
  color: #6b7280;
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-top: 20px;
}

.no-data p {
  margin: 0;
  font-size: 1rem;
}

/* 모바일 메뉴 토글 버튼 */
.mobile-menu-toggle {
  position: fixed;
  bottom: 20px;
  left: 20px;
  z-index: 1001;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.2s ease;
}

.mobile-menu-toggle:hover {
  background-color: var(--dark-blue);
  transform: scale(1.05);
}

/* 애니메이션 */
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
  .security-audit-layout {
    flex-direction: column;
  }

  .main-content {
    margin: 20px;
  }
}

@media (max-width: 768px) {
  .mobile-menu-toggle {
    display: block;
  }

  .main-content {
    padding: 20px;
    margin: 10px;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
  }

  .chart-bars {
    overflow-x: auto;
    justify-content: flex-start;
    gap: 16px;
    padding: 20px 10px;
  }

  .chart-bar-group {
    min-width: 50px;
  }

  .chart-bars-container {
    height: 150px;
  }

  .items-container,
  .logs-table-container,
  .daily-stats-table {
    overflow-x: auto;
  }

  .items-header,
  .item-row {
    grid-template-columns: 60px 1fr 100px 60px 60px 120px 80px;
    min-width: 600px;
  }

  .item-detail-container {
    padding: 16px;
  }

  .logs-table-container-inline {
    overflow-x: auto;
  }

  .logs-table {
    min-width: 600px;
  }

  .detail-header {
    flex-direction: column;
    gap: 16px;
  }

  .close-button {
    align-self: flex-end;
  }

  .contact-details {
    gap: 8px;
  }

  .contact-item {
    font-size: 0.875rem;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .chart-legend {
    flex-direction: column;
    gap: 12px;
  }

  .progress-container {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .progress-bar {
    width: 100%;
  }

  .chart-bar-group {
    min-width: 40px;
  }

  .chart-bars-container {
    height: 120px;
  }
}

@media (min-width: 769px) {
  .mobile-menu-toggle {
    display: none;
  }
}
</style>
