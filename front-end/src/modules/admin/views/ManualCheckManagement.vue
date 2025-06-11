<!-- ManualCheckManagement.vue - Template 부분 -->
<template>
  <div class="admin-training">
    <div class="admin-header">
      <h1>수시 점검 관리</h1>
      <div class="admin-nav">
        <RouterLink to="/admin/training" class="nav-item">모의훈련 관리</RouterLink>
        <RouterLink to="/admin/manual-check" class="nav-item active">점검 관리</RouterLink>
        <RouterLink to="/admin/exceptions" class="nav-item">제외 설정</RouterLink>
      </div>
    </div>

    <div class="management-content">
      <!-- 필터 및 검색 -->
      <div class="filter-section">
        <div class="filter-group">
          <label>연도:</label>
          <select v-model="selectedYear" @change="loadCheckData">
            <option v-for="year in availableYears" :key="year" :value="year">{{ year }}년</option>
          </select>
        </div>

        <div class="filter-group">
          <label>점검 유형:</label>
          <select v-model="selectedCheckType" @change="loadCheckData">
            <option value="">전체</option>
            <option value="screen_saver">화면보호기</option>
            <option value="antivirus">백신</option>
            <option value="patch_update">패치</option>
          </select>
        </div>

        <div class="filter-group">
          <label>결과:</label>
          <select v-model="selectedResult" @change="loadCheckData">
            <option value="">전체</option>
            <option value="pass">통과</option>
            <option value="fail">실패</option>
          </select>
        </div>

        <div class="search-group">
          <input
            type="text"
            v-model="searchQuery"
            @input="searchCheckData"
            placeholder="사용자명, ID 또는 이메일 검색..."
            class="search-input"
          />
        </div>
      </div>

      <!-- 기간 설정 섹션 -->
      <div class="period-management-section">
        <div class="section-header">
          <h3>🗓️ 점검 기간 관리</h3>
          <button @click="openPeriodModal" class="primary-button">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"
              />
            </svg>
            기간 추가
          </button>
        </div>

        <!-- 점검 유형별 기간 현황 카드 -->
        <div class="check-types-grid" v-if="periodStatus.check_types">
          <div
            v-for="(typeData, checkType) in periodStatus.check_types"
            :key="checkType"
            class="check-type-section"
          >
            <div class="type-header">
              <h4>{{ getCheckTypeName(checkType) }} 점검</h4>
              <div class="type-summary">
                <span class="summary-badge"> {{ typeData.periods?.length || 0 }}개 기간 </span>
              </div>
            </div>

            <!-- 기간 카드들 -->
            <div class="period-cards-container">
              <div
                v-for="period in typeData.periods"
                :key="period.period_id"
                class="period-card"
                :class="[`status-${period.status}`, { completed: period.is_completed }]"
              >
                <div class="card-header">
                  <h5>{{ period.period_name }}</h5>
                  <div class="card-actions">
                    <button
                      @click="editPeriod(period)"
                      class="icon-button edit-button"
                      :disabled="period.is_completed"
                      title="수정"
                    >
                      ✏️
                    </button>
                    <button
                      @click="deletePeriod(period)"
                      class="icon-button delete-button"
                      :disabled="period.is_completed || period.total_users > 0"
                      title="삭제"
                    >
                      🗑️
                    </button>
                  </div>
                </div>

                <div class="card-content">
                  <div class="period-info">
                    <span class="date-range">
                      {{ formatDate(period.start_date) }} ~ {{ formatDate(period.end_date) }}
                    </span>
                    <span class="status-badge" :class="period.status">
                      {{ getStatusText(period.status) }}
                    </span>
                  </div>

                  <div class="period-stats" v-if="period.total_users > 0">
                    <div class="stats-grid">
                      <div class="stat-item">
                        <span class="stat-value">{{ period.total_users }}</span>
                        <span class="stat-label">참여자</span>
                      </div>
                      <div class="stat-item success">
                        <span class="stat-value">{{ period.pass_count || 0 }}</span>
                        <span class="stat-label">통과</span>
                      </div>
                      <div class="stat-item danger">
                        <span class="stat-value">{{ period.fail_count || 0 }}</span>
                        <span class="stat-label">실패</span>
                      </div>
                    </div>
                  </div>

                  <div class="period-stats" v-else>
                    <span class="no-data">아직 참여자가 없습니다</span>
                  </div>
                </div>

                <div class="card-footer">
                  <div v-if="period.is_completed" class="completion-info">
                    <span class="completed-badge">✅ 완료됨</span>
                    <small>{{ formatDateTime(period.completed_at) }}</small>
                  </div>
                  <div v-else class="action-buttons">
                    <button
                      v-if="period.status === 'ended'"
                      @click="completePeriod(period)"
                      class="complete-button"
                      :disabled="completing"
                    >
                      {{ completing ? '처리 중...' : '완료 처리' }}
                    </button>
                    <button
                      v-if="period.is_completed"
                      @click="reopenPeriod(period)"
                      class="reopen-button"
                      :disabled="reopening"
                    >
                      {{ reopening ? '처리 중...' : '재개' }}
                    </button>
                  </div>
                </div>
              </div>

              <!-- 기간이 없는 경우 -->
              <div
                v-if="!typeData.periods || typeData.periods.length === 0"
                class="no-periods-card"
              >
                <div class="no-periods-content">
                  <span
                    >{{ selectedYear }}년 {{ getCheckTypeName(checkType) }} 점검 기간이
                    없습니다</span
                  >
                  <button @click="openPeriodModal(checkType)" class="add-period-link">
                    기간 추가하기
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 점검 결과 목록 -->
      <div class="results-section">
        <div class="section-header">
          <h3>📋 점검 결과</h3>
          <div class="section-actions">
            <button @click="downloadTemplate" class="secondary-button">📄 템플릿 다운로드</button>
            <button @click="openBulkUploadModal" class="primary-button">📤 일괄 업로드</button>
          </div>
        </div>

        <!-- 선택 및 액션 -->
        <div class="bulk-actions" v-if="selectedRecords.length > 0">
          <span>{{ selectedRecords.length }}개 선택됨</span>
          <button @click="bulkDelete" class="danger-button">선택 삭제</button>
        </div>

        <!-- 결과 테이블 -->
        <div class="table-container">
          <table class="results-table">
            <thead>
              <tr>
                <th>
                  <input type="checkbox" v-model="selectAll" @change="toggleSelectAll" />
                </th>
                <th>사용자</th>
                <th>점검 유형</th>
                <th>기간</th>
                <th>점검 결과</th>
                <th>점검일시</th>
                <th>비고</th>
                <th>액션</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="record in paginatedRecords"
                :key="`${record.user_id}-${record.check_type}-${record.period_id}`"
                :class="{ selected: selectedRecords.includes(record.result_id) }"
              >
                <td>
                  <input type="checkbox" :value="record.result_id" v-model="selectedRecords" />
                </td>
                <td>
                  <div class="user-info">
                    <strong>{{ record.username }}</strong>
                    <small>{{ record.user_email }}</small>
                  </div>
                </td>
                <td>
                  <span class="check-type-badge" :class="record.check_type">
                    {{ getCheckTypeName(record.check_type) }}
                  </span>
                </td>
                <td>{{ record.period_name }}</td>
                <td>
                  <span class="result-badge" :class="getResultClass(record.check_result)">
                    {{ getResultText(record.check_result) }}
                  </span>
                </td>
                <td>{{ formatDateTime(record.created_at) }}</td>
                <td>
                  <span class="notes">{{ truncateText(record.notes, 30) }}</span>
                </td>
                <td>
                  <div class="action-buttons">
                    <button @click="editRecord(record)" class="edit-btn" title="수정">✏️</button>
                    <button @click="deleteRecord(record)" class="delete-btn" title="삭제">
                      🗑️
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 페이지네이션 -->
        <div class="pagination" v-if="totalPages > 1">
          <button @click="changePage(currentPage - 1)" :disabled="currentPage === 1">이전</button>
          <span class="page-info">
            {{ currentPage }} / {{ totalPages }} (총 {{ filteredRecords.length }}건)
          </span>
          <button @click="changePage(currentPage + 1)" :disabled="currentPage === totalPages">
            다음
          </button>
        </div>
      </div>
    </div>

    <!-- 기간 추가/수정 모달 -->
    <div v-if="showPeriodModal" class="modal-overlay" @click="closePeriodModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingPeriod ? '기간 수정' : '기간 추가' }}</h3>
          <button @click="closePeriodModal" class="close-button">✕</button>
        </div>

        <div class="modal-body">
          <form @submit.prevent="savePeriod">
            <div class="form-group">
              <label>점검 유형 *</label>
              <select v-model="periodForm.check_type" :disabled="editingPeriod" required>
                <option value="">선택하세요</option>
                <option value="screen_saver">화면보호기</option>
                <option value="antivirus">백신</option>
                <option value="patch_update">패치</option>
              </select>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>연도 *</label>
                <select v-model="periodForm.period_year" :disabled="editingPeriod" required>
                  <option v-for="year in availableYears" :key="year" :value="year">
                    {{ year }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label>기간명 *</label>
                <input
                  type="text"
                  v-model="periodForm.period_name"
                  placeholder="예: Q1, 상반기, 3월 등"
                  required
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>시작일 *</label>
                <input type="date" v-model="periodForm.start_date" required />
              </div>

              <div class="form-group">
                <label>종료일 *</label>
                <input type="date" v-model="periodForm.end_date" required />
              </div>
            </div>

            <div class="form-group">
              <label>설명</label>
              <textarea
                v-model="periodForm.description"
                placeholder="기간에 대한 설명을 입력하세요"
                rows="3"
              ></textarea>
            </div>

            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="periodForm.auto_pass_setting" />
                기간 종료 시 자동 통과 처리
              </label>
              <small class="help-text">
                체크 시 기간 종료 후 완료 처리할 때 미실시 사용자들을 자동으로 통과 처리합니다.
              </small>
            </div>

            <div class="modal-footer">
              <button type="button" @click="closePeriodModal" class="secondary-button">취소</button>
              <button type="submit" class="primary-button" :disabled="savingPeriod">
                {{ savingPeriod ? '저장 중...' : '저장' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 일괄 업로드 모달 -->
    <div v-if="showBulkUploadModal" class="modal-overlay" @click="closeBulkUploadModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>점검 결과 일괄 등록</h3>
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
                <li>필수 컬럼: 사용자ID, 점검유형, 점검결과, 기간명</li>
                <li>첫 번째 행은 헤더로 처리됩니다</li>
                <li>템플릿을 다운로드하여 양식을 확인하세요</li>
              </ul>
            </div>
          </div>

          <div v-if="uploadPreview.length > 0" class="preview-section">
            <h4>미리보기 (처음 5개 레코드)</h4>
            <div class="preview-table">
              <table>
                <thead>
                  <tr>
                    <th>사용자ID</th>
                    <th>점검유형</th>
                    <th>결과</th>
                    <th>기간</th>
                    <th>비고</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(record, index) in uploadPreview.slice(0, 5)" :key="index">
                    <td>{{ record.user_id || '-' }}</td>
                    <td>{{ getCheckTypeName(record.check_type) || '-' }}</td>
                    <td>{{ getResultText(record.check_result) || '-' }}</td>
                    <td>{{ record.period_name || '-' }}</td>
                    <td>{{ truncateText(record.notes, 20) || '-' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="closeBulkUploadModal" class="cancel-button">취소</button>
          <button @click="uploadFile" :disabled="!selectedFile || uploading" class="upload-button">
            {{ uploading ? '처리 중...' : '업로드' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 수정 모달 -->
    <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>점검 결과 수정</h3>
          <button @click="closeEditModal" class="close-button">✕</button>
        </div>

        <div class="modal-body">
          <form @submit.prevent="saveRecord">
            <div class="form-group">
              <label>사용자</label>
              <input type="text" :value="editingRecord.username" disabled />
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>점검 유형</label>
                <select v-model="editingRecord.check_type" disabled>
                  <option value="screen_saver">화면보호기</option>
                  <option value="antivirus">백신</option>
                  <option value="patch_update">패치</option>
                </select>
              </div>

              <div class="form-group">
                <label>결과 *</label>
                <select v-model="editingRecord.check_result" required>
                  <option value="pass">통과</option>
                  <option value="fail">실패</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>비고</label>
              <textarea
                v-model="editingRecord.notes"
                placeholder="비고사항을 입력하세요"
                rows="3"
              ></textarea>
            </div>

            <div class="modal-footer">
              <button type="button" @click="closeEditModal" class="secondary-button">취소</button>
              <button type="submit" class="primary-button" :disabled="saving">
                {{ saving ? '저장 중...' : '저장' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 토스트 메시지 -->
    <div v-if="showToast" :class="['toast-message', toastType]">
      {{ toastMessage }}
    </div>
  </div>
</template>

// ManualCheckManagement.vue - Script Setup 부분
<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { RouterLink } from 'vue-router'

// 기존 반응형 데이터
const selectedYear = ref(new Date().getFullYear())
const selectedCheckType = ref('')
const selectedResult = ref('')
const searchQuery = ref('')
const checkData = ref([])
const filteredRecords = ref([])
const selectedRecords = ref([])
const selectAll = ref(false)
const loading = ref(false)
const error = ref('')

// 페이지네이션
const currentPage = ref(1)
const itemsPerPage = ref(20)

// 모달 상태
const showBulkUploadModal = ref(false)
const showEditModal = ref(false)
const showPeriodModal = ref(false)
const selectedFile = ref(null)
const uploadPreview = ref([])
const uploading = ref(false)
const editingRecord = ref({})
const saving = ref(false)

// 기간 관리 관련
const editingPeriod = ref(null)
const savingPeriod = ref(false)
const completing = ref(false)
const reopening = ref(false)
const periodStatus = ref({ check_types: {} })

// 토스트
const showToast = ref(false)
const toastMessage = ref('')
const toastType = ref('success')

// 기간 폼
const periodForm = reactive({
  check_type: '',
  period_year: new Date().getFullYear(),
  period_name: '',
  start_date: '',
  end_date: '',
  description: '',
  auto_pass_setting: true,
})

// 계산된 속성
const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: 11 }, (_, i) => currentYear - 5 + i)
})

const paginatedRecords = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredRecords.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredRecords.value.length / itemsPerPage.value)
})

// 주요 데이터 로딩 메서드
const loadCheckData = async () => {
  try {
    loading.value = true
    const params = new URLSearchParams({
      year: selectedYear.value,
    })

    if (selectedCheckType.value) params.append('check_type', selectedCheckType.value)
    if (selectedResult.value) params.append('result', selectedResult.value)
    if (searchQuery.value) params.append('search', searchQuery.value)

    const response = await fetch(`/api/manual-check/results?${params}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })

    if (!response.ok) throw new Error('점검 결과 조회 실패')

    const result = await response.json()
    checkData.value = result.data || []
    filteredRecords.value = result.data || []
  } catch (err) {
    console.error('점검 결과 조회 오류:', err)
    displayToast('점검 결과 조회에 실패했습니다.', 'error')
  } finally {
    loading.value = false
  }
}

const loadPeriodStatus = async () => {
  try {
    const response = await fetch(`/api/manual-check/periods/status?year=${selectedYear.value}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })

    if (!response.ok) throw new Error('기간 상태 조회 실패')

    const result = await response.json()
    periodStatus.value = result.data
  } catch (err) {
    console.error('기간 상태 조회 오류:', err)
    displayToast('기간 상태 조회에 실패했습니다.', 'error')
  }
}

// 검색 및 필터링
const searchCheckData = () => {
  // 디바운싱 구현
  setTimeout(() => {
    loadCheckData()
  }, 300)
}

// 유틸리티 함수들
const getCheckTypeName = (type) => {
  const names = {
    screen_saver: '화면보호기',
    antivirus: '백신',
    patch_update: '패치',
  }
  return names[type] || type
}

const getStatusText = (status) => {
  const texts = {
    active: '진행 중',
    upcoming: '예정',
    ended: '종료',
  }
  return texts[status] || status
}

const getResultClass = (result) => {
  const classes = {
    pass: 'success',
    fail: 'danger',
  }
  return classes[result] || 'warning'
}

const getResultText = (result) => {
  const texts = {
    pass: '통과',
    fail: '실패',
  }
  return texts[result] || '알 수 없음'
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('ko-KR')
}

const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return ''
  return new Date(dateTimeString).toLocaleString('ko-KR')
}

const truncateText = (text, maxLength) => {
  if (!text) return ''
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

// 기간 관리 메서드
const openPeriodModal = (checkType = '') => {
  editingPeriod.value = null
  periodForm.check_type = checkType
  periodForm.period_year = selectedYear.value
  periodForm.period_name = ''
  periodForm.start_date = ''
  periodForm.end_date = ''
  periodForm.description = ''
  periodForm.auto_pass_setting = true
  showPeriodModal.value = true
}

const closePeriodModal = () => {
  showPeriodModal.value = false
  editingPeriod.value = null
}

const savePeriod = async () => {
  if (savingPeriod.value) return

  savingPeriod.value = true

  try {
    const url = editingPeriod.value
      ? `/api/manual-check/periods/${editingPeriod.value.period_id}`
      : '/api/manual-check/periods'

    const method = editingPeriod.value ? 'PUT' : 'POST'

    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify(periodForm),
    })

    const result = await response.json()

    if (!response.ok) {
      throw new Error(result.error || '저장 실패')
    }

    displayToast(result.message, 'success')
    closePeriodModal()
    await loadPeriodStatus()
  } catch (err) {
    console.error('기간 저장 오류:', err)
    displayToast(err.message, 'error')
  } finally {
    savingPeriod.value = false
  }
}

const editPeriod = (period) => {
  editingPeriod.value = period
  periodForm.check_type = period.check_type
  periodForm.period_year = period.period_year
  periodForm.period_name = period.period_name
  periodForm.start_date = period.start_date
  periodForm.end_date = period.end_date
  periodForm.description = period.description || ''
  periodForm.auto_pass_setting = period.auto_pass_setting
  showPeriodModal.value = true
}

const deletePeriod = async (period) => {
  if (!confirm(`${period.period_name} 기간을 삭제하시겠습니까?`)) return

  try {
    const response = await fetch(`/api/manual-check/periods/${period.period_id}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })

    const result = await response.json()

    if (!response.ok) {
      throw new Error(result.error || '삭제 실패')
    }

    displayToast(result.message, 'success')
    await loadPeriodStatus()
  } catch (err) {
    console.error('기간 삭제 오류:', err)
    displayToast(err.message, 'error')
  }
}

const completePeriod = async (period) => {
  if (
    !confirm(
      `${period.period_name} 기간을 완료 처리하시겠습니까?\n\n` +
        `자동 통과 설정이 켜져있어 미실시 사용자들이 자동으로 통과 처리됩니다.`,
    )
  )
    return

  completing.value = true

  try {
    const response = await fetch(`/api/manual-check/periods/${period.period_id}/complete`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })

    const result = await response.json()

    if (!response.ok) {
      throw new Error(result.error || '완료 처리 실패')
    }

    displayToast(result.message, 'success')
    await loadPeriodStatus()
    await loadCheckData()
  } catch (err) {
    console.error('완료 처리 오류:', err)
    displayToast(err.message, 'error')
  } finally {
    completing.value = false
  }
}

const reopenPeriod = async (period) => {
  if (
    !confirm(
      `${period.period_name} 기간을 재개하시겠습니까?\n\n` + `자동 통과 처리된 결과가 삭제됩니다.`,
    )
  )
    return

  reopening.value = true

  try {
    const response = await fetch(`/api/manual-check/periods/${period.period_id}/reopen`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })

    const result = await response.json()

    if (!response.ok) {
      throw new Error(result.error || '재개 처리 실패')
    }

    displayToast(result.message, 'success')
    await loadPeriodStatus()
    await loadCheckData()
  } catch (err) {
    console.error('재개 처리 오류:', err)
    displayToast(err.message, 'error')
  } finally {
    reopening.value = false
  }
}

// 점검 결과 관리 메서드
const editRecord = (record) => {
  editingRecord.value = { ...record }
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
  editingRecord.value = {}
}

const saveRecord = async () => {
  if (saving.value) return

  saving.value = true

  try {
    const response = await fetch('/api/manual-check/results/update', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify(editingRecord.value),
    })

    const result = await response.json()

    if (!response.ok) {
      throw new Error(result.error || '수정 실패')
    }

    displayToast(result.message, 'success')
    closeEditModal()
    await loadCheckData()
  } catch (err) {
    console.error('기록 수정 오류:', err)
    displayToast(err.message, 'error')
  } finally {
    saving.value = false
  }
}

const deleteRecord = async (record) => {
  if (
    !confirm(
      `${record.username}의 ${getCheckTypeName(record.check_type)} 점검 결과를 삭제하시겠습니까?`,
    )
  )
    return

  try {
    const response = await fetch(`/api/manual-check/results/${record.result_id}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })

    const result = await response.json()

    if (!response.ok) {
      throw new Error(result.error || '삭제 실패')
    }

    displayToast(result.message, 'success')
    await loadCheckData()
  } catch (err) {
    console.error('기록 삭제 오류:', err)
    displayToast(err.message, 'error')
  }
}

// 일괄 처리 메서드
const toggleSelectAll = () => {
  if (selectAll.value) {
    selectedRecords.value = paginatedRecords.value.map((record) => record.result_id)
  } else {
    selectedRecords.value = []
  }
}

const bulkDelete = async () => {
  if (!confirm(`선택된 ${selectedRecords.value.length}개의 결과를 삭제하시겠습니까?`)) return

  try {
    const response = await fetch('/api/manual-check/results/bulk-delete', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({ result_ids: selectedRecords.value }),
    })

    const result = await response.json()

    if (!response.ok) {
      throw new Error(result.error || '일괄 삭제 실패')
    }

    displayToast(result.message, 'success')
    selectedRecords.value = []
    selectAll.value = false
    await loadCheckData()
  } catch (err) {
    console.error('일괄 삭제 오류:', err)
    displayToast(err.message, 'error')
  }
}

// 파일 업로드 관련 메서드
const openBulkUploadModal = () => {
  showBulkUploadModal.value = true
  selectedFile.value = null
  uploadPreview.value = []
}

const closeBulkUploadModal = () => {
  showBulkUploadModal.value = false
  selectedFile.value = null
  uploadPreview.value = []
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (!file) return

  selectedFile.value = file

  // 파일 미리보기 처리
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const text = e.target.result
      const lines = text.split('\n')
      const headers = lines[0].split(',')

      const preview = lines
        .slice(1, 6)
        .map((line) => {
          const values = line.split(',')
          return {
            user_id: values[0]?.trim(),
            check_type: values[1]?.trim(),
            check_result: values[2]?.trim(),
            period_name: values[3]?.trim(),
            notes: values[4]?.trim(),
          }
        })
        .filter((row) => row.user_id)

      uploadPreview.value = preview
    } catch (err) {
      console.error('파일 미리보기 오류:', err)
      displayToast('파일 형식을 확인해주세요.', 'error')
    }
  }
  reader.readAsText(file)
}

const handleFileDrop = (event) => {
  event.preventDefault()
  const files = event.dataTransfer.files
  if (files.length > 0) {
    const file = files[0]
    if (
      file.type === 'text/csv' ||
      file.name.endsWith('.csv') ||
      file.type.includes('spreadsheet') ||
      file.name.endsWith('.xlsx') ||
      file.name.endsWith('.xls')
    ) {
      selectedFile.value = file
      handleFileSelect({ target: { files: [file] } })
    } else {
      displayToast('CSV 또는 Excel 파일만 업로드 가능합니다.', 'error')
    }
  }
}

const removeSelectedFile = () => {
  selectedFile.value = null
  uploadPreview.value = []
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const uploadFile = async () => {
  if (!selectedFile.value || uploading.value) return

  uploading.value = true

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const response = await fetch('/api/manual-check/results/upload', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
      body: formData,
    })

    const result = await response.json()

    if (!response.ok) {
      throw new Error(result.error || '업로드 실패')
    }

    displayToast(result.message, 'success')
    closeBulkUploadModal()
    await loadCheckData()
  } catch (err) {
    console.error('파일 업로드 오류:', err)
    displayToast(err.message, 'error')
  } finally {
    uploading.value = false
  }
}

const downloadTemplate = async () => {
  try {
    const response = await fetch('/api/manual-check/template', {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })

    if (!response.ok) throw new Error('템플릿 다운로드 실패')

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'manual_check_template.csv'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)

    displayToast('템플릿이 다운로드되었습니다.', 'success')
  } catch (err) {
    console.error('템플릿 다운로드 오류:', err)
    displayToast('템플릿 다운로드에 실패했습니다.', 'error')
  }
}

// 페이지네이션
const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

// 토스트 메시지
const displayToast = (message, type = 'success') => {
  toastMessage.value = message
  toastType.value = type
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

// 감시자
watch(selectedYear, () => {
  loadPeriodStatus()
  loadCheckData()
})

// 생명주기
onMounted(() => {
  loadPeriodStatus()
  loadCheckData()
})
</script>

/* ManualCheckManagement.vue - Style 부분 */
<style scoped>
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

/* 관리 컨텐츠 */
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

/* 기간 관리 섹션 */
.period-management-section {
  background-color: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
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
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

/* 점검 유형별 그리드 */
.check-types-grid {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.check-type-section {
  background-color: #f8fafc;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e2e8f0;
}

.type-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.type-header h4 {
  margin: 0;
  color: #1e293b;
  font-size: 1.1rem;
  font-weight: 600;
}

.type-summary {
  display: flex;
  gap: 8px;
}

.summary-badge {
  background: #e0e7ff;
  color: #3730a3;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

/* 기간 카드 컨테이너 */
.period-cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.period-card {
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  background-color: #fafafa;
  transition: all 0.3s ease;
  position: relative;
}

.period-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

/* 기간 상태별 스타일 */
.period-card.status-upcoming {
  border-color: #3b82f6;
  background-color: #eff6ff;
}

.period-card.status-active {
  border-color: #10b981;
  background-color: #ecfdf5;
}

.period-card.status-ended {
  border-color: #f59e0b;
  background-color: #fffbeb;
}

.period-card.completed {
  border-color: #6b7280;
  background-color: #f9fafb;
  opacity: 0.9;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.card-header h5 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
}

.card-actions {
  display: flex;
  gap: 4px;
}

.icon-button {
  background: none;
  border: none;
  padding: 6px;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
  opacity: 0.7;
}

.icon-button:hover:not(:disabled) {
  opacity: 1;
  background: #f3f4f6;
}

.icon-button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.card-content {
  margin-bottom: 16px;
}

.period-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.date-range {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.upcoming {
  background-color: #dbeafe;
  color: #1e40af;
}

.status-badge.active {
  background-color: #d1fae5;
  color: #065f46;
}

.status-badge.ended {
  background-color: #fef3c7;
  color: #92400e;
}

.period-stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.stat-item {
  text-align: center;
  padding: 8px;
  background: #f8fafc;
  border-radius: 8px;
}

.stat-item.success {
  background: #ecfdf5;
}

.stat-item.danger {
  background: #fef2f2;
}

.stat-value {
  display: block;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.stat-item.success .stat-value {
  color: #059669;
}

.stat-item.danger .stat-value {
  color: #dc2626;
}

.stat-label {
  display: block;
  font-size: 12px;
  color: #6b7280;
  margin-top: 2px;
}

.no-data {
  color: #9ca3af;
  font-style: italic;
  text-align: center;
  padding: 16px;
}

.card-footer {
  border-top: 1px solid #f3f4f6;
  padding-top: 12px;
}

.completion-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.completed-badge {
  color: #3b82f6;
  font-weight: 500;
  font-size: 14px;
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.complete-button {
  background: #10b981;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
}

.complete-button:hover:not(:disabled) {
  background: #059669;
}

.complete-button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.reopen-button {
  background: #f59e0b;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
}

.reopen-button:hover:not(:disabled) {
  background: #d97706;
}

.reopen-button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.no-periods-card {
  grid-column: 1 / -1;
  background: white;
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  padding: 40px 20px;
  text-align: center;
}

.no-periods-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: center;
  color: #6b7280;
}

.add-period-link {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.add-period-link:hover {
  background: #2563eb;
}

/* 버튼 스타일 */
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
  text-decoration: none;
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

.outline-button:hover {
  background-color: #f9fafb;
  border-color: #9ca3af;
}

.danger-button {
  background: #ef4444;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.danger-button:hover {
  background: #dc2626;
}

/* CSS 변수 정의 */
:root {
  --primary-color: #3b82f6;
  --dark-blue: #2563eb;
}

/* 결과 섹션 */
.results-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
}

.section-actions {
  display: flex;
  gap: 12px;
}

/* 일괄 액션 */
.bulk-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8fafc;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 14px;
}

/* 테이블 스타일 */
.table-container {
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.results-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.results-table th,
.results-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.results-table th {
  background: #f8fafc;
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}

.results-table tr:hover {
  background: #f8fafc;
}

.results-table tr.selected {
  background: #eff6ff;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-info strong {
  color: #1f2937;
}

.user-info small {
  color: #6b7280;
  font-size: 12px;
}

.check-type-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.check-type-badge.screen_saver {
  background: #dbeafe;
  color: #1d4ed8;
}

.check-type-badge.antivirus {
  background: #dcfce7;
  color: #166534;
}

.check-type-badge.patch_update {
  background: #fef3c7;
  color: #92400e;
}

.result-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.result-badge.success {
  background: #dcfce7;
  color: #166534;
}

.result-badge.danger {
  background: #fee2e2;
  color: #991b1b;
}

.result-badge.warning {
  background: #fef3c7;
  color: #92400e;
}

.notes {
  color: #6b7280;
  font-size: 13px;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.edit-btn,
.delete-btn {
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.2s;
}

.edit-btn:hover {
  background: #e0e7ff;
}

.delete-btn:hover {
  background: #fee2e2;
}

/* 업로드 관련 스타일 */
.upload-section {
  margin-bottom: 30px;
}

.upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  transition: all 0.2s ease;
  cursor: pointer;
}

.upload-area:hover {
  border-color: var(--primary-color);
  background-color: #fafafa;
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

.upload-placeholder p {
  color: #6b7280;
  margin: 0;
}

.select-file-button {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.select-file-button:hover {
  background-color: var(--dark-blue);
}

.file-selected {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f8fafc;
  padding: 20px;
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
  font-weight: 500;
  color: #1f2937;
}

.file-size {
  font-size: 12px;
  color: #6b7280;
}

.remove-file-button {
  background: #ef4444;
  color: white;
  border: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-file-button:hover {
  background: #dc2626;
}

.upload-instructions {
  background: #f9fafb;
  padding: 20px;
  border-radius: 8px;
  margin-top: 20px;
}

.upload-instructions h4 {
  margin: 0 0 12px 0;
  color: #1f2937;
  font-size: 16px;
  font-weight: 600;
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
  background: white;
}

.preview-table th,
.preview-table td {
  padding: 10px 8px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.preview-table th {
  background: #f3f4f6;
  font-weight: 600;
  color: #374151;
}

.preview-table td {
  color: #6b7280;
}

/* 모달 푸터 버튼 */
.cancel-button,
.upload-button {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.cancel-button {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.cancel-button:hover {
  background: #e5e7eb;
}

.upload-button {
  background: #10b981;
  color: white;
}

.upload-button:hover:not(:disabled) {
  background: #059669;
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
}

.upload-button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 결과 섹션 */
.results-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

/* 일괄 액션 */
.bulk-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8fafc;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 14px;
}

/* 테이블 스타일 */
.table-container {
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.results-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.results-table th,
.results-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.results-table th {
  background: #f8fafc;
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}

.results-table tr:hover {
  background: #f8fafc;
}

.results-table tr.selected {
  background: #eff6ff;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-info strong {
  color: #1f2937;
}

.user-info small {
  color: #6b7280;
  font-size: 12px;
}

.check-type-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.check-type-badge.screen_saver {
  background: #dbeafe;
  color: #1d4ed8;
}

.check-type-badge.antivirus {
  background: #dcfce7;
  color: #166534;
}

.check-type-badge.patch_update {
  background: #fef3c7;
  color: #92400e;
}

.result-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.result-badge.success {
  background: #dcfce7;
  color: #166534;
}

.result-badge.danger {
  background: #fee2e2;
  color: #991b1b;
}

.result-badge.warning {
  background: #fef3c7;
  color: #92400e;
}

.notes {
  color: #6b7280;
  font-size: 13px;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.edit-btn,
.delete-btn {
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.2s;
}

.edit-btn:hover {
  background: #e0e7ff;
}

.delete-btn:hover {
  background: #fee2e2;
}

/* 페이지네이션 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 20px;
  padding: 16px;
}

.pagination button {
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination button:hover:not(:disabled) {
  background: #e5e7eb;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
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
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  animation: modalSlideIn 0.3s ease;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* 모달 헤더 */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px;
  border-bottom: 1px solid #e5e7eb;
  background: #f8fafc;
  border-radius: 12px 12px 0 0;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 600;
  color: #1f2937;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6b7280;
  padding: 5px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.close-button:hover {
  background: #e5e7eb;
  color: #374151;
}

/* 모달 바디 */
.modal-body {
  padding: 30px;
}

/* 모달 푸터 */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 25px;
  border-top: 1px solid #e5e7eb;
  background: #f8fafc;
  border-radius: 0 0 12px 12px;
}

/* 폼 스타일 */
.form-group {
  margin-bottom: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #374151;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-group input:disabled {
  background: #f9fafb;
  color: #6b7280;
}

.checkbox-label {
  display: flex !important;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  margin-bottom: 8px !important;
}

.checkbox-label input {
  width: auto !important;
  margin: 0;
}

.help-text {
  color: #6b7280;
  font-size: 13px;
  margin-top: 4px;
}

/* 업로드 섹션 */
.upload-section {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  padding: 20px;
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  background: #f8fafc;
}

.file-input {
  display: none;
}

.upload-button {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}

.upload-button:hover {
  background: #2563eb;
}

.file-name {
  color: #374151;
  font-weight: 500;
}

/* 미리보기 섹션 */
.preview-section {
  margin-top: 20px;
}

.preview-section h4 {
  margin: 0 0 12px 0;
  color: #374151;
}

.preview-table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
}

.preview-table th,
.preview-table td {
  padding: 8px 12px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
  font-size: 13px;
}

.preview-table th {
  background: #f8fafc;
  font-weight: 600;
}

/* 토스트 메시지 */
.toast-message {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
  z-index: 1100;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: slideIn 0.3s ease;
}

.toast-message.success {
  background: #dcfce7;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.toast-message.error {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.toast-message.warning {
  background: #fef3c7;
  color: #92400e;
  border: 1px solid #fde68a;
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
  .admin-manual-check {
    padding: 16px;
  }

  .admin-header {
    padding: 20px;
  }

  .admin-header h1 {
    font-size: 1.8rem;
  }

  .filter-section {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .search-group {
    margin-left: 0;
  }

  .search-input {
    width: 100%;
  }

  .section-header {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }

  .period-cards-container {
    grid-template-columns: 1fr;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .modal-content {
    width: 95%;
    margin: 20px;
  }

  .table-container {
    font-size: 14px;
  }

  .results-table th,
  .results-table td {
    padding: 8px;
  }
}
</style>
