<!-- views/admin/AdminTrainingManagement.vue -->
<template>
  <div class="admin-training">
    <div class="admin-header">
      <h1>악성메일 모의훈련 관리</h1>
      <div class="admin-nav">
        <RouterLink to="/admin" class="nav-item">대시보드</RouterLink>
        <RouterLink to="/admin/users" class="nav-item">사용자 관리</RouterLink>
        <RouterLink to="/admin/education" class="nav-item">교육 관리</RouterLink>
        <RouterLink to="/admin/training" class="nav-item active">훈련 관리</RouterLink>
        <RouterLink to="/admin/scores" class="nav-item">점수 관리</RouterLink>
      </div>
    </div>

    <div class="management-content">
      <!-- 필터 및 검색 -->
      <div class="filter-section">
        <div class="filter-group">
          <label>연도:</label>
          <select v-model="selectedYear" @change="loadTrainingData">
            <option v-for="year in availableYears" :key="year" :value="year">{{ year }}년</option>
          </select>
        </div>

        <div class="filter-group">
          <label>기간:</label>
          <select v-model="selectedPeriod" @change="loadTrainingData">
            <option value="">전체</option>
            <option value="first_half">상반기</option>
            <option value="second_half">하반기</option>
          </select>
        </div>

        <div class="filter-group">
          <label>결과:</label>
          <select v-model="selectedResult" @change="loadTrainingData">
            <option value="">전체</option>
            <option value="pass">통과</option>
            <option value="fail">실패</option>
            <option value="pending">미실시</option>
          </select>
        </div>

        <div class="search-group">
          <input
            type="text"
            v-model="searchQuery"
            @input="searchTrainingData"
            placeholder="사용자명, ID 또는 이메일 검색..."
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

        <button @click="exportTrainingData" class="secondary-button">
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

      <!-- 모의훈련 데이터 테이블 -->
      <div class="table-section">
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>모의훈련 데이터를 불러오는 중...</p>
        </div>

        <div v-else-if="error" class="error-state">
          <div class="error-icon">⚠️</div>
          <p>{{ error }}</p>
          <button @click="loadTrainingData" class="retry-button">다시 시도</button>
        </div>

        <div v-else class="table-container">
          <table class="training-table">
            <thead>
              <tr>
                <th><input type="checkbox" v-model="selectAll" @change="toggleSelectAll" /></th>
                <th>사용자 ID</th>
                <th>사용자명</th>
                <th>부서</th>
                <th>연도</th>
                <th>기간</th>
                <th>이메일</th>
                <th>메일발송시각</th>
                <th>수행시간</th>
                <th>로그유형</th>
                <th>메일유형</th>
                <th>IP주소</th>
                <th>결과</th>
                <th>점수</th>
                <th>점수제외</th>
                <th>액션</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="record in paginatedRecords"
                :key="`${record.user_id}-${record.training_year}-${record.training_period}`"
              >
                <td><input type="checkbox" v-model="selectedRecords" :value="record" /></td>
                <td>{{ record.user_id }}</td>
                <td>{{ record.username }}</td>
                <td>{{ record.department }}</td>
                <td>{{ record.training_year }}</td>
                <td>{{ getPeriodName(record.training_period) }}</td>
                <td>{{ record.user_email || '-' }}</td>
                <td>{{ formatDateTime(record.email_sent_time) }}</td>
                <td>{{ formatDateTime(record.action_time) }}</td>
                <td>
                  <span v-if="record.log_type" class="log-type danger-text">
                    {{ record.log_type }}
                  </span>
                  <span v-else>-</span>
                </td>
                <td class="mail-type-cell" :title="record.mail_type">
                  {{ truncateText(record.mail_type, 20) }}
                </td>
                <td>{{ record.ip_address || '-' }}</td>
                <td>
                  <span class="status-badge" :class="getResultClass(record.training_result)">
                    {{ getResultText(record.training_result) }}
                  </span>
                </td>
                <td>{{ record.training_score || '-' }}</td>
                <td>
                  <button
                    @click="toggleScoring(record)"
                    :class="[
                      'scoring-toggle',
                      record.exclude_from_scoring ? 'excluded' : 'included',
                    ]"
                    :title="
                      record.exclude_from_scoring ? '점수 계산에서 제외됨' : '점수 계산에 포함됨'
                    "
                  >
                    {{ record.exclude_from_scoring ? '제외' : '포함' }}
                  </button>
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
          <h3>모의훈련 결과 일괄 등록</h3>
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
                <li>필수 컬럼: user_email, training_year, training_period</li>
                <li>선택 컬럼: email_sent_time, action_time, log_type, mail_type, ip_address</li>
                <li>첫 번째 행은 헤더로 처리됩니다</li>
                <li>training_period: 상반기/하반기 또는 first_half/second_half</li>
                <li>log_type이 있으면 자동으로 실패 처리됩니다</li>
              </ul>
            </div>
          </div>

          <div v-if="uploadPreview.length > 0" class="preview-section">
            <h4>미리보기 (처음 5개 레코드)</h4>
            <div class="preview-table">
              <table>
                <thead>
                  <tr>
                    <th>이메일</th>
                    <th>연도</th>
                    <th>기간</th>
                    <th>발송시각</th>
                    <th>수행시간</th>
                    <th>로그유형</th>
                    <th>메일유형</th>
                    <th>점수제외</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(record, index) in uploadPreview.slice(0, 5)" :key="index">
                    <td>{{ record.user_email || '-' }}</td>
                    <td>{{ record.training_year || '-' }}</td>
                    <td>{{ getPeriodName(record.training_period) || '-' }}</td>
                    <td>{{ record.email_sent_time || '-' }}</td>
                    <td>{{ record.action_time || '-' }}</td>
                    <td>{{ record.log_type || '-' }}</td>
                    <td>{{ truncateText(record.mail_type, 30) || '-' }}</td>
                    <td>{{ record.exclude_from_scoring ? '제외' : '포함' }}</td>
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
          <h3>모의훈련 기록 수정</h3>
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
                <select v-model="editingRecord.training_year" required>
                  <option v-for="year in availableYears" :key="year" :value="year">
                    {{ year }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label>기간:</label>
                <select v-model="editingRecord.training_period" required>
                  <option value="first_half">상반기</option>
                  <option value="second_half">하반기</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>사용자 이메일:</label>
              <input type="email" v-model="editingRecord.user_email" />
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>메일 발송시각:</label>
                <input type="datetime-local" v-model="editingRecord.email_sent_time" />
              </div>

              <div class="form-group">
                <label>수행시간:</label>
                <input type="datetime-local" v-model="editingRecord.action_time" />
              </div>
            </div>

            <div class="form-group">
              <label>로그유형:</label>
              <input
                type="text"
                v-model="editingRecord.log_type"
                placeholder="예: 스크립트 첨부파일 열람, 링크 클릭"
              />
            </div>

            <div class="form-group">
              <label>메일유형:</label>
              <input
                type="text"
                v-model="editingRecord.mail_type"
                placeholder="예: 퇴직연금 운용상품 안내 (HTML)"
              />
            </div>

            <div class="form-group">
              <label>IP주소:</label>
              <input
                type="text"
                v-model="editingRecord.ip_address"
                placeholder="예: 192.168.1.100"
              />
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>훈련 결과:</label>
                <select v-model="editingRecord.training_result" required>
                  <option value="pass">통과</option>
                  <option value="fail">실패</option>
                  <option value="pending">미실시</option>
                </select>
              </div>

              <div class="form-group">
                <label>점수:</label>
                <input
                  type="number"
                  v-model="editingRecord.training_score"
                  min="0"
                  max="100"
                  step="0.1"
                />
              </div>
            </div>

            <div class="form-group">
              <label>점수 계산 제외:</label>
              <select v-model="editingRecord.exclude_from_scoring">
                <option :value="false">포함 (점수에 반영)</option>
                <option :value="true">제외 (점수에 반영 안함)</option>
              </select>
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
import * as XLSX from 'xlsx'

// 반응형 데이터
const loading = ref(false)
const error = ref(null)
const trainingRecords = ref([])
const filteredRecords = ref([])
const selectedRecords = ref([])
const selectAll = ref(false)

// 필터 및 검색
const selectedYear = ref(new Date().getFullYear())
const selectedPeriod = ref('')
const selectedResult = ref('')
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
const loadTrainingData = async () => {
  loading.value = true
  error.value = null

  try {
    const params = new URLSearchParams({
      year: selectedYear.value,
      ...(selectedPeriod.value && { period: selectedPeriod.value }),
      ...(selectedResult.value && { result: selectedResult.value }),
    })

    const response = await fetch(`/api/admin/training?${params}`, {
      credentials: 'include',
    })

    if (!response.ok) {
      throw new Error('모의훈련 데이터를 불러올 수 없습니다.')
    }

    trainingRecords.value = await response.json()
    applyFilters()
  } catch (err) {
    console.error('모의훈련 데이터 로드 실패:', err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  let filtered = [...trainingRecords.value]

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(
      (record) =>
        record.username.toLowerCase().includes(query) ||
        record.user_id.toLowerCase().includes(query) ||
        (record.user_email && record.user_email.toLowerCase().includes(query)),
    )
  }

  filteredRecords.value = filtered
  currentPage.value = 1
}

const searchTrainingData = () => {
  applyFilters()
}

const toggleSelectAll = () => {
  if (selectAll.value) {
    selectedRecords.value = [...paginatedRecords.value]
  } else {
    selectedRecords.value = []
  }
}

const formatDateTime = (dateTimeStr) => {
  if (!dateTimeStr) return '-'
  return new Date(dateTimeStr).toLocaleString('ko-KR')
}

const truncateText = (text, maxLength) => {
  if (!text) return '-'
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

const getPeriodName = (period) => {
  const names = {
    first_half: '상반기',
    second_half: '하반기',
  }
  return names[period] || period
}

const getResultClass = (result) => {
  const classes = {
    pass: 'success',
    fail: 'danger',
    pending: 'warning',
  }
  return classes[result] || 'warning'
}

const getResultText = (result) => {
  const texts = {
    pass: '통과',
    fail: '실패',
    pending: '미실시',
  }
  return texts[result] || '알 수 없음'
}

const toggleScoring = async (record) => {
  try {
    const response = await fetch('/api/admin/toggle-scoring', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        user_id: record.user_id,
        year: record.training_year,
        record_type: 'training',
        period: record.training_period,
        exclude: !record.exclude_from_scoring,
      }),
    })

    if (!response.ok) {
      throw new Error('점수 계산 설정 변경에 실패했습니다.')
    }

    // 로컬 데이터 업데이트
    record.exclude_from_scoring = !record.exclude_from_scoring
    showToastMessage('점수 계산 설정이 변경되었습니다.', 'success')
  } catch (err) {
    console.error('점수 계산 설정 변경 실패:', err)
    showToastMessage(err.message, 'error')
  }
}

const editRecord = (record) => {
  editingRecord.value = { ...record }
  // datetime-local 형식으로 변환
  if (editingRecord.value.email_sent_time) {
    editingRecord.value.email_sent_time = new Date(editingRecord.value.email_sent_time)
      .toISOString()
      .slice(0, 16)
  }
  if (editingRecord.value.action_time) {
    editingRecord.value.action_time = new Date(editingRecord.value.action_time)
      .toISOString()
      .slice(0, 16)
  }
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
  editingRecord.value = {}
}

const saveRecord = async () => {
  saving.value = true

  try {
    const response = await fetch('/api/admin/training/update', {
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

    showToastMessage('모의훈련 기록이 저장되었습니다.', 'success')
    closeEditModal()
    await loadTrainingData()
  } catch (err) {
    console.error('저장 실패:', err)
    showToastMessage(err.message, 'error')
  } finally {
    saving.value = false
  }
}

const deleteRecord = async (record) => {
  if (!confirm('이 모의훈련 기록을 삭제하시겠습니까?')) return

  try {
    const response = await fetch('/api/admin/training/delete', {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        user_id: record.user_id,
        training_year: record.training_year,
        training_period: record.training_period,
      }),
    })

    if (!response.ok) {
      throw new Error('삭제에 실패했습니다.')
    }

    showToastMessage('모의훈련 기록이 삭제되었습니다.', 'success')
    await loadTrainingData()
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

// AdminTrainingManagement.vue에서 parseFile 메서드의 필드 매핑 부분을 완전히 수정

const parseFile = async (file) => {
  try {
    const fileName = file.name.toLowerCase()

    if (fileName.endsWith('.csv')) {
      // CSV 파일 처리
      const text = await file.text()
      const lines = text.split('\n')
      const headers = lines[0].split(',').map((h) => h.trim().replace(/"/g, ''))

      const records = []
      for (let i = 1; i < lines.length; i++) {
        if (lines[i].trim()) {
          const values = lines[i].split(',').map((v) => v.trim().replace(/"/g, ''))
          const record = {}
          headers.forEach((header, index) => {
            record[header] = values[index] || ''
          })
          records.push(record)
        }
      }

      const processedRecords = postProcessRecords(records)
      uploadPreview.value = processedRecords
      showToastMessage(`${processedRecords.length}개의 레코드가 파싱되었습니다.`, 'success')
    } else if (fileName.endsWith('.xlsx') || fileName.endsWith('.xls')) {
      // Excel 파일 처리
      const arrayBuffer = await file.arrayBuffer()
      const XLSX = window.XLSX || (await import('xlsx'))

      const workbook = XLSX.read(arrayBuffer, { type: 'array' })
      const sheetName = workbook.SheetNames[0]
      const worksheet = workbook.Sheets[sheetName]

      // JSON으로 변환 (첫 번째 행을 헤더로 사용)
      const jsonData = XLSX.utils.sheet_to_json(worksheet, {
        raw: false,
        dateNF: 'yyyy-mm-dd hh:mm:ss',
      })

      const processedRecords = postProcessRecords(jsonData)
      uploadPreview.value = processedRecords
      showToastMessage(`${processedRecords.length}개의 레코드가 파싱되었습니다.`, 'success')
    } else {
      throw new Error('지원하지 않는 파일 형식입니다. CSV 또는 Excel 파일을 선택해주세요.')
    }
  } catch (err) {
    console.error('파일 파싱 실패:', err)
    showToastMessage(`파일 파싱에 실패했습니다: ${err.message}`, 'error')
    uploadPreview.value = []
  }
}

// 레코드 후처리 함수 - 완전히 새로 작성
const postProcessRecords = (records) => {
  // 한글-영문 필드명 완전 매핑 테이블
  const fieldMapping = {
    // 기본 필드들
    사용자ID: 'user_id',
    사용자명: 'username',
    사용자이름: 'username',
    이름: 'username',
    부서: 'department',
    연도: 'training_year',
    훈련연도: 'training_year',
    기간: 'training_period',
    훈련기간: 'training_period',
    이메일: 'user_email',
    사용자이메일: 'user_email',
    email: 'user_email',
    mail: 'user_email',

    // 시간 관련
    메일발송시각: 'email_sent_time',
    발송시각: 'email_sent_time',
    메일발송시간: 'email_sent_time',
    발송시간: 'email_sent_time',
    수행시각: 'action_time',
    수행시간: 'action_time',
    액션시각: 'action_time',
    액션시간: 'action_time',
    클릭시간: 'action_time',
    응답시간: 'response_time_minutes',
    '응답시간(분)': 'response_time_minutes',

    // 훈련 관련
    로그유형: 'log_type',
    로그타입: 'log_type',
    액션유형: 'log_type',
    메일유형: 'mail_type',
    메일타입: 'mail_type',
    훈련유형: 'mail_type',
    IP주소: 'ip_address',
    IP: 'ip_address',
    아이피: 'ip_address',
    아이피주소: 'ip_address',

    // 결과 관련
    결과: 'training_result',
    훈련결과: 'training_result',
    점수: 'training_score',
    훈련점수: 'training_score',
    점수제외: 'exclude_from_scoring',
    '점수 제외': 'exclude_from_scoring',
    제외여부: 'exclude_from_scoring',
    채점제외: 'exclude_from_scoring',
    비고: 'notes',
    메모: 'notes',
    노트: 'notes',
    설명: 'notes',

    // 영문 필드들도 그대로 유지
    user_id: 'user_id',
    username: 'username',
    department: 'department',
    training_year: 'training_year',
    training_period: 'training_period',
    user_email: 'user_email',
    email_sent_time: 'email_sent_time',
    action_time: 'action_time',
    log_type: 'log_type',
    mail_type: 'mail_type',
    ip_address: 'ip_address',
    training_result: 'training_result',
    response_time_minutes: 'response_time_minutes',
    training_score: 'training_score',
    exclude_from_scoring: 'exclude_from_scoring',
    notes: 'notes',
  }

  return records
    .map((originalRecord) => {
      const mappedRecord = {}

      // 모든 필드를 영문 필드명으로 매핑
      Object.keys(originalRecord).forEach((originalKey) => {
        const value = originalRecord[originalKey]

        // 값이 비어있지 않은 경우만 처리
        if (value !== undefined && value !== null && value !== '') {
          // 매핑 테이블에서 영문 필드명 찾기
          const mappedKey = fieldMapping[originalKey.trim()]

          if (mappedKey) {
            mappedRecord[mappedKey] = value
          } else {
            // 매핑되지 않은 필드는 소문자_스네이크케이스로 변환 시도
            const normalizedKey = originalKey
              .trim()
              .toLowerCase()
              .replace(/\s+/g, '_')
              .replace(/[()]/g, '')

            if (fieldMapping[normalizedKey]) {
              mappedRecord[fieldMapping[normalizedKey]] = value
            } else {
              // 그래도 매핑되지 않으면 원본 키 사용 (디버깅용)
              console.warn(`매핑되지 않은 필드: ${originalKey}`)
              mappedRecord[originalKey] = value
            }
          }
        }
      })

      // 데이터 후처리
      return processRecordData(mappedRecord)
    })
    .filter((record) => {
      // 최소 필수 필드가 있는 레코드만 포함
      const hasEmail = record.user_email && record.user_email.includes('@')
      const hasValidData = record.training_year || record.email_sent_time || record.log_type

      return hasEmail && hasValidData
    })
}

// 개별 레코드 데이터 처리
const processRecordData = (record) => {
  const processedRecord = { ...record }

  // 1. training_year 처리
  if (!processedRecord.training_year && processedRecord.email_sent_time) {
    const year = extractYearFromDateTime(processedRecord.email_sent_time)
    if (year) {
      processedRecord.training_year = year
    }
  }

  if (processedRecord.training_year) {
    processedRecord.training_year = parseInt(processedRecord.training_year)
  }

  // 2. training_period 처리 및 정규화
  if (!processedRecord.training_period && processedRecord.email_sent_time) {
    const period = estimatePeriodFromDateTime(processedRecord.email_sent_time)
    if (period) {
      processedRecord.training_period = period
    }
  }

  if (processedRecord.training_period) {
    const period = processedRecord.training_period.toString().trim()
    const periodMapping = {
      상반기: 'first_half',
      하반기: 'second_half',
      '1학기': 'first_half',
      '2학기': 'second_half',
      1: 'first_half',
      2: 'second_half',
      first_half: 'first_half',
      second_half: 'second_half',
      '1반기': 'first_half',
      '2반기': 'second_half',
    }

    processedRecord.training_period = periodMapping[period] || period
  }

  // 3. exclude_from_scoring을 boolean으로 변환
  if (processedRecord.exclude_from_scoring !== undefined) {
    const excludeValue = processedRecord.exclude_from_scoring.toString().toLowerCase().trim()
    const trueValues = ['true', '1', '제외', 'exclude', 'yes', 'y', '참']
    processedRecord.exclude_from_scoring = trueValues.includes(excludeValue)
  } else {
    processedRecord.exclude_from_scoring = false
  }

  // 4. training_result 정규화
  if (processedRecord.training_result) {
    const result = processedRecord.training_result.toString().trim()
    const resultMapping = {
      통과: 'pass',
      성공: 'pass',
      합격: 'pass',
      실패: 'fail',
      탈락: 'fail',
      불합격: 'fail',
      미실시: 'pending',
      대기: 'pending',
      보류: 'pending',
      pass: 'pass',
      fail: 'fail',
      pending: 'pending',
    }

    processedRecord.training_result = resultMapping[result] || result
  }

  // 5. 날짜 형식 정규화
  if (processedRecord.email_sent_time) {
    processedRecord.email_sent_time = normalizeDateTime(processedRecord.email_sent_time)
  }
  if (processedRecord.action_time) {
    processedRecord.action_time = normalizeDateTime(processedRecord.action_time)
  }

  // 6. 숫자 필드 처리
  if (processedRecord.training_score) {
    processedRecord.training_score = parseFloat(processedRecord.training_score)
  }

  if (processedRecord.response_time_minutes) {
    processedRecord.response_time_minutes = parseInt(processedRecord.response_time_minutes)
  }

  // 7. 응답시간 자동 계산
  if (
    !processedRecord.response_time_minutes &&
    processedRecord.email_sent_time &&
    processedRecord.action_time
  ) {
    try {
      const sentTime = new Date(processedRecord.email_sent_time)
      const actionTime = new Date(processedRecord.action_time)
      if (!isNaN(sentTime.getTime()) && !isNaN(actionTime.getTime())) {
        processedRecord.response_time_minutes = Math.round((actionTime - sentTime) / (1000 * 60))
      }
    } catch (error) {
      console.warn('응답시간 계산 실패:', error)
    }
  }

  // 8. training_result 자동 결정
  if (!processedRecord.training_result) {
    if (processedRecord.log_type && processedRecord.log_type.trim()) {
      processedRecord.training_result = 'fail' // 로그가 있으면 실패
    } else if (processedRecord.email_sent_time && !processedRecord.action_time) {
      processedRecord.training_result = 'pass' // 발송했지만 액션이 없으면 통과
    } else {
      processedRecord.training_result = 'pending' // 기본값
    }
  }

  // 9. 기본 점수 설정
  if (!processedRecord.training_score) {
    if (processedRecord.training_result === 'pass') {
      processedRecord.training_score = 95.0
    } else if (processedRecord.training_result === 'fail') {
      processedRecord.training_score = 40.0
    }
  }

  return processedRecord
}

// 기존의 유틸리티 함수들은 그대로 유지
const extractYearFromDateTime = (dateTimeStr) => {
  if (!dateTimeStr) return null

  try {
    const dateStr = dateTimeStr.toString().trim()

    // YYYY-MM-DD HH:mm:ss 형식
    const isoMatch = dateStr.match(/(\d{4})-\d{2}-\d{2}/)
    if (isoMatch) {
      return parseInt(isoMatch[1])
    }

    // YYYY/MM/DD 형식
    const slashMatch = dateStr.match(/(\d{4})\/\d{2}\/\d{2}/)
    if (slashMatch) {
      return parseInt(slashMatch[1])
    }

    // YYYY.MM.DD 형식
    const dotMatch = dateStr.match(/(\d{4})\.\d{2}\.\d{2}/)
    if (dotMatch) {
      return parseInt(dotMatch[1])
    }

    // Excel 날짜 시리얼 번호 처리
    const serialNumber = parseFloat(dateStr)
    if (serialNumber > 40000 && serialNumber < 50000) {
      const excelStartDate = new Date(1900, 0, 1)
      const date = new Date(excelStartDate.getTime() + (serialNumber - 2) * 24 * 60 * 60 * 1000)
      return date.getFullYear()
    }

    // JavaScript Date 객체로 파싱 시도
    const date = new Date(dateStr)
    if (!isNaN(date.getTime())) {
      return date.getFullYear()
    }

    return null
  } catch (error) {
    console.warn('날짜 파싱 실패:', dateTimeStr, error)
    return null
  }
}

const estimatePeriodFromDateTime = (dateTimeStr) => {
  if (!dateTimeStr) return null

  try {
    const date = new Date(dateTimeStr)
    if (isNaN(date.getTime())) return null

    const month = date.getMonth() + 1
    return month <= 6 ? 'first_half' : 'second_half'
  } catch (error) {
    console.warn('기간 추정 실패:', dateTimeStr, error)
    return null
  }
}

const normalizeDateTime = (dateTimeStr) => {
  if (!dateTimeStr) return null

  try {
    const date = new Date(dateTimeStr)
    if (isNaN(date.getTime())) return dateTimeStr

    return (
      date.getFullYear() +
      '-' +
      String(date.getMonth() + 1).padStart(2, '0') +
      '-' +
      String(date.getDate()).padStart(2, '0') +
      ' ' +
      String(date.getHours()).padStart(2, '0') +
      ':' +
      String(date.getMinutes()).padStart(2, '0') +
      ':' +
      String(date.getSeconds()).padStart(2, '0')
    )
  } catch (error) {
    console.warn('날짜 정규화 실패:', dateTimeStr, error)
    return dateTimeStr
  }
}

const processBulkUpload = async () => {
  uploading.value = true

  try {
    const response = await fetch('/api/admin/training/bulk-update', {
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
    await loadTrainingData()
  } catch (err) {
    console.error('업로드 실패:', err)
    showToastMessage(err.message, 'error')
  } finally {
    uploading.value = false
  }
}

const exportTrainingData = async () => {
  try {
    const params = new URLSearchParams({
      year: selectedYear.value,
      format: 'csv',
    })

    const response = await fetch(`/api/admin/export/training?${params}`, {
      credentials: 'include',
    })

    if (!response.ok) {
      throw new Error('데이터 내보내기에 실패했습니다.')
    }

    const result = await response.json()

    // CSV 다운로드
    const blob = new Blob([result.data], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', result.filename)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    showToastMessage('데이터가 성공적으로 내보내졌습니다.', 'success')
  } catch (err) {
    console.error('내보내기 실패:', err)
    showToastMessage('데이터 내보내기에 실패했습니다.', 'error')
  }
}

const downloadTemplate = async () => {
  try {
    const response = await fetch('/api/phishing-training/template/download', {
      credentials: 'include',
    })

    if (!response.ok) {
      throw new Error('템플릿 다운로드에 실패했습니다.')
    }

    const blob = await response.blob()
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = '모의훈련_업로드_템플릿.csv'
    link.click()

    showToastMessage('템플릿이 다운로드되었습니다.', 'success')
  } catch (err) {
    console.error('템플릿 다운로드 실패:', err)
    showToastMessage('템플릿 다운로드에 실패했습니다.', 'error')
  }
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
watch([selectedYear, selectedPeriod, selectedResult], () => {
  loadTrainingData()
})

// 라이프사이클 훅
onMounted(() => {
  loadTrainingData()
})
</script>

<style scoped>
/* AdminTrainingManagement.vue CSS */
.admin-training {
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

.training-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.training-table th,
.training-table td {
  padding: 8px 6px;
  text-align: left;
  border-bottom: 1px solid #f3f4f6;
  white-space: nowrap;
}

.training-table th {
  background-color: #f9fafb;
  font-weight: 600;
  color: #374151;
  position: sticky;
  top: 0;
  z-index: 10;
  font-size: 11px;
}

.training-table tbody tr:hover {
  background-color: #f9fafb;
}

.status-badge {
  padding: 2px 6px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 600;
}

.status-badge.success {
  background-color: #d1fae5;
  color: #065f46;
}

.status-badge.danger {
  background-color: #fee2e2;
  color: #991b1b;
}

.status-badge.warning {
  background-color: #fef3c7;
  color: #92400e;
}

.log-type.danger-text {
  color: #ef4444;
  font-weight: 600;
  font-size: 11px;
}

.mail-type-cell {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.scoring-toggle {
  padding: 2px 8px;
  border-radius: 12px;
  border: none;
  font-size: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.scoring-toggle.included {
  background-color: #d1fae5;
  color: #065f46;
}

.scoring-toggle.excluded {
  background-color: #fee2e2;
  color: #991b1b;
}

.scoring-toggle:hover {
  opacity: 0.8;
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
  width: 800px;
}

.modal-content.edit-modal {
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

/* 업로드 관련 스타일 */
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

/* 미리보기 테이블 */
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
  font-size: 12px;
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
  .admin-training {
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

  .training-table {
    font-size: 11px;
  }

  .training-table th,
  .training-table td {
    padding: 6px 4px;
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
  .mail-type-cell {
    max-width: 80px;
  }

  .upload-area {
    padding: 20px 10px;
  }

  .upload-icon {
    font-size: 36px;
  }

  .training-table th,
  .training-table td {
    padding: 4px 2px;
    font-size: 10px;
  }
}
</style>
