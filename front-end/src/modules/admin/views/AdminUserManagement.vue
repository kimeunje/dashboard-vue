<template>
  <div class="admin-user-management">
    <!-- 헤더 -->
    <div class="admin-header">
      <div class="header-content">
        <div class="title-section">
          <h1>사용자 관리</h1>
          <p>전체 사용자의 보안 현황을 조회하고 관리합니다</p>
        </div>
        <div class="header-stats">
          <div class="stat-item">
            <span class="stat-label">전체 사용자</span>
            <span class="stat-value">{{ totalUsers }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">선택됨</span>
            <span class="stat-value">{{ selectedUsers.length }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 필터 및 검색 섹션 -->
    <div class="filters-section">
      <div class="filters-header">
        <h3>필터 및 검색</h3>
        <div class="filter-actions">
          <button @click="toggleFilters" class="toggle-btn">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M6 10.5a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1h-3a.5.5 0 0 1-.5-.5zm-2-3a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7a.5.5 0 0 1-.5-.5zm-2-3a.5.5 0 0 1 .5-.5h11a.5.5 0 0 1 0 1h-11a.5.5 0 0 1-.5-.5z"
              />
            </svg>
            {{ showFilters ? '필터 숨기기' : '필터 보기' }}
          </button>
          <button @click="resetFilters" class="reset-btn">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M11.534 7h3.932a.25.25 0 0 1 .192.41l-1.966 2.36a.25.25 0 0 1-.384 0l-1.966-2.36a.25.25 0 0 1 .192-.41zm-11 2h3.932a.25.25 0 0 0 .192-.41L2.692 6.23a.25.25 0 0 0-.384 0L.342 8.59A.25.25 0 0 0 .534 9z"
              />
            </svg>
            초기화
          </button>
        </div>
      </div>

      <div v-if="showFilters" class="filters-content">
        <div class="filter-row">
          <!-- 년도 선택 -->
          <div class="filter-group">
            <label>평가 년도</label>
            <select v-model="filters.year" @change="applyFilters">
              <option v-for="year in availableYears" :key="year" :value="year">{{ year }}년</option>
            </select>
          </div>

          <!-- 부서 선택 -->
          <div class="filter-group">
            <label>부서</label>
            <select v-model="filters.department" @change="applyFilters">
              <option value="">전체</option>
              <option v-for="dept in departmentOptions" :key="dept" :value="dept">
                {{ dept }}
              </option>
            </select>
          </div>

          <!-- 위험도 선택 -->
          <div class="filter-group">
            <label>위험도</label>
            <select v-model="filters.riskLevel" @change="applyFilters">
              <option value="">전체</option>
              <option value="low">낮음</option>
              <option value="medium">보통</option>
              <option value="high">높음</option>
              <option value="critical">매우 높음</option>
              <option value="not_evaluated">미평가</option>
            </select>
          </div>

          <!-- 검색 -->
          <div class="filter-group search-group">
            <label>검색</label>
            <div class="search-input">
              <input
                type="text"
                v-model="filters.search"
                @input="debounceSearch"
                placeholder="이름, 사번, 이메일 검색..."
              />
              <svg
                class="search-icon"
                width="16"
                height="16"
                fill="currentColor"
                viewBox="0 0 16 16"
              >
                <path
                  d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"
                />
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 액션 바 -->
    <div class="action-bar">
      <div class="selection-info">
        <label class="select-all">
          <input
            type="checkbox"
            :checked="isAllSelected"
            :indeterminate="isPartiallySelected"
            @change="toggleSelectAll"
          />
          전체 선택 ({{ selectedUsers.length }}/{{ users.length }})
        </label>
      </div>

      <div class="action-buttons">
        <div class="sort-controls">
          <label>정렬:</label>
          <select v-model="filters.sortBy" @change="applyFilters">
            <option value="total_penalty">감점 순</option>
            <option value="name">이름 순</option>
            <option value="department">부서 순</option>
            <option value="last_updated">업데이트 순</option>
          </select>
          <button @click="toggleSortOrder" class="sort-order-btn">
            <svg
              v-if="filters.sortOrder === 'desc'"
              width="16"
              height="16"
              fill="currentColor"
              viewBox="0 0 16 16"
            >
              <path
                d="M7.247 11.14 2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z"
              />
            </svg>
            <svg v-else width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="m7.247 4.86-4.796 5.481c-.566.647-.106 1.659.753 1.659h9.592a1 1 0 0 0 .753-1.659l-4.796-5.48a1 1 0 0 0-1.506 0z"
              />
            </svg>
          </button>
        </div>

        <div class="bulk-actions">
          <button @click="exportSelected" :disabled="selectedUsers.length === 0" class="export-btn">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"
              />
              <path
                d="M7.646 1.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 2.707V11.5a.5.5 0 0 1-1 0V2.707L5.354 4.854a.5.5 0 1 1-.708-.708l3-3z"
              />
            </svg>
            선택된 사용자 내보내기 ({{ selectedUsers.length }})
          </button>

          <button @click="exportAll" class="export-btn">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M14 14V4.5L9.5 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2zM9.5 3A1.5 1.5 0 0 0 11 4.5h2V14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h5.5v2z"
              />
            </svg>
            전체 내보내기
          </button>
        </div>
      </div>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>사용자 데이터를 불러오는 중...</p>
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
      <button @click="loadUsers" class="retry-btn">다시 시도</button>
    </div>

    <!-- 사용자 테이블 -->
    <div v-else class="users-table-section">
      <div class="table-container">
        <table class="users-table">
          <thead>
            <tr>
              <th class="checkbox-col">
                <input
                  type="checkbox"
                  :checked="isAllSelected"
                  :indeterminate="isPartiallySelected"
                  @change="toggleSelectAll"
                />
              </th>
              <th class="user-col">사용자</th>
              <th class="department-col">부서</th>
              <th class="penalty-col">총 감점</th>
              <th class="breakdown-col">감점 내역</th>
              <th class="risk-col">위험도</th>
              <th class="updated-col">마지막 업데이트</th>
              <th class="actions-col">작업</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="user in users"
              :key="user.uid"
              class="user-row"
              :class="{
                selected: selectedUsers.includes(user.uid),
                'high-risk': user.risk_level === 'critical' || user.risk_level === 'high',
              }"
            >
              <td class="checkbox-col">
                <input type="checkbox" :value="user.uid" v-model="selectedUsers" />
              </td>

              <td class="user-col">
                <div class="user-info">
                  <div class="user-name">{{ user.name }}</div>
                  <div class="user-details">
                    <span class="employee-id">{{ user.employee_id }}</span>
                    <span class="email">{{ user.email }}</span>
                  </div>
                </div>
              </td>

              <td class="department-col">
                <span class="department-badge">{{ user.department || '미분류' }}</span>
              </td>

              <td class="penalty-col">
                <div class="penalty-score" :class="getPenaltyClass(user.total_penalty)">
                  {{ formatDecimal(user.total_penalty) }}점
                </div>
              </td>

              <td class="breakdown-col">
                <div class="penalty-breakdown">
                  <div v-if="user.audit_penalty > 0" class="breakdown-item audit">
                    <span class="label">감사:</span>
                    <span class="value">{{ formatDecimal(user.audit_penalty) }}</span>
                  </div>
                  <div v-if="user.education_penalty > 0" class="breakdown-item education">
                    <span class="label">교육:</span>
                    <span class="value">{{ formatDecimal(user.education_penalty) }}</span>
                  </div>
                  <div v-if="user.training_penalty > 0" class="breakdown-item training">
                    <span class="label">훈련:</span>
                    <span class="value">{{ formatDecimal(user.training_penalty) }}</span>
                  </div>
                  <div v-if="user.total_penalty === 0" class="no-penalty">감점 없음</div>
                </div>
              </td>

              <td class="risk-col">
                <span class="risk-badge" :class="user.risk_level">
                  {{ getRiskLevelLabel(user.risk_level) }}
                </span>
              </td>

              <td class="updated-col">
                <div class="update-info">
                  <span v-if="user.last_updated" class="update-date">
                    {{ formatDate(user.last_updated) }}
                  </span>
                  <span v-else class="no-update">미평가</span>
                </div>
              </td>

              <td class="actions-col">
                <div class="action-buttons">
                  <button @click="viewUserDetail(user.uid)" class="detail-btn" title="상세 보기">
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                      <path
                        d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8zM1.173 8a13.133 13.133 0 0 1 1.66-2.043C4.12 4.668 5.88 3.5 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.133 13.133 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755C11.879 11.332 10.119 12.5 8 12.5c-2.12 0-3.879-1.168-5.168-2.457A13.134 13.134 0 0 1 1.172 8z"
                      />
                      <path
                        d="M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0z"
                      />
                    </svg>
                  </button>

                  <button
                    @click="exportUserData(user.uid)"
                    class="export-btn"
                    title="개별 내보내기"
                  >
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                      <path
                        d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"
                      />
                      <path
                        d="M7.646 1.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 2.707V11.5a.5.5 0 0 1-1 0V2.707L5.354 4.854a.5.5 0 1 1-.708-.708l3-3z"
                      />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 데이터가 없는 경우 -->
      <div v-if="users.length === 0" class="no-data">
        <div class="no-data-icon">
          <svg width="64" height="64" fill="currentColor" viewBox="0 0 16 16">
            <path
              d="M6 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm-5 6s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1H1zM11 3.5a.5.5 0 0 1 .5-.5h4a.5.5 0 0 1 0 1h-4a.5.5 0 0 1-.5-.5zm.5 2.5a.5.5 0 0 0 0 1h4a.5.5 0 0 0 0-1h-4zm2 3a.5.5 0 0 0 0 1h2a.5.5 0 0 0 0-1h-2zm0 3a.5.5 0 0 0 0 1h2a.5.5 0 0 0 0-1h-2z"
            />
          </svg>
        </div>
        <h3>사용자가 없습니다</h3>
        <p>현재 필터 조건에 맞는 사용자가 없습니다.</p>
        <button @click="resetFilters" class="reset-btn">필터 초기화</button>
      </div>
    </div>

    <!-- 페이지네이션 -->
    <div v-if="pagination && pagination.total_count > 0" class="pagination-section">
      <div class="pagination-info">
        <span>
          {{ (pagination.page - 1) * pagination.per_page + 1 }} -
          {{ Math.min(pagination.page * pagination.per_page, pagination.total_count) }} /
          {{ totalUsers }}
        </span>
      </div>

      <div class="pagination-controls">
        <button @click="goToPage(1)" :disabled="pagination.page === 1" class="page-btn">
          처음
        </button>

        <button
          @click="goToPage(pagination.page - 1)"
          :disabled="pagination.page === 1"
          class="page-btn"
        >
          이전
        </button>

        <div class="page-numbers">
          <button
            v-for="page in visiblePages"
            :key="page"
            @click="goToPage(page)"
            :class="{ active: page === pagination.page }"
            class="page-num"
          >
            {{ page }}
          </button>
        </div>

        <button
          @click="goToPage(pagination.page + 1)"
          :disabled="pagination.page === pagination.total_pages"
          class="page-btn"
        >
          다음
        </button>

        <button
          @click="goToPage(pagination.total_pages)"
          :disabled="pagination.page === pagination.total_pages"
          class="page-btn"
        >
          마지막
        </button>
      </div>

      <div class="per-page-selector">
        <label>페이지당:</label>
        <select v-model="filters.perPage" @change="changePerPage">
          <option value="20">20개</option>
          <option value="50">50개</option>
          <option value="100">100개</option>
        </select>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// 상태 관리
const loading = ref(false)
const error = ref('')
const showFilters = ref(true)
const users = ref([])
const selectedUsers = ref([])
const pagination = ref(null)
const departmentOptions = ref([])
const positionOptions = ref([])

// 라우터 및 스토어
const router = useRouter()
const authStore = useAuthStore()

// 필터 상태
const filters = reactive({
  year: new Date().getFullYear(),
  department: '',
  position: '',
  riskLevel: '',
  search: '',
  sortBy: 'total_penalty',
  sortOrder: 'desc',
  page: 1,
  perPage: 20,
})

// 사용 가능한 년도 목록
const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  const years = []
  for (let i = currentYear; i >= currentYear - 5; i--) {
    years.push(i)
  }
  return years
})

// 계산된 속성들
const totalUsers = computed(() => {
  return pagination.value?.total_count || 0
})

const formattedTotalUsers = computed(() => {
  return formatNumber(totalUsers.value)
})

// 선택 상태 계산
const isAllSelected = computed(() => {
  return users.value.length > 0 && selectedUsers.value.length === users.value.length
})

const isPartiallySelected = computed(() => {
  return selectedUsers.value.length > 0 && selectedUsers.value.length < users.value.length
})

// 페이지네이션 계산
const visiblePages = computed(() => {
  if (!pagination.value) return []

  const current = pagination.value.page
  const total = pagination.value.total_pages
  const delta = 2

  const range = []
  const rangeWithDots = []

  for (let i = Math.max(2, current - delta); i <= Math.min(total - 1, current + delta); i++) {
    range.push(i)
  }

  if (current - delta > 2) {
    rangeWithDots.push(1, '...')
  } else {
    rangeWithDots.push(1)
  }

  rangeWithDots.push(...range)

  if (current + delta < total - 1) {
    rangeWithDots.push('...', total)
  } else if (total > 1) {
    rangeWithDots.push(total)
  }

  return rangeWithDots.filter((item, index, arr) => arr.indexOf(item) === index)
})

// API 호출 함수들
const adminAPI = {
  async getUsers(filterParams) {
    const params = new URLSearchParams({
      year: filterParams.year,
      department: filterParams.department,
      position: filterParams.position,
      risk_level: filterParams.riskLevel,
      search: filterParams.search,
      sort_by: filterParams.sortBy,
      sort_order: filterParams.sortOrder,
      page: filterParams.page,
      per_page: filterParams.perPage,
    })

    // 빈 값 제거
    for (const [key, value] of params.entries()) {
      if (!value) {
        params.delete(key)
      }
    }

    const response = await fetch(`/api/admin/dashboard/users?${params}`, {
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

  async exportUsers(userIds = null, format = 'csv') {
    const params = new URLSearchParams({
      year: filters.year,
      format: format,
    })

    if (userIds && userIds.length > 0) {
      params.append('user_ids', userIds.join(','))
    }

    const response = await fetch(`/api/admin/dashboard/export?${params}`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${authStore.token}`,
      },
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    return response
  },

  async getUserDetail(userId) {
    const response = await fetch(
      `/api/admin/dashboard/users/${userId}/detail?year=${filters.year}`,
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
}

// 메인 함수들
async function loadUsers() {
  if (!authStore.isAuthenticated || !isAdmin()) {
    router.push('/login')
    return
  }

  loading.value = true
  error.value = ''

  try {
    console.log('사용자 목록 로드:', filters)

    const data = await adminAPI.getUsers(filters)

    users.value = data.users || []
    pagination.value = data.pagination

    // 부서 및 직급 옵션 업데이트
    updateFilterOptions()

    console.log('사용자 목록 로드 완료:', data)
  } catch (err) {
    console.error('사용자 목록 로드 실패:', err)
    error.value = err.message || '사용자 목록을 불러오는데 실패했습니다.'
  } finally {
    loading.value = false
  }
}

function updateFilterOptions() {
  // 부서 옵션 업데이트
  const departments = [...new Set(users.value.map((user) => user.department).filter(Boolean))]
  departmentOptions.value = departments.sort()

  // 직급 옵션 업데이트
  const positions = [...new Set(users.value.map((user) => user.position).filter(Boolean))]
  positionOptions.value = positions.sort()
}

async function applyFilters() {
  filters.page = 1 // 필터 적용 시 첫 페이지로 이동
  selectedUsers.value = [] // 선택 초기화
  await loadUsers()
}

function resetFilters() {
  Object.assign(filters, {
    year: new Date().getFullYear(),
    department: '',
    position: '',
    riskLevel: '',
    search: '',
    sortBy: 'total_penalty',
    sortOrder: 'desc',
    page: 1,
    perPage: 20,
  })
  selectedUsers.value = []
  applyFilters()
}

function toggleFilters() {
  showFilters.value = !showFilters.value
}

function toggleSortOrder() {
  filters.sortOrder = filters.sortOrder === 'desc' ? 'asc' : 'desc'
  applyFilters()
}

// 선택 관련 함수들
function toggleSelectAll() {
  if (isAllSelected.value) {
    selectedUsers.value = []
  } else {
    selectedUsers.value = users.value.map((user) => user.uid)
  }
}

// 페이지네이션 함수들
async function goToPage(page) {
  if (page === '...' || page < 1 || (pagination.value && page > pagination.value.total_pages)) {
    return
  }

  filters.page = page
  await loadUsers()
}

async function changePerPage() {
  filters.page = 1
  await loadUsers()
}

// 내보내기 함수들
async function exportSelected() {
  if (selectedUsers.value.length === 0) return

  try {
    loading.value = true
    const response = await adminAPI.exportUsers(selectedUsers.value, 'csv')

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `선택된_사용자_${selectedUsers.value.length}명_${filters.year}.csv`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)

    showSuccess(`${selectedUsers.value.length}명의 사용자 데이터를 내보냈습니다.`)
  } catch (err) {
    console.error('선택된 사용자 내보내기 실패:', err)
    error.value = '선택된 사용자 데이터 내보내기에 실패했습니다.'
  } finally {
    loading.value = false
  }
}

async function exportAll() {
  try {
    loading.value = true
    const response = await adminAPI.exportUsers(null, 'csv')

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `전체_사용자_${totalUsers.value}명_${filters.year}.csv`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)

    showSuccess(`전체 ${totalUsers.value}명의 사용자 데이터를 내보냈습니다.`)
  } catch (err) {
    console.error('전체 사용자 내보내기 실패:', err)
    error.value = '전체 사용자 데이터 내보내기에 실패했습니다.'
  } finally {
    loading.value = false
  }
}

async function exportUserData(userId) {
  try {
    loading.value = true
    const response = await adminAPI.exportUsers([userId], 'csv')

    const user = users.value.find((u) => u.uid === userId)
    const userName = user ? user.name : '사용자'

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${userName}_상세데이터_${filters.year}.csv`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)

    showSuccess(`${userName}의 데이터를 내보냈습니다.`)
  } catch (err) {
    console.error('개별 사용자 내보내기 실패:', err)
    error.value = '사용자 데이터 내보내기에 실패했습니다.'
  } finally {
    loading.value = false
  }
}

// 사용자 상세 보기
async function viewUserDetail(userId) {
  router.push(`/admin/users/${userId}/detail`)
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

function getPenaltyClass(penalty) {
  const penaltyNum = parseFloat(penalty || 0)
  if (penaltyNum === 0) return 'penalty-none'
  if (penaltyNum <= 0.5) return 'penalty-low'
  if (penaltyNum <= 2.0) return 'penalty-medium'
  return 'penalty-high'
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

function isAdmin() {
  const userRole = authStore.user?.role || 'user'
  return userRole === 'admin' || authStore.user?.username === 'admin'
}

// 디바운스 검색
let searchTimeout = null
function debounceSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    applyFilters()
  }, 500)
}

// 성공 메시지 표시
function showSuccess(message) {
  // TODO: 성공 토스트 메시지 구현
  console.log('성공:', message)
  alert(message) // 임시로 alert 사용
}

// 확인 대화상자
function confirmAction(message) {
  return confirm(message)
}

// 오류 처리
function handleError(error, context) {
  console.error(`${context} 오류:`, error)
  error.value = `${context} 중 오류가 발생했습니다: ${error.message}`
}

// 데이터 유효성 검사
function validateFilters() {
  if (filters.year < 2020 || filters.year > new Date().getFullYear() + 1) {
    filters.year = new Date().getFullYear()
  }

  if (filters.page < 1) {
    filters.page = 1
  }

  if (filters.perPage < 10 || filters.perPage > 200) {
    filters.perPage = 20
  }
}

// 키보드 단축키 처리
function handleKeydown(event) {
  // Ctrl+A: 전체 선택
  if (event.ctrlKey && event.key === 'a' && !event.target.matches('input, textarea')) {
    event.preventDefault()
    toggleSelectAll()
  }

  // Ctrl+E: 선택된 항목 내보내기
  if (event.ctrlKey && event.key === 'e' && selectedUsers.value.length > 0) {
    event.preventDefault()
    exportSelected()
  }

  // F5: 새로고침
  if (event.key === 'F5') {
    event.preventDefault()
    loadUsers()
  }
}

// 반응형 데이터 감시
watch(
  () => filters.year,
  () => {
    if (filters.year) {
      applyFilters()
    }
  },
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
  if (authStore.isAuthenticated && isAdmin()) {
    validateFilters()
    loadUsers()
  }

  // 키보드 이벤트 리스너 추가
  document.addEventListener('keydown', handleKeydown)
})

// 컴포넌트 언마운트 시 정리
onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
  clearTimeout(searchTimeout)
})

const statistics = computed(() => {
  if (!users.value.length) return null

  const stats = {
    total: users.value.length,
    excellent: users.value.filter((u) => u.risk_level === 'low').length,
    warning: users.value.filter((u) => u.risk_level === 'medium').length,
    critical: users.value.filter((u) => u.risk_level === 'high' || u.risk_level === 'critical')
      .length,
    notEvaluated: users.value.filter((u) => u.risk_level === 'not_evaluated').length,
  }

  return stats
})
</script>
<style scoped>
/* 관리자 사용자 관리 전체 컨테이너 */
.admin-user-management {
  max-width: 1600px;
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
  margin-bottom: 20px;
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

.header-stats {
  display: flex;
  gap: 24px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.stat-label {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
}

/* 필터 섹션 */
.filters-section {
  background-color: white;
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.filters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #f3f4f6;
  background-color: #fafbfc;
}

.filters-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.filter-actions {
  display: flex;
  gap: 8px;
}

.toggle-btn,
.reset-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background-color: white;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s ease;
}

.toggle-btn:hover,
.reset-btn:hover {
  background-color: #f9fafb;
  border-color: #9ca3af;
}

.filters-content {
  padding: 24px;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 200px;
  }
}

.filter-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-group label {
  font-size: 12px;
  font-weight: 500;
  color: #374151;
}

.filter-group select,
.filter-group input {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background-color: white;
  transition: border-color 0.2s ease;
}

.filter-group select:focus,
.filter-group input:focus {
  outline: none;
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.search-group {
  grid-column: span 2;
  min-width: 300px;
}

.search-input {
  position: relative;
}

.search-input input {
  padding-right: 40px;
  width: 100%;
}

.search-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #6b7280;
  pointer-events: none;
}

/* 액션 바 */
.action-bar {
  background-color: white;
  border-radius: 12px;
  padding: 16px 24px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.select-all {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #374151;
}

.select-all input[type='checkbox'] {
  width: 16px;
  height: 16px;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.sort-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.sort-controls label {
  color: #6b7280;
  font-weight: 500;
}

.sort-controls select {
  padding: 4px 8px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 12px;
}

.sort-order-btn {
  padding: 4px 8px;
  background-color: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.sort-order-btn:hover {
  background-color: #e5e7eb;
}

.bulk-actions {
  display: flex;
  gap: 8px;
}

.export-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background-color: white;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s ease;
}

.export-btn:hover:not(:disabled) {
  background-color: #f9fafb;
  border-color: #9ca3af;
}

.export-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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

/* 사용자 테이블 */
.users-table-section {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
  overflow: hidden;
  margin-bottom: 20px;
}

.table-container {
  overflow-x: auto;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  min-width: 1200px;
}

.users-table th {
  background-color: #f9fafb;
  padding: 16px 12px;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 2px solid #e5e7eb;
  white-space: nowrap;
}

.users-table td {
  padding: 16px 12px;
  border-bottom: 1px solid #f3f4f6;
  vertical-align: top;
}

.user-row {
  transition: background-color 0.2s ease;
}

.user-row:hover {
  background-color: #f9fafb;
}

.user-row.selected {
  background-color: #eff6ff;
}

.user-row.high-risk {
  background-color: #fef2f2;
}

.user-row.high-risk:hover {
  background-color: #fee2e2;
}

/* 테이블 컬럼 너비 */
.checkbox-col {
  width: 40px;
  text-align: center;
}

.user-col {
  width: 200px;
  min-width: 180px;
}

.department-col {
  width: 120px;
}

.position-col {
  width: 100px;
}

.penalty-col {
  width: 80px;
  text-align: center;
}

.breakdown-col {
  width: 200px;
  min-width: 180px;
}

.risk-col {
  width: 80px;
  text-align: center;
}

.updated-col {
  width: 120px;
}

.actions-col {
  width: 80px;
  text-align: center;
}

/* 사용자 정보 */
.user-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.user-name {
  font-weight: 600;
  color: #1f2937;
  font-size: 14px;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 12px;
  color: #6b7280;
}

.employee-id {
  font-family: 'Monaco', 'Menlo', monospace;
}

.email {
  color: #4f46e5;
}

/* 배지 스타일 */
.department-badge,
.position-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  background-color: #f3f4f6;
  color: #374151;
  white-space: nowrap;
}

.risk-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  white-space: nowrap;
}

.risk-badge.low {
  background-color: #d1fae5;
  color: #065f46;
}

.risk-badge.medium {
  background-color: #fef3c7;
  color: #92400e;
}

.risk-badge.high {
  background-color: #fee2e2;
  color: #991b1b;
}

.risk-badge.critical {
  background-color: #fecaca;
  color: #7f1d1d;
}

.risk-badge.not_evaluated {
  background-color: #f3f4f6;
  color: #6b7280;
}

/* 감점 관련 스타일 */
.penalty-score {
  font-weight: 600;
  font-size: 16px;
}

.penalty-none {
  color: #059669;
}

.penalty-low {
  color: #059669;
}

.penalty-medium {
  color: #d97706;
}

.penalty-high {
  color: #dc2626;
}

.penalty-breakdown {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.breakdown-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
}

.breakdown-item.audit {
  background-color: #fef3c7;
  color: #92400e;
}

.breakdown-item.education {
  background-color: #dbeafe;
  color: #1e40af;
}

.breakdown-item.training {
  background-color: #fee2e2;
  color: #991b1b;
}

.breakdown-item .label {
  font-weight: 500;
}

.breakdown-item .value {
  font-weight: 600;
}

.no-penalty {
  font-size: 12px;
  color: #059669;
  font-style: italic;
  text-align: center;
  padding: 4px;
}

/* 업데이트 정보 */
.update-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.update-date {
  font-size: 12px;
  color: #374151;
}

.no-update {
  font-size: 12px;
  color: #6b7280;
  font-style: italic;
}

/* 액션 버튼 */
.action-buttons {
  display: flex;
  gap: 4px;
}

.detail-btn,
.export-btn {
  padding: 6px;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  background-color: white;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-btn:hover {
  background-color: #eff6ff;
  border-color: #3b82f6;
  color: #3b82f6;
}

.export-btn:hover {
  background-color: #f0fdf4;
  border-color: #22c55e;
  color: #22c55e;
}

/* 데이터 없음 */
.no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  color: #6b7280;
}

.no-data-icon {
  margin-bottom: 16px;
  color: #9ca3af;
}

.no-data h3 {
  font-size: 18px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 8px 0;
}

.no-data p {
  margin: 0 0 16px 0;
  color: #6b7280;
}

/* 페이지네이션 */
.pagination-section {
  background-color: white;
  border-radius: 12px;
  padding: 16px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.pagination-info {
  font-size: 14px;
  color: #6b7280;
}

.pagination-controls {
  display: flex;
  gap: 4px;
  align-items: center;
}

.page-btn,
.page-num {
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  background-color: white;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
  border-radius: 6px;
}

.page-btn:hover:not(:disabled),
.page-num:hover {
  background-color: #f9fafb;
  border-color: #d1d5db;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-num.active {
  background-color: #4f46e5;
  color: white;
  border-color: #4f46e5;
}

.page-numbers {
  display: flex;
  gap: 2px;
}

.per-page-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.per-page-selector label {
  color: #6b7280;
  font-weight: 500;
}

.per-page-selector select {
  padding: 4px 8px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 12px;
}

/* 반응형 디자인 */
@media (max-width: 1200px) {
  .admin-user-management {
    padding: 15px;
  }

  .filter-row {
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  }

  .search-group {
    grid-column: span 1;
    min-width: unset;
  }

  .action-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .action-buttons {
    justify-content: space-between;
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: stretch;
  }

  .header-stats {
    justify-content: space-around;
  }

  .filters-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .filter-row {
    grid-template-columns: 1fr;
  }

  .action-bar {
    padding: 12px 16px;
  }

  .action-buttons {
    flex-direction: column;
    gap: 12px;
  }

  .bulk-actions {
    flex-direction: column;
  }

  .table-container {
    border-radius: 0;
    margin: 0 -15px;
  }

  .users-table {
    font-size: 12px;
  }

  .users-table th,
  .users-table td {
    padding: 8px 6px;
  }

  .pagination-section {
    flex-direction: column;
    gap: 12px;
  }

  .pagination-controls {
    flex-wrap: wrap;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .admin-user-management {
    padding: 10px;
  }

  .admin-header {
    padding: 20px;
  }

  .title-section h1 {
    font-size: 24px;
  }

  .stat-value {
    font-size: 20px;
  }

  .users-table {
    min-width: 800px;
  }

  .page-btn,
  .page-num {
    padding: 6px 8px;
    font-size: 12px;
  }
}

/* 체크박스 커스텀 스타일 */
input[type='checkbox'] {
  appearance: none;
  width: 16px;
  height: 16px;
  border: 1px solid #d1d5db;
  border-radius: 3px;
  background-color: white;
  cursor: pointer;
  position: relative;
  transition: all 0.2s ease;
}

input[type='checkbox']:checked {
  background-color: #4f46e5;
  border-color: #4f46e5;
}

input[type='checkbox']:checked::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 12px;
  font-weight: bold;
}

input[type='checkbox']:indeterminate {
  background-color: #6b7280;
  border-color: #6b7280;
}

input[type='checkbox']:indeterminate::after {
  content: '−';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 14px;
  font-weight: bold;
}

/* 접근성 개선 */
@media (prefers-reduced-motion: reduce) {
  .loading-spinner {
    animation: none;
  }

  .filters-content {
    animation: none;
  }

  * {
    transition-duration: 0.01ms !important;
  }
}

/* 고대비 모드 지원 */
@media (prefers-contrast: high) {
  .users-table th {
    border-bottom: 3px solid #000;
  }

  .user-row {
    border-bottom: 2px solid #666;
  }

  .risk-badge,
  .department-badge,
  .position-badge {
    border: 1px solid #000;
  }
}
</style>
