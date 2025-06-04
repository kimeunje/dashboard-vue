<!-- views/admin/AdminScoreManagement.vue - Template Part 1 -->
<template>
  <div class="admin-scores">
    <div class="admin-header">
      <h1>점수 관리</h1>
      <div class="admin-nav">
        <RouterLink to="/admin" class="nav-item">대시보드</RouterLink>
        <RouterLink to="/admin/users" class="nav-item">사용자 관리</RouterLink>
        <RouterLink to="/admin/education" class="nav-item">교육 관리</RouterLink>
        <RouterLink to="/admin/training" class="nav-item">훈련 관리</RouterLink>
        <RouterLink to="/admin/scores" class="nav-item active">점수 관리</RouterLink>
      </div>
    </div>

    <div class="management-content">
      <!-- 통계 요약 -->
      <div class="stats-section">
        <h2>{{ selectedYear }}년 점수 현황</h2>
        <div class="stats-grid">
          <div class="stat-card total">
            <div class="stat-icon">👥</div>
            <div class="stat-content">
              <div class="stat-value">{{ scoreStats.total_users }}</div>
              <div class="stat-label">전체 사용자</div>
            </div>
          </div>

          <div class="stat-card average">
            <div class="stat-icon">⭐</div>
            <div class="stat-content">
              <div class="stat-value">{{ scoreStats.average_score }}점</div>
              <div class="stat-label">평균 점수</div>
            </div>
          </div>

          <div class="stat-card excellent">
            <div class="stat-icon">🏆</div>
            <div class="stat-content">
              <div class="stat-value">{{ scoreStats.excellent_count }}</div>
              <div class="stat-label">우수(A등급 이상)</div>
            </div>
          </div>

          <div class="stat-card poor">
            <div class="stat-icon">⚠️</div>
            <div class="stat-content">
              <div class="stat-value">{{ scoreStats.poor_count }}</div>
              <div class="stat-label">미흡(C등급 이하)</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 필터 및 검색 -->
      <div class="filter-section">
        <div class="filter-group">
          <label>연도:</label>
          <select v-model="selectedYear" @change="loadScoreData">
            <option v-for="year in availableYears" :key="year" :value="year">{{ year }}년</option>
          </select>
        </div>

        <div class="filter-group">
          <label>등급:</label>
          <select v-model="selectedGrade" @change="applyFilters">
            <option value="">전체 등급</option>
            <option value="A+">A+</option>
            <option value="A">A</option>
            <option value="B+">B+</option>
            <option value="B">B</option>
            <option value="C+">C+</option>
            <option value="C">C</option>
            <option value="D">D</option>
            <option value="F">F</option>
          </select>
        </div>

        <div class="filter-group">
          <label>점수 범위:</label>
          <select v-model="selectedScoreRange" @change="applyFilters">
            <option value="">전체</option>
            <option value="95-100">95-100점</option>
            <option value="90-94">90-94점</option>
            <option value="80-89">80-89점</option>
            <option value="70-79">70-79점</option>
            <option value="60-69">60-69점</option>
            <option value="0-59">60점 미만</option>
          </select>
        </div>

        <div class="filter-group">
          <label>정렬:</label>
          <select v-model="sortBy" @change="applySorting">
            <option value="total_score_desc">점수 높은순</option>
            <option value="total_score_asc">점수 낮은순</option>
            <option value="username">사용자명</option>
            <option value="department">부서</option>
            <option value="last_calculated">최근 계산순</option>
          </select>
        </div>

        <div class="search-group">
          <input
            type="text"
            v-model="searchQuery"
            @input="searchScores"
            placeholder="사용자명, 부서 검색..."
            class="search-input"
          />
        </div>
      </div>

      <!-- 액션 버튼 -->
      <div class="action-section">
        <div class="action-buttons">
          <button @click="recalculateAllScores" class="primary-button" :disabled="calculating">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path
                fill-rule="evenodd"
                d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2v1z"
              />
              <path
                d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466z"
              />
            </svg>
            {{ calculating ? '계산 중...' : '전체 점수 재계산' }}
          </button>

          <button @click="exportScores" class="secondary-button">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"
              />
              <path
                d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"
              />
            </svg>
            점수 내보내기
          </button>

          <button @click="generateReport" class="outline-button">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M14 14V4.5L9.5 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2zM9.5 3A1.5 1.5 0 0 0 11 4.5h2V14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h5.5v2z"
              />
            </svg>
            종합 보고서 생성
          </button>

          <button
            @click="showSelectedActions = !showSelectedActions"
            class="outline-button"
            :disabled="selectedScores.length === 0"
          >
            선택된 사용자 ({{ selectedScores.length }})
          </button>
        </div>

        <div v-if="showSelectedActions && selectedScores.length > 0" class="selected-actions">
          <button @click="bulkRecalculateSelected" class="action-btn">선택 재계산</button>
          <button @click="bulkExportSelected" class="action-btn">선택 내보내기</button>
          <button @click="bulkSendReport" class="action-btn">개별 보고서 발송</button>
        </div>
      </div>

      <!-- 등급별 분포 차트 -->
      <div class="chart-section">
        <h2>등급별 분포</h2>
        <div class="grade-distribution">
          <div
            v-for="grade in gradeDistribution"
            :key="grade.grade"
            class="grade-bar"
            :class="getGradeClass(grade.grade)"
          >
            <div class="grade-label">{{ grade.grade }}</div>
            <div class="grade-count">{{ grade.count }}명</div>
            <div class="grade-percentage">{{ grade.percentage }}%</div>
            <div class="grade-fill" :style="{ height: `${grade.percentage}%` }"></div>
          </div>
        </div>
      </div>
      <!-- views/admin/AdminScoreManagement.vue - Template Part 2 (테이블 및 모달) -->

      <!-- 점수 목록 테이블 -->
      <div class="table-section">
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>점수 데이터를 불러오는 중...</p>
        </div>

        <div v-else-if="error" class="error-state">
          <div class="error-icon">⚠️</div>
          <p>{{ error }}</p>
          <button @click="loadScoreData" class="retry-button">다시 시도</button>
        </div>

        <div v-else class="table-container">
          <table class="scores-table">
            <thead>
              <tr>
                <th>
                  <input type="checkbox" v-model="selectAll" @change="toggleSelectAll" />
                </th>
                <th>사용자명</th>
                <th>부서</th>
                <th>총점</th>
                <th>등급</th>
                <th>상시감사</th>
                <th>교육 감점</th>
                <th>훈련 감점</th>
                <th>최종 계산일</th>
                <th>액션</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="score in paginatedScores" :key="score.user_id">
                <td>
                  <input type="checkbox" v-model="selectedScores" :value="score.user_id" />
                </td>
                <td>
                  <div class="user-cell">
                    <span class="username">{{ score.username }}</span>
                    <small class="user-id">{{ score.user_id }}</small>
                  </div>
                </td>
                <td>{{ score.department }}</td>
                <td>
                  <div class="score-cell">
                    <span class="score-value" :class="getScoreClass(score.total_score)">
                      {{ score.total_score }}점
                    </span>
                    <div class="score-trend" v-if="score.score_trend">
                      <span :class="score.score_trend > 0 ? 'trend-up' : 'trend-down'">
                        {{ score.score_trend > 0 ? '↗' : '↘' }} {{ Math.abs(score.score_trend) }}
                      </span>
                    </div>
                  </div>
                </td>
                <td>
                  <span class="grade-badge" :class="getGradeClass(score.grade)">
                    {{ score.grade }}
                  </span>
                </td>
                <td class="audit-score">{{ score.audit_score }}점</td>
                <td class="penalty-score">-{{ score.education_penalty }}점</td>
                <td class="penalty-score">-{{ score.training_penalty }}점</td>
                <td>{{ formatDate(score.last_calculated) }}</td>
                <td>
                  <div class="action-buttons">
                    <button @click="viewScoreDetails(score)" class="view-button" title="상세 보기">
                      📊
                    </button>
                    <button
                      @click="recalculateScore(score)"
                      class="calculate-button"
                      title="재계산"
                    >
                      🔄
                    </button>
                    <button
                      @click="sendScoreReport(score)"
                      class="report-button"
                      title="보고서 발송"
                    >
                      📧
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>

          <!-- 페이지네이션 -->
          <div class="pagination">
            <button
              @click="currentPage = Math.max(1, currentPage - 1)"
              :disabled="currentPage === 1"
              class="pagination-button"
            >
              이전
            </button>

            <div class="pagination-info">
              {{ currentPage }} / {{ totalPages }} 페이지 (총 {{ filteredScores.length }}명)
            </div>

            <button
              @click="currentPage = Math.min(totalPages, currentPage + 1)"
              :disabled="currentPage === totalPages"
              class="pagination-button"
            >
              다음
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 점수 상세 정보 모달 -->
    <div v-if="showScoreModal" class="modal-overlay" @click="closeScoreModal">
      <div class="modal-content score-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ selectedScore?.username }} 점수 상세</h3>
          <button @click="closeScoreModal" class="close-button">×</button>
        </div>

        <div class="modal-body" v-if="scoreDetails">
          <!-- 점수 요약 -->
          <div class="score-detail-summary">
            <div class="score-circle">
              <div class="circle-chart" :class="getGradeClass(scoreDetails.grade)">
                <div class="circle-score">
                  <span class="score-number">{{ scoreDetails.total_score }}</span>
                  <span class="score-unit">점</span>
                </div>
                <div class="circle-grade">{{ scoreDetails.grade }}</div>
              </div>
            </div>
            <div class="score-breakdown-detail">
              <h4>점수 구성</h4>
              <div class="breakdown-item">
                <span class="breakdown-label">상시감사 점수:</span>
                <span class="breakdown-value">{{ scoreDetails.audit_score }}점</span>
              </div>
              <div class="breakdown-item">
                <span class="breakdown-label">교육 미이수 감점:</span>
                <span class="breakdown-value penalty">-{{ scoreDetails.education_penalty }}점</span>
              </div>
              <div class="breakdown-item">
                <span class="breakdown-label">모의훈련 감점:</span>
                <span class="breakdown-value penalty">-{{ scoreDetails.training_penalty }}점</span>
              </div>
              <div class="breakdown-total">
                <span class="breakdown-label">총점:</span>
                <span class="breakdown-value total">{{ scoreDetails.total_score }}점</span>
              </div>
            </div>
          </div>

          <!-- 세부 정보 -->
          <div class="score-detail-sections">
            <div class="detail-section">
              <h4>상시감사 현황</h4>
              <div class="detail-content">
                <p>총 검사 항목: {{ scoreDetails.details?.total_audit_items }}개</p>
                <p>통과 항목: {{ scoreDetails.details?.passed_audit_items }}개</p>
                <p>통과율: {{ scoreDetails.details?.audit_pass_rate }}%</p>
              </div>
            </div>

            <div class="detail-section">
              <h4>교육 현황</h4>
              <div class="detail-content">
                <p>미이수 횟수: {{ scoreDetails.education_incomplete }}회</p>
                <p>
                  이수율: {{ Math.round(((4 - scoreDetails.education_incomplete) / 4) * 100) }}%
                </p>
                <p>감점: {{ scoreDetails.education_penalty }}점</p>
              </div>
            </div>

            <div class="detail-section">
              <h4>모의훈련 현황</h4>
              <div class="detail-content">
                <p>실패 횟수: {{ scoreDetails.training_failed }}회</p>
                <p>통과율: {{ Math.round(((4 - scoreDetails.training_failed) / 4) * 100) }}%</p>
                <p>감점: {{ scoreDetails.training_penalty }}점</p>
              </div>
            </div>
          </div>

          <!-- 개선 권장사항 -->
          <div class="recommendations-section" v-if="scoreDetails.recommendations?.length > 0">
            <h4>개선 권장사항</h4>
            <div class="recommendations-list">
              <div
                v-for="(rec, index) in scoreDetails.recommendations"
                :key="index"
                class="recommendation-item"
                :class="rec.priority"
              >
                <div class="rec-header">
                  <span class="rec-priority">{{ getPriorityText(rec.priority) }}</span>
                  <span class="rec-title">{{ rec.title }}</span>
                </div>
                <p class="rec-description">{{ rec.description }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="closeScoreModal" class="cancel-button">닫기</button>
          <button @click="recalculateScore(selectedScore)" class="primary-button">
            점수 재계산
          </button>
          <button @click="sendScoreReport(selectedScore)" class="secondary-button">
            보고서 발송
          </button>
        </div>
      </div>
    </div>

    <!-- 토스트 메시지 -->
    <div v-if="showToast" :class="['toast-message', toastType]">
      {{ toastMessage }}
    </div>
  </div>
</template>

// views/admin/AdminScoreManagement.vue - Script Part 1 (기본 설정 및 상태)
<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import '@/assets/styles/views/admin/AdminScoreManagement.css'

// 반응형 데이터
const loading = ref(false)
const error = ref(null)
const calculating = ref(false)
const scores = ref([])
const filteredScores = ref([])
const selectedScores = ref([])
const selectAll = ref(false)
const showSelectedActions = ref(false)

// 통계 데이터
const scoreStats = ref({
  total_users: 0,
  average_score: 0,
  excellent_count: 0,
  poor_count: 0,
})

const gradeDistribution = ref([])

// 필터 및 검색
const selectedYear = ref(new Date().getFullYear())
const selectedGrade = ref('')
const selectedScoreRange = ref('')
const sortBy = ref('total_score_desc')
const searchQuery = ref('')

// 페이지네이션
const currentPage = ref(1)
const itemsPerPage = ref(20)

// 모달
const showScoreModal = ref(false)
const selectedScore = ref(null)
const scoreDetails = ref(null)

// 토스트
const showToast = ref(false)
const toastMessage = ref('')
const toastType = ref('success')

// 계산된 속성
const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  return [currentYear - 2, currentYear - 1, currentYear, currentYear + 1]
})

const paginatedScores = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredScores.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredScores.value.length / itemsPerPage.value)
})

// 데이터 로드 및 통계 계산 메서드
const loadScoreData = async () => {
  loading.value = true
  error.value = null

  try {
    // 점수 목록 조회
    const scoresResponse = await fetch(`/api/admin/scores?year=${selectedYear.value}`, {
      credentials: 'include',
    })

    if (!scoresResponse.ok) {
      throw new Error('점수 데이터를 불러올 수 없습니다.')
    }

    scores.value = await scoresResponse.json()

    // 통계 데이터 계산
    calculateStats()
    calculateGradeDistribution()
    applyFilters()
  } catch (err) {
    console.error('점수 데이터 로드 실패:', err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const calculateStats = () => {
  const total = scores.value.length
  const totalScore = scores.value.reduce((sum, score) => sum + (score.total_score || 0), 0)
  const excellentCount = scores.value.filter((score) => ['A+', 'A'].includes(score.grade)).length
  const poorCount = scores.value.filter((score) =>
    ['C+', 'C', 'D', 'F'].includes(score.grade),
  ).length

  scoreStats.value = {
    total_users: total,
    average_score: total > 0 ? Math.round((totalScore / total) * 10) / 10 : 0,
    excellent_count: excellentCount,
    poor_count: poorCount,
  }
}

const calculateGradeDistribution = () => {
  const grades = ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'F']
  const total = scores.value.length

  gradeDistribution.value = grades.map((grade) => {
    const count = scores.value.filter((score) => score.grade === grade).length
    const percentage = total > 0 ? Math.round((count / total) * 100) : 0

    return {
      grade,
      count,
      percentage,
    }
  })
}

// views/admin/AdminScoreManagement.vue - Script Part 2 (필터링 및 정렬)

// 필터링 및 정렬 메서드
const applyFilters = () => {
  let filtered = [...scores.value]

  // 등급 필터
  if (selectedGrade.value) {
    filtered = filtered.filter((score) => score.grade === selectedGrade.value)
  }

  // 점수 범위 필터
  if (selectedScoreRange.value) {
    const [min, max] = selectedScoreRange.value.split('-').map(Number)
    filtered = filtered.filter((score) => {
      const totalScore = score.total_score || 0
      if (max) {
        return totalScore >= min && totalScore <= max
      } else {
        return totalScore >= min
      }
    })
  }

  // 검색 필터
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(
      (score) =>
        score.username.toLowerCase().includes(query) ||
        score.department.toLowerCase().includes(query),
    )
  }

  filteredScores.value = filtered
  applySorting()
  currentPage.value = 1
}

const applySorting = () => {
  filteredScores.value.sort((a, b) => {
    switch (sortBy.value) {
      case 'total_score_desc':
        return (b.total_score || 0) - (a.total_score || 0)
      case 'total_score_asc':
        return (a.total_score || 0) - (b.total_score || 0)
      case 'username':
        return a.username.localeCompare(b.username)
      case 'department':
        return a.department.localeCompare(b.department)
      case 'last_calculated':
        return new Date(b.last_calculated) - new Date(a.last_calculated)
      default:
        return 0
    }
  })
}

const searchScores = () => {
  applyFilters()
}

const toggleSelectAll = () => {
  if (selectAll.value) {
    selectedScores.value = paginatedScores.value.map((score) => score.user_id)
  } else {
    selectedScores.value = []
  }
}

// views/admin/AdminScoreManagement.vue - Script Part 3 (점수 계산 및 액션)

// 점수 계산 관련 메서드
const recalculateAllScores = async () => {
  if (calculating.value) return

  const confirmed = confirm(`${selectedYear.value}년 전체 사용자의 점수를 재계산하시겠습니까?`)
  if (!confirmed) return

  calculating.value = true

  try {
    const response = await fetch('/api/admin/scores/recalculate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ year: selectedYear.value }),
    })

    if (!response.ok) {
      throw new Error('전체 점수 재계산에 실패했습니다.')
    }

    const result = await response.json()
    showToastMessage(`${result.success_count}명의 점수가 재계산되었습니다.`, 'success')

    await loadScoreData()
  } catch (err) {
    console.error('전체 점수 재계산 실패:', err)
    showToastMessage(err.message, 'error')
  } finally {
    calculating.value = false
  }
}

const recalculateScore = async (score) => {
  try {
    const response = await fetch('/api/admin/scores/recalculate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        user_id: score.user_id,
        year: selectedYear.value,
      }),
    })

    if (!response.ok) {
      throw new Error('점수 재계산에 실패했습니다.')
    }

    showToastMessage(`${score.username}의 점수가 재계산되었습니다.`, 'success')
    await loadScoreData()
  } catch (err) {
    console.error('점수 재계산 실패:', err)
    showToastMessage(err.message, 'error')
  }
}

const bulkRecalculateSelected = async () => {
  if (selectedScores.value.length === 0) return

  const confirmed = confirm(`선택된 ${selectedScores.value.length}명의 점수를 재계산하시겠습니까?`)
  if (!confirmed) return

  try {
    const promises = selectedScores.value.map((userId) =>
      fetch('/api/admin/scores/recalculate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          user_id: userId,
          year: selectedYear.value,
        }),
      }),
    )

    await Promise.all(promises)
    showToastMessage(`${selectedScores.value.length}명의 점수가 재계산되었습니다.`, 'success')

    selectedScores.value = []
    showSelectedActions.value = false
    await loadScoreData()
  } catch (err) {
    console.error('선택 점수 재계산 실패:', err)
    showToastMessage('선택된 점수 재계산에 실패했습니다.', 'error')
  }
}

// 모달 관련 메서드
const viewScoreDetails = async (score) => {
  selectedScore.value = score
  showScoreModal.value = true

  try {
    const response = await fetch(
      `/api/admin/users/${score.user_id}/details?year=${selectedYear.value}`,
      {
        credentials: 'include',
      },
    )

    if (response.ok) {
      const userDetails = await response.json()

      // 점수 세부 정보에 추가 데이터 포함
      scoreDetails.value = {
        ...score,
        details: userDetails.score_info?.details || {},
        education_incomplete: userDetails.score_info?.education_incomplete || 0,
        training_failed: userDetails.score_info?.training_failed || 0,
        recommendations: [], // 추후 구현
      }
    }
  } catch (err) {
    console.error('점수 상세 정보 조회 실패:', err)
    scoreDetails.value = score
  }
}

const closeScoreModal = () => {
  showScoreModal.value = false
  selectedScore.value = null
  scoreDetails.value = null
}

// 보고서 발송 관련 메서드
const sendScoreReport = (score) => {
  showToastMessage(`${score.username}에게 개별 점수 보고서를 발송했습니다.`, 'success')
}

const bulkSendReport = () => {
  showToastMessage(
    `선택된 ${selectedScores.value.length}명에게 개별 보고서를 발송했습니다.`,
    'success',
  )
  selectedScores.value = []
  showSelectedActions.value = false
}

// views/admin/AdminScoreManagement.vue - Script Part 4 (내보내기 및 유틸리티)

// 내보내기 관련 메서드
const exportScores = () => {
  // CSV 내보내기 구현
  const csvContent = generateCSV()
  downloadCSV(csvContent, `보안점수_${selectedYear.value}.csv`)
}

const bulkExportSelected = () => {
  // 선택된 사용자만 내보내기
  const selectedData = scores.value.filter((score) => selectedScores.value.includes(score.user_id))
  const csvContent = generateCSV(selectedData)
  downloadCSV(csvContent, `선택된_보안점수_${selectedYear.value}.csv`)

  selectedScores.value = []
  showSelectedActions.value = false
}

const generateCSV = (data = filteredScores.value) => {
  const headers = [
    '사용자명',
    '사용자ID',
    '부서',
    '총점',
    '등급',
    '상시감사점수',
    '교육감점',
    '훈련감점',
    '최종계산일',
  ]
  const rows = data.map((score) => [
    score.username,
    score.user_id,
    score.department,
    score.total_score,
    score.grade,
    score.audit_score,
    score.education_penalty,
    score.training_penalty,
    formatDate(score.last_calculated),
  ])

  return [headers, ...rows].map((row) => row.join(',')).join('\n')
}

const downloadCSV = (content, filename) => {
  const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = filename
  link.click()
}

const generateReport = () => {
  showToastMessage('종합 보고서 생성 기능이 준비중입니다.', 'info')
}

// 유틸리티 메서드
const getScoreClass = (score) => {
  if (!score) return 'no-score'
  if (score >= 95) return 'excellent'
  if (score >= 90) return 'very-good'
  if (score >= 80) return 'good'
  if (score >= 70) return 'warning'
  return 'poor'
}

const getGradeClass = (grade) => {
  if (!grade) return 'no-grade'
  if (['A+', 'A'].includes(grade)) return 'grade-a'
  if (['B+', 'B'].includes(grade)) return 'grade-b'
  if (['C+', 'C'].includes(grade)) return 'grade-c'
  return 'grade-d'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('ko-KR')
}

const getPriorityText = (priority) => {
  const priorities = {
    high: '긴급',
    medium: '중요',
    low: '권장',
    info: '정보',
  }
  return priorities[priority] || '일반'
}

const showToastMessage = (message, type = 'success') => {
  toastMessage.value = message
  toastType.value = type
  showToast.value = true

  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

// 라이프사이클 훅
onMounted(() => {
  loadScoreData()
})
</script>
