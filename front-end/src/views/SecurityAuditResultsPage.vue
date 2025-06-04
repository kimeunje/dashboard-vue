<!-- SecurityAuditResultsPage.vue Template - 제외 설정 반영 버전 -->
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
        <div class="page-header">
          <h1 class="page-title">보안 감사 결과 및 감점 현황</h1>
        </div>

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

          <!-- 요약 통계 카드 (제외 항목 정보 추가) -->
          <div class="section">
            <h2 class="section-title">
              {{ getTabTitle() }} 감점 요약
              <span v-if="activeTab !== 'all'" class="tab-indicator">{{ getTabSubtitle() }}</span>
            </h2>
            <div class="stats-grid">
              <StatsCard
                title="총 점검 항목"
                :value="currentStats.totalChecks"
                :subtitle="`전체 항목 (제외: ${currentStats.excludedItems || 0}개)`"
              />

              <!-- 활성 점검 항목 표시 -->
              <StatsCard
                title="활성 점검 항목"
                :value="getActiveChecks()"
                :subtitle="`실제 점검 대상 항목`"
                value-color="blue"
              />

              <StatsCard
                title="통과"
                :value="currentStats.completedChecks"
                :subtitle="`통과 항목 (${getPassRate()}%)`"
                value-color="green"
              />

              <StatsCard
                title="실패"
                :value="currentStats.criticalIssues"
                :subtitle="`실패 항목 (${getFailRate()}%)`"
                value-color="red"
              />

              <!-- 감점 표시 -->
              <StatsCard
                title="총 감점"
                :value="formatPenalty(currentStats.totalPenalty)"
                :subtitle="getPenaltyDescription(currentStats.totalPenalty)"
                value-color="orange"
              />
            </div>
          </div>

          <!-- 일별 감점 시각화 -->
          <div class="section" v-if="currentDailyStats.length > 0">
            <h2 class="section-title">{{ getTabTitle() }} 일별 감점 현황</h2>
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
                      <div class="chart-penalty">-{{ day.penalty }}점</div>
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
                  <div class="legend-item">
                    <div class="legend-color penalty"></div>
                    <span>감점</span>
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
                      <th>감점</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(day, index) in currentDailyStats" :key="index">
                      <td>{{ day.date }}</td>
                      <td class="passed-count">{{ day.passed }}</td>
                      <td class="failed-count">{{ day.failed }}</td>
                      <td>{{ day.passRate }}%</td>
                      <td class="penalty-count">-{{ day.penalty }}점</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- 데이터 없음 상태 (일별 통계) -->
          <div v-else class="section">
            <h2 class="section-title">{{ getTabTitle() }} 일별 감점 현황</h2>
            <div class="no-data">
              <p>{{ getTabTitle() }} 검사 결과 데이터가 없습니다.</p>
            </div>
          </div>

          <!-- 항목별 상세 결과 테이블 (제외 설정 정보 추가) -->
          <div class="section">
            <h2 class="section-title">{{ getTabTitle() }} 항목별 검사 결과 및 감점</h2>
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
                <div class="header-cell">감점</div>
                <div class="header-cell">제외</div>
                <!-- 제외 상태 -->
                <div class="header-cell">상세</div>
              </div>

              <div v-for="item in currentItemStats" :key="item.id" class="item-row-container">
                <!-- 항목 정보 행 (제외 정보 추가) -->
                <div
                  class="item-row"
                  :class="{ expanded: selectedItemId === item.id, excluded: item.isExcluded }"
                >
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
                          :class="getPenaltyClass(item.penalty)"
                        ></div>
                      </div>
                      <span class="progress-text">{{ item.passRate }}%</span>
                    </div>
                  </div>
                  <!-- 감점 표시 -->
                  <div class="item-cell penalty-cell">
                    <span class="penalty-value" :class="getPenaltyClass(item.penalty)">
                      {{ formatPenalty(item.penalty) }}
                    </span>
                    <div class="penalty-info">
                      ({{ item.penaltyWeight }}점 × {{ item.failed }}개)
                    </div>
                  </div>
                  <!-- 제외 상태 표시 -->
                  <div class="item-cell excluded-cell">
                    <span v-if="item.isExcluded" class="excluded-badge" :title="item.excludeReason">
                      <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                        <path
                          d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"
                        />
                        <path
                          d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"
                        />
                      </svg>
                      제외
                    </span>
                    <span v-else class="included-badge">포함</span>
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

                <!-- 선택된 항목의 상세 정보 (제외 설정 정보 추가) -->
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
                        <span class="meta-item">
                          <strong>감점 가중치:</strong> {{ item.penaltyWeight }}점/실패
                        </span>
                        <span class="meta-item">
                          <strong>현재 감점:</strong> {{ formatPenalty(item.penalty) }}
                        </span>
                        <!-- 제외 설정 정보 -->
                        <span v-if="item.isExcluded" class="meta-item exclusion-info">
                          <strong>제외 설정:</strong> {{ item.excludeReason }}
                          <span class="exclusion-type"
                            >({{ getExclusionTypeText(item.exclusionType) }})</span
                          >
                        </span>
                      </div>
                    </div>
                  </div>

                  <!-- 항목 상세 로그 (제외 정보 추가) -->
                  <div v-if="getItemLogs(item.id).length > 0" class="logs-table-container-inline">
                    <table class="logs-table">
                      <thead>
                        <tr>
                          <th>검사 일시</th>
                          <th>결과</th>
                          <th>실제 값</th>
                          <th>감점</th>
                          <th>제외</th>
                          <!-- 제외 상태 -->
                          <th>메모</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-for="log in getItemLogs(item.id)"
                          :key="log.log_id"
                          :class="{ 'excluded-row': log.is_excluded }"
                        >
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
                          <!-- 감점 표시 (제외 설정 반영) -->
                          <td class="penalty-applied">
                            <span
                              v-if="log.is_excluded"
                              class="excluded-penalty"
                              title="제외 설정으로 인해 감점 없음"
                            >
                              0점 (제외)
                            </span>
                            <span v-else-if="log.passed === 0" class="penalty-value">
                              -{{ log.penalty_applied || log.penalty_weight || 0.5 }}점
                            </span>
                            <span v-else class="no-penalty">0점</span>
                          </td>
                          <!-- 제외 상태 -->
                          <td class="exclusion-status">
                            <span
                              v-if="log.is_excluded"
                              class="excluded-indicator"
                              :title="log.exclude_reason || '제외 설정 적용'"
                            >
                              <svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                                <path
                                  d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"
                                />
                                <path
                                  d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"
                                />
                              </svg>
                              제외
                            </span>
                            <span v-else class="included-indicator">포함</span>
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
import '@/assets/styles/views/SecurityAuditResultsPage.css'

// Pinia Store
const authStore = useAuthStore()

// 반응형 데이터
const loading = ref(false)
const error = ref(null)
const activeTab = ref('daily') // 'daily', 'manual', 'all'

// 통계 데이터 (제외 설정 정보 포함)
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

// 로그 데이터 (탭별, 제외 설정 정보 포함)
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

// 항목별 통과/실패 통계 - 탭별 (제외 설정 정보 포함)
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
      activeChecks: 0, // 실제 점검 대상 항목 수
      completedChecks: 0, // 통과 항목
      criticalIssues: 0, // 실패 항목 (감점 대상)
      lastCheckedAt: '',
      totalPenalty: 0, // 총 감점
      excludedItems: 0, // 제외된 항목 수
    }
  )
})

const currentDailyStats = computed(() => {
  return dailyStats.value[activeTab.value] || []
})

const currentItemStats = computed(() => {
  return itemStats.value[activeTab.value] || []
})

// 통계 계산 함수들 (제외 항목 반영)
const getActiveChecks = () => {
  return (
    currentStats.value.activeChecks ||
    currentStats.value.totalChecks - (currentStats.value.excludedItems || 0)
  )
}

const getPassedCount = () => {
  return currentStats.value.completedChecks || 0
}

const getFailedCount = () => {
  return currentStats.value.criticalIssues || 0
}

const getPassRate = () => {
  const activeChecks = getActiveChecks()
  const passedCount = getPassedCount()
  if (activeChecks === 0) return 0
  return Math.round((passedCount / activeChecks) * 100)
}

const getFailRate = () => {
  const activeChecks = getActiveChecks()
  const failedCount = getFailedCount()
  if (activeChecks === 0) return 0
  return Math.round((failedCount / activeChecks) * 100)
}

const getTotalPenalty = () => {
  return (currentStats.value.totalPenalty || 0).toFixed(1)
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

    // 로그 데이터 설정 (제외 설정 정보 포함)
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

    // 각 탭별 통계 계산 (제외 설정 반영)
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
    penaltyWeight: item.penalty_weight || 0.5, // 감점 가중치
  }))
}

// 통계 계산 (제외 설정 반영)
const calculateAllStats = () => {
  ;['daily', 'manual', 'all'].forEach((tabType) => {
    const logs = auditLogs.value[tabType]
    const totalChecks = logs.length

    // 제외 설정을 반영한 통과/실패 계산
    const passedChecks = logs.filter((log) => log.passed === 1 && !log.is_excluded).length
    const failedChecks = logs.filter((log) => log.passed === 0 && !log.is_excluded).length
    const excludedChecks = logs.filter((log) => log.is_excluded).length
    const activeChecks = passedChecks + failedChecks // 제외되지 않은 실제 점검 항목

    // 가장 최근 검사 날짜
    const sortedLogs = [...logs].sort((a, b) => new Date(b.checked_at) - new Date(a.checked_at))
    const lastCheckedAt = sortedLogs.length > 0 ? sortedLogs[0].checked_at : ''

    // 감점 계산 (제외된 항목은 감점에서 제외)
    let totalPenalty = 0
    logs.forEach((log) => {
      if (log.passed === 0 && !log.is_excluded) {
        totalPenalty += log.penalty_applied || log.penalty_weight || 0.5
      }
    })

    stats.value[tabType] = {
      totalChecks,
      activeChecks, // 실제 점검 대상 항목 수
      completedChecks: passedChecks,
      criticalIssues: failedChecks, // 제외된 항목 제외
      lastCheckedAt,
      totalPenalty: totalPenalty,
      excludedItems: excludedChecks, // 제외된 항목 수
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
        groupedByDate[dateOnly] = {
          date: dateOnly,
          passed: 0,
          failed: 0,
          penalty: 0, // 감점 추가
        }
      }

      if (log.passed === 1 && !log.is_excluded) {
        groupedByDate[dateOnly].passed += 1
      } else if (log.passed === 0 && !log.is_excluded) {
        // 제외된 항목은 실패로 카운트하지 않음
        groupedByDate[dateOnly].failed += 1
        // 감점 누적 (제외된 항목은 감점에서 제외)
        groupedByDate[dateOnly].penalty += log.penalty_applied || log.penalty_weight || 0.5
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
        penalty: Math.round(day.penalty * 10) / 10, // 감점 반올림
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

      // 제외 설정 정보 확인 (최근 로그 기준)
      const latestLog = itemLogs.sort((a, b) => new Date(b.checked_at) - new Date(a.checked_at))[0]
      const isExcluded = latestLog ? latestLog.is_excluded : false
      const excludeReason = latestLog ? latestLog.exclude_reason : null
      const exclusionType = latestLog ? latestLog.exception_type : null

      // 감점 계산 (제외된 항목은 감점에서 제외)
      const actualFailedCount = itemLogs.filter(
        (log) => log.passed === 0 && !log.is_excluded,
      ).length
      const penalty = actualFailedCount * (item.penaltyWeight || 0.5)

      return {
        id: item.id,
        name: item.name,
        category: item.category,
        description: item.description,
        checkType: item.checkType,
        penaltyWeight: item.penaltyWeight,
        total: totalCount,
        passed: passedCount,
        failed: failedCount,
        passRate: Math.round(passRate),
        penalty: Math.round(penalty * 10) / 10,
        isExcluded: isExcluded, // 제외 설정 여부
        excludeReason: excludeReason, // 제외 사유
        exclusionType: exclusionType, // 제외 유형
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

// 진행률 클래스를 감점 클래스로 변경
const getPenaltyClass = (penalty) => {
  if (penalty === 0) return 'no-penalty'
  if (penalty <= 1.0) return 'low-penalty'
  if (penalty <= 2.5) return 'medium-penalty'
  return 'high-penalty'
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

// 수시 점검용 실제 값 포맷팅 (기존 유지)
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

// 감점 포맷팅 함수
const formatPenalty = (penalty) => {
  return penalty ? `-${penalty}점` : '0점'
}

const getPenaltyDescription = (penalty) => {
  if (penalty === 0) return '감점 없음'
  if (penalty <= 1.0) return '경미한 감점'
  if (penalty <= 2.5) return '주의 필요'
  return '즉시 개선 필요'
}

// 제외 유형 텍스트 변환
const getExclusionTypeText = (exclusionType) => {
  switch (exclusionType) {
    case 'user':
      return '사용자별 제외'
    case 'user_extended':
      return '사용자별 확장 제외'
    case 'department':
      return '부서별 제외'
    case 'department_extended':
      return '부서별 확장 제외'
    default:
      return '제외 설정'
  }
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
