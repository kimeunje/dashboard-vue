<!-- views/admin/AdminUserManagement.vue - Template -->
<template>
  <div class="admin-users">
    <div class="admin-header">
      <h1>사용자 관리</h1>
      <div class="admin-nav">
        <RouterLink to="/admin" class="nav-item">대시보드</RouterLink>
        <RouterLink to="/admin/users" class="nav-item active">사용자 관리</RouterLink>
        <RouterLink to="/admin/education" class="nav-item">교육 관리</RouterLink>
        <RouterLink to="/admin/training" class="nav-item">훈련 관리</RouterLink>
        <RouterLink to="/admin/scores" class="nav-item">점수 관리</RouterLink>
      </div>
    </div>

    <div class="management-content">
      <!-- 필터 및 검색 -->
      <div class="filter-section">
        <div class="filter-group">
          <label>부서:</label>
          <select v-model="selectedDepartment" @change="applyFilters">
            <option value="">전체 부서</option>
            <option v-for="dept in departments" :key="dept" :value="dept">{{ dept }}</option>
          </select>
        </div>

        <div class="filter-group">
          <label>점수 등급:</label>
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
          <label>정렬:</label>
          <select v-model="sortBy" @change="applySorting">
            <option value="username">사용자명</option>
            <option value="department">부서</option>
            <option value="latest_score">최신 점수</option>
            <option value="latest_grade">최신 등급</option>
            <option value="last_updated">최종 업데이트</option>
          </select>
        </div>

        <div class="search-group">
          <input
            type="text"
            v-model="searchQuery"
            @input="searchUsers"
            placeholder="사용자명, ID, 이메일 검색..."
            class="search-input"
          />
        </div>
      </div>

      <!-- 액션 버튼 -->
      <div class="action-section">
        <div class="action-buttons">
          <button @click="refreshUsers" class="primary-button" :disabled="loading">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path
                fill-rule="evenodd"
                d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2v1z"
              />
              <path
                d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466z"
              />
            </svg>
            새로고침
          </button>

          <button @click="exportUsers" class="secondary-button">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"
              />
              <path
                d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"
              />
            </svg>
            내보내기
          </button>

          <button
            @click="showSelectedActions = !showSelectedActions"
            class="outline-button"
            :disabled="selectedUsers.length === 0"
          >
            선택된 사용자 작업 ({{ selectedUsers.length }})
          </button>
        </div>

        <div v-if="showSelectedActions && selectedUsers.length > 0" class="selected-actions">
          <button @click="bulkRecalculateScores" class="action-btn">점수 재계산</button>
          <button @click="bulkSendNotification" class="action-btn">알림 발송</button>
          <button @click="exportSelectedUsers" class="action-btn">선택 내보내기</button>
        </div>
      </div>

      <!-- 사용자 목록 테이블 -->
      <div class="table-section">
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>사용자 목록을 불러오는 중...</p>
        </div>

        <div v-else-if="error" class="error-state">
          <div class="error-icon">⚠️</div>
          <p>{{ error }}</p>
          <button @click="loadUsers" class="retry-button">다시 시도</button>
        </div>

        <div v-else class="table-container">
          <table class="users-table">
            <thead>
              <tr>
                <th>
                  <input type="checkbox" v-model="selectAll" @change="toggleSelectAll" />
                </th>
                <th>사용자 ID</th>
                <th>사용자명</th>
                <th>이메일</th>
                <th>부서</th>
                <th>최신 점수</th>
                <th>등급</th>
                <th>점수 업데이트</th>
                <th>최종 활동</th>
                <th>액션</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in paginatedUsers" :key="user.uid">
                <td>
                  <input type="checkbox" v-model="selectedUsers" :value="user.uid" />
                </td>
                <td>{{ user.user_id }}</td>
                <td>
                  <div class="user-info">
                    <span class="username">{{ user.username }}</span>
                  </div>
                </td>
                <td>{{ user.mail }}</td>
                <td>{{ user.department }}</td>
                <td>
                  <span class="score-badge" :class="getScoreClass(user.latest_score)">
                    {{ user.latest_score ? `${user.latest_score}점` : '-' }}
                  </span>
                </td>
                <td>
                  <span class="grade-badge" :class="getGradeClass(user.latest_grade)">
                    {{ user.latest_grade || '-' }}
                  </span>
                </td>
                <td>{{ formatDate(user.last_score_update) }}</td>
                <td>{{ formatDate(user.last_updated) }}</td>
                <td>
                  <div class="action-buttons">
                    <button @click="viewUserDetails(user)" class="view-button" title="상세 보기">
                      👁️
                    </button>
                    <button
                      @click="recalculateUserScore(user)"
                      class="calculate-button"
                      title="점수 재계산"
                    >
                      🔄
                    </button>
                    <button @click="sendNotification(user)" class="notify-button" title="알림 발송">
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
              {{ currentPage }} / {{ totalPages }} 페이지 (총 {{ filteredUsers.length }}명)
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

    <!-- 사용자 상세 정보 모달 -->
    <div v-if="showUserModal" class="modal-overlay" @click="closeUserModal">
      <div class="modal-content user-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ selectedUser?.username }} 상세 정보</h3>
          <button @click="closeUserModal" class="close-button">×</button>
        </div>

        <div class="modal-body" v-if="userDetails">
          <!-- 기본 정보 -->
          <div class="user-detail-section">
            <h4>기본 정보</h4>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="label">사용자 ID:</span>
                <span class="value">{{ userDetails.user_info.user_id }}</span>
              </div>
              <div class="detail-item">
                <span class="label">사용자명:</span>
                <span class="value">{{ userDetails.user_info.username }}</span>
              </div>
              <div class="detail-item">
                <span class="label">이메일:</span>
                <span class="value">{{ userDetails.user_info.mail }}</span>
              </div>
              <div class="detail-item">
                <span class="label">부서:</span>
                <span class="value">{{ userDetails.user_info.department }}</span>
              </div>
            </div>
          </div>

          <!-- 점수 정보 -->
          <div class="user-detail-section" v-if="userDetails.score_info">
            <h4>{{ userDetails.year }}년 보안 점수</h4>
            <div class="score-summary">
              <div class="score-card">
                <div class="score-number">{{ userDetails.score_info.total_score }}</div>
                <div class="score-grade">{{ userDetails.score_info.grade }}</div>
              </div>
              <div class="score-breakdown">
                <div class="breakdown-item">
                  <span class="breakdown-label">상시감사:</span>
                  <span class="breakdown-value">{{ userDetails.score_info.audit_score }}점</span>
                </div>
                <div class="breakdown-item">
                  <span class="breakdown-label">교육 감점:</span>
                  <span class="breakdown-value penalty"
                    >-{{ userDetails.score_info.education_penalty }}점</span
                  >
                </div>
                <div class="breakdown-item">
                  <span class="breakdown-label">훈련 감점:</span>
                  <span class="breakdown-value penalty"
                    >-{{ userDetails.score_info.training_penalty }}점</span
                  >
                </div>
              </div>
            </div>
          </div>

          <!-- 교육 현황 -->
          <div class="user-detail-section">
            <h4>{{ userDetails.year }}년 교육 현황</h4>
            <div class="quarterly-grid">
              <div v-for="quarter in [1, 2, 3, 4]" :key="quarter" class="quarter-item">
                <div class="quarter-header">{{ quarter }}분기</div>
                <div
                  class="quarter-status"
                  :class="getEducationStatus(userDetails.education_records, quarter)"
                >
                  {{ getEducationText(userDetails.education_records, quarter) }}
                </div>
              </div>
            </div>
          </div>

          <!-- 모의훈련 현황 -->
          <div class="user-detail-section">
            <h4>{{ userDetails.year }}년 모의훈련 현황</h4>
            <div class="quarterly-grid">
              <div v-for="quarter in [1, 2, 3, 4]" :key="quarter" class="quarter-item">
                <div class="quarter-header">{{ quarter }}분기</div>
                <div
                  class="quarter-status"
                  :class="getTrainingStatus(userDetails.training_records, quarter)"
                >
                  {{ getTrainingText(userDetails.training_records, quarter) }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="closeUserModal" class="cancel-button">닫기</button>
          <button @click="recalculateUserScore(selectedUser)" class="primary-button">
            점수 재계산
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

// views/admin/AdminUserManagement.vue - Script
<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'

// 반응형 데이터
const loading = ref(false)
const error = ref(null)
const users = ref([])
const filteredUsers = ref([])
const selectedUsers = ref([])
const selectAll = ref(false)
const showSelectedActions = ref(false)

// 필터 및 검색
const selectedDepartment = ref('')
const selectedGrade = ref('')
const sortBy = ref('username')
const searchQuery = ref('')

// 페이지네이션
const currentPage = ref(1)
const itemsPerPage = ref(20)

// 모달
const showUserModal = ref(false)
const selectedUser = ref(null)
const userDetails = ref(null)

// 토스트
const showToast = ref(false)
const toastMessage = ref('')
const toastType = ref('success')

// 계산된 속성
const departments = computed(() => {
  const depts = [...new Set(users.value.map((user) => user.department).filter(Boolean))]
  return depts.sort()
})

const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredUsers.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredUsers.value.length / itemsPerPage.value)
})

// 메서드
const loadUsers = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await fetch('/api/admin/users', {
      credentials: 'include',
    })

    if (!response.ok) {
      throw new Error('사용자 목록을 불러올 수 없습니다.')
    }

    users.value = await response.json()
    applyFilters()
  } catch (err) {
    console.error('사용자 목록 로드 실패:', err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  let filtered = [...users.value]

  // 부서 필터
  if (selectedDepartment.value) {
    filtered = filtered.filter((user) => user.department === selectedDepartment.value)
  }

  // 등급 필터
  if (selectedGrade.value) {
    filtered = filtered.filter((user) => user.latest_grade === selectedGrade.value)
  }

  // 검색 필터
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(
      (user) =>
        user.username.toLowerCase().includes(query) ||
        user.user_id.toLowerCase().includes(query) ||
        user.mail.toLowerCase().includes(query),
    )
  }

  filteredUsers.value = filtered
  applySorting()
  currentPage.value = 1
}

const applySorting = () => {
  filteredUsers.value.sort((a, b) => {
    let aValue = a[sortBy.value]
    let bValue = b[sortBy.value]

    if (sortBy.value === 'latest_score') {
      aValue = aValue || 0
      bValue = bValue || 0
      return bValue - aValue // 내림차순
    }

    if (typeof aValue === 'string') {
      return aValue.localeCompare(bValue)
    }

    if (aValue instanceof Date || bValue instanceof Date) {
      return new Date(bValue) - new Date(aValue) // 최신순
    }

    return aValue > bValue ? 1 : -1
  })
}

const searchUsers = () => {
  applyFilters()
}

const refreshUsers = () => {
  loadUsers()
}

const toggleSelectAll = () => {
  if (selectAll.value) {
    selectedUsers.value = paginatedUsers.value.map((user) => user.uid)
  } else {
    selectedUsers.value = []
  }
}

const viewUserDetails = async (user) => {
  selectedUser.value = user
  showUserModal.value = true

  try {
    const response = await fetch(`/api/admin/users/${user.uid}/details`, {
      credentials: 'include',
    })

    if (response.ok) {
      userDetails.value = await response.json()
    }
  } catch (err) {
    console.error('사용자 상세 정보 조회 실패:', err)
  }
}

const closeUserModal = () => {
  showUserModal.value = false
  selectedUser.value = null
  userDetails.value = null
}

const recalculateUserScore = async (user) => {
  try {
    const response = await fetch('/api/admin/scores/recalculate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        user_id: user.uid,
        year: new Date().getFullYear(),
      }),
    })

    if (!response.ok) {
      throw new Error('점수 재계산에 실패했습니다.')
    }

    showToastMessage(`${user.username}의 점수가 재계산되었습니다.`, 'success')
    await loadUsers()
  } catch (err) {
    console.error('점수 재계산 실패:', err)
    showToastMessage(err.message, 'error')
  }
}

const bulkRecalculateScores = async () => {
  if (selectedUsers.value.length === 0) return

  try {
    const promises = selectedUsers.value.map((userId) =>
      fetch('/api/admin/scores/recalculate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          user_id: userId,
          year: new Date().getFullYear(),
        }),
      }),
    )

    await Promise.all(promises)
    showToastMessage(`${selectedUsers.value.length}명의 점수가 재계산되었습니다.`, 'success')
    selectedUsers.value = []
    showSelectedActions.value = false
    await loadUsers()
  } catch (err) {
    console.error('일괄 점수 재계산 실패:', err)
    showToastMessage('일괄 점수 재계산에 실패했습니다.', 'error')
  }
}

const sendNotification = (user) => {
  showToastMessage(`${user.username}에게 알림을 발송했습니다.`, 'success')
}

const bulkSendNotification = () => {
  showToastMessage(`선택된 ${selectedUsers.value.length}명에게 알림을 발송했습니다.`, 'success')
  selectedUsers.value = []
  showSelectedActions.value = false
}

const exportUsers = () => {
  showToastMessage('사용자 목록 내보내기 기능이 준비중입니다.', 'info')
}

const exportSelectedUsers = () => {
  showToastMessage(`선택된 ${selectedUsers.value.length}명의 정보를 내보냈습니다.`, 'success')
  selectedUsers.value = []
  showSelectedActions.value = false
}

const getScoreClass = (score) => {
  if (!score) return 'no-score'
  if (score >= 90) return 'excellent'
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

const getEducationStatus = (records, quarter) => {
  const record = records.find((r) => r.quarter === quarter)
  return record?.completion_status ? 'completed' : 'incomplete'
}

const getEducationText = (records, quarter) => {
  const record = records.find((r) => r.quarter === quarter)
  return record?.completion_status ? '이수완료' : '미이수'
}

const getTrainingStatus = (records, quarter) => {
  const record = records.find((r) => r.quarter === quarter)
  if (!record) return 'pending'
  return record.training_result === 'pass' ? 'passed' : 'failed'
}

const getTrainingText = (records, quarter) => {
  const record = records.find((r) => r.quarter === quarter)
  if (!record) return '미실시'
  return record.training_result === 'pass' ? '통과' : '실패'
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
  loadUsers()
})
</script>

<style scoped>
.admin-users {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f8fafc;
  min-height: calc(100vh - 114px);
}

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
  margin: 0 0 20px 0;
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

.management-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 필터 섹션 */
.filter-section {
  background-color: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 120px;
}

.filter-group label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.filter-group select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background-color: white;
}

.search-group {
  flex: 1;
  min-width: 200px;
}

.search-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}
/* AdminUserManagement.vue - CSS Part 2: 액션 섹션 */

/* 액션 섹션 */
.action-section {
  background-color: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
  position: relative;
}

.action-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.primary-button,
.secondary-button,
.outline-button {
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

.primary-button:hover:not(:disabled) {
  background-color: var(--dark-blue);
}

.primary-button:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

.secondary-button {
  background-color: #10b981;
  color: white;
}

.secondary-button:hover {
  background-color: #059669;
}

.outline-button {
  background-color: white;
  color: #6b7280;
  border: 1px solid #d1d5db;
}

.outline-button:hover:not(:disabled) {
  background-color: #f9fafb;
  border-color: #9ca3af;
}

.outline-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.selected-actions {
  position: absolute;
  top: 70px;
  right: 20px;
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  gap: 8px;
  z-index: 10;
}

.action-btn {
  padding: 6px 12px;
  background-color: #f3f4f6;
  color: #374151;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.action-btn:hover {
  background-color: #e5e7eb;
}
/* AdminUserManagement.vue - CSS Part 3: 테이블 섹션 */

/* 테이블 섹션 */
.table-section {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.loading-state,
.error-state {
  padding: 60px 20px;
  text-align: center;
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
}

.table-container {
  overflow-x: auto;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.users-table th,
.users-table td {
  padding: 12px 8px;
  text-align: left;
  border-bottom: 1px solid #f3f4f6;
}

.users-table th {
  background-color: #f9fafb;
  font-weight: 600;
  color: #374151;
  position: sticky;
  top: 0;
  z-index: 10;
}

.users-table tbody tr:hover {
  background-color: #f9fafb;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.username {
  font-weight: 500;
  color: #1f2937;
}

.score-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.score-badge.excellent {
  background-color: #d1fae5;
  color: #065f46;
}

.score-badge.good {
  background-color: #dbeafe;
  color: #1e40af;
}

.score-badge.warning {
  background-color: #fef3c7;
  color: #92400e;
}

.score-badge.poor {
  background-color: #fee2e2;
  color: #991b1b;
}

.score-badge.no-score {
  background-color: #f3f4f6;
  color: #6b7280;
}

.grade-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  min-width: 30px;
  text-align: center;
}

.grade-badge.grade-a {
  background-color: #d1fae5;
  color: #065f46;
}

.grade-badge.grade-b {
  background-color: #dbeafe;
  color: #1e40af;
}

.grade-badge.grade-c {
  background-color: #fef3c7;
  color: #92400e;
}

.grade-badge.grade-d {
  background-color: #fee2e2;
  color: #991b1b;
}

.grade-badge.no-grade {
  background-color: #f3f4f6;
  color: #6b7280;
}

.action-buttons {
  display: flex;
  gap: 4px;
  align-items: center;
}

.view-button,
.calculate-button,
.notify-button {
  background: none;
  border: none;
  padding: 4px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s ease;
}

.view-button:hover {
  background-color: #eff6ff;
}

.calculate-button:hover {
  background-color: #fef3c7;
}

.notify-button:hover {
  background-color: #ecfdf5;
}

/* 페이지네이션 */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-top: 1px solid #f3f4f6;
}

.pagination-button {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s ease;
}

.pagination-button:hover:not(:disabled) {
  background-color: var(--dark-blue);
}

.pagination-button:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

.pagination-info {
  font-size: 14px;
  color: #6b7280;
}

/* AdminUserManagement.vue - CSS Part 4: 모달 및 반응형 */

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
  width: 800px;
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
  max-height: 60vh;
  overflow-y: auto;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #f3f4f6;
}

/* 사용자 상세 정보 */
.user-detail-section {
  margin-bottom: 24px;
}

.user-detail-section h4 {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #f3f4f6;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.detail-item .label {
  font-weight: 500;
  color: #6b7280;
  min-width: 80px;
}

.detail-item .value {
  color: #1f2937;
  text-align: right;
}

.score-summary {
  display: flex;
  align-items: center;
  gap: 20px;
}

.score-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  min-width: 120px;
}

.score-number {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 4px;
}

.score-grade {
  font-size: 18px;
  font-weight: 600;
}

.score-breakdown {
  flex: 1;
}

.breakdown-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.breakdown-label {
  color: #6b7280;
  font-weight: 500;
}

.breakdown-value {
  color: #1f2937;
  font-weight: 600;
}

.breakdown-value.penalty {
  color: #ef4444;
}

.quarterly-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.quarter-item {
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
  text-align: center;
}

.quarter-header {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
}

.quarter-status {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.quarter-status.completed {
  background-color: #d1fae5;
  color: #065f46;
}

.quarter-status.incomplete {
  background-color: #fef3c7;
  color: #92400e;
}

.quarter-status.passed {
  background-color: #d1fae5;
  color: #065f46;
}

.quarter-status.failed {
  background-color: #fee2e2;
  color: #991b1b;
}

.quarter-status.pending {
  background-color: #f3f4f6;
  color: #6b7280;
}

.cancel-button {
  background-color: white;
  color: #6b7280;
  border: 1px solid #d1d5db;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.cancel-button:hover {
  background-color: #f9fafb;
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

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .admin-users {
    padding: 15px;
  }

  .admin-header {
    padding: 20px;
  }

  .admin-nav {
    flex-direction: column;
    gap: 8px;
  }

  .filter-section {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-group {
    min-width: auto;
  }

  .action-buttons {
    flex-direction: column;
  }

  .users-table {
    font-size: 12px;
  }

  .users-table th,
  .users-table td {
    padding: 8px 4px;
  }

  .modal-content {
    width: 95vw;
    margin: 20px;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }

  .score-summary {
    flex-direction: column;
    align-items: stretch;
  }

  .quarterly-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .pagination {
    flex-direction: column;
    gap: 12px;
  }
}

@media (max-width: 480px) {
  .quarterly-grid {
    grid-template-columns: 1fr;
  }

  .users-table th,
  .users-table td {
    padding: 6px 3px;
    font-size: 11px;
  }

  .action-buttons {
    flex-direction: column;
    gap: 2px;
  }
}
</style>
