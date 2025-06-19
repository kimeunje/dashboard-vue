<template>
  <div class="admin-user-detail">
    <!-- 헤더 -->
    <div class="detail-header">
      <div class="header-content">
        <div class="back-navigation">
          <button @click="goBack" class="back-btn">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M8 0a8 8 0 1 0 0 16A8 8 0 0 0 8 0zm3.5 6H5.707l1.147-1.146a.5.5 0 0 0-.708-.708l-2 2a.5.5 0 0 0 0 .708l2 2a.5.5 0 0 0 .708-.708L5.707 7H11.5a.5.5 0 0 0 0-1z"
              />
            </svg>
            돌아가기
          </button>
        </div>

        <div class="title-section">
          <h1 v-if="userDetail">{{ userDetail.user_info?.name }} 상세 정보</h1>
          <h1 v-else>사용자 상세 정보</h1>
          <p>보안 점수 및 상세 감점 내역을 확인합니다</p>
        </div>

        <div class="header-actions">
          <div class="year-selector">
            <label>평가 년도:</label>
            <select v-model="selectedYear" @change="loadUserDetail">
              <option v-for="year in availableYears" :key="year" :value="year">{{ year }}년</option>
            </select>
          </div>

          <button @click="exportUserDetail" class="export-btn" :disabled="loading">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"
              />
              <path
                d="M7.646 1.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 2.707V11.5a.5.5 0 0 1-1 0V2.707L5.354 4.854a.5.5 0 1 1-.708-.708l3-3z"
              />
            </svg>
            상세 보고서 내보내기
          </button>
        </div>
      </div>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>사용자 상세 정보를 불러오는 중...</p>
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
      <button @click="loadUserDetail" class="retry-btn">다시 시도</button>
    </div>

    <!-- 사용자 상세 정보 -->
    <div v-else-if="userDetail" class="detail-content">
      <!-- 1. 사용자 기본 정보 카드 -->
      <div class="user-info-card">
        <div class="card-header">
          <h2>기본 정보</h2>
          <div class="risk-indicator" :class="getRiskLevel()">
            <span class="risk-dot"></span>
            {{ getRiskLevelLabel() }}
          </div>
        </div>

        <div class="user-basic-info">
          <div class="info-grid">
            <div class="info-item">
              <label>이름</label>
              <span class="value">{{ userDetail.user_info?.name }}</span>
            </div>
            <div class="info-item">
              <label>사번</label>
              <span class="value employee-id">{{ userDetail.user_info?.employee_id }}</span>
            </div>
            <div class="info-item">
              <label>부서</label>
              <span class="value">{{ userDetail.user_info?.department }}</span>
            </div>
            <div class="info-item">
              <label>직급</label>
              <span class="value">{{ userDetail.user_info?.position }}</span>
            </div>
            <div class="info-item">
              <label>이메일</label>
              <span class="value email">{{ userDetail.user_info?.email }}</span>
            </div>
            <div class="info-item">
              <label>마지막 업데이트</label>
              <span class="value">{{ formatDateTime(userDetail.last_updated) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 2. 종합 점수 요약 -->
      <div class="score-summary">
        <div class="summary-header">
          <h2>종합 보안 점수</h2>
          <div class="score-period">{{ selectedYear }}년 기준</div>
        </div>

        <div class="score-cards">
          <div class="score-card total">
            <div class="score-icon">
              <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                <path
                  d="M9.669.864 8 0 6.331.864l-1.858.282-.842 1.68-1.337 1.32L2.6 6l-.306 1.854 1.337 1.32.842 1.68 1.858.282L8 12l1.669-.864 1.858-.282.842-1.68 1.337-1.32L13.4 6l.306-1.854-1.337-1.32-.842-1.68L9.669.864zm1.196 1.193.684 1.365 1.086 1.072L12.387 6l.248 1.506-1.086 1.072-.684 1.365-1.51.229L8 10.874l-1.355-.702-1.51-.229-.684-1.365-1.086-1.072L3.614 6l-.25-1.506 1.087-1.072.684-1.365 1.51-.229L8 1.126l1.356.702 1.509.229z"
                />
                <path d="M4 11.794V16l4-1 4 1v-4.206l-2.018.306L8 13.126 6.018 12.1 4 11.794z" />
              </svg>
            </div>
            <div class="score-content">
              <h3>총 감점</h3>
              <div
                class="score-value"
                :class="getPenaltyClass(userDetail.score_detail?.total_penalty)"
              >
                {{ formatDecimal(userDetail.score_detail?.total_penalty || 0) }}점
              </div>
              <div class="score-max">최대 5.0점</div>
            </div>
          </div>

          <div class="score-card audit">
            <div class="score-icon">
              <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                <path
                  d="M8 0C5.829 0 5.556.01 4.703.048 3.85.088 3.269.222 2.76.42a3.917 3.917 0 0 0-1.417.923A3.927 3.927 0 0 0 .42 2.76C.222 3.268.087 3.85.048 4.7.01 5.555 0 5.827 0 8.001c0 2.172.01 2.444.048 3.297.04.852.174 1.433.372 1.942.205.526.478.972.923 1.417.444.445.89.719 1.416.923.51.198 1.09.333 1.942.372C5.555 15.99 5.827 16 8 16s2.444-.01 3.298-.048c.851-.04 1.434-.174 1.943-.372a3.916 3.916 0 0 0 1.416-.923c.445-.445.718-.891.923-1.417.197-.509.332-1.09.372-1.942C15.99 10.445 16 10.173 16 8s-.01-2.445-.048-3.299c-.04-.851-.175-1.433-.372-1.941a3.926 3.926 0 0 0-.923-1.417A3.911 3.911 0 0 0 13.24.42c-.51-.198-1.092-.333-1.943-.372C10.443.01 10.172 0 7.998 0h.003zm-.717 1.442h.718c2.136 0 2.389.007 3.232.046.78.035 1.204.166 1.486.275.373.145.64.319.92.599.28.28.453.546.598.92.11.281.24.705.275 1.485.039.843.047 1.096.047 3.231s-.008 2.389-.047 3.232c-.035.78-.166 1.203-.275 1.485a2.47 2.47 0 0 1-.599.919c-.28.28-.546.453-.92.598-.28.11-.704.24-1.485.276-.843.038-1.096.047-3.232.047s-2.39-.009-3.233-.047c-.78-.036-1.203-.166-1.485-.276a2.478 2.478 0 0 1-.92-.598 2.48 2.48 0 0 1-.6-.92c-.109-.281-.24-.705-.275-1.485-.038-.843-.046-1.096-.046-3.233 0-2.136.008-2.388.046-3.231.036-.78.166-1.204.276-1.486.145-.373.319-.64.599-.92.28-.28.546-.453.92-.598.282-.11.705-.24 1.485-.276.738-.034 1.024-.044 2.515-.045v.002zm4.988 1.328a.96.96 0 1 0 0 1.92.96.96 0 0 0 0-1.92zm-4.27 1.122a4.109 4.109 0 1 0 0 8.217 4.109 4.109 0 0 0 0-8.217zm0 1.441a2.667 2.667 0 1 1 0 5.334 2.667 2.667 0 0 1 0-5.334z"
                />
              </svg>
            </div>
            <div class="score-content">
              <h3>상시감사 감점</h3>
              <div class="score-value audit">
                {{ formatDecimal(userDetail.score_detail?.audit_penalty || 0) }}점
              </div>
              <div class="score-detail">
                실패: {{ userDetail.score_detail?.audit_stats?.failed_count || 0 }}건
              </div>
            </div>
          </div>

          <div class="score-card education">
            <div class="score-icon">
              <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                <path
                  d="M8.211 2.047a.5.5 0 0 0-.422 0l-7.5 3.5a.5.5 0 0 0 .025.917l7.5 3a.5.5 0 0 0 .372 0L14 7.14V13a1 1 0 0 0-1 1v2h3v-2a1 1 0 0 0-1-1V6.739l.686-.275a.5.5 0 0 0 .025-.917l-7.5-3.5ZM8 8.46 1.758 5.965 8 3.052l6.242 2.913L8 8.46Z"
                />
                <path
                  d="M4.176 9.032a.5.5 0 0 0-.656.327l-.5 1.7a.5.5 0 0 0 .294.605l4.5 1.8a.5.5 0 0 0 .372 0l4.5-1.8a.5.5 0 0 0 .294-.605l-.5-1.7a.5.5 0 0 0-.656-.327L8 10.466 4.176 9.032Zm-.068 1.873.22-.748 3.496 1.311a.5.5 0 0 0 .352 0l3.496-1.311.22.748L8 12.46l-3.892-1.555Z"
                />
              </svg>
            </div>
            <div class="score-content">
              <h3>교육 감점</h3>
              <div class="score-value education">
                {{ formatDecimal(userDetail.score_detail?.education_penalty || 0) }}점
              </div>
              <div class="score-detail">
                미완료: {{ userDetail.score_detail?.education_stats?.incomplete_count || 0 }}건
              </div>
            </div>
          </div>

          <div class="score-card training">
            <div class="score-icon">
              <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                <path
                  d="M0 4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V4zm2-1a1 1 0 0 0-1 1v.217l7 4.2 7-4.2V4a1 1 0 0 0-1-1H2zm13 2.383-4.708 2.825L15 11.105V5.383zm-.034 6.876-5.64-3.471L8 9.583l-1.326-.795-5.64 3.47A1 1 0 0 0 2 13h12a1 1 0 0 0 .966-.741zM1 11.105l4.708-2.897L1 5.383v5.722z"
                />
              </svg>
            </div>
            <div class="score-content">
              <h3>모의훈련 감점</h3>
              <div class="score-value training">
                {{ formatDecimal(userDetail.score_detail?.training_penalty || 0) }}점
              </div>
              <div class="score-detail">
                실패: {{ userDetail.score_detail?.training_stats?.failed_count || 0 }}건
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 3. 상세 감점 내역 -->
      <div class="penalty-details">
        <!-- 상시감사 상세 -->
        <div class="penalty-section">
          <div class="section-header">
            <h3>
              <svg width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                <path
                  d="M1.5 1.5A.5.5 0 0 1 2 1h12a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-.128.334L10 8.692V13.5a.5.5 0 0 1-.342.474l-3 1A.5.5 0 0 1 6 14.5V8.692L1.628 3.834A.5.5 0 0 1 1.5 3.5v-2z"
                />
              </svg>
              상시감사 상세 내역
            </h3>
            <div class="section-summary">
              총 {{ userDetail.score_detail?.audit_stats?.total_count || 0 }}건 중
              {{ userDetail.score_detail?.audit_stats?.failed_count || 0 }}건 실패
            </div>
          </div>

          <div
            v-if="userDetail.score_detail?.audit_stats?.failed_items?.length"
            class="penalty-items"
          >
            <div
              v-for="(item, index) in userDetail.score_detail.audit_stats.failed_items"
              :key="index"
              class="penalty-item audit"
            >
              <div class="item-info">
                <div class="item-name">{{ item.item_name }}</div>
                <div class="item-date">{{ formatDateTime(item.checked_at) }}</div>
              </div>
              <div class="item-penalty">-{{ formatDecimal(item.penalty) }}점</div>
            </div>
          </div>
          <div v-else class="no-penalty-items">상시감사 관련 감점 내역이 없습니다.</div>
        </div>

        <!-- 교육 상세 -->
        <div class="penalty-section">
          <div class="section-header">
            <h3>
              <svg width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                <path
                  d="M8.211 2.047a.5.5 0 0 0-.422 0l-7.5 3.5a.5.5 0 0 0 .025.917l7.5 3a.5.5 0 0 0 .372 0L14 7.14V13a1 1 0 0 0-1 1v2h3v-2a1 1 0 0 0-1-1V6.739l.686-.275a.5.5 0 0 0 .025-.917l-7.5-3.5ZM8 8.46 1.758 5.965 8 3.052l6.242 2.913L8 8.46Z"
                />
              </svg>
              정보보호 교육 상세 내역
            </h3>
            <div class="section-summary">
              총 {{ userDetail.score_detail?.education_stats?.total_count || 0 }}건 중
              {{ userDetail.score_detail?.education_stats?.incomplete_count || 0 }}건 미완료
            </div>
          </div>

          <div
            v-if="userDetail.score_detail?.education_stats?.incomplete_items?.length"
            class="penalty-items"
          >
            <div
              v-for="(item, index) in userDetail.score_detail.education_stats.incomplete_items"
              :key="index"
              class="penalty-item education"
            >
              <div class="item-info">
                <div class="item-name">{{ item.education_name }}</div>
                <div class="item-date">마감일: {{ formatDate(item.due_date) }}</div>
              </div>
              <div class="item-penalty">-{{ formatDecimal(item.penalty) }}점</div>
            </div>
          </div>
          <div v-else class="no-penalty-items">교육 관련 감점 내역이 없습니다.</div>
        </div>

        <!-- 모의훈련 상세 -->
        <div class="penalty-section">
          <div class="section-header">
            <h3>
              <svg width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                <path
                  d="M0 4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V4zm2-1a1 1 0 0 0-1 1v.217l7 4.2 7-4.2V4a1 1 0 0 0-1-1H2zm13 2.383-4.708 2.825L15 11.105V5.383zm-.034 6.876-5.64-3.471L8 9.583l-1.326-.795-5.64 3.47A1 1 0 0 0 2 13h12a1 1 0 0 0 .966-.741zM1 11.105l4.708-2.897L1 5.383v5.722z"
                />
              </svg>
              악성메일 모의훈련 상세 내역
            </h3>
            <div class="section-summary">
              총 {{ userDetail.score_detail?.training_stats?.total_count || 0 }}건 중
              {{ userDetail.score_detail?.training_stats?.failed_count || 0 }}건 실패
            </div>
          </div>

          <div
            v-if="userDetail.score_detail?.training_stats?.failed_items?.length"
            class="penalty-items"
          >
            <div
              v-for="(item, index) in userDetail.score_detail.training_stats.failed_items"
              :key="index"
              class="penalty-item training"
            >
              <div class="item-info">
                <div class="item-name">{{ item.training_name }}</div>
                <div class="item-date">실시일: {{ formatDate(item.conducted_at) }}</div>
                <div class="item-result">결과: {{ item.result }}</div>
              </div>
              <div class="item-penalty">-{{ formatDecimal(item.penalty) }}점</div>
            </div>
          </div>
          <div v-else class="no-penalty-items">모의훈련 관련 감점 내역이 없습니다.</div>
        </div>
      </div>

      <!-- 4. 개선 권고사항 -->
      <div class="recommendations">
        <div class="section-header">
          <h3>
            <svg width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412-1 4.705c-.07.34.029.533.304.533.194 0 .487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381 2.29-.287zM8 5.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"
              />
            </svg>
            개선 권고사항
          </h3>
        </div>

        <div class="recommendation-list">
          <div v-if="getRecommendations().length === 0" class="no-recommendations">
            현재 모든 보안 항목이 우수한 상태입니다. 지속적인 관리를 권장합니다.
          </div>

          <div
            v-for="(recommendation, index) in getRecommendations()"
            :key="index"
            class="recommendation-item"
            :class="recommendation.priority"
          >
            <div class="recommendation-icon">
              <svg
                v-if="recommendation.priority === 'high'"
                width="16"
                height="16"
                fill="currentColor"
                viewBox="0 0 16 16"
              >
                <path
                  d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"
                />
              </svg>
              <svg
                v-else-if="recommendation.priority === 'medium'"
                width="16"
                height="16"
                fill="currentColor"
                viewBox="0 0 16 16"
              >
                <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
                <path
                  d="M7.002 11a1 1 0 1 1 2 0 1 1 0 0 1-2 0zM7.1 4.995a.905.905 0 1 1 1.8 0l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 4.995z"
                />
              </svg>
              <svg v-else width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
                <path
                  d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"
                />
              </svg>
            </div>
            <div class="recommendation-content">
              <div class="recommendation-title">{{ recommendation.title }}</div>
              <div class="recommendation-description">{{ recommendation.description }}</div>
            </div>
            <div class="recommendation-priority">
              <span class="priority-badge" :class="recommendation.priority">
                {{ getPriorityLabel(recommendation.priority) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 5. 연도별 트렌드 (간단한 비교) -->
      <div class="trend-comparison" v-if="trendData">
        <div class="section-header">
          <h3>
            <svg width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M1.5 1.5A.5.5 0 0 1 2 1h12a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-.5.5h-12a.5.5 0 0 1-.5-.5v-2zM2 2v1h12V2H2zm0 3v1h12V5H2zm0 3v1h12V8H2zm0 3v1h12v-1H2z"
              />
            </svg>
            연도별 트렌드
          </h3>
        </div>

        <div class="trend-items">
          <div v-for="(trend, year) in trendData" :key="year" class="trend-item">
            <div class="trend-year">{{ year }}년</div>
            <div class="trend-score" :class="getPenaltyClass(trend.total_penalty)">
              {{ formatDecimal(trend.total_penalty) }}점
            </div>
            <div class="trend-change" v-if="getTrendChange(year)">
              <span :class="getTrendDirection(year)">
                {{ getTrendChangeText(year) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Props 정의
const props = defineProps({
  userId: {
    type: [String, Number],
    required: true,
  },
})

// 상태 관리
const loading = ref(false)
const error = ref('')
const userDetail = ref(null)
const trendData = ref(null)
const selectedYear = ref(new Date().getFullYear())

// 라우터 및 스토어
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 사용 가능한 년도 목록
const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  const years = []
  for (let i = currentYear; i >= currentYear - 5; i--) {
    years.push(i)
  }
  return years
})

// API 호출 함수
const adminAPI = {
  async getUserDetail(userId, year) {
    const response = await fetch(`/api/admin/personal-scores/users/${userId}/detail?year=${year}`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${authStore.token}`,
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    return await response.json()
  },

  async exportUserDetail(userId, year) {
    const response = await fetch(
      `/api/admin/dashboard/export?type=user_detail&user_id=${userId}&year=${year}&format=csv`,
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

  async getUserTrend(userId) {
    // 최근 3년간 데이터 조회
    const years = []
    const currentYear = new Date().getFullYear()
    for (let i = 0; i < 3; i++) {
      years.push(currentYear - i)
    }

    const trendPromises = years.map((year) => this.getUserDetail(userId, year).catch(() => null))

    const results = await Promise.all(trendPromises)
    const trends = {}

    results.forEach((result, index) => {
      if (result && result.score_detail) {
        trends[years[index]] = {
          total_penalty: result.score_detail.total_penalty || 0,
          audit_penalty: result.score_detail.audit_penalty || 0,
          education_penalty: result.score_detail.education_penalty || 0,
          training_penalty: result.score_detail.training_penalty || 0,
        }
      }
    })

    return trends
  },
}

// 메인 함수들
async function loadUserDetail() {
  if (!authStore.isAuthenticated || !isAdmin()) {
    router.push('/login')
    return
  }

  if (!props.userId) {
    error.value = '사용자 ID가 유효하지 않습니다.'
    return
  }

  loading.value = true
  error.value = ''

  try {
    console.log(`사용자 상세 정보 로드: userId=${props.userId}, year=${selectedYear.value}`)

    // 사용자 상세 정보와 트렌드 데이터를 병렬로 로드
    const [detailData, trendResult] = await Promise.all([
      adminAPI.getUserDetail(props.userId, selectedYear.value),
      adminAPI.getUserTrend(props.userId),
    ])

    userDetail.value = detailData
    trendData.value = trendResult

    console.log('사용자 상세 정보 로드 완료:', detailData)
  } catch (err) {
    console.error('사용자 상세 정보 로드 실패:', err)
    error.value = err.message || '사용자 상세 정보를 불러오는데 실패했습니다.'
  } finally {
    loading.value = false
  }
}

// 내보내기 함수
async function exportUserDetail() {
  if (!userDetail.value) return

  try {
    loading.value = true
    const response = await adminAPI.exportUserDetail(props.userId, selectedYear.value)

    const userName = userDetail.value.user_info?.name || '사용자'

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${userName}_상세보고서_${selectedYear.value}.csv`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)

    showSuccess(`${userName}의 상세 보고서를 내보냈습니다.`)
  } catch (err) {
    console.error('상세 보고서 내보내기 실패:', err)
    error.value = '상세 보고서 내보내기에 실패했습니다.'
  } finally {
    loading.value = false
  }
}

// 네비게이션 함수
function goBack() {
  // 이전 페이지가 사용자 관리 페이지인지 확인
  if (document.referrer.includes('/admin/users')) {
    router.go(-1)
  } else {
    router.push('/admin/users')
  }
}

// 유틸리티 함수들
function formatNumber(num) {
  return new Intl.NumberFormat('ko-KR').format(num || 0)
}

function formatDecimal(num, decimals = 1) {
  return parseFloat(num || 0).toFixed(decimals)
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function formatDateTime(dateStr) {
  if (!dateStr) return '정보 없음'
  const date = new Date(dateStr)
  return date.toLocaleString('ko-KR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// 위험도 및 감점 관련 함수들
function getRiskLevel() {
  if (!userDetail.value?.score_detail) return 'not_evaluated'

  const totalPenalty = userDetail.value.score_detail.total_penalty || 0

  if (totalPenalty === 0) return 'excellent'
  if (totalPenalty <= 0.5) return 'low'
  if (totalPenalty <= 2.0) return 'medium'
  if (totalPenalty <= 3.0) return 'high'
  return 'critical'
}

function getRiskLevelLabel() {
  const level = getRiskLevel()
  const labels = {
    excellent: '완벽',
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
  if (penaltyNum === 0) return 'penalty-none'
  if (penaltyNum <= 0.5) return 'penalty-low'
  if (penaltyNum <= 2.0) return 'penalty-medium'
  return 'penalty-high'
}

// 권고사항 생성
function getRecommendations() {
  if (!userDetail.value?.score_detail) return []

  const recommendations = []
  const scoreDetail = userDetail.value.score_detail

  // 상시감사 관련 권고사항
  if (scoreDetail.audit_penalty > 1.0) {
    recommendations.push({
      priority: 'high',
      title: '상시감사 항목 개선 필요',
      description: `${scoreDetail.audit_stats?.failed_count || 0}건의 보안 항목에서 실패했습니다. 보안 정책을 검토하고 개선하세요.`,
    })
  } else if (scoreDetail.audit_penalty > 0.5) {
    recommendations.push({
      priority: 'medium',
      title: '상시감사 주의 필요',
      description: '일부 보안 항목에서 미흡한 부분이 있습니다. 정기적인 점검을 권장합니다.',
    })
  }

  // 교육 관련 권고사항
  if (scoreDetail.education_penalty > 0) {
    recommendations.push({
      priority: scoreDetail.education_penalty > 1.0 ? 'high' : 'medium',
      title: '정보보호 교육 이수 필요',
      description: `${scoreDetail.education_stats?.incomplete_count || 0}건의 필수 교육이 미완료되었습니다. 즉시 이수하세요.`,
    })
  }

  // 모의훈련 관련 권고사항
  if (scoreDetail.training_penalty > 1.0) {
    recommendations.push({
      priority: 'high',
      title: '모의훈련 대응 능력 향상 필요',
      description: `${scoreDetail.training_stats?.failed_count || 0}건의 모의훈련에서 실패했습니다. 추가 교육을 받으세요.`,
    })
  } else if (scoreDetail.training_penalty > 0) {
    recommendations.push({
      priority: 'medium',
      title: '모의훈련 주의사항 숙지',
      description: '모의훈련에서 일부 실패가 있었습니다. 보안 인식을 높이세요.',
    })
  }

  // 종합 점수가 낮은 경우
  if (scoreDetail.total_penalty <= 0.5 && scoreDetail.total_penalty > 0) {
    recommendations.push({
      priority: 'low',
      title: '우수한 보안 수준 유지',
      description: '현재 양호한 보안 수준을 유지하고 있습니다. 지속적인 관리를 권장합니다.',
    })
  }

  return recommendations.sort((a, b) => {
    const priorityOrder = { high: 0, medium: 1, low: 2 }
    return priorityOrder[a.priority] - priorityOrder[b.priority]
  })
}

function getPriorityLabel(priority) {
  const labels = {
    high: '높음',
    medium: '보통',
    low: '낮음',
  }
  return labels[priority] || priority
}

// 트렌드 분석 함수들
function getTrendChange(year) {
  if (!trendData.value) return null

  const currentYear = parseInt(year)
  const previousYear = currentYear - 1

  const current = trendData.value[currentYear]
  const previous = trendData.value[previousYear]

  if (!current || !previous) return null

  return current.total_penalty - previous.total_penalty
}

function getTrendDirection(year) {
  const change = getTrendChange(year)
  if (!change) return 'stable'

  if (change > 0.5) return 'worse'
  if (change < -0.5) return 'better'
  return 'stable'
}

function getTrendChangeText(year) {
  const change = getTrendChange(year)
  if (!change) return ''

  const absChange = Math.abs(change)
  const direction = change > 0 ? '증가' : '감소'

  return `전년 대비 ${formatDecimal(absChange)}점 ${direction}`
}

function isAdmin() {
  const userRole = authStore.user?.role || 'user'
  return userRole === 'admin' || authStore.user?.username === 'admin'
}

// 성공 메시지 표시
function showSuccess(message) {
  // TODO: 성공 토스트 메시지 구현
  console.log('성공:', message)
  alert(message) // 임시로 alert 사용
}

// 오류 처리
function handleError(error, context) {
  console.error(`${context} 오류:`, error)
  error.value = `${context} 중 오류가 발생했습니다: ${error.message}`
}

// 데이터 유효성 검사
function validateData() {
  if (!props.userId) {
    error.value = '사용자 ID가 필요합니다.'
    return false
  }

  if (selectedYear.value < 2020 || selectedYear.value > new Date().getFullYear() + 1) {
    selectedYear.value = new Date().getFullYear()
  }

  return true
}

// 키보드 단축키 처리
function handleKeydown(event) {
  // ESC: 뒤로가기
  if (event.key === 'Escape') {
    goBack()
  }

  // Ctrl+E: 내보내기
  if (event.ctrlKey && event.key === 'e' && userDetail.value) {
    event.preventDefault()
    exportUserDetail()
  }

  // F5: 새로고침
  if (event.key === 'F5') {
    event.preventDefault()
    loadUserDetail()
  }
}

// 반응형 데이터 감시
watch(
  () => selectedYear.value,
  () => {
    if (selectedYear.value && props.userId) {
      loadUserDetail()
    }
  },
)

watch(
  () => props.userId,
  (newUserId) => {
    if (newUserId) {
      loadUserDetail()
    }
  },
  { immediate: true },
)

watch(
  () => authStore.user,
  (newUser) => {
    if (!newUser || !isAdmin()) {
      router.push('/login')
    }
  },
  { immediate: true },
)

// 생명주기 훅
onMounted(() => {
  if (validateData() && authStore.isAuthenticated && isAdmin()) {
    loadUserDetail()
  }

  // 키보드 이벤트 리스너 추가
  document.addEventListener('keydown', handleKeydown)
})

// 컴포넌트 언마운트 시 정리
onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})

// 계산된 속성들
const totalPenaltyStatus = computed(() => {
  if (!userDetail.value?.score_detail) return 'unknown'

  const penalty = userDetail.value.score_detail.total_penalty || 0

  if (penalty === 0) return 'perfect'
  if (penalty <= 0.5) return 'excellent'
  if (penalty <= 2.0) return 'good'
  if (penalty <= 3.0) return 'warning'
  return 'critical'
})

const auditSuccessRate = computed(() => {
  if (!userDetail.value?.score_detail?.audit_stats) return 0

  const stats = userDetail.value.score_detail.audit_stats
  const total = stats.total_count || 0
  const passed = stats.passed_count || 0

  return total > 0 ? ((passed / total) * 100).toFixed(1) : 0
})

const educationCompletionRate = computed(() => {
  if (!userDetail.value?.score_detail?.education_stats) return 0

  const stats = userDetail.value.score_detail.education_stats
  const total = stats.total_count || 0
  const completed = (stats.total_count || 0) - (stats.incomplete_count || 0)

  return total > 0 ? ((completed / total) * 100).toFixed(1) : 0
})

const trainingSuccessRate = computed(() => {
  if (!userDetail.value?.score_detail?.training_stats) return 0

  const stats = userDetail.value.score_detail.training_stats
  const total = stats.total_count || 0
  const passed = (stats.total_count || 0) - (stats.failed_count || 0)

  return total > 0 ? ((passed / total) * 100).toFixed(1) : 0
})

// 내보내기
defineExpose({
  loadUserDetail,
  exportUserDetail,
  goBack,
})
</script>

<style scoped>
/* 관리자 사용자 상세 전체 컨테이너 */
.admin-user-detail {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f8fafc;
  min-height: calc(100vh - 114px);
}

/* 상세 헤더 */
.detail-header {
  background-color: white;
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 20px;
}

.back-navigation {
  flex-shrink: 0;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background-color: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  color: #374151;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background-color: #e5e7eb;
  border-color: #9ca3af;
}

.title-section {
  flex: 1;
  min-width: 300px;
}

.title-section h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.title-section p {
  color: #6b7280;
  margin: 0;
  font-size: 16px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.year-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.year-selector label {
  color: #6b7280;
  font-weight: 500;
}

.year-selector select {
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background-color: white;
  cursor: pointer;
}

.export-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background-color: #4f46e5;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.export-btn:hover:not(:disabled) {
  background-color: #4338ca;
}

.export-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 로딩 및 에러 상태 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
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
  padding: 80px 20px;
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

/* 상세 콘텐츠 */
.detail-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 사용자 기본 정보 카드 */
.user-info-card {
  background-color: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f3f4f6;
}

.card-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.risk-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.risk-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.risk-indicator.excellent {
  background-color: #d1fae5;
  color: #065f46;
}

.risk-indicator.excellent .risk-dot {
  background-color: #059669;
}

.risk-indicator.low {
  background-color: #dbeafe;
  color: #1e40af;
}

.risk-indicator.low .risk-dot {
  background-color: #3b82f6;
}

.risk-indicator.medium {
  background-color: #fef3c7;
  color: #92400e;
}

.risk-indicator.medium .risk-dot {
  background-color: #f59e0b;
}

.risk-indicator.high {
  background-color: #fee2e2;
  color: #991b1b;
}

.risk-indicator.high .risk-dot {
  background-color: #ef4444;
}

.risk-indicator.critical {
  background-color: #fecaca;
  color: #7f1d1d;
}

.risk-indicator.critical .risk-dot {
  background-color: #dc2626;
}

.risk-indicator.not_evaluated {
  background-color: #f3f4f6;
  color: #6b7280;
}

.risk-indicator.not_evaluated .risk-dot {
  background-color: #9ca3af;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-item label {
  font-size: 12px;
  font-weight: 500;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-item .value {
  font-size: 16px;
  color: #1f2937;
  font-weight: 500;
}

.info-item .value.employee-id {
  font-family: 'Monaco', 'Menlo', monospace;
  color: #4f46e5;
}

.info-item .value.email {
  color: #059669;
}

/* 종합 점수 요약 */
.score-summary {
  background-color: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.summary-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.score-period {
  font-size: 14px;
  color: #6b7280;
  background-color: #f3f4f6;
  padding: 4px 12px;
  border-radius: 12px;
}

.score-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.score-card {
  padding: 24px;
  border-radius: 12px;
  border: 2px solid;
  display: flex;
  align-items: center;
  gap: 16px;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.score-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.score-card.total {
  background-color: #f8fafc;
  border-color: #e2e8f0;
}

.score-card.audit {
  background-color: #fef3c7;
  border-color: #f59e0b;
}

.score-card.education {
  background-color: #dbeafe;
  border-color: #3b82f6;
}

.score-card.training {
  background-color: #fee2e2;
  border-color: #ef4444;
}

.score-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.score-card.total .score-icon {
  background-color: #e2e8f0;
  color: #64748b;
}

.score-card.audit .score-icon {
  background-color: #f59e0b;
  color: white;
}

.score-card.education .score-icon {
  background-color: #3b82f6;
  color: white;
}

.score-card.training .score-icon {
  background-color: #ef4444;
  color: white;
}

.score-content h3 {
  font-size: 14px;
  font-weight: 500;
  color: #6b7280;
  margin: 0 0 8px 0;
}

.score-value {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 4px 0;
}

.score-value.penalty-none {
  color: #059669;
}

.score-value.penalty-low {
  color: #059669;
}

.score-value.penalty-medium {
  color: #f59e0b;
}

.score-value.penalty-high {
  color: #ef4444;
}

.score-value.audit {
  color: #92400e;
}

.score-value.education {
  color: #1d4ed8;
}

.score-value.training {
  color: #dc2626;
}

.score-max,
.score-detail {
  font-size: 12px;
  color: #6b7280;
}

/* 상세 감점 내역 */
.penalty-details {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.penalty-section {
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
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.section-summary {
  font-size: 14px;
  color: #6b7280;
  background-color: #f9fafb;
  padding: 6px 12px;
  border-radius: 6px;
}

.penalty-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.penalty-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid;
  transition: all 0.2s ease;
}

.penalty-item:hover {
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.penalty-item.audit {
  background-color: #fef3c7;
  border-color: #f59e0b;
}

.penalty-item.education {
  background-color: #dbeafe;
  border-color: #3b82f6;
}

.penalty-item.training {
  background-color: #fee2e2;
  border-color: #ef4444;
}

.item-info {
  flex: 1;
}

.item-name {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.item-date {
  font-size: 12px;
  color: #6b7280;
}

.item-result {
  font-size: 12px;
  color: #ef4444;
  font-weight: 500;
}

.item-penalty {
  font-size: 18px;
  font-weight: 700;
  color: #dc2626;
}

.no-penalty-items {
  text-align: center;
  padding: 40px 20px;
  color: #6b7280;
  font-style: italic;
}

/* 개선 권고사항 */
.recommendations {
  background-color: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
}

.recommendation-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.no-recommendations {
  text-align: center;
  padding: 40px 20px;
  color: #059669;
  background-color: #d1fae5;
  border-radius: 8px;
  font-weight: 500;
}

.recommendation-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid;
  transition: all 0.2s ease;
}

.recommendation-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.recommendation-item.high {
  background-color: #fef2f2;
  border-color: #fecaca;
}

.recommendation-item.medium {
  background-color: #fffbeb;
  border-color: #fed7aa;
}

.recommendation-item.low {
  background-color: #f0f9ff;
  border-color: #bae6fd;
}

.recommendation-icon {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.recommendation-item.high .recommendation-icon {
  color: #dc2626;
}

.recommendation-item.medium .recommendation-icon {
  color: #f59e0b;
}

.recommendation-item.low .recommendation-icon {
  color: #3b82f6;
}

.recommendation-content {
  flex: 1;
}

.recommendation-title {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.recommendation-description {
  font-size: 14px;
  color: #6b7280;
  line-height: 1.5;
}

.recommendation-priority {
  flex-shrink: 0;
}

.priority-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.priority-badge.high {
  background-color: #fecaca;
  color: #7f1d1d;
}

.priority-badge.medium {
  background-color: #fed7aa;
  color: #92400e;
}

.priority-badge.low {
  background-color: #bae6fd;
  color: #0c4a6e;
}

/* 연도별 트렌드 */
.trend-comparison {
  background-color: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
}

.trend-items {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.trend-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background-color: #fafbfc;
  transition: all 0.2s ease;
}

.trend-item:hover {
  border-color: #d1d5db;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.trend-year {
  font-size: 14px;
  font-weight: 500;
  color: #6b7280;
  margin-bottom: 8px;
}

.trend-score {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 4px;
}

.trend-change {
  font-size: 12px;
  font-weight: 500;
}

.trend-change .better {
  color: #059669;
}

.trend-change .worse {
  color: #dc2626;
}

.trend-change .stable {
  color: #6b7280;
}

/* 감점 색상 클래스 */
.penalty-none {
  color: #059669;
}

.penalty-low {
  color: #059669;
}

.penalty-medium {
  color: #f59e0b;
}

.penalty-high {
  color: #dc2626;
}

/* 반응형 디자인 */
@media (max-width: 1024px) {
  .header-content {
    flex-direction: column;
    align-items: stretch;
  }

  .header-actions {
    justify-content: space-between;
  }

  .score-cards {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  }

  .info-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
}

@media (max-width: 768px) {
  .admin-user-detail {
    padding: 15px;
  }

  .detail-header {
    padding: 20px;
  }

  .title-section h1 {
    font-size: 24px;
  }

  .header-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .score-cards {
    grid-template-columns: 1fr;
  }

  .score-card {
    flex-direction: column;
    text-align: center;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .penalty-item {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .item-penalty {
    text-align: center;
    font-size: 20px;
  }

  .recommendation-item {
    flex-direction: column;
    align-items: stretch;
  }

  .trend-items {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
}

@media (max-width: 480px) {
  .admin-user-detail {
    padding: 10px;
  }

  .detail-header {
    padding: 15px;
  }

  .user-info-card,
  .score-summary,
  .penalty-section,
  .recommendations,
  .trend-comparison {
    padding: 20px;
  }

  .score-value {
    font-size: 28px;
  }

  .section-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .section-summary {
    text-align: center;
  }
}

/* 접근성 개선 */
@media (prefers-reduced-motion: reduce) {
  .loading-spinner {
    animation: none;
  }

  * {
    transition-duration: 0.01ms !important;
  }
}

/* 고대비 모드 지원 */
@media (prefers-contrast: high) {
  .score-card,
  .penalty-item,
  .recommendation-item,
  .trend-item {
    border-width: 2px;
  }

  .risk-indicator {
    border: 1px solid;
  }
}

/* 프린트 스타일 */
@media print {
  .admin-user-detail {
    background-color: white;
    padding: 0;
  }

  .back-btn,
  .export-btn {
    display: none;
  }

  .detail-header {
    box-shadow: none;
    border: 1px solid #ccc;
  }

  .score-card,
  .penalty-section,
  .recommendations {
    box-shadow: none;
    border: 1px solid #ccc;
    margin-bottom: 20px;
    break-inside: avoid;
  }
}
</style>
