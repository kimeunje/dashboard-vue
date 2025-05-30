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
          <!-- 점검 유형 탭 -->
          <div class="section">
            <div class="tabs-container">
              <div class="tabs-header">
                <button
                  @click="activeTab = 'daily'"
                  class="tab-button"
                  :class="{ active: activeTab === 'daily' }"
                >
                  <svg width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                    <path
                      d="M8 3.5a.5.5 0 0 0-1 0V9a.5.5 0 0 0 .252.434l3.5 2a.5.5 0 0 0 .496-.868L8 8.71V3.5z"
                    />
                    <path
                      d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm7-8A7 7 0 1 1 1 8a7 7 0 0 1 14 0z"
                    />
                  </svg>
                  정기 점검
                  <span class="tab-count">{{ stats.daily?.totalChecks || 0 }}개 항목</span>
                </button>

                <button
                  @click="activeTab = 'manual'"
                  class="tab-button"
                  :class="{ active: activeTab === 'manual' }"
                >
                  <svg width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                    <path
                      d="M9.405 1.05c-.413-1.4-2.397-1.4-2.81 0l-.1.34a1.464 1.464 0 0 1-2.105.872l-.31-.17c-1.283-.698-2.686.705-1.987 1.987l.169.311c.446.82.023 1.841-.872 2.105l-.34.1c-1.4.413-1.4 2.397 0 2.81l.34.1a1.464 1.464 0 0 1 .872 2.105l-.17.31c-.698 1.283.705 2.686 1.987 1.987l.311-.169a1.464 1.464 0 0 1 2.105.872l.1.34c.413 1.4 2.397 1.4 2.81 0l.1-.34a1.464 1.464 0 0 1 2.105-.872l.31.17c1.283.698 2.686-.705 1.987-1.987l-.169-.311a1.464 1.464 0 0 1 .872-2.105l.34-.1c1.4-.413 1.4-2.397 0-2.81l-.34-.1a1.464 1.464 0 0 1-.872-2.105l.17-.31c.698-1.283-.705-2.686-1.987-1.987l-.311.169a1.464 1.464 0 0 1-2.105-.872l-.1-.34zM8 10.93a2.929 2.929 0 1 1 0-5.86 2.929 2.929 0 0 1 0 5.858z"
                    />
                  </svg>
                  수시 점검
                  <span class="tab-count">{{ stats.manual?.totalChecks || 0 }}개 항목</span>
                </button>

                <button
                  @click="activeTab = 'all'"
                  class="tab-button"
                  :class="{ active: activeTab === 'all' }"
                >
                  <svg width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                    <path
                      d="M1.5 1.5A.5.5 0 0 1 2 1h12a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-.128.334L10 8.692V13.5a.5.5 0 0 1-.342.474l-3 1A.5.5 0 0 1 6 14.5V8.692L1.628 3.834A.5.5 0 0 1 1.5 3.5v-2z"
                    />
                  </svg>
                  전체 결과
                  <span class="tab-count">{{ stats.all?.totalChecks || 0 }}개 항목</span>
                </button>
              </div>
            </div>
          </div>

          <!-- 요약 통계 카드 -->
          <div class="section">
            <h2 class="section-title">
              {{ getTabTitle() }} 요약 통계
              <span v-if="activeTab !== 'all'" class="tab-indicator">{{ getTabSubtitle() }}</span>
            </h2>
            <div class="stats-grid">
              <StatsCard
                title="총 점검 항목"
                :value="currentStats.totalChecks"
                :subtitle="`최근 업데이트: ${formatDate(currentStats.lastCheckedAt)}`"
              />

              <StatsCard
                title="통과"
                :value="currentStats.passedChecks"
                :subtitle="`통과율: ${getPassRate()}%`"
                value-color="green"
              />

              <StatsCard
                title="실패"
                :value="currentStats.failedChecks"
                :subtitle="`실패율: ${getFailRate()}%`"
                value-color="red"
              />

              <StatsCard title="감점" :value="currentStats.score" subtitle="" value-color="blue" />
            </div>
          </div>

          <!-- 일별 통계 시각화 -->
          <div class="section" v-if="currentDailyStats.length > 0">
            <h2 class="section-title">{{ getTabTitle() }} 일별 검사 결과</h2>
            <div class="daily-stats-container">
              <!-- 차트 영역 -->
              <div class="chart-container">
                <div class="chart-area">
                  <div class="chart-bars">
                    <div
                      v-for="(day, index) in currentDailyStats"
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
                    <tr v-for="(day, index) in currentDailyStats" :key="index">
                      <td>{{ day.date }}</td>
                      <td class="passed-count">{{ day.passed }}</td>
                      <td class="failed-count">{{ day.failed }}</td>
                      <td>{{ day.passRate }}%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- 데이터 없음 상태 (일별 통계) -->
          <div v-else class="section">
            <h2 class="section-title">{{ getTabTitle() }} 일별 검사 결과</h2>
            <div class="no-data">
              <p>{{ getTabTitle() }} 검사 결과 데이터가 없습니다.</p>
            </div>
          </div>

          <!-- 항목별 상세 결과 테이블 -->
          <div class="section">
            <h2 class="section-title">{{ getTabTitle() }} 항목별 검사 결과</h2>
            <div v-if="currentItemStats.length > 0" class="items-container">
              <!-- 테이블 헤더 -->
              <div class="items-header">
                <div class="header-cell">ID</div>
                <div class="header-cell">항목명</div>
                <div class="header-cell">카테고리</div>
                <div class="header-cell">점검 유형</div>
                <div class="header-cell">통과</div>
                <div class="header-cell">실패</div>
                <div class="header-cell">통과율</div>
                <div class="header-cell">상세</div>
              </div>

              <div v-for="item in currentItemStats" :key="item.id" class="item-row-container">
                <!-- 항목 정보 행 -->
                <div class="item-row" :class="{ expanded: selectedItemId === item.id }">
                  <div class="item-cell item-id">{{ item.id }}</div>
                  <div class="item-cell item-name">{{ item.name }}</div>
                  <div class="item-cell item-category">{{ item.category }}</div>
                  <div class="item-cell">
                    <span class="check-type-badge" :class="item.checkType">
                      {{ item.checkType === 'daily' ? '정기' : '수시' }}
                    </span>
                  </div>
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
                      :class="{ active: selectedItemId === item.id }"
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
                      <div class="detail-meta">
                        <span class="meta-item">
                          <strong>점검 유형:</strong>
                          {{
                            item.checkType === 'daily'
                              ? '정기 점검 (매일 자동)'
                              : '수시 점검 (수동 실행)'
                          }}
                        </span>
                        <span class="meta-item">
                          <strong>카테고리:</strong> {{ item.category }}
                        </span>
                      </div>
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
                                {{ formatActualValueKey(key) }}: {{ formatActualValueValue(value) }}
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
              <p>{{ getTabTitle() }} 검사 결과 데이터가 없습니다.</p>
            </div>
          </div>
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
const activeTab = ref('daily') // 'daily', 'manual', 'all'

// 통계 데이터 (탭별)
const stats = ref({
  daily: null,
  manual: null,
  all: null,
})

// 보안 점검 항목 데이터 (탭별)
const checklistItems = ref({
  daily: [],
  manual: [],
  all: [],
})

// 로그 데이터 (탭별)
const auditLogs = ref({
  daily: [],
  manual: [],
  all: [],
})

// 선택된 항목 ID
const selectedItemId = ref(null)

// 시간별로 그룹화된 로그 (최근 7일) - 탭별
const dailyStats = ref({
  daily: [],
  manual: [],
  all: [],
})

// 항목별 통과/실패 통계 - 탭별
const itemStats = ref({
  daily: [],
  manual: [],
  all: [],
})

// Sidebar ref
const sidebarRef = ref(null)

// 계산된 속성
const isAuthenticated = computed(() => !!authStore.user)

const currentStats = computed(() => {
  return (
    stats.value[activeTab.value] || {
      totalChecks: 0,
      passedChecks: 0,
      failedChecks: 0,
      lastCheckedAt: '',
      score: 0,
    }
  )
})

const currentDailyStats = computed(() => {
  return dailyStats.value[activeTab.value] || []
})

const currentItemStats = computed(() => {
  return itemStats.value[activeTab.value] || []
})

const getPassRate = () => {
  if (currentStats.value.totalChecks === 0) return 0
  return Math.round((currentStats.value.passedChecks / currentStats.value.totalChecks) * 100)
}

const getFailRate = () => {
  if (currentStats.value.totalChecks === 0) return 0
  return Math.round((currentStats.value.failedChecks / currentStats.value.totalChecks) * 100)
}

const getMaxValue = () => {
  if (currentDailyStats.value.length === 0) return 1
  return Math.max(...currentDailyStats.value.map((day) => Math.max(day.passed, day.failed)))
}

// 탭 관련 메서드
const getTabTitle = () => {
  switch (activeTab.value) {
    case 'daily':
      return '정기 점검'
    case 'manual':
      return '수시 점검'
    case 'all':
      return '전체'
    default:
      return '정기 점검'
  }
}

const getTabSubtitle = () => {
  switch (activeTab.value) {
    case 'daily':
      return '매일 자동 실행'
    case 'manual':
      return '관리자 수동 실행'
    default:
      return ''
  }
}

// 메서드
const fetchData = async () => {
  if (!authStore.user) return

  loading.value = true
  error.value = null

  try {
    // 모든 탭의 데이터를 병렬로 가져오기
    const [
      dailyLogsResponse,
      manualLogsResponse,
      allLogsResponse,
      dailyChecklistResponse,
      manualChecklistResponse,
      allChecklistResponse,
    ] = await Promise.all([
      fetch('/api/security-audit/logs?type=daily', { credentials: 'include' }),
      fetch('/api/security-audit/logs?type=manual', { credentials: 'include' }),
      fetch('/api/security-audit/logs', { credentials: 'include' }),
      fetch('/api/security-audit/checklist-items?type=daily', { credentials: 'include' }),
      fetch('/api/security-audit/checklist-items?type=manual', { credentials: 'include' }),
      fetch('/api/security-audit/checklist-items', { credentials: 'include' }),
    ])

    // 응답 확인
    const responses = [
      dailyLogsResponse,
      manualLogsResponse,
      allLogsResponse,
      dailyChecklistResponse,
      manualChecklistResponse,
      allChecklistResponse,
    ]
    for (const response of responses) {
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }
    }

    // 데이터 파싱
    const [
      dailyLogsData,
      manualLogsData,
      allLogsData,
      dailyChecklistData,
      manualChecklistData,
      allChecklistData,
    ] = await Promise.all(responses.map((res) => res.json()))

    // 로그 데이터 설정
    auditLogs.value = {
      daily: dailyLogsData,
      manual: manualLogsData,
      all: allLogsData,
    }

    // 체크리스트 데이터 변환 및 설정
    checklistItems.value = {
      daily: formatChecklistItems(dailyChecklistData),
      manual: formatChecklistItems(manualChecklistData),
      all: formatChecklistItems(allChecklistData),
    }

    // 각 탭별 통계 계산
    calculateAllStats()
    prepareAllDailyStats()
    prepareAllItemStats()

    console.log('모든 데이터 로드 완료')
  } catch (err) {
    console.error('Failed to fetch data:', err)
    error.value = '데이터를 불러오는 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.'
  } finally {
    loading.value = false
  }
}

const formatChecklistItems = (checklistData) => {
  return checklistData.map((item) => ({
    id: item.item_id,
    name: item.name || item.item_name,
    category: item.category,
    description: item.description,
    checkType: item.check_type,
    checkFrequency: item.check_frequency,
  }))
}

const calculateAllStats = () => {
  ;['daily', 'manual', 'all'].forEach((tabType) => {
    const logs = auditLogs.value[tabType]
    const totalChecks = logs.length
    const passedChecks = logs.filter((log) => log.passed === 1).length
    const failedChecks = logs.filter((log) => log.passed === 0).length

    // 가장 최근 검사 날짜
    const sortedLogs = [...logs].sort((a, b) => new Date(b.checked_at) - new Date(a.checked_at))
    const lastCheckedAt = sortedLogs.length > 0 ? sortedLogs[0].checked_at : ''

    // 점수 계산
    const score = -(failedChecks * 0.5)

    stats.value[tabType] = {
      totalChecks,
      passedChecks,
      failedChecks,
      lastCheckedAt,
      score,
    }
  })
}

const prepareAllDailyStats = () => {
  ;['daily', 'manual', 'all'].forEach((tabType) => {
    const logs = auditLogs.value[tabType]

    // 날짜별로 로그를 그룹화
    const groupedByDate = {}

    logs.forEach((log) => {
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

    // 차트에서 사용하기 쉽게 데이터 구조 조정
    const chartData = sortedDates.map((day) => {
      const total = day.passed + day.failed
      const passRate = total > 0 ? Math.round((day.passed / total) * 100) : 0

      return {
        ...day,
        passRate,
        total,
      }
    })

    dailyStats.value[tabType] = chartData
  })
}

const prepareAllItemStats = () => {
  ;['daily', 'manual', 'all'].forEach((tabType) => {
    const items = checklistItems.value[tabType]
    const logs = auditLogs.value[tabType]

    const itemStatsData = items.map((item) => {
      const itemLogs = logs.filter((log) => log.item_id === item.id)
      const passedCount = itemLogs.filter((log) => log.passed === 1).length
      const failedCount = itemLogs.filter((log) => log.passed === 0).length
      const totalCount = passedCount + failedCount
      const passRate = totalCount > 0 ? (passedCount / totalCount) * 100 : 0

      return {
        id: item.id,
        name: item.name,
        category: item.category,
        description: item.description,
        checkType: item.checkType,
        total: totalCount,
        passed: passedCount,
        failed: failedCount,
        passRate: Math.round(passRate),
      }
    })

    itemStats.value[tabType] = itemStatsData
  })
}

const toggleItemDetail = (itemId) => {
  if (selectedItemId.value === itemId) {
    selectedItemId.value = null
  } else {
    selectedItemId.value = itemId
  }
}

const getItemLogs = (itemId) => {
  const logs = auditLogs.value[activeTab.value]
  return logs
    .filter((log) => log.item_id === itemId)
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
    minute: '2-digit',
  })
}

const formatChartDate = (dateStr) => {
  if (!dateStr) return ''

  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

// 수시 점검용 실제 값 포맷팅
const formatActualValueKey = (key) => {
  const keyMap = {
    seal_status: '봉인씰 상태',
    check_date: '확인 날짜',
    malware_detected: '악성코드 탐지',
    threats_found: '위협 발견 수',
    last_scan_date: '마지막 검사',
    total_files: '전체 파일',
    encrypted_files: '암호화된 파일',
    encryption_rate: '암호화율',
    screenSaverTime: '화면보호기 시간',
    screenSaverSecure: '보안 설정',
    screenSaverEnabled: '활성화 상태',
    UpToDate: '업데이트',
    DisplayName: '백신명',
    RealTimeProtection: '실시간 보호',
    minimumPasswordLength: '최소 길이',
    passwordComplexity: '복잡도',
    maximumPasswordAge: '변경 주기',
    passwordHistorySize: '이력 크기',
    folders: '공유 폴더',
    fDenyTSConnections: '원격 접속 제한',
  }
  return keyMap[key] || key
}

const formatActualValueValue = (value) => {
  if (typeof value === 'boolean') {
    return value ? '예' : '아니오'
  }
  if (typeof value === 'number') {
    return value.toString()
  }
  if (Array.isArray(value)) {
    return value.join(', ')
  }
  if (value === 'intact') return '정상'
  if (value === 'damaged') return '훼손됨'
  return value
}

// 탭 변경 시 선택된 항목 초기화
watch(activeTab, () => {
  selectedItemId.value = null
})

// 라이프사이클 훅
onMounted(() => {
  if (authStore.user) {
    fetchData()
  }
})

// 인증 상태 변경 감지
watch(
  () => authStore.user,
  (newUser) => {
    if (newUser) {
      fetchData()
    } else {
      // 로그아웃 시 데이터 초기화
      stats.value = {
        daily: null,
        manual: null,
        all: null,
      }
      checklistItems.value = {
        daily: [],
        manual: [],
        all: [],
      }
      auditLogs.value = {
        daily: [],
        manual: [],
        all: [],
      }
      dailyStats.value = {
        daily: [],
        manual: [],
        all: [],
      }
      itemStats.value = {
        daily: [],
        manual: [],
        all: [],
      }
      selectedItemId.value = null
    }
  },
)
</script>

<style scoped>
/* SecurityAuditResultsPage.vue 확장 스타일 */
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

/* 탭 컨테이너 */
.tabs-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.tabs-header {
  display: flex;
  background-color: #f8fafc;
  border-bottom: 1px solid #e5e7eb;
}

.tab-button {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px 20px;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  transition: all 0.3s ease;
  position: relative;
}

.tab-button:hover {
  background-color: #f1f5f9;
  color: #374151;
}

.tab-button.active {
  background-color: white;
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
}

.tab-button.active svg {
  color: var(--primary-color);
}

.tab-count {
  font-size: 0.75rem;
  background-color: #e5e7eb;
  color: #6b7280;
  padding: 2px 8px;
  border-radius: 12px;
  margin-left: 4px;
}

.tab-button.active .tab-count {
  background-color: var(--light-blue);
  color: var(--primary-color);
}

.tab-indicator {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 400;
  margin-left: 8px;
}

/* 점검 유형 배지 */
.check-type-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.check-type-badge.daily {
  background-color: #dbeafe;
  color: #1d4ed8;
}

.check-type-badge.manual {
  background-color: #d1fae5;
  color: #059669;
}

/* 상세 메타 정보 */
.detail-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e5e7eb;
}

.meta-item {
  font-size: 0.875rem;
  color: #6b7280;
}

.meta-item strong {
  color: var(--dark-blue);
}

/* 기존 스타일들 유지 */
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

/* 항목별 테이블 - 확장된 구조 */
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
  grid-template-columns: 80px 1fr 120px 100px 80px 80px 150px 100px;
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

/* 테이블 헤더 */
.items-header {
  display: grid;
  grid-template-columns: 80px 1fr 120px 100px 80px 80px 150px 100px;
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

/* 진행률 바 */
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

/* 로그 테이블 */
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

/* 섹션 및 제목 */
.section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--dark-blue);
  margin-bottom: 20px;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--light-blue);
  display: flex;
  align-items: center;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--dark-blue);
  margin-bottom: 32px;
  text-align: center;
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

/* 반응형 디자인 */
@media (max-width: 1024px) {
  .security-audit-layout {
    flex-direction: column;
  }

  .main-content {
    margin: 20px;
  }

  .tabs-header {
    flex-direction: column;
  }

  .tab-button {
    border-bottom: 1px solid #e5e7eb;
    border-right: none;
  }

  .tab-button.active {
    border-bottom: 1px solid var(--primary-color);
    border-left: 3px solid var(--primary-color);
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
  .logs-table-container-inline,
  .daily-stats-table {
    overflow-x: auto;
  }

  .items-header,
  .item-row {
    grid-template-columns: 60px 1fr 100px 80px 60px 60px 120px 80px;
    min-width: 700px;
  }

  .item-detail-container {
    padding: 16px;
  }

  .logs-table {
    min-width: 600px;
  }

  .tab-button {
    flex-direction: column;
    gap: 4px;
    padding: 12px 16px;
  }

  .tab-count {
    margin-left: 0;
    margin-top: 4px;
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

  .page-title {
    font-size: 1.5rem;
  }

  .section-title {
    font-size: 1.25rem;
    flex-direction: column;
    align-items: flex-start;
  }

  .tab-indicator {
    margin-left: 0;
    margin-top: 4px;
  }
}

@media (min-width: 769px) {
  .mobile-menu-toggle {
    display: none;
  }
}
</style>
