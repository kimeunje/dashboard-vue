<!-- views/admin/AdminEducationManagement.vue -->
<template>
  <div class="admin-education">
    <div class="admin-header">
      <h1>정보보호 교육 관리</h1>
      <div class="admin-nav">
        <RouterLink to="/admin" class="nav-item">대시보드</RouterLink>
        <RouterLink to="/admin/users" class="nav-item">사용자 관리</RouterLink>
        <RouterLink to="/admin/education" class="nav-item active">교육 관리</RouterLink>
        <RouterLink to="/admin/training" class="nav-item">훈련 관리</RouterLink>
        <RouterLink to="/admin/scores" class="nav-item">점수 관리</RouterLink>
      </div>
    </div>

    <div class="management-content">
      <!-- 필터 및 검색 -->
      <div class="filter-section">
        <div class="filter-group">
          <label>연도:</label>
          <select v-model="selectedYear" @change="loadEducationData">
            <option v-for="year in availableYears" :key="year" :value="year">{{ year }}년</option>
          </select>
        </div>

        <div class="filter-group">
          <label>분기:</label>
          <select v-model="selectedQuarter" @change="loadEducationData">
            <option value="">전체</option>
            <option value="1">1분기</option>
            <option value="2">2분기</option>
            <option value="3">3분기</option>
            <option value="4">4분기</option>
          </select>
        </div>

        <div class="filter-group">
          <label>상태:</label>
          <select v-model="selectedStatus" @change="loadEducationData">
            <option value="">전체</option>
            <option value="1">이수완료</option>
            <option value="0">미이수</option>
          </select>
        </div>

        <div class="search-group">
          <input
            type="text"
            v-model="searchQuery"
            @input="searchEducationData"
            placeholder="사용자명 또는 ID 검색..."
            class="search-input"
          />
        </div>
      </div>

      <!-- 액션 버튼 -->
      <div class="action-section">
        <button @click="showBulkUploadModal = true" class="primary-button">
          <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path
              d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"
            />
            <path
              d="M7.646 1.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 2.707V11.5a.5.5 0 0 1-1 0V2.707L5.354 4.854a.5.5 0 1 1-.708-.708l3-3z"
            />
          </svg>
          일괄 등록
        </button>

        <button @click="exportEducationData" class="secondary-button">
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

        <button @click="downloadTemplate" class="outline-button">
          <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path
              d="M14 14V4.5L9.5 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2zM9.5 3A1.5 1.5 0 0 0 11 4.5h2V14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h5.5v2z"
            />
          </svg>
          템플릿 다운로드
        </button>
      </div>

      <!-- 교육 데이터 테이블 -->
      <div class="table-section">
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>교육 데이터를 불러오는 중...</p>
        </div>

        <div v-else-if="error" class="error-state">
          <div class="error-icon">⚠️</div>
          <p>{{ error }}</p>
          <button @click="loadEducationData" class="retry-button">다시 시도</button>
        </div>

        <div v-else class="table-container">
          <table class="education-table">
            <thead>
              <tr>
                <th>
                  <input type="checkbox" v-model="selectAll" @change="toggleSelectAll" />
                </th>
                <th>사용자 ID</th>
                <th>사용자명</th>
                <th>부서</th>
                <th>연도</th>
                <th>분기</th>
                <th>교육일</th>
                <th>이수상태</th>
                <th>점수</th>
                <th>비고</th>
                <th>액션</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="record in paginatedRecords"
                :key="`${record.user_id}-${record.education_year}-${record.quarter}`"
              >
                <td>
                  <input type="checkbox" v-model="selectedRecords" :value="record" />
                </td>
                <td>{{ record.user_id }}</td>
                <td>{{ record.username }}</td>
                <td>{{ record.department }}</td>
                <td>{{ record.education_year }}</td>
                <td>{{ record.quarter }}분기</td>
                <td>{{ formatDate(record.education_date) }}</td>
                <td>
                  <span
                    class="status-badge"
                    :class="record.completion_status ? 'completed' : 'pending'"
                  >
                    {{ record.completion_status ? '이수완료' : '미이수' }}
                  </span>
                </td>
                <td>{{ record.score || '-' }}</td>
                <td class="notes-cell" :title="record.notes">
                  {{ truncateText(record.notes, 20) }}
                </td>
                <td>
                  <div class="action-buttons">
                    <button @click="editRecord(record)" class="edit-button" title="수정">✏️</button>
                    <button @click="deleteRecord(record)" class="delete-button" title="삭제">
                      🗑️
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
              {{ currentPage }} / {{ totalPages }} 페이지 (총 {{ filteredRecords.length }}건)
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

    <!-- 일괄 업로드 모달 -->
    <div v-if="showBulkUploadModal" class="modal-overlay" @click="closeBulkUploadModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>교육 결과 일괄 등록</h3>
          <button @click="closeBulkUploadModal" class="close-button">×</button>
        </div>

        <div class="modal-body">
          <div class="upload-section">
            <div class="upload-area" @drop="handleFileDrop" @dragover.prevent @dragenter.prevent>
              <input
                type="file"
                ref="fileInput"
                @change="handleFileSelect"
                accept=".csv,.xlsx,.xls"
                style="display: none"
              />

              <div v-if="!selectedFile" class="upload-placeholder">
                <div class="upload-icon">📁</div>
                <p>CSV 또는 Excel 파일을 드래그하거나 클릭하여 선택하세요</p>
                <button @click="$refs.fileInput.click()" class="select-file-button">
                  파일 선택
                </button>
              </div>

              <div v-else class="file-selected">
                <div class="file-info">
                  <div class="file-icon">📄</div>
                  <div>
                    <div class="file-name">{{ selectedFile.name }}</div>
                    <div class="file-size">{{ formatFileSize(selectedFile.size) }}</div>
                  </div>
                </div>
                <button @click="removeSelectedFile" class="remove-file-button">×</button>
              </div>
            </div>

            <div class="upload-instructions">
              <h4>업로드 형식 안내</h4>
              <ul>
                <li>CSV 또는 Excel 파일 형식 지원</li>
                <li>필수 컬럼: user_id, education_year, quarter, completion_status</li>
                <li>선택 컬럼: education_date, score, notes</li>
                <li>첫 번째 행은 헤더로 처리됩니다</li>
              </ul>
            </div>
          </div>

          <div v-if="uploadPreview.length > 0" class="preview-section">
            <h4>미리보기 (처음 5개 레코드)</h4>
            <div class="preview-table">
              <table>
                <thead>
                  <tr>
                    <th>사용자 ID</th>
                    <th>연도</th>
                    <th>분기</th>
                    <th>이수상태</th>
                    <th>교육일</th>
                    <th>점수</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(record, index) in uploadPreview.slice(0, 5)" :key="index">
                    <td>{{ record.user_id }}</td>
                    <td>{{ record.education_year }}</td>
                    <td>{{ record.quarter }}</td>
                    <td>{{ record.completion_status ? '이수' : '미이수' }}</td>
                    <td>{{ record.education_date || '-' }}</td>
                    <td>{{ record.score || '-' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="closeBulkUploadModal" class="cancel-button">취소</button>
          <button
            @click="processBulkUpload"
            :disabled="!selectedFile || uploading"
            class="upload-button"
          >
            {{ uploading ? '처리 중...' : '업로드' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 편집 모달 -->
    <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
      <div class="modal-content edit-modal" @click.stop>
        <div class="modal-header">
          <h3>교육 기록 수정</h3>
          <button @click="closeEditModal" class="close-button">×</button>
        </div>

        <div class="modal-body">
          <form @submit.prevent="saveRecord" class="edit-form">
            <div class="form-group">
              <label>사용자 ID:</label>
              <input type="text" v-model="editingRecord.user_id" disabled />
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>연도:</label>
                <select v-model="editingRecord.education_year" required>
                  <option v-for="year in availableYears" :key="year" :value="year">
                    {{ year }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label>분기:</label>
                <select v-model="editingRecord.quarter" required>
                  <option value="1">1분기</option>
                  <option value="2">2분기</option>
                  <option value="3">3분기</option>
                  <option value="4">4분기</option>
                </select>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>이수상태:</label>
                <select v-model="editingRecord.completion_status" required>
                  <option :value="1">이수완료</option>
                  <option :value="0">미이수</option>
                </select>
              </div>

              <div class="form-group">
                <label>교육일:</label>
                <input type="date" v-model="editingRecord.education_date" />
              </div>
            </div>

            <div class="form-group">
              <label>점수:</label>
              <input type="number" v-model="editingRecord.score" min="0" max="100" step="0.1" />
            </div>

            <div class="form-group">
              <label>비고:</label>
              <textarea
                v-model="editingRecord.notes"
                rows="3"
                placeholder="비고 사항을 입력하세요..."
              ></textarea>
            </div>
          </form>
        </div>

        <div class="modal-footer">
          <button @click="closeEditModal" class="cancel-button">취소</button>
          <button @click="saveRecord" :disabled="saving" class="save-button">
            {{ saving ? '저장 중...' : '저장' }}
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

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { RouterLink } from 'vue-router'

// 반응형 데이터
const loading = ref(false)
const error = ref(null)
const educationRecords = ref([])
const filteredRecords = ref([])
const selectedRecords = ref([])
const selectAll = ref(false)

// 필터 및 검색
const selectedYear = ref(new Date().getFullYear())
const selectedQuarter = ref('')
const selectedStatus = ref('')
const searchQuery = ref('')

// 페이지네이션
const currentPage = ref(1)
const itemsPerPage = ref(20)

// 모달 상태
const showBulkUploadModal = ref(false)
const showEditModal = ref(false)
const selectedFile = ref(null)
const uploadPreview = ref([])
const uploading = ref(false)
const editingRecord = ref({})
const saving = ref(false)

// 토스트
const showToast = ref(false)
const toastMessage = ref('')
const toastType = ref('success')

// 계산된 속성
const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  return [currentYear - 2, currentYear - 1, currentYear, currentYear + 1]
})

const paginatedRecords = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredRecords.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredRecords.value.length / itemsPerPage.value)
})

// 메서드
const loadEducationData = async () => {
  loading.value = true
  error.value = null

  try {
    // API 호출하여 교육 데이터 로드
    const params = new URLSearchParams({
      year: selectedYear.value,
      ...(selectedQuarter.value && { quarter: selectedQuarter.value }),
      ...(selectedStatus.value && { status: selectedStatus.value }),
    })

    const response = await fetch(`/api/admin/education?${params}`, {
      credentials: 'include',
    })

    if (!response.ok) {
      throw new Error('교육 데이터를 불러올 수 없습니다.')
    }

    educationRecords.value = await response.json()
    applyFilters()
  } catch (err) {
    console.error('교육 데이터 로드 실패:', err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  let filtered = [...educationRecords.value]

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(
      (record) =>
        record.username.toLowerCase().includes(query) ||
        record.user_id.toLowerCase().includes(query),
    )
  }

  filteredRecords.value = filtered
  currentPage.value = 1
}

const searchEducationData = () => {
  applyFilters()
}

const toggleSelectAll = () => {
  if (selectAll.value) {
    selectedRecords.value = [...paginatedRecords.value]
  } else {
    selectedRecords.value = []
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('ko-KR')
}

const truncateText = (text, maxLength) => {
  if (!text) return '-'
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

const editRecord = (record) => {
  editingRecord.value = { ...record }
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
  editingRecord.value = {}
}

const saveRecord = async () => {
  saving.value = true

  try {
    const response = await fetch('/api/admin/education/update', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify(editingRecord.value),
    })

    if (!response.ok) {
      throw new Error('저장에 실패했습니다.')
    }

    showToastMessage('교육 기록이 저장되었습니다.', 'success')
    closeEditModal()
    await loadEducationData()
  } catch (err) {
    console.error('저장 실패:', err)
    showToastMessage(err.message, 'error')
  } finally {
    saving.value = false
  }
}

const deleteRecord = async (record) => {
  if (!confirm('이 교육 기록을 삭제하시겠습니까?')) return

  try {
    const response = await fetch('/api/admin/education/delete', {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        user_id: record.user_id,
        education_year: record.education_year,
        quarter: record.quarter,
      }),
    })

    if (!response.ok) {
      throw new Error('삭제에 실패했습니다.')
    }

    showToastMessage('교육 기록이 삭제되었습니다.', 'success')
    await loadEducationData()
  } catch (err) {
    console.error('삭제 실패:', err)
    showToastMessage(err.message, 'error')
  }
}

const closeBulkUploadModal = () => {
  showBulkUploadModal.value = false
  selectedFile.value = null
  uploadPreview.value = []
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
    parseFile(file)
  }
}

const handleFileDrop = (event) => {
  event.preventDefault()
  const file = event.dataTransfer.files[0]
  if (file) {
    selectedFile.value = file
    parseFile(file)
  }
}

const removeSelectedFile = () => {
  selectedFile.value = null
  uploadPreview.value = []
}

const parseFile = async (file) => {
  // 파일 파싱 로직 (CSV 또는 Excel)
  // 실제 구현에서는 Papa Parse나 SheetJS 사용
  showToastMessage('파일 파싱 기능이 준비중입니다.', 'info')
}

const processBulkUpload = async () => {
  uploading.value = true

  try {
    const response = await fetch('/api/admin/education/bulk-update', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ records: uploadPreview.value }),
    })

    if (!response.ok) {
      throw new Error('일괄 업로드에 실패했습니다.')
    }

    const result = await response.json()
    showToastMessage(`${result.success_count}건이 성공적으로 처리되었습니다.`, 'success')

    closeBulkUploadModal()
    await loadEducationData()
  } catch (err) {
    console.error('업로드 실패:', err)
    showToastMessage(err.message, 'error')
  } finally {
    uploading.value = false
  }
}

const exportEducationData = () => {
  showToastMessage('데이터 내보내기 기능이 준비중입니다.', 'info')
}

const downloadTemplate = () => {
  // 템플릿 파일 다운로드
  const csvContent =
    'user_id,education_year,quarter,completion_status,education_date,score,notes\n' +
    'admin,2025,1,1,2025-03-15,85,1분기 교육 완료\n' +
    'user1,2025,1,0,,,1분기 교육 미이수'

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = '교육_업로드_템플릿.csv'
  link.click()
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
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
watch([selectedYear, selectedQuarter, selectedStatus], () => {
  loadEducationData()
})

// 라이프사이클 훅
onMounted(() => {
  loadEducationData()
})
</script>

/* AdminEducationManagement.vue 스타일 */
<style scoped>
.admin-education {
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

/* 액션 섹션 */
.action-section {
  background-color: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
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

.outline-button {
  background-color: white;
  color: #6b7280;
  border: 1px solid #d1d5db;
}

.outline-button:hover {
  background-color: #f9fafb;
  border-color: #9ca3af;
}

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

.education-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.education-table th,
.education-table td {
  padding: 12px 8px;
  text-align: left;
  border-bottom: 1px solid #f3f4f6;
}

.education-table th {
  background-color: #f9fafb;
  font-weight: 600;
  color: #374151;
  position: sticky;
  top: 0;
  z-index: 10;
}

.education-table tbody tr:hover {
  background-color: #f9fafb;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.completed {
  background-color: #d1fae5;
  color: #065f46;
}

.status-badge.pending {
  background-color: #fef3c7;
  color: #92400e;
}

.notes-cell {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.action-buttons {
  display: flex;
  gap: 4px;
}

.edit-button,
.delete-button {
  background: none;
  border: none;
  padding: 4px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s ease;
}

.edit-button:hover {
  background-color: #eff6ff;
}

.delete-button:hover {
  background-color: #fef2f2;
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

.modal-content.edit-modal {
  width: 500px;
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

/* 업로드 섹션 */
.upload-section {
  margin-bottom: 24px;
}

.upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  padding: 40px 20px;
  text-align: center;
  transition: border-color 0.2s ease;
  margin-bottom: 16px;
}

.upload-area:hover {
  border-color: var(--primary-color);
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.upload-icon {
  font-size: 48px;
  opacity: 0.5;
}

.select-file-button {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.file-selected {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #f9fafb;
  padding: 16px;
  border-radius: 8px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-icon {
  font-size: 24px;
}

.file-name {
  font-weight: 600;
  color: #1f2937;
}

.file-size {
  font-size: 12px;
  color: #6b7280;
}

.remove-file-button {
  background-color: #ef4444;
  color: white;
  border: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-instructions {
  background-color: #eff6ff;
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid #3b82f6;
}

.upload-instructions h4 {
  margin: 0 0 8px 0;
  color: #1f2937;
  font-size: 14px;
}

.upload-instructions ul {
  margin: 0;
  padding-left: 16px;
  font-size: 13px;
  color: #6b7280;
}

.upload-instructions li {
  margin-bottom: 4px;
}

/* 미리보기 섹션 */
.preview-section {
  margin-top: 24px;
}

.preview-section h4 {
  margin: 0 0 12px 0;
  color: #1f2937;
  font-size: 16px;
}

.preview-table {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.preview-table table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.preview-table th,
.preview-table td {
  padding: 8px 12px;
  text-align: left;
  border-bottom: 1px solid #f3f4f6;
}

.preview-table th {
  background-color: #f9fafb;
  font-weight: 600;
}

/* 편집 폼 */
.edit-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.form-group input:disabled {
  background-color: #f9fafb;
  color: #6b7280;
}

/* 버튼 스타일 */
.cancel-button,
.save-button,
.upload-button {
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

.save-button,
.upload-button {
  background-color: var(--primary-color);
  color: white;
}

.save-button:hover:not(:disabled),
.upload-button:hover:not(:disabled) {
  background-color: var(--dark-blue);
}

.save-button:disabled,
.upload-button:disabled {
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
  .admin-education {
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

  .action-section {
    flex-direction: column;
  }

  .education-table {
    font-size: 12px;
  }

  .education-table th,
  .education-table td {
    padding: 8px 4px;
  }

  .modal-content {
    width: 95vw;
    margin: 20px;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .pagination {
    flex-direction: column;
    gap: 12px;
  }
}

@media (max-width: 480px) {
  .notes-cell {
    max-width: 80px;
  }

  .upload-area {
    padding: 20px 10px;
  }

  .upload-icon {
    font-size: 36px;
  }
}
</style>
