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

    <!-- 액션 버튼 섹션 -->
    <div class="action-buttons-section">
      <div class="button-group">
        <button @click="showAddUserModal = true" class="add-user-btn">
          <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
          </svg>
          사용자 추가
        </button>

        <button @click="exportSelected" :disabled="selectedUsers.length === 0" class="export-selected-btn">
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
          <button @click="resetFilters" class="reset-btn">초기화</button>
        </div>
      </div>

      <div v-show="showFilters" class="filters-content">
        <div class="filter-row">
          <div class="filter-item">
            <label for="yearFilter">기준년도</label>
            <select id="yearFilter" v-model="filters.year" @change="applyFilters">
              <option v-for="year in yearOptions" :key="year" :value="year">{{ year }}년</option>
            </select>
          </div>

          <div class="filter-item">
            <label for="departmentFilter">부서</label>
            <select id="departmentFilter" v-model="filters.department" @change="applyFilters">
              <option value="">전체 부서</option>
              <option v-for="dept in departmentOptions" :key="dept" :value="dept">{{ dept }}</option>
            </select>
          </div>

          <div class="filter-item">
            <label for="positionFilter">직급</label>
            <select id="positionFilter" v-model="filters.position" @change="applyFilters">
              <option value="">전체 직급</option>
              <option v-for="pos in positionOptions" :key="pos" :value="pos">{{ pos }}</option>
            </select>
          </div>

          <div class="filter-item">
            <label for="riskFilter">위험도</label>
            <select id="riskFilter" v-model="filters.riskLevel" @change="applyFilters">
              <option value="">전체 위험도</option>
              <option value="low">낮음</option>
              <option value="medium">보통</option>
              <option value="high">높음</option>
              <option value="critical">매우 높음</option>
              <option value="not_evaluated">미평가</option>
            </select>
          </div>
        </div>

        <div class="filter-row">
          <div class="filter-item search-item">
            <label for="searchInput">검색</label>
            <input
              id="searchInput"
              v-model="filters.search"
              type="text"
              placeholder="사용자명, 사번, 이메일로 검색..."
              @input="debounceSearch"
            />
          </div>

          <div class="filter-item">
            <label for="sortFilter">정렬</label>
            <div class="sort-controls">
              <select id="sortFilter" v-model="filters.sortBy" @change="applyFilters">
                <option value="total_penalty">총 감점</option>
                <option value="name">이름</option>
                <option value="department">부서</option>
                <option value="risk_level">위험도</option>
                <option value="last_audit_date">마지막 감사일</option>
              </select>
              <button @click="toggleSortOrder" class="sort-order-btn">
                <svg
                  width="16"
                  height="16"
                  fill="currentColor"
                  viewBox="0 0 16 16"
                  :class="{ rotated: filters.sortOrder === 'asc' }"
                >
                  <path
                    d="M8 15a.5.5 0 0 0 .5-.5V2.707l3.146 3.147a.5.5 0 0 0 .708-.708l-4-4a.5.5 0 0 0-.708 0l-4 4a.5.5 0 1 0 .708.708L7.5 2.707V14.5a.5.5 0 0 0 .5.5z"
                  />
                </svg>
              </button>
            </div>
          </div>

          <div class="filter-item">
            <label for="perPageFilter">페이지당 개수</label>
            <select id="perPageFilter" v-model="filters.perPage" @change="changePerPage">
              <option value="10">10개</option>
              <option value="20">20개</option>
              <option value="50">50개</option>
              <option value="100">100개</option>
            </select>
          </div>
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
            <tr v-if="users.length === 0" class="empty-row">
              <td colspan="8" class="empty-message">
                <div class="empty-content">
                  <svg width="48" height="48" fill="currentColor" viewBox="0 0 16 16">
                    <path
                      d="M15 14s1 0 1-1-1-4-5-4-5 3-5 4 1 1 1 1h8zm-7.978-1A.261.261 0 0 1 7 12.996c.001-.264.167-1.03.76-1.72C8.312 10.629 9.282 10 11 10c1.717 0 2.687.63 3.24 1.276.593.69.758 1.457.76 1.72l-.008.002a.274.274 0 0 1-.014.002H7.022zM11 7a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm3-2a3 3 0 1 1-6 0 3 3 0 0 1 6 0zM6.936 9.28a5.88 5.88 0 0 0-1.23-.247A7.35 7.35 0 0 0 5 9c-4 0-5 3-5 4 0 .667.333 1 1 1h4.216A2.238 2.238 0 0 1 5 13c0-1.01.377-2.042 1.09-2.904.243-.294.526-.569.846-.816zM4.92 10A5.493 5.493 0 0 0 4 13H1c0-.26.164-1.03.76-1.724.545-.636 1.492-1.256 3.16-1.275zM1.5 5.5a3 3 0 1 1 6 0 3 3 0 0 1-6 0zm3-2a2 2 0 1 0 0 4 2 2 0 0 0 0-4z"
                    />
                  </svg>
                  <h3>사용자가 없습니다</h3>
                  <p>필터 조건을 변경하거나 새 사용자를 추가해보세요.</p>
                </div>
              </td>
            </tr>
            <tr v-else v-for="user in users" :key="user.uid" class="user-row">
              <td class="checkbox-col">
                <input
                  type="checkbox"
                  :value="user.uid"
                  v-model="selectedUsers"
                />
              </td>
              <td class="user-col">
                <div class="user-info">
                  <div class="user-name">{{ user.name }}</div>
                  <div class="user-details">
                    <span class="user-id">{{ user.uid }}</span>
                    <span class="user-email">{{ user.email }}</span>
                  </div>
                  <div class="user-position">{{ user.position }}</div>
                </div>
              </td>
              <td class="department-col">
                <span class="department-badge">{{ user.department }}</span>
              </td>
              <td class="penalty-col">
                <span :class="['penalty-value', getPenaltyClass(user.total_penalty)]">
                  -{{ formatDecimal(user.total_penalty) }}점
                </span>
              </td>
              <td class="breakdown-col">
                <div class="penalty-breakdown">
                  <div v-if="parseFloat(user.audit_penalty || 0) > 0" class="breakdown-item">
                    <span class="breakdown-label">감사:</span>
                    <span class="breakdown-value">-{{ formatDecimal(user.audit_penalty) }}</span>
                  </div>
                  <div v-if="parseFloat(user.education_penalty || 0) > 0" class="breakdown-item">
                    <span class="breakdown-label">교육:</span>
                    <span class="breakdown-value">-{{ formatDecimal(user.education_penalty) }}</span>
                  </div>
                  <div v-if="parseFloat(user.training_penalty || 0) > 0" class="breakdown-item">
                    <span class="breakdown-label">훈련:</span>
                    <span class="breakdown-value">-{{ formatDecimal(user.training_penalty) }}</span>
                  </div>
                </div>
              </td>
              <td class="risk-col">
                <span :class="['risk-badge', `risk-${user.risk_level}`]">
                  {{ getRiskLevelLabel(user.risk_level) }}
                </span>
              </td>
              <td class="updated-col">
                <span class="update-date">{{ formatDate(user.last_audit_date) }}</span>
              </td>
              <td class="actions-col">
                <div class="action-buttons">
                  <button
                    @click="viewUserDetail(user.uid)"
                    class="detail-btn"
                    title="상세 보기"
                  >
                    <svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                      <path d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8zM1.173 8a13.133 13.133 0 0 1 1.66-2.043C4.12 4.668 5.88 3.5 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.133 13.133 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755C11.879 11.332 10.119 12.5 8 12.5c-2.12 0-3.879-1.168-5.168-2.457A13.134 13.134 0 0 1 1.172 8z"/>
                      <path d="M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0z"/>
                    </svg>
                  </button>
                  <button
                    @click="exportUserData(user.uid)"
                    class="export-btn"
                    title="개별 내보내기"
                  >
                    <svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
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

      <!-- 페이지네이션 -->
      <div v-if="pagination && pagination.total_pages > 1" class="pagination-section">
        <div class="pagination-info">
          <span>
            전체 {{ formatNumber(totalUsers) }}명 중
            {{ formatNumber((pagination.current_page - 1) * pagination.per_page + 1) }} -
            {{
              formatNumber(
                Math.min(pagination.current_page * pagination.per_page, totalUsers),
              )
            }}명
          </span>
        </div>
        <div class="pagination-controls">
          <button
            @click="goToPage(1)"
            :disabled="pagination.current_page === 1"
            class="page-btn"
          >
            처음
          </button>
          <button
            @click="goToPage(pagination.current_page - 1)"
            :disabled="pagination.current_page === 1"
            class="page-btn"
          >
            이전
          </button>

          <template v-for="page in paginationPages" :key="page">
            <button
              v-if="page !== '...'"
              @click="goToPage(page)"
              :class="['page-btn', { active: page === pagination.current_page }]"
            >
              {{ page }}
            </button>
            <span v-else class="page-ellipsis">...</span>
          </template>

          <button
            @click="goToPage(pagination.current_page + 1)"
            :disabled="pagination.current_page === pagination.total_pages"
            class="page-btn"
          >
            다음
          </button>
          <button
            @click="goToPage(pagination.total_pages)"
            :disabled="pagination.current_page === pagination.total_pages"
            class="page-btn"
          >
            마지막
          </button>
        </div>
      </div>
    </div>

    <!-- 사용자 추가 모달 -->
    <div v-if="showAddUserModal" class="modal-overlay" @click="closeAddUserModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>새 사용자 추가</h2>
          <button @click="closeAddUserModal" class="close-btn">
            <svg width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
              <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"/>
            </svg>
          </button>
        </div>

        <form @submit.prevent="submitAddUser" class="add-user-form">
          <div class="form-section">
            <h3>기본 정보</h3>
            <div class="form-row">
              <div class="form-group">
                <label for="newUserName">이름 *</label>
                <input
                  id="newUserName"
                  v-model="newUser.name"
                  type="text"
                  required
                  placeholder="사용자 이름"
                  :class="{ error: newUserErrors.name }"
                />
                <span v-if="newUserErrors.name" class="error-message">{{ newUserErrors.name }}</span>
              </div>

              <div class="form-group">
                <label for="newUserUid">사번 *</label>
                <input
                  id="newUserUid"
                  v-model="newUser.uid"
                  type="text"
                  required
                  placeholder="사번 (예: EMP001)"
                  :class="{ error: newUserErrors.uid }"
                />
                <span v-if="newUserErrors.uid" class="error-message">{{ newUserErrors.uid }}</span>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="newUserEmail">이메일 *</label>
                <input
                  id="newUserEmail"
                  v-model="newUser.email"
                  type="email"
                  required
                  placeholder="user@company.com"
                  :class="{ error: newUserErrors.email }"
                />
                <span v-if="newUserErrors.email" class="error-message">{{ newUserErrors.email }}</span>
              </div>

              <div class="form-group">
                <label for="newUserDepartment">부서 *</label>
                <input
                  id="newUserDepartment"
                  v-model="newUser.department"
                  type="text"
                  required
                  placeholder="부서명"
                  list="departmentList"
                  :class="{ error: newUserErrors.department }"
                />
                <datalist id="departmentList">
                  <option v-for="dept in departmentOptions" :key="dept" :value="dept">{{ dept }}</option>
                </datalist>
                <span v-if="newUserErrors.department" class="error-message">{{ newUserErrors.department }}</span>
              </div>
            </div>
          </div>

          <div class="form-section">
            <h3>권한 설정</h3>
            <div class="form-row">
              <div class="form-group">
                <label for="newUserRole">사용자 역할</label>
                <select id="newUserRole" v-model="newUser.role">
                  <option value="user">일반 사용자</option>
                  <option value="admin">관리자</option>
                </select>
              </div>

              <div class="form-group">
                <label for="newUserStatus">계정 상태</label>
                <select id="newUserStatus" v-model="newUser.is_active">
                  <option :value="true">활성</option>
                  <option :value="false">비활성</option>
                </select>
              </div>
            </div>
          </div>

          <div class="form-section">
            <h3>추가 정보</h3>
            <div class="form-group">
              <label for="newUserNotes">메모</label>
              <textarea
                id="newUserNotes"
                v-model="newUser.notes"
                placeholder="추가 정보나 메모 (선택사항)"
                rows="3"
              ></textarea>
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" @click="closeAddUserModal" class="cancel-btn">취소</button>
            <button type="submit" :disabled="addUserLoading" class="submit-btn">
              <span v-if="addUserLoading" class="loading-spinner-small"></span>
              {{ addUserLoading ? '추가 중...' : '사용자 추가' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 기존 데이터 및 상태 (변경 없음)
const users = ref([])
const selectedUsers = ref([])
const loading = ref(false)
const error = ref('')
const showFilters = ref(false)
const pagination = ref(null)
const departmentOptions = ref([])
const positionOptions = ref([])

// 사용자 추가 관련 새로운 상태
const showAddUserModal = ref(false)
const addUserLoading = ref(false)
const newUser = ref({
  name: '',
  uid: '',
  email: '',
  department: '',
  role: 'user',
  is_active: true,
  notes: ''
})
const newUserErrors = ref({})

// 기존 필터 상태 (변경 없음)
const filters = ref({
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

// 연도 옵션 (변경 없음)
const yearOptions = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: 5 }, (_, i) => currentYear - i)
})

// 계산된 속성들 (변경 없음)
const totalUsers = computed(() => pagination.value?.total_count || 0)

const isAllSelected = computed(() => {
  return users.value.length > 0 && selectedUsers.value.length === users.value.length
})

const isPartiallySelected = computed(() => {
  return selectedUsers.value.length > 0 && selectedUsers.value.length < users.value.length
})

const paginationPages = computed(() => {
  if (!pagination.value) return []

  const current = pagination.value.current_page
  const total = pagination.value.total_pages
  const pages = []

  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    pages.push(1)

    if (current > 4) {
      pages.push('...')
    }

    const start = Math.max(2, current - 1)
    const end = Math.min(total - 1, current + 1)

    for (let i = start; i <= end; i++) {
      pages.push(i)
    }

    if (current < total - 3) {
      pages.push('...')
    }

    pages.push(total)
  }

  return pages
})

// 기존 API 객체 (변경 없음, 단지 addUser 메서드 추가)
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
      year: filters.value.year,
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
      `/api/admin/dashboard/users/${userId}/detail?year=${filters.value.year}`,
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

  // 새로 추가된 사용자 생성 API
  async addUser(userData) {
    const response = await fetch('/api/admin/users', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${authStore.token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`)
    }

    return await response.json()
  },
}

// 사용자 추가 관련 새로운 함수들
function resetNewUser() {
  newUser.value = {
    name: '',
    uid: '',
    email: '',
    department: '',
    role: 'user',
    is_active: true,
    notes: ''
  }
  newUserErrors.value = {}
}

function closeAddUserModal() {
  showAddUserModal.value = false
  resetNewUser()
}

function validateNewUser() {
  const errors = {}

  // 필수 필드 검증
  if (!newUser.value.name.trim()) {
    errors.name = '이름은 필수입니다.'
  }

  if (!newUser.value.uid.trim()) {
    errors.uid = '사번은 필수입니다.'
  } else if (!/^[A-Za-z0-9]+$/.test(newUser.value.uid)) {
    errors.uid = '사번은 영문자와 숫자만 사용할 수 있습니다.'
  }

  if (!newUser.value.email.trim()) {
    errors.email = '이메일은 필수입니다.'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(newUser.value.email)) {
    errors.email = '올바른 이메일 형식을 입력해주세요.'
  }

  if (!newUser.value.department.trim()) {
    errors.department = '부서는 필수입니다.'
  }

  newUserErrors.value = errors
  return Object.keys(errors).length === 0
}

async function submitAddUser() {
  if (!validateNewUser()) {
    return
  }

  addUserLoading.value = true

  try {
    // 사용자 데이터 준비 (실제 DB 스키마에 맞춤)
    const userData = {
      name: newUser.value.name.trim(),
      uid: newUser.value.uid.trim(),
      email: newUser.value.email.trim(),
      department: newUser.value.department.trim(),
      role: newUser.value.role,
      is_active: newUser.value.is_active,
      notes: newUser.value.notes.trim() || null,
    }

    console.log('새 사용자 추가 시도:', userData)

    const result = await adminAPI.addUser(userData)

    showSuccess(`사용자 '${userData.name}'가 성공적으로 추가되었습니다.`)
    closeAddUserModal()

    // 사용자 목록 새로고침
    await loadUsers()

  } catch (err) {
    console.error('사용자 추가 실패:', err)

    // 서버에서 반환된 구체적인 오류 처리
    if (err.message.includes('이미 존재')) {
      if (err.message.includes('사번')) {
        newUserErrors.value.uid = '이미 사용 중인 사번입니다.'
      } else if (err.message.includes('이메일')) {
        newUserErrors.value.email = '이미 사용 중인 이메일입니다.'
      } else {
        error.value = err.message
      }
    } else {
      error.value = err.message || '사용자 추가에 실패했습니다.'
    }
  } finally {
    addUserLoading.value = false
  }
}

// 기존 함수들 (변경 없음)
async function loadUsers() {
  if (!authStore.isAuthenticated || !isAdmin()) {
    router.push('/login')
    return
  }

  loading.value = true
  error.value = ''

  try {
    console.log('사용자 목록 로드:', filters.value)

    const data = await adminAPI.getUsers(filters.value)

    users.value = data.users || []
    pagination.value = data.pagination

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
  const departments = [...new Set(users.value.map((user) => user.department).filter(Boolean))]
  departmentOptions.value = departments.sort()

  const positions = [...new Set(users.value.map((user) => user.position).filter(Boolean))]
  positionOptions.value = positions.sort()
}

async function applyFilters() {
  filters.value.page = 1
  selectedUsers.value = []
  await loadUsers()
}

function resetFilters() {
  Object.assign(filters.value, {
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
  filters.value.sortOrder = filters.value.sortOrder === 'desc' ? 'asc' : 'desc'
  applyFilters()
}

function toggleSelectAll() {
  if (isAllSelected.value) {
    selectedUsers.value = []
  } else {
    selectedUsers.value = users.value.map((user) => user.uid)
  }
}

async function goToPage(page) {
  if (page === '...' || page < 1 || (pagination.value && page > pagination.value.total_pages)) {
    return
  }

  filters.value.page = page
  await loadUsers()
}

async function changePerPage() {
  filters.value.page = 1
  await loadUsers()
}

async function exportSelected() {
  if (selectedUsers.value.length === 0) return

  try {
    loading.value = true
    const response = await adminAPI.exportUsers(selectedUsers.value, 'csv')

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `선택된_사용자_${selectedUsers.value.length}명_${filters.value.year}.csv`
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
    a.download = `전체_사용자_${totalUsers.value}명_${filters.value.year}.csv`
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
    a.download = `${userName}_상세데이터_${filters.value.year}.csv`
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

async function viewUserDetail(userId) {
  router.push(`/admin/users/${userId}/detail`)
}

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

let searchTimeout = null
function debounceSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    applyFilters()
  }, 500)
}

function showSuccess(message) {
  console.log('성공:', message)
  alert(message) // 임시로 alert 사용
}

function confirmAction(message) {
  return confirm(message)
}

function handleError(error, context) {
  console.error(`${context} 오류:`, error)
  error.value = `${context} 중 오류가 발생했습니다: ${error.message}`
}

function validateFilters() {
  if (filters.value.year < 2020 || filters.value.year > new Date().getFullYear() + 1) {
    filters.value.year = new Date().getFullYear()
  }

  if (filters.value.page < 1) {
    filters.value.page = 1
  }

  if (filters.value.perPage < 10 || filters.value.perPage > 200) {
    filters.value.perPage = 20
  }
}

function handleKeydown(event) {
  // 모달이 열려있을 때는 키보드 단축키 비활성화
  if (showAddUserModal.value) return

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

  // Ctrl+N: 새 사용자 추가
  if (event.ctrlKey && event.key === 'n') {
    event.preventDefault()
    showAddUserModal.value = true
  }

  // F5: 새로고침
  if (event.key === 'F5') {
    event.preventDefault()
    loadUsers()
  }

  // Escape: 모달 닫기
  if (event.key === 'Escape' && showAddUserModal.value) {
    event.preventDefault()
    closeAddUserModal()
  }
}

watch(
  () => filters.value.year,
  () => {
    if (filters.value.year) {
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

onMounted(() => {
  if (authStore.isAuthenticated && isAdmin()) {
    validateFilters()
    loadUsers()
  }

  document.addEventListener('keydown', handleKeydown)
})

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
@import '../styles/AdminUserManagement.css';

/* 새로 추가된 스타일 */
.action-buttons-section {
  background: #fff;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;
}

.button-group {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.add-user-btn {
  background: #2563eb;
  color: white;
  border: none;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background-color 0.2s;
}

.add-user-btn:hover {
  background: #1d4ed8;
}

.export-selected-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 모달 스타일 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #6b7280;
  transition: color 0.2s;
  padding: 0.25rem;
  border-radius: 4px;
}

.close-btn:hover {
  color: #374151;
  background: #f3f4f6;
}

.add-user-form {
  padding: 1.5rem;
}

.form-section {
  margin-bottom: 2rem;
}

.form-section h3 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 0.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-group input.error,
.form-group select.error,
.form-group textarea.error {
  border-color: #dc2626;
}

.error-message {
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: #dc2626;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.cancel-btn {
  background: #f3f4f6;
  color: #374151;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.cancel-btn:hover {
  background: #e5e7eb;
}

.submit-btn {
  background: #2563eb;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.submit-btn:hover:not(:disabled) {
  background: #1d4ed8;
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    margin: 1rem;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .button-group {
    flex-direction: column;
  }

  .modal-actions {
    flex-direction: column;
  }
}
</style>
