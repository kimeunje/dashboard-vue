<template>
  <div class="admin-dashboard">
    <!-- 헤더 -->
    <div class="admin-header">
      <h1>관리자 대시보드</h1>
      <p>전체 사용자 보안 현황 및 통계를 확인하고 관리하세요</p>

      <!-- 년도 선택 및 컨트롤 -->
      <div class="header-controls">
        <div class="year-selector">
          <label>평가 년도:</label>
          <select v-model="selectedYear" @change="loadDashboardData">
            <option v-for="year in availableYears" :key="year" :value="year">{{ year }}년</option>
          </select>
        </div>
        <div class="action-buttons">
          <button @click="refreshData" class="refresh-btn" :disabled="loading">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M11.534 7h3.932a.25.25 0 0 1 .192.41l-1.966 2.36a.25.25 0 0 1-.384 0l-1.966-2.36a.25.25 0 0 1 .192-.41zm-11 2h3.932a.25.25 0 0 0 .192-.41L2.692 6.23a.25.25 0 0 0-.384 0L.342 8.59A.25.25 0 0 0 .534 9z"
              />
              <path
                d="M8 3c-1.552 0-2.94.707-3.857 1.818a.5.5 0 1 1-.771-.636A6.002 6.002 0 0 1 13.917 7H12.9A5.002 5.002 0 0 0 8 3zM3.1 9a5.002 5.002 0 0 0 8.757 2.182.5.5 0 1 1 .771.636A6.002 6.002 0 0 1 2.083 9H3.1z"
              />
            </svg>
            새로고침
          </button>
          <button @click="exportSummary" class="export-btn" :disabled="loading">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"
              />
              <path
                d="M7.646 1.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 2.707V11.5a.5.5 0 0 1-1 0V2.707L5.354 4.854a.5.5 0 1 1-.708-.708l3-3z"
              />
            </svg>
            데이터 내보내기
          </button>
        </div>
      </div>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>데이터를 불러오는 중...</p>
    </div>

    <!-- 에러 상태 -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">
        <svg width="48" height="48" fill="currentColor" viewBox="0 0 16 16">
          <path
            d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"
          />
        </svg>
      </div>
      <h3>데이터 로드 실패</h3>
      <p>{{ error }}</p>
      <button @click="loadDashboardData" class="retry-btn">다시 시도</button>
    </div>

    <!-- 대시보드 콘텐츠 -->
    <div v-else-if="dashboardData" class="dashboard-content">
      <!-- 1. 전체 통계 카드 -->
      <div class="stats-grid">
        <div class="stat-card total-users">
          <div class="stat-icon">
            <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M15 14s1 0 1-1-1-4-5-4-5 3-5 4 1 1 1 1h8Zm-7.978-1A.261.261 0 0 1 7 12.996c.001-.264.167-1.03.76-1.72C8.312 10.629 9.282 10 11 10c1.717 0 2.687.63 3.24 1.276.593.69.758 1.457.76 1.72l-.008.002A.274.274 0 0 1 15 13H7ZM11 7a2 2 0 1 0 0-4 2 2 0 0 0 0 4Zm3-2a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"
              />
            </svg>
          </div>
          <div class="stat-content">
            <h3>전체 사용자</h3>
            <div class="stat-value">
              {{ formatNumber(dashboardData.user_stats?.total_users || 0) }}
            </div>
            <div class="stat-detail">
              평가완료: {{ formatNumber(dashboardData.user_stats?.evaluated_users || 0) }}명
            </div>
          </div>
        </div>

        <div class="stat-card excellent-users">
          <div class="stat-icon">
            <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"
              />
            </svg>
          </div>
          <div class="stat-content">
            <h3>우수 사용자</h3>
            <div class="stat-value excellent">
              {{ formatNumber(dashboardData.user_stats?.excellent_users || 0) }}
            </div>
            <div class="stat-detail">
              {{
                calculatePercentage(
                  dashboardData.user_stats?.excellent_users,
                  dashboardData.user_stats?.total_users,
                )
              }}%
            </div>
          </div>
        </div>

        <div class="stat-card warning-users">
          <div class="stat-icon">
            <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"
              />
            </svg>
          </div>
          <div class="stat-content">
            <h3>주의 사용자</h3>
            <div class="stat-value warning">
              {{ formatNumber(dashboardData.user_stats?.warning_users || 0) }}
            </div>
            <div class="stat-detail">
              {{
                calculatePercentage(
                  dashboardData.user_stats?.warning_users,
                  dashboardData.user_stats?.total_users,
                )
              }}%
            </div>
          </div>
        </div>

        <div class="stat-card critical-users">
          <div class="stat-icon">
            <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"
              />
            </svg>
          </div>
          <div class="stat-content">
            <h3>위험 사용자</h3>
            <div class="stat-value critical">
              {{ formatNumber(dashboardData.user_stats?.critical_users || 0) }}
            </div>
            <div class="stat-detail">
              {{
                calculatePercentage(
                  dashboardData.user_stats?.critical_users,
                  dashboardData.user_stats?.total_users,
                )
              }}%
            </div>
          </div>
        </div>

        <div class="stat-card avg-penalty">
          <div class="stat-icon">
            <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M1 2.828c.885-.37 2.154-.769 3.388-.893 1.33-.134 2.458.063 3.112.752v9.746c-.935-.53-2.12-.603-3.213-.493-1.18.12-2.37.461-3.287.811V2.828zm7.5-.141c.654-.689 1.782-.886 3.112-.752 1.234.124 2.503.523 3.388.893v9.923c-.918-.35-2.107-.692-3.287-.81-1.094-.111-2.278-.039-3.213.492V2.687zM8 1.783C7.015.936 5.587.81 4.287.94c-1.514.153-3.042.672-3.994 1.105A.5.5 0 0 0 0 2.5v11a.5.5 0 0 0 .707.455c.882-.4 2.303-.881 3.68-1.02 1.409-.142 2.59.087 3.223.877a.5.5 0 0 0 .78 0c.633-.79 1.814-1.019 3.222-.877 1.378.139 2.8.62 3.681 1.02A.5.5 0 0 0 16 13.5v-11a.5.5 0 0 0-.293-.455c-.952-.433-2.48-.952-3.994-1.105C10.413.809 8.985.936 8 1.783z"
              />
            </svg>
          </div>
          <div class="stat-content">
            <h3>평균 감점</h3>
            <div class="stat-value">
              {{ formatDecimal(dashboardData.user_stats?.avg_penalty || 0) }}
            </div>
            <div class="stat-detail">
              최대: {{ formatDecimal(dashboardData.user_stats?.max_penalty || 0) }}점
            </div>
          </div>
        </div>
      </div>

      <!-- 2. 차트 및 분석 섹션 -->
      <div class="charts-row">
        <!-- 보안 점수 분포 차트 -->
        <div class="chart-section">
          <div class="section-header">
            <h3>보안 점수 분포</h3>
            <div class="chart-controls">
              <button @click="toggleChartType" class="chart-type-btn">
                {{ chartType === 'pie' ? '막대차트' : '원형차트' }}
              </button>
            </div>
          </div>
          <div class="chart-container">
            <div class="score-distribution-chart">
              <!-- 점수 분포 데이터 표시 -->
              <div v-if="dashboardData.score_distribution?.length" class="distribution-grid">
                <div
                  v-for="item in dashboardData.score_distribution"
                  :key="item.score_range"
                  class="distribution-item"
                  :class="item.score_range"
                >
                  <div class="range-label">{{ getRangeLabel(item.score_range) }}</div>
                  <div class="range-count">{{ item.user_count }}명</div>
                  <div class="range-percentage">{{ formatDecimal(item.percentage) }}%</div>
                </div>
              </div>
              <div v-else class="no-data">데이터가 없습니다.</div>
            </div>
          </div>
        </div>

        <!-- 월별 트렌드 -->
        <div class="trend-section">
          <div class="section-header">
            <h3>월별 트렌드</h3>
            <select v-model="trendMetric" @change="updateTrendChart" class="trend-select">
              <option value="failure_rate">실패율</option>
              <option value="active_users">활성 사용자</option>
              <option value="total_checks">전체 점검</option>
            </select>
          </div>
          <div class="trend-chart">
            <div v-if="dashboardData.monthly_trends?.length" class="trend-data">
              <div
                v-for="trend in dashboardData.monthly_trends"
                :key="trend.month"
                class="trend-month"
              >
                <div class="month-label">{{ trend.month }}월</div>
                <div class="trend-value">
                  <span v-if="trendMetric === 'failure_rate'"
                    >{{ formatDecimal(trend.failure_rate) }}%</span
                  >
                  <span v-else-if="trendMetric === 'active_users'">{{ trend.active_users }}명</span>
                  <span v-else>{{ trend.total_checks }}건</span>
                </div>
              </div>
            </div>
            <div v-else class="no-data">트렌드 데이터가 없습니다.</div>
          </div>
        </div>
      </div>

      <!-- 3. 부서별/직급별 현황 -->
      <div class="overview-sections">
        <!-- 부서별 현황 -->
        <div class="department-section">
          <div class="section-header">
            <h3>부서별 현황</h3>
            <button @click="exportDepartmentData" class="export-btn">
              <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path
                  d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"
                />
                <path
                  d="M7.646 1.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 2.707V11.5a.5.5 0 0 1-1 0V2.707L5.354 4.854a.5.5 0 1 1-.708-.708l3-3z"
                />
              </svg>
              내보내기
            </button>
          </div>
          <div class="department-grid">
            <div
              v-for="dept in dashboardData.department_overview"
              :key="dept.department"
              class="department-card"
            >
              <div class="dept-header">
                <h4>{{ dept.department }}</h4>
                <span class="user-count">{{ formatNumber(dept.total_users) }}명</span>
              </div>
              <div class="dept-stats">
                <div class="stat-row">
                  <span class="label">평균 감점:</span>
                  <span class="value" :class="getPenaltyClass(dept.avg_penalty)">
                    {{ formatDecimal(dept.avg_penalty) }}점
                  </span>
                </div>
                <div class="dept-distribution">
                  <div class="dist-item excellent">
                    <span class="count">{{ dept.excellent_count }}</span>
                    <span class="label">우수</span>
                  </div>
                  <div class="dist-item warning">
                    <span class="count">{{ dept.warning_count }}</span>
                    <span class="label">주의</span>
                  </div>
                  <div class="dist-item critical">
                    <span class="count">{{ dept.critical_count }}</span>
                    <span class="label">위험</span>
                  </div>
                </div>
                <div class="excellent-rate">우수율: {{ formatDecimal(dept.excellent_rate) }}%</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 직급별 현황 -->
        <div class="position-section">
          <div class="section-header">
            <h3>직급별 현황</h3>
          </div>
          <div class="position-table">
            <table>
              <thead>
                <tr>
                  <th>직급</th>
                  <th>인원</th>
                  <th>평균 감점</th>
                  <th>우수율</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="pos in dashboardData.position_overview" :key="pos.position">
                  <td class="position-name">{{ pos.position }}</td>
                  <td>{{ formatNumber(pos.total_users) }}</td>
                  <td :class="getPenaltyClass(pos.avg_penalty)">
                    {{ formatDecimal(pos.avg_penalty) }}점
                  </td>
                  <td>{{ calculatePercentage(pos.excellent_count, pos.total_users) }}%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- 4. 위험 사용자 및 최근 활동 -->
      <div class="activity-sections">
        <!-- 위험 사용자 -->
        <div class="risk-users-section">
          <div class="section-header">
            <h3>위험 사용자 목록</h3>
            <RouterLink to="/admin/users?risk_level=high" class="view-all-btn">
              전체 보기
            </RouterLink>
          </div>
          <div class="risk-users-list">
            <div
              v-for="user in dashboardData.risk_users"
              :key="user.uid"
              class="risk-user-card"
              @click="viewUserDetail(user.uid)"
            >
              <div class="user-info">
                <div class="user-name">{{ user.name }}</div>
                <div class="user-details">{{ user.department }} · {{ user.position }}</div>
              </div>
              <div class="user-risk">
                <div class="risk-level" :class="user.risk_level">
                  {{ getRiskLevelLabel(user.risk_level) }}
                </div>
                <div class="penalty-score">{{ formatDecimal(user.total_penalty) }}점</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 최근 활동 -->
        <div class="recent-activities-section">
          <div class="section-header">
            <h3>최근 활동</h3>
            <select v-model="activityFilter" @change="filterActivities" class="activity-filter">
              <option value="all">전체</option>
              <option value="success">성공</option>
              <option value="failure">실패</option>
              <option value="pending">대기</option>
            </select>
          </div>
          <div class="activities-list">
            <div
              v-for="activity in filteredActivities"
              :key="`${activity.activity_type}-${activity.activity_time}`"
              class="activity-item"
            >
              <div class="activity-icon" :class="activity.status">
                <svg
                  v-if="activity.status === 'success'"
                  width="16"
                  height="16"
                  fill="currentColor"
                  viewBox="0 0 16 16"
                >
                  <path
                    d="M13.854 3.646a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 10.293l6.646-6.647a.5.5 0 0 1 .708 0z"
                  />
                </svg>
                <svg
                  v-else-if="activity.status === 'failure'"
                  width="16"
                  height="16"
                  fill="currentColor"
                  viewBox="0 0 16 16"
                >
                  <path
                    d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"
                  />
                </svg>
                <svg v-else width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
                </svg>
              </div>
              <div class="activity-content">
                <div class="activity-description">
                  <strong>{{ activity.user_name }}</strong> · {{ activity.department }}
                  <br />
                  {{ activity.activity_description }}
                </div>
                <div class="activity-time">
                  {{ formatDateTime(activity.activity_time) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 5. 빠른 액션 버튼들 -->
      <div class="quick-actions">
        <div class="section-header">
          <h3>빠른 작업</h3>
        </div>
        <div class="action-buttons-grid">
          <RouterLink to="/admin/users" class="action-button">
            <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M15 14s1 0 1-1-1-4-5-4-5 3-5 4 1 1 1 1h8Zm-7.978-1A.261.261 0 0 1 7 12.996c.001-.264.167-1.03.76-1.72C8.312 10.629 9.282 10 11 10c1.717 0 2.687.63 3.24 1.276.593.69.758 1.457.76 1.72l-.008.002A.274.274 0 0 1 15 13H7Z"
              />
            </svg>
            <span>사용자 관리</span>
          </RouterLink>

          <RouterLink to="/admin/training" class="action-button">
            <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M8.5 5a.5.5 0 0 0-1 0v1.5H6a.5.5 0 0 0 0 1h1.5V9a.5.5 0 0 0 1 0V7.5H10a.5.5 0 0 0 0-1H8.5V5z"
              />
              <path
                d="M2 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v13.5a.5.5 0 0 1-.777.416L8 13.101l-5.223 2.815A.5.5 0 0 1 2 15.5V2zm2-1a1 1 0 0 0-1 1v12.566l4.723-2.482a.5.5 0 0 1 .554 0L13 14.566V2a1 1 0 0 0-1-1H4z"
              />
            </svg>
            <span>모의훈련 관리</span>
          </RouterLink>

          <RouterLink to="/admin/exceptions" class="action-button">
            <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M9.405 1.05c-.413-1.4-2.397-1.4-2.81 0l-.1.34a1.464 1.464 0 0 1-2.105.872l-.31-.17c-1.283-.698-2.686.705-1.987 1.987l.169.311c.446.82.023 1.841-.872 2.105l-.34.1c-1.4.413-1.4 2.397 0 2.81l.34.1a1.464 1.464 0 0 1 .872 2.105l-.17.31c-.698 1.283.705 2.686 1.987 1.987l.311-.169a1.464 1.464 0 0 1 2.105.872l.1.34c.413 1.4 2.397 1.4 2.81 0l.1-.34a1.464 1.464 0 0 1 2.105-.872l.31.17c1.283.698 2.686-.705 1.987-1.987l-.169-.311a1.464 1.464 0 0 1 .872-2.105l.34-.1c1.4-.413 1.4-2.397 0-2.81l-.34-.1a1.464 1.464 0 0 1-.872-2.105l.17-.31c.698-1.283-.705-2.686-1.987-1.987l-.311.169a1.464 1.464 0 0 1-2.105-.872l-.1-.34zM8 10.93a2.929 2.929 0 1 1 0-5.86 2.929 2.929 0 0 1 0 5.858z"
              />
            </svg>
            <span>예외 관리</span>
          </RouterLink>

          <button @click="exportDetailed" class="action-button">
            <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M14 14V4.5L9.5 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2zM9.5 3A1.5 1.5 0 0 0 11 4.5h2V14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h5.5v2z"
              />
            </svg>
            <span>상세 보고서</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// 상태 관리
const loading = ref(false)
const error = ref('')
const selectedYear = ref(new Date().getFullYear())
const chartType = ref('pie')
const trendMetric = ref('failure_rate')
const activityFilter = ref('all')
const dashboardData = ref(null)

// 스토어
const authStore = useAuthStore()
const router = useRouter()

// 사용 가능한 년도 목록
const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  const years = []
  for (let i = currentYear; i >= currentYear - 5; i--) {
    years.push(i)
  }
  return years
})

// 필터링된 활동 목록
const filteredActivities = computed(() => {
  if (!dashboardData.value?.recent_activities) return []

  if (activityFilter.value === 'all') {
    return dashboardData.value.recent_activities
  }

  return dashboardData.value.recent_activities.filter(
    (activity) => activity.status === activityFilter.value,
  )
})
// API 객체에 새로운 함수들 추가
const adminAPI = {
  async getDashboardOverview(year, autoCalculate = true) {
    const response = await fetch(
      `/api/admin/dashboard/overview?year=${year}&auto_calculate=${autoCalculate}`,
      {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${authStore.token}`,
          'Content-Type': 'application/json',
        },
      },
    )

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    return await response.json()
  },

  async getCalculationStatus(year) {
    const response = await fetch(`/api/admin/dashboard/calculation-status?year=${year}`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${authStore.token}`,
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`계산 상태 조회 실패: ${response.status}`)
    }

    return await response.json()
  },

  async triggerFullCalculation(year, forceRecalculate = false) {
    const response = await fetch('/api/admin/dashboard/trigger-calculation', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${authStore.token}`,
      },
      body: JSON.stringify({
        year: year,
        force_recalculate: forceRecalculate,
      }),
    })

    if (!response.ok) {
      throw new Error(`계산 실행 실패: ${response.status}`)
    }

    return await response.json()
  },

  // 기존 exportData 함수는 그대로 유지
  async exportData(exportType, format = 'csv') {
    const response = await fetch(
      `/api/admin/dashboard/export?year=${selectedYear.value}&type=${exportType}&format=${format}`,
      {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${authStore.token}`,
        },
      },
    )

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    return response
  },
}

// loadDashboardData 함수 수정
async function loadDashboardData() {
  if (!authStore.isAuthenticated || !isAdmin()) {
    router.push('/login')
    return
  }

  loading.value = true
  error.value = ''

  try {
    console.log(`관리자 대시보드 데이터 로드: ${selectedYear.value}년`)

    // 자동 계산을 포함한 대시보드 데이터 조회
    const data = await adminAPI.getDashboardOverview(selectedYear.value, true) // auto_calculate=true

    dashboardData.value = data

    // 자동 계산된 사용자가 있으면 알림 표시
    if (data.auto_calculated_users > 0) {
      showSuccess(`${data.auto_calculated_users}명의 미계산 사용자 점수가 자동으로 계산되었습니다.`)
    }

    console.log('대시보드 데이터 로드 완료:', data)
  } catch (err) {
    console.error('대시보드 데이터 로드 실패:', err)
    error.value = err.message || '데이터를 불러오는데 실패했습니다.'
  } finally {
    loading.value = false
  }
}

// refreshData 함수 수정 (더 간단하게)
async function refreshData() {
  loading.value = true
  error.value = ''

  try {
    console.log('데이터 새로고침 시작...')

    // 1. 계산 상태 확인
    const statusResponse = await adminAPI.getCalculationStatus(selectedYear.value)
    console.log('계산 상태:', statusResponse)

    // 2. 미계산 사용자가 많으면 사용자에게 알림
    if (statusResponse.missing_users > 10) {
      const confirmCalculate = confirm(
        `${statusResponse.missing_users}명의 미계산 사용자가 있습니다.\n` +
          `전체 계산을 실행하시겠습니까? (시간이 걸릴 수 있습니다)`,
      )

      if (confirmCalculate) {
        await adminAPI.triggerFullCalculation(selectedYear.value, false) // 미계산만
        showSuccess('전체 계산이 완료되었습니다.')
      }
    }

    // 3. 대시보드 데이터 새로고침 (자동 계산 포함)
    await loadDashboardData()
  } catch (err) {
    console.error('새로고침 중 오류:', err)
    error.value = err.message || '새로고침 중 오류가 발생했습니다.'
  } finally {
    loading.value = false
  }
}

// 배치 작업 완료 대기 함수 (새로 추가)
async function waitForBatchCompletion() {
  const maxWaitTime = 30000 // 30초
  const checkInterval = 2000 // 2초마다 확인
  const startTime = Date.now()

  while (Date.now() - startTime < maxWaitTime) {
    try {
      const statusResponse = await fetch('/api/admin/batch/status', {
        headers: {
          Authorization: `Bearer ${authStore.token}`,
        },
      })

      if (statusResponse.ok) {
        const status = await statusResponse.json()

        if (!status.is_running) {
          console.log(
            `배치 작업 완료: 성공 ${status.success_count}명, 실패 ${status.error_count}명`,
          )
          break
        }
      }

      // 2초 대기
      await new Promise((resolve) => setTimeout(resolve, checkInterval))
    } catch (err) {
      console.error('배치 상태 확인 중 오류:', err)
      break
    }
  }
}

function toggleChartType() {
  chartType.value = chartType.value === 'pie' ? 'bar' : 'pie'
}

function updateTrendChart() {
  // 트렌드 차트 업데이트 로직
  console.log('트렌드 메트릭 변경:', trendMetric.value)
}

function filterActivities() {
  // 활동 필터링은 computed로 자동 처리됨
  console.log('활동 필터 변경:', activityFilter.value)
}

// 유틸리티 함수들
function formatNumber(num) {
  return new Intl.NumberFormat('ko-KR').format(num || 0)
}

function formatDecimal(num, decimals = 1) {
  return parseFloat(num || 0).toFixed(decimals)
}

function calculatePercentage(value, total) {
  if (!total || total === 0) return '0.0'
  return ((value / total) * 100).toFixed(1)
}

function formatDateTime(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('ko-KR', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// 위험도 및 감점 관련 함수들
function getRiskLevelColor(level) {
  const colors = {
    low: '#10b981',
    medium: '#f59e0b',
    high: '#ef4444',
    critical: '#dc2626',
    not_evaluated: '#6b7280',
  }
  return colors[level] || '#6b7280'
}

function getRiskLevelLabel(level) {
  const labels = {
    low: '낮음',
    medium: '보통',
    high: '높음',
    critical: '매우 높음',
    not_evaluated: '미평가',
  }
  return labels[level] || '알 수 없음'
}

function getPenaltyClass(penalty) {
  const penaltyNum = parseFloat(penalty || 0)
  if (penaltyNum <= 0.5) return 'penalty-low'
  if (penaltyNum <= 2.0) return 'penalty-medium'
  return 'penalty-high'
}

function getRangeLabel(range) {
  const labels = {
    perfect: '완벽 (0점)',
    excellent: '우수 (0.5점 이하)',
    good: '양호 (1.0점 이하)',
    warning: '주의 (2.0점 이하)',
    danger: '위험 (3.0점 이하)',
    critical: '매우 위험 (3.0점 초과)',
    not_evaluated: '미평가',
  }
  return labels[range] || range
}

// 사용자 관련 함수들
async function viewUserDetail(userId) {
  router.push(`/admin/users/${userId}/detail`)
}

function isAdmin() {
  const userRole = authStore.user?.role || 'user'
  return userRole === 'admin' || authStore.user?.username === 'admin'
}

// 내보내기 함수들
async function exportSummary() {
  try {
    loading.value = true
    const response = await adminAPI.exportData('summary', 'csv')

    // 파일 다운로드 처리
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `관리자_대시보드_요약_${selectedYear.value}.csv`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  } catch (err) {
    console.error('요약 데이터 내보내기 실패:', err)
    error.value = '데이터 내보내기에 실패했습니다.'
  } finally {
    loading.value = false
  }
}

async function exportDetailed() {
  try {
    loading.value = true
    const response = await adminAPI.exportData('detailed', 'csv')

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `사용자_상세_현황_${selectedYear.value}.csv`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  } catch (err) {
    console.error('상세 데이터 내보내기 실패:', err)
    error.value = '상세 데이터 내보내기에 실패했습니다.'
  } finally {
    loading.value = false
  }
}

async function exportDepartmentData() {
  try {
    loading.value = true
    const response = await adminAPI.exportData('department', 'csv')

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `부서별_현황_${selectedYear.value}.csv`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  } catch (err) {
    console.error('부서별 데이터 내보내기 실패:', err)
    error.value = '부서별 데이터 내보내기에 실패했습니다.'
  } finally {
    loading.value = false
  }
}

// 디바운스 함수
function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

// 반응형 데이터 감시
watch(selectedYear, () => {
  loadDashboardData()
})

// 권한 체크
watch(
  () => authStore.user,
  (newUser) => {
    if (!newUser || !isAdmin()) {
      router.push('/login')
    }
  },
  { immediate: true },
)

// 페이지 로드 시 자동으로 계산 상태 확인하는 훅 추가
onMounted(async () => {
  if (authStore.isAuthenticated && isAdmin()) {
    // 계산 상태 먼저 확인
    try {
      const status = await adminAPI.getCalculationStatus(selectedYear.value)
      if (status.missing_users > 0) {
        console.log(`알림: ${status.missing_users}명의 미계산 사용자가 있습니다.`)
      }
    } catch (err) {
      console.warn('계산 상태 확인 실패:', err)
    }

    // 대시보드 데이터 로드 (자동 계산 포함)
    loadDashboardData()
  }
})
// 에러 처리
function handleError(error, context) {
  console.error(`${context} 오류:`, error)
  error.value = `${context} 중 오류가 발생했습니다: ${error.message}`
}

// 성공 메시지 표시 함수 개선
function showSuccess(message) {
  // 간단한 알림 (실제 프로젝트에서는 toast 라이브러리 사용 권장)
  const notification = document.createElement('div')
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: #10b981;
    color: white;
    padding: 12px 20px;
    border-radius: 6px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    z-index: 1000;
    font-size: 14px;
    max-width: 400px;
  `
  notification.textContent = message

  document.body.appendChild(notification)

  // 3초 후 자동 제거
  setTimeout(() => {
    if (notification.parentNode) {
      notification.parentNode.removeChild(notification)
    }
  }, 3000)
}

// 확인 대화상자
function confirmAction(message) {
  return confirm(message)
}

// 데이터 유효성 검사
function validateData(data) {
  if (!data) return false
  if (!data.user_stats) return false
  return true
}

// 통계 계산 헬퍼
function calculateTotalUsers() {
  if (!dashboardData.value?.user_stats) return 0
  return dashboardData.value.user_stats.total_users || 0
}

function calculateComplianceRate() {
  if (!dashboardData.value?.user_stats) return 0
  const stats = dashboardData.value.user_stats
  const total = stats.total_users || 0
  const excellent = stats.excellent_users || 0

  if (total === 0) return 0
  return ((excellent / total) * 100).toFixed(1)
}

// 내보내기
defineExpose({
  loadDashboardData,
  refreshData,
  exportSummary,
  exportDetailed,
  exportDepartmentData,
})
</script>
<style scoped>
/* 관리자 대시보드 전체 컨테이너 */
.admin-dashboard {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f8fafc;
  min-height: calc(100vh - 114px);
}

/* 헤더 스타일 */
.admin-header {
  background-color: white;
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
}

.admin-header h1 {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.admin-header p {
  color: #6b7280;
  margin: 0 0 24px 0;
  font-size: 16px;
}

.header-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.year-selector {
  display: flex;
  align-items: center;
  gap: 12px;
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
  cursor: pointer;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.refresh-btn,
.export-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background-color: white;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.refresh-btn {
  background-color: #4f46e5;
  color: white;
  border-color: #4f46e5;
}

.refresh-btn:hover:not(:disabled) {
  background-color: #4338ca;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.export-btn:hover:not(:disabled) {
  background-color: #f9fafb;
  border-color: #9ca3af;
}

/* 로딩 및 에러 상태 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #4f46e5;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  text-align: center;
}

.error-icon {
  color: #ef4444;
  margin-bottom: 16px;
}

.retry-btn {
  padding: 12px 24px;
  background-color: #4f46e5;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 16px;
  transition: background-color 0.2s ease;
}

.retry-btn:hover {
  background-color: #4338ca;
}

/* 통계 카드 그리드 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background-color: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 16px;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.total-users .stat-icon {
  background-color: #dbeafe;
  color: #1d4ed8;
}

.excellent-users .stat-icon {
  background-color: #d1fae5;
  color: #059669;
}

.warning-users .stat-icon {
  background-color: #fef3c7;
  color: #d97706;
}

.critical-users .stat-icon {
  background-color: #fee2e2;
  color: #dc2626;
}

.avg-penalty .stat-icon {
  background-color: #f3f4f6;
  color: #4b5563;
}

.stat-content h3 {
  font-size: 14px;
  font-weight: 500;
  color: #6b7280;
  margin: 0 0 8px 0;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 4px 0;
}

.stat-value.excellent {
  color: #059669;
}

.stat-value.warning {
  color: #d97706;
}

.stat-value.critical {
  color: #dc2626;
}

.stat-detail {
  font-size: 12px;
  color: #6b7280;
}

/* 차트 및 분석 섹션 */
.charts-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}

.chart-section,
.trend-section {
  background-color: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f3f4f6;
}

.section-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.chart-controls {
  display: flex;
  gap: 8px;
}

.chart-type-btn {
  padding: 6px 12px;
  background-color: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.chart-type-btn:hover {
  background-color: #e5e7eb;
}

.chart-container {
  height: 300px;
  position: relative;
}

/* 점수 분포 차트 */
.score-distribution-chart {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.distribution-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 12px;
  width: 100%;
}

.distribution-item {
  text-align: center;
  padding: 16px 8px;
  border-radius: 8px;
  border: 2px solid;
  transition: transform 0.2s ease;
}

.distribution-item:hover {
  transform: scale(1.05);
}

.distribution-item.perfect {
  background-color: #ecfdf5;
  border-color: #10b981;
  color: #065f46;
}

.distribution-item.excellent {
  background-color: #f0f9ff;
  border-color: #0ea5e9;
  color: #0c4a6e;
}

.distribution-item.good {
  background-color: #fefce8;
  border-color: #eab308;
  color: #713f12;
}

.distribution-item.warning {
  background-color: #fff7ed;
  border-color: #f97316;
  color: #9a3412;
}

.distribution-item.danger {
  background-color: #fef2f2;
  border-color: #ef4444;
  color: #991b1b;
}

.distribution-item.critical {
  background-color: #fef1f1;
  border-color: #dc2626;
  color: #7f1d1d;
}

.distribution-item.not_evaluated {
  background-color: #f9fafb;
  border-color: #6b7280;
  color: #374151;
}

.range-label {
  font-size: 12px;
  font-weight: 500;
  margin-bottom: 8px;
}

.range-count {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 4px;
}

.range-percentage {
  font-size: 11px;
  opacity: 0.8;
}

.no-data {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #6b7280;
  font-size: 14px;
}

/* 트렌드 차트 */
.trend-select,
.activity-filter {
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background-color: white;
  cursor: pointer;
}

.trend-chart {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.trend-data {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
  gap: 12px;
  width: 100%;
}

.trend-month {
  text-align: center;
  padding: 12px 8px;
  background-color: #f9fafb;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

.month-label {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 8px;
}

.trend-value {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

/* 부서별/직급별 현황 */
.overview-sections {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}

.department-section,
.position-section {
  background-color: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
}

.department-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}

.department-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  background-color: #fafbfc;
  transition: all 0.2s ease;
}

.department-card:hover {
  border-color: #d1d5db;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.dept-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.dept-header h4 {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.user-count {
  font-size: 12px;
  color: #6b7280;
  background-color: #f3f4f6;
  padding: 2px 8px;
  border-radius: 12px;
}

.dept-stats .stat-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.stat-row .label {
  color: #6b7280;
}

.stat-row .value {
  font-weight: 500;
}

.dept-distribution {
  display: flex;
  gap: 12px;
  margin: 12px 0;
}

.dist-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-size: 12px;
  flex: 1;
}

.dist-item .count {
  font-weight: 600;
  font-size: 14px;
}

.dist-item .label {
  color: #6b7280;
  margin-top: 2px;
}

.dist-item.excellent .count {
  color: #059669;
}

.dist-item.warning .count {
  color: #d97706;
}

.dist-item.critical .count {
  color: #dc2626;
}

.excellent-rate {
  font-size: 12px;
  color: #059669;
  font-weight: 500;
  text-align: center;
  margin-top: 8px;
}

/* 직급별 테이블 */
.position-table {
  overflow-x: auto;
}

.position-table table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.position-table th,
.position-table td {
  padding: 12px 8px;
  text-align: left;
  border-bottom: 1px solid #f3f4f6;
}

.position-table th {
  font-weight: 600;
  color: #374151;
  background-color: #f9fafb;
  font-size: 12px;
}

.position-name {
  font-weight: 500;
}

/* 감점 색상 클래스 */
.penalty-low {
  color: #059669;
  font-weight: 500;
}

.penalty-medium {
  color: #d97706;
  font-weight: 500;
}

.penalty-high {
  color: #dc2626;
  font-weight: 500;
}

/* 활동 섹션 */
.activity-sections {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}

.risk-users-section,
.recent-activities-section {
  background-color: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
}

.view-all-btn {
  padding: 6px 12px;
  background-color: #4f46e5;
  color: white;
  border-radius: 6px;
  text-decoration: none;
  font-size: 12px;
  transition: background-color 0.2s ease;
}

.view-all-btn:hover {
  background-color: #4338ca;
}

/* 위험 사용자 목록 */
.risk-users-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.risk-user-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.risk-user-card:hover {
  border-color: #4f46e5;
  background-color: #fafbff;
}

.user-info .user-name {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.user-details {
  font-size: 12px;
  color: #6b7280;
}

.user-risk {
  text-align: right;
}

.risk-level {
  font-size: 12px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 12px;
  margin-bottom: 4px;
  display: inline-block;
}

.risk-level.low {
  background-color: #d1fae5;
  color: #065f46;
}

.risk-level.medium {
  background-color: #fef3c7;
  color: #92400e;
}

.risk-level.high {
  background-color: #fee2e2;
  color: #991b1b;
}

.risk-level.critical {
  background-color: #fecaca;
  color: #7f1d1d;
}

.penalty-score {
  font-weight: 600;
  color: #dc2626;
  font-size: 14px;
}

/* 최근 활동 */
.activities-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border: 1px solid #f3f4f6;
  border-radius: 6px;
  transition: background-color 0.2s ease;
}

.activity-item:hover {
  background-color: #f9fafb;
}

.activity-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.activity-icon.success {
  background-color: #d1fae5;
  color: #059669;
}

.activity-icon.failure {
  background-color: #fee2e2;
  color: #dc2626;
}

.activity-icon.pending {
  background-color: #fef3c7;
  color: #d97706;
}

.activity-content {
  flex: 1;
}

.activity-description {
  font-size: 14px;
  color: #374151;
  margin-bottom: 4px;
  line-height: 1.4;
}

.activity-time {
  font-size: 12px;
  color: #6b7280;
}

/* 빠른 액션 버튼들 */
.quick-actions {
  background-color: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
}

.action-buttons-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.action-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 24px 16px;
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  text-decoration: none;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-button:hover {
  background-color: #f3f4f6;
  border-color: #d1d5db;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.action-button svg {
  color: #4f46e5;
}

.action-button span {
  font-size: 14px;
  font-weight: 500;
  text-align: center;
}

/* 반응형 디자인 */
@media (max-width: 1024px) {
  .charts-row {
    grid-template-columns: 1fr;
  }

  .overview-sections {
    grid-template-columns: 1fr;
  }

  .activity-sections {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  }
}

@media (max-width: 768px) {
  .admin-dashboard {
    padding: 15px;
  }

  .admin-header {
    padding: 20px;
  }

  .header-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .action-buttons {
    justify-content: center;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .department-grid {
    grid-template-columns: 1fr;
  }

  .action-buttons-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }

  .action-button {
    padding: 16px 12px;
  }

  .distribution-grid {
    grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
  }

  .trend-data {
    grid-template-columns: repeat(auto-fit, minmax(60px, 1fr));
  }
}

@media (max-width: 480px) {
  .admin-header h1 {
    font-size: 24px;
  }

  .stat-card {
    flex-direction: column;
    text-align: center;
  }

  .risk-user-card {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .user-risk {
    text-align: left;
  }
}
</style>