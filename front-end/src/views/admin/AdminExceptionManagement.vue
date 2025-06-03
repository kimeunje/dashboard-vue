<!-- views/admin/AdminExceptionManagement.vue - Template -->
<template>
  <div class="admin-exception-management">
    <div class="admin-header">
      <h1>제외 설정 관리</h1>
      <p>사용자별/부서별 보안 감사 항목 제외 설정을 관리합니다.</p>
      <div class="admin-nav">
        <RouterLink to="/admin" class="nav-item">대시보드</RouterLink>
        <RouterLink to="/admin/users" class="nav-item">사용자 관리</RouterLink>
        <RouterLink to="/admin/education" class="nav-item">교육 관리</RouterLink>
        <RouterLink to="/admin/training" class="nav-item">훈련 관리</RouterLink>
        <RouterLink to="/admin/scores" class="nav-item">점수 관리</RouterLink>
        <RouterLink to="/admin/exceptions" class="nav-item active">제외 설정</RouterLink>
      </div>
    </div>

    <!-- 탭 네비게이션 -->
    <div class="tabs-container">
      <div class="tabs-header">
        <button
          @click="activeTab = 'user'"
          class="tab-button"
          :class="{ active: activeTab === 'user' }"
        >
          <svg width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
            <path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm2-3a2 2 0 1 1-4 0 2 2 0 0 1 4 0zm4 8c0 1-1 1-1 1H3s-1 0-1-1 1-4 6-4 6 3 6 4zm-1-.004c-.001-.246-.154-.986-.832-1.664C11.516 10.68 10.289 10 8 10c-2.29 0-3.516.68-4.168 1.332-.678.678-.83 1.418-.832 1.664h10z"/>
          </svg>
          사용자별 제외 설정
          <span class="tab-count">{{ userExceptions.length }}개</span>
        </button>

        <button
          @click="activeTab = 'department'"
          class="tab-button"
          :class="{ active: activeTab === 'department' }"
        >
          <svg width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
            <path d="m8.186 1.113a.5.5 0 0 0-.372 0L1.846 3.5l2.404.961L10.404 2l-2.218-.887zm3.564 1.426L5.596 5 8 5.961 14.154 3.5l-2.404-.961zm3.25 1.7-6.5 2.6v7.922l6.5-2.6V4.24zM7.5 14.762V6.838L1 4.239v7.923l6.5 2.6zM7.443.184a1.5 1.5 0 0 1 1.114 0l7.129 2.852A.5.5 0 0 1 16 3.5v8.662a1 1 0 0 1-.629.928l-7.185 2.874a.5.5 0 0 1-.372 0L.629 13.09a1 1 0 0 1-.629-.928V3.5a.5.5 0 0 1 .314-.464L7.443.184z"/>
          </svg>
          부서별 제외 설정
          <span class="tab-count">{{ departmentExceptions.length }}개</span>
        </button>

        <button
          @click="activeTab = 'summary'"
          class="tab-button"
          :class="{ active: activeTab === 'summary' }"
        >
          <svg width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
            <path d="M1 2.5A1.5 1.5 0 0 1 2.5 1h3A1.5 1.5 0 0 1 7 2.5v3A1.5 1.5 0 0 1 5.5 7h-3A1.5 1.5 0 0 1 1 5.5v-3zM2.5 2a.5.5 0 0 0-.5.5v3a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5-.5v-3a.5.5 0 0 0-.5-.5h-3zm6.5.5A1.5 1.5 0 0 1 10.5 1h3A1.5 1.5 0 0 1 15 2.5v3A1.5 1.5 0 0 1 13.5 7h-3A1.5 1.5 0 0 1 9 5.5v-3zm1.5-.5a.5.5 0 0 0-.5.5v3a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5-.5v-3a.5.5 0 0 0-.5-.5h-3zM1 10.5A1.5 1.5 0 0 1 2.5 9h3A1.5 1.5 0 0 1 7 10.5v3A1.5 1.5 0 0 1 5.5 15h-3A1.5 1.5 0 0 1 1 13.5v-3zm1.5-.5a.5.5 0 0 0-.5.5v3a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5-.5v-3a.5.5 0 0 0-.5-.5h-3zm6.5.5A1.5 1.5 0 0 1 10.5 9h3a1.5 1.5 0 0 1 1.5 1.5v3a1.5 1.5 0 0 1-1.5 1.5h-3A1.5 1.5 0 0 1 9 13.5v-3zm1.5-.5a.5.5 0 0 0-.5.5v3a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5-.5v-3a.5.5 0 0 0-.5-.5h-3z"/>
          </svg>
          요약 통계
        </button>
      </div>
    </div>

    <!-- 액션 바 -->
    <div v-if="activeTab !== 'summary'" class="action-bar">
      <div class="filters">
        <div class="search-group">
          <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16" class="search-icon">
            <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/>
          </svg>
          <input
            type="text"
            placeholder="검색..."
            v-model="searchQuery"
            class="search-input"
          />
        </div>

        <select v-model="filterDepartment" class="filter-select">
          <option value="">모든 부서</option>
          <option v-for="dept in departments" :key="dept" :value="dept">{{ dept }}</option>
        </select>

        <select v-model="filterItem" class="filter-select">
          <option value="">모든 항목</option>
          <option v-for="item in checklistItems" :key="item.item_id" :value="item.item_id">
            {{ item.item_name }} ({{ item.category }})
          </option>
        </select>
      </div>

      <div class="action-buttons">
        <button @click="showAddModal = true" class="primary-button">
          <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path d="M8 2a.5.5 0 0 1 .5.5v5h5a.5.5 0 0 1 0 1h-5v5a.5.5 0 0 1-1 0v-5h-5a.5.5 0 0 1 0-1h5v-5A.5.5 0 0 1 8 2z"/>
          </svg>
          제외 설정 추가
        </button>

        <button @click="handleExport('csv')" class="secondary-button">
          <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/>
            <path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"/>
          </svg>
          CSV 내보내기
        </button>
      </div>
    </div>

    <!-- 컨텐츠 영역 -->
    <div class="content-area">
      <!-- 로딩 상태 -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>데이터를 불러오는 중...</p>
      </div>

      <!-- 사용자별 제외 설정 테이블 -->
      <div v-else-if="activeTab === 'user'" class="table-container">
        <table class="exception-table">
          <thead>
            <tr>
              <th>사용자</th>
              <th>부서</th>
              <th>점검 항목</th>
              <th>제외 사유</th>
              <th>제외 유형</th>
              <th>기간</th>
              <th>생성자</th>
              <th>액션</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filteredUserExceptions.length === 0">
              <td colspan="8" class="no-data">사용자별 제외 설정이 없습니다.</td>
            </tr>
            <tr v-for="exc in filteredUserExceptions" :key="`${exc.user_id}-${exc.item_id}`" class="table-row">
              <td>
                <div class="user-info">
                  <div class="user-name">{{ exc.username }}</div>
                  <div class="user-id">{{ exc.user_login_id }}</div>
                </div>
              </td>
              <td>{{ exc.department }}</td>
              <td>
                <div class="item-info">
                  <div class="item-name">{{ exc.item_name }}</div>
                  <div class="item-category">{{ exc.category }}</div>
                </div>
              </td>
              <td>
                <div class="exclude-reason" :title="exc.exclude_reason">
                  {{ truncateText(exc.exclude_reason, 50) }}
                </div>
              </td>
              <td>
                <div class="exclude-type" :class="exc.exclude_type">
                  <span class="type-icon">
                    {{ exc.exclude_type === 'permanent' ? '🔒' : '⏰' }}
                  </span>
                  {{ exc.exclude_type === 'permanent' ? '영구' : '임시' }}
                </div>
              </td>
              <td>
                {{ exc.exclude_type === 'temporary' && exc.start_date && exc.end_date
                  ? `${exc.start_date} ~ ${exc.end_date}` : '-' }}
              </td>
              <td>{{ exc.created_by }}</td>
              <td>
                <div class="action-buttons">
                  <button
                    @click="handleDeleteException('user', exc.user_id, exc.item_id)"
                    class="delete-button"
                    title="삭제"
                  >
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                      <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                      <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 부서별 제외 설정 테이블 -->
      <div v-else-if="activeTab === 'department'" class="table-container">
        <table class="exception-table">
          <thead>
            <tr>
              <th>부서</th>
              <th>점검 항목</th>
              <th>제외 사유</th>
              <th>제외 유형</th>
              <th>기간</th>
              <th>영향받는 사용자</th>
              <th>생성자</th>
              <th>액션</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filteredDepartmentExceptions.length === 0">
              <td colspan="8" class="no-data">부서별 제외 설정이 없습니다.</td>
            </tr>
            <tr v-for="exc in filteredDepartmentExceptions" :key="`${exc.department}-${exc.item_id}`" class="table-row">
              <td class="department-name">{{ exc.department }}</td>
              <td>
                <div class="item-info">
                  <div class="item-name">{{ exc.item_name }}</div>
                  <div class="item-category">{{ exc.category }}</div>
                </div>
              </td>
              <td>
                <div class="exclude-reason" :title="exc.exclude_reason">
                  {{ truncateText(exc.exclude_reason, 50) }}
                </div>
              </td>
              <td>
                <div class="exclude-type" :class="exc.exclude_type">
                  <span class="type-icon">
                    {{ exc.exclude_type === 'permanent' ? '🔒' : '⏰' }}
                  </span>
                  {{ exc.exclude_type === 'permanent' ? '영구' : '임시' }}
                </div>
              </td>
              <td>
                {{ exc.exclude_type === 'temporary' && exc.start_date && exc.end_date
                  ? `${exc.start_date} ~ ${exc.end_date}` : '-' }}
              </td>
              <td>
                <span class="affected-users">{{ exc.affected_users }}명</span>
              </td>
              <td>{{ exc.created_by }}</td>
              <td>
                <div class="action-buttons">
                  <button
                    @click="handleDeleteException('department', exc.department, exc.item_id)"
                    class="delete-button"
                    title="삭제"
                  >
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                      <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                      <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 요약 통계 -->
      <div v-else-if="activeTab === 'summary' && summary" class="summary-container">
        <div class="summary-grid">
          <!-- 사용자별 제외 설정 통계 -->
          <div class="summary-card user-stats">
            <h3>사용자별 제외 설정</h3>
            <div class="stats-list">
              <div class="stat-item">
                <span class="stat-label">총 설정 수:</span>
                <span class="stat-value">{{ summary.user_exceptions?.total_user_exceptions || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">영구 제외:</span>
                <span class="stat-value">{{ summary.user_exceptions?.permanent_user_exceptions || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">임시 제외:</span>
                <span class="stat-value">{{ summary.user_exceptions?.temporary_user_exceptions || 0 }}</span>
              </div>
            </div>
          </div>

          <!-- 부서별 제외 설정 통계 -->
          <div class="summary-card dept-stats">
            <h3>부서별 제외 설정</h3>
            <div class="stats-list">
              <div class="stat-item">
                <span class="stat-label">총 설정 수:</span>
                <span class="stat-value">{{ summary.department_exceptions?.total_dept_exceptions || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">영구 제외:</span>
                <span class="stat-value">{{ summary.department_exceptions?.permanent_dept_exceptions || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">임시 제외:</span>
                <span class="stat-value">{{ summary.department_exceptions?.temporary_dept_exceptions || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">영향받는 부서:</span>
                <span class="stat-value">{{ summary.department_exceptions?.affected_departments || 0 }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 가장 많이 제외된 항목들 -->
        <div v-if="summary.top_excluded_items && summary.top_excluded_items.length > 0" class="top-items-card">
          <h3>가장 많이 제외된 항목</h3>
          <div class="top-items-list">
            <div
              v-for="(item, index) in summary.top_excluded_items"
              :key="index"
              class="top-item"
            >
              <div class="item-info">
                <span class="item-name">{{ item.item_name }}</span>
                <span class="item-category">({{ item.category }})</span>
              </div>
              <span class="exception-count">{{ item.exception_count }}건</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 제외 설정 추가 모달 -->
    <div v-if="showAddModal" class="modal-overlay" @click="closeAddModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>제외 설정 추가</h3>
          <button @click="closeAddModal" class="close-button">×</button>
        </div>

        <div class="modal-body">
          <form @submit.prevent="handleAddException" class="exception-form">
            <!-- 제외 유형 선택 -->
            <div class="form-group">
              <label>제외 유형:</label>
              <div class="radio-group">
                <label class="radio-option">
                  <input type="radio" v-model="formData.type" value="user" />
                  <span>사용자별</span>
                </label>
                <label class="radio-option">
                  <input type="radio" v-model="formData.type" value="department" />
                  <span>부서별</span>
                </label>
              </div>
            </div>

            <!-- 사용자 선택 (사용자별인 경우) -->
            <div v-if="formData.type === 'user'" class="form-group">
              <label>사용자:</label>
              <select v-model="formData.user_id" required class="form-select">
                <option value="">사용자를 선택하세요</option>
                <option v-for="user in users" :key="user.uid" :value="user.uid">
                  {{ user.username }} ({{ user.user_id }}) - {{ user.department }}
                </option>
              </select>
            </div>

            <!-- 부서 선택 (부서별인 경우) -->
            <div v-if="formData.type === 'department'" class="form-group">
              <label>부서:</label>
              <select v-model="formData.department" required class="form-select">
                <option value="">부서를 선택하세요</option>
                <option v-for="dept in departments" :key="dept" :value="dept">
                  {{ dept }}
                </option>
              </select>
            </div>

            <!-- 점검 항목 선택 -->
            <div class="form-group">
              <label>점검 항목:</label>
              <select v-model="formData.item_id" required class="form-select">
                <option value="">점검 항목을 선택하세요</option>
                <optgroup v-for="category in groupedItems" :key="category.name" :label="category.name">
                  <option v-for="item in category.items" :key="item.item_id" :value="item.item_id">
                    {{ item.item_name }} ({{ item.check_type === 'daily' ? '정기' : '수시' }})
                  </option>
                </optgroup>
              </select>
            </div>

            <!-- 제외 사유 -->
            <div class="form-group">
              <label>제외 사유:</label>
              <textarea
                v-model="formData.exclude_reason"
                required
                class="form-textarea"
                rows="3"
                placeholder="제외 사유를 입력하세요..."
              ></textarea>
            </div>

            <!-- 제외 기간 유형 -->
            <div class="form-group">
              <label>제외 기간:</label>
              <div class="radio-group">
                <label class="radio-option">
                  <input type="radio" v-model="formData.exclude_type" value="permanent" />
                  <span>영구 제외</span>
                </label>
                <label class="radio-option">
                  <input type="radio" v-model="formData.exclude_type" value="temporary" />
                  <span>임시 제외</span>
                </label>
              </div>
            </div>

            <!-- 임시 제외 기간 설정 -->
            <div v-if="formData.exclude_type === 'temporary'" class="form-row">
              <div class="form-group">
                <label>시작일:</label>
                <input type="date" v-model="formData.start_date" required class="form-input" />
              </div>
              <div class="form-group">
                <label>종료일:</label>
                <input type="date" v-model="formData.end_date" required class="form-input" />
              </div>
            </div>
          </form>
        </div>

        <div class="modal-footer">
          <button @click="closeAddModal" class="cancel-button">취소</button>
          <button @click="handleAddException" :disabled="!isFormValid" class="save-button">
            추가
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

// views/admin/AdminExceptionManagement.vue - Script
<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { RouterLink } from 'vue-router'

// 반응형 데이터
const loading = ref(false)
const activeTab = ref('user') // 'user' | 'department' | 'summary'
const userExceptions = ref([])
const departmentExceptions = ref([])
const summary = ref(null)

// 폼 데이터
const users = ref([])
const departments = ref([])
const checklistItems = ref([])

// 모달 상태
const showAddModal = ref(false)
const showBulkModal = ref(false)

// 폼 상태
const formData = ref({
  type: 'user', // 'user' | 'department'
  user_id: '',
  department: '',
  item_id: '',
  exclude_reason: '',
  exclude_type: 'permanent',
  start_date: '',
  end_date: ''
})

// 검색 및 필터
const searchQuery = ref('')
const filterDepartment = ref('')
const filterItem = ref('')

// 토스트 메시지
const showToast = ref(false)
const toastMessage = ref('')
const toastType = ref('success')

// 계산된 속성
const groupedItems = computed(() => {
  const groups = {}
  checklistItems.value.forEach(item => {
    if (!groups[item.category]) {
      groups[item.category] = {
        name: item.category,
        items: []
      }
    }
    groups[item.category].items.push(item)
  })
  return Object.values(groups)
})

const filteredUserExceptions = computed(() => {
  return userExceptions.value.filter(exc => {
    const matchesSearch = !searchQuery.value ||
      exc.username.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      exc.user_login_id.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      exc.item_name.toLowerCase().includes(searchQuery.value.toLowerCase())

    const matchesDept = !filterDepartment.value || exc.department === filterDepartment.value
    const matchesItem = !filterItem.value || exc.item_id.toString() === filterItem.value

    return matchesSearch && matchesDept && matchesItem
  })
})

const filteredDepartmentExceptions = computed(() => {
  return departmentExceptions.value.filter(exc => {
    const matchesSearch = !searchQuery.value ||
      exc.department.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      exc.item_name.toLowerCase().includes(searchQuery.value.toLowerCase())

    const matchesDept = !filterDepartment.value || exc.department === filterDepartment.value
    const matchesItem = !filterItem.value || exc.item_id.toString() === filterItem.value

    return matchesSearch && matchesDept && matchesItem
  })
})

const isFormValid = computed(() => {
  const basicValid = formData.value.exclude_reason && formData.value.item_id

  if (formData.value.type === 'user') {
    return basicValid && formData.value.user_id
  } else {
    return basicValid && formData.value.department
  }
})

// 메서드
const loadInitialData = async () => {
  try {
    const [usersRes, deptsRes, itemsRes] = await Promise.all([
      fetch('/api/exceptions/users', { credentials: 'include' }),
      fetch('/api/exceptions/departments', { credentials: 'include' }),
      fetch('/api/exceptions/items', { credentials: 'include' })
    ])

    if (usersRes.ok) {
      users.value = await usersRes.json()
    }
    if (deptsRes.ok) {
      departments.value = await deptsRes.json()
    }
    if (itemsRes.ok) {
      checklistItems.value = await itemsRes.json()
    }
  } catch (error) {
    showToastMessage('초기 데이터 로드 실패: ' + error.message, 'error')
  }
}

const loadUserExceptions = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/exceptions/user-exceptions', {
      credentials: 'include'
    })

    if (response.ok) {
      userExceptions.value = await response.json()
    } else {
      throw new Error('사용자 제외 설정 로드 실패')
    }
  } catch (error) {
    showToastMessage('사용자 제외 설정 로드 실패', 'error')
  } finally {
    loading.value = false
  }
}

const loadDepartmentExceptions = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/exceptions/department-exceptions', {
      credentials: 'include'
    })

    if (response.ok) {
      departmentExceptions.value = await response.json()
    } else {
      throw new Error('부서 제외 설정 로드 실패')
    }
  } catch (error) {
    showToastMessage('부서 제외 설정 로드 실패', 'error')
  } finally {
    loading.value = false
  }
}

const loadSummary = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/exceptions/summary', {
      credentials: 'include'
    })

    if (response.ok) {
      summary.value = await response.json()
    } else {
      throw new Error('요약 데이터 로드 실패')
    }
  } catch (error) {
    showToastMessage('요약 데이터 로드 실패', 'error')
  } finally {
    loading.value = false
  }
}

const handleAddException = async () => {
  if (!isFormValid.value) {
    showToastMessage('필수 항목을 모두 입력해주세요.', 'error')
    return
  }

  try {
    const endpoint = formData.value.type === 'user' ? 'user-exceptions' : 'department-exceptions'
    const payload = { ...formData.value }

    // 필요 없는 필드 제거
    if (formData.value.type === 'user') {
      delete payload.department
      payload.user_id = parseInt(payload.user_id)
    } else {
      delete payload.user_id
    }

    payload.item_id = parseInt(payload.item_id)
    delete payload.type

    // 임시 제외가 아닌 경우 날짜 필드 제거
    if (payload.exclude_type !== 'temporary') {
      delete payload.start_date
      delete payload.end_date
    }

    const response = await fetch(`/api/exceptions/${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify(payload)
    })

    if (response.ok) {
      const result = await response.json()
      showToastMessage(result.message || '제외 설정이 추가되었습니다.', 'success')
      closeAddModal()
      resetForm()

      // 현재 탭에 따라 데이터 새로고침
      if (activeTab.value === 'user') {
        await loadUserExceptions()
      } else if (activeTab.value === 'department') {
        await loadDepartmentExceptions()
      }
    } else {
      const error = await response.json()
      showToastMessage(error.error || '추가 실패', 'error')
    }
  } catch (error) {
    showToastMessage('제외 설정 추가 실패: ' + error.message, 'error')
  }
}

const handleDeleteException = async (type, id1, id2) => {
  if (!confirm('이 제외 설정을 삭제하시겠습니까?')) {
    return
  }

  try {
    const endpoint = type === 'user'
      ? `user-exceptions/${id1}/${id2}`
      : `department-exceptions/${encodeURIComponent(id1)}/${id2}`

    const response = await fetch(`/api/exceptions/${endpoint}`, {
      method: 'DELETE',
      credentials: 'include'
    })

    if (response.ok) {
      const result = await response.json()
      showToastMessage(result.message || '제외 설정이 삭제되었습니다.', 'success')

      // 현재 탭에 따라 데이터 새로고침
      if (type === 'user') {
        await loadUserExceptions()
      } else {
        await loadDepartmentExceptions()
      }
    } else {
      const error = await response.json()
      showToastMessage(error.error || '삭제 실패', 'error')
    }
  } catch (error) {
    showToastMessage('제외 설정 삭제 실패: ' + error.message, 'error')
  }
}

const handleExport = async (format = 'json') => {
  try {
    const response = await fetch(`/api/exceptions/export?format=${format}`, {
      credentials: 'include'
    })

    if (response.ok) {
      if (format === 'csv') {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'exception_settings.csv'
        a.click()
        window.URL.revokeObjectURL(url)
      } else {
        const data = await response.json()
        const blob = new Blob([JSON.stringify(data, null, 2)], {
          type: 'application/json'
        })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'exception_settings.json'
        a.click()
        window.URL.revokeObjectURL(url)
      }
      showToastMessage('제외 설정이 내보내졌습니다.', 'success')
    } else {
      throw new Error('내보내기 실패')
    }
  } catch (error) {
    showToastMessage('내보내기 실패: ' + error.message, 'error')
  }
}

const closeAddModal = () => {
  showAddModal.value = false
}

const resetForm = () => {
  formData.value = {
    type: 'user',
    user_id: '',
    department: '',
    item_id: '',
    exclude_reason: '',
    exclude_type: 'permanent',
    start_date: '',
    end_date: ''
  }
}

const truncateText = (text, maxLength) => {
  if (!text) return '-'
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

const showToastMessage = (message, type = 'success') => {
  toastMessage.value = message
  toastType.value = type
  showToast.value = true

  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

// 감시자
watch(activeTab, async (newTab) => {
  if (newTab === 'user') {
    await loadUserExceptions()
  } else if (newTab === 'department') {
    await loadDepartmentExceptions()
  } else if (newTab === 'summary') {
    await loadSummary()
  }
})

// 폼 타입 변경시 관련 필드 초기화
watch(() => formData.value.type, (newType) => {
  if (newType === 'user') {
    formData.value.department = ''
  } else {
    formData.value.user_id = ''
  }
})

// 제외 유형 변경시 날짜 필드 초기화
watch(() => formData.value.exclude_type, (newType) => {
  if (newType === 'permanent') {
    formData.value.start_date = ''
    formData.value.end_date = ''
  }
})

// 라이프사이클 훅
onMounted(async () => {
  await loadInitialData()
  await loadUserExceptions() // 기본적으로 사용자별 제외 설정 로드
})
</script>

/* views/admin/AdminExceptionManagement.vue - CSS */
<style scoped>
.admin-exception-management {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f8fafc;
  min-height: calc(100vh - 114px);
}

/* 관리자 헤더 */
.admin-header {
  background-color: white;
  border-radius: 12px;
  padding: 20px 30px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
}

.admin-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.admin-header p {
  color: #6b7280;
  margin: 0 0 20px 0;
  font-size: 16px;
}

.admin-nav {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.nav-item {
  padding: 8px 16px;
  border-radius: 8px;
  text-decoration: none;
  color: #6b7280;
  font-weight: 500;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.nav-item:hover {
  background-color: #f3f4f6;
  color: #374151;
}

.nav-item.active {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

/* 탭 컨테이너 */
.tabs-container {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
  margin-bottom: 20px;
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
  font-size: 14px;
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
  font-size: 12px;
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

/* 액션 바 */
.action-bar {
  background-color: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
  margin-bottom: 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: end;
  justify-content: space-between;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  flex: 1;
}

.search-group {
  position: relative;
  min-width: 200px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
}

.search-input {
  width: 100%;
  padding: 8px 12px 8px 36px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background-color: white;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background-color: white;
  min-width: 120px;
}

.filter-select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.action-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.primary-button,
.secondary-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.primary-button {
  background-color: var(--primary-color);
  color: white;
}

.primary-button:hover {
  background-color: var(--dark-blue);
}

.secondary-button {
  background-color: #10b981;
  color: white;
}

.secondary-button:hover {
  background-color: #059669;
}

/* 컨텐츠 영역 */
.content-area {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

.loading-state p {
  color: #6b7280;
  margin: 0;
}

/* 테이블 스타일 */
.table-container {
  overflow-x: auto;
}

.exception-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.exception-table th {
  background-color: #f9fafb;
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
  white-space: nowrap;
}

.exception-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #f3f4f6;
  vertical-align: top;
}

.table-row:hover {
  background-color: #f9fafb;
}

.no-data {
  text-align: center;
  color: #9ca3af;
  font-style: italic;
  padding: 40px;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-weight: 600;
  color: #1f2937;
}

.user-id {
  font-size: 12px;
  color: #6b7280;
}

.item-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.item-name {
  font-weight: 500;
  color: #1f2937;
}

.item-category {
  font-size: 12px;
  color: #6b7280;
}

.exclude-reason {
  max-width: 200px;
  color: #374151;
  line-height: 1.4;
}

.exclude-type {
  display: flex;
  align-items: center;
  gap: 6px;
}

.exclude-type.permanent {
  color: #059669;
}

.exclude-type.temporary {
  color: #d97706;
}

.type-icon {
  font-size: 16px;
}

.department-name {
  font-weight: 600;
  color: #1f2937;
}

.affected-users {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  background-color: #dbeafe;
  color: #1e40af;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.action-buttons {
  display: flex;
  gap: 8px;
  align-items: center;
}

.delete-button {
  background: none;
  border: none;
  padding: 6px;
  border-radius: 4px;
  cursor: pointer;
  color: #ef4444;
  transition: all 0.2s ease;
}

.delete-button:hover {
  background-color: #fef2f2;
  color: #dc2626;
}

/* 요약 통계 스타일 */
.summary-container {
  padding: 24px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.summary-card {
  padding: 24px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.summary-card.user-stats {
  background: linear-gradient(135deg, #dbeafe, #bfdbfe);
  border-color: #3b82f6;
}

.summary-card.dept-stats {
  background: linear-gradient(135deg, #d1fae5, #a7f3d0);
  border-color: #10b981;
}

.summary-card h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.stats-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  color: #374151;
  font-weight: 500;
}

.stat-value {
  font-weight: 700;
  color: #1f2937;
  font-size: 16px;
}

.top-items-card {
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  border: 1px solid #f59e0b;
  border-radius: 12px;
  padding: 24px;
}

.top-items-card h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.top-items-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.top-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid rgba(245, 158, 11, 0.3);
}

.top-item:last-child {
  border-bottom: none;
}

.top-item .item-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.top-item .item-name {
  font-weight: 600;
  color: #1f2937;
}

.top-item .item-category {
  color: #6b7280;
  font-size: 14px;
}

.exception-count {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  background-color: #fbbf24;
  color: #92400e;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 700;
}

/* 모달 스타일 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
  width: 600px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #f3f4f6;
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #9ca3af;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
}

.close-button:hover {
  background-color: #f3f4f6;
  color: #6b7280;
}

.modal-body {
  padding: 24px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #f3f4f6;
}

/* 폼 스타일 */
.exception-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.radio-group {
  display: flex;
  gap: 16px;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-size: 14px;
  color: #374151;
}

.radio-option input[type="radio"] {
  margin: 0;
}

.form-input,
.form-select,
.form-textarea {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  background-color: white;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.form-textarea {
  resize: vertical;
  font-family: inherit;
}

.cancel-button,
.save-button {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.cancel-button {
  background-color: white;
  color: #6b7280;
  border: 1px solid #d1d5db;
}

.cancel-button:hover {
  background-color: #f9fafb;
}

.save-button {
  background-color: var(--primary-color);
  color: white;
}

.save-button:hover:not(:disabled) {
  background-color: var(--dark-blue);
}

.save-button:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

/* 토스트 메시지 */
.toast-message {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 8px;
  color: white;
  font-size: 14px;
  font-weight: 500;
  z-index: 1000;
  animation: slideIn 0.3s ease;
  max-width: 400px;
}

.toast-message.success {
  background-color: #10b981;
}

.toast-message.error {
  background-color: #ef4444;
}

.toast-message.info {
  background-color: #3b82f6;
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

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .admin-exception-management {
    padding: 15px;
  }

  .admin-header {
    padding: 20px;
  }

  .admin-nav {
    flex-direction: column;
    gap: 8px;
  }

  .action-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filters {
    flex-direction: column;
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

  .exception-table {
    font-size: 12px;
  }

  .exception-table th,
  .exception-table td {
    padding: 8px 6px;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }

  .modal-content {
    width: 95vw;
    margin: 20px;
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .exclude-reason {
    max-width: 120px;
  }

  .user-info,
  .item-info {
    font-size: 12px;
  }

  .action-buttons {
    flex-direction: column;
  }

  .exception-table th,
  .exception-table td {
    padding: 6px 4px;
    font-size: 11px;
  }
}
</style>
