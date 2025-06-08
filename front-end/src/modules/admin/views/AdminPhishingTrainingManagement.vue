<!-- AdminPhishingTrainingManagement.vue - Template 부분 -->
<template>
  <div class="admin-training">
    <div class="admin-header">
      <h1>악성메일 모의훈련 관리</h1>
      <div class="admin-nav">
        <RouterLink to="/admin/training" class="nav-item active">훈련 관리</RouterLink>
        <RouterLink to="/admin/exceptions" class="nav-item">제외 설정</RouterLink>
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

      <!-- 기간 설정 섹션 -->
      <div class="period-management-section">
        <div class="section-header">
          <h3>🗓️ 훈련 기간 관리</h3>
          <button @click="openPeriodModal" class="primary-button">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"
              />
            </svg>
            기간 추가
          </button>
        </div>

        <!-- 기간 상태 카드 -->
        <div class="period-cards" v-if="periodStatus.periods">
          <div
            v-for="period in periodStatus.periods"
            :key="`${period.training_period}`"
            class="period-card"
            :class="[`status-${period.status}`, { completed: period.is_completed }]"
          >
            <div class="card-header">
              <h4>{{ period.training_period === 'first_half' ? '상반기' : '하반기' }}</h4>
              <div class="status-badges">
                <span class="status-badge" :class="period.status">
                  {{ getStatusText(period.status) }}
                </span>
                <span v-if="period.is_completed" class="completion-badge">완료됨</span>
              </div>
            </div>

            <div class="card-content">
              <div class="period-info">
                <p><strong>기간:</strong> {{ period.start_date }} ~ {{ period.end_date }}</p>
                <div class="stats">
                  <span class="stat pass">성공: {{ period.pass_count || 0 }}</span>
                  <span class="stat fail">실패: {{ period.fail_count || 0 }}</span>
                  <span class="stat pending">미실시: {{ period.pending_count || 0 }}</span>
                </div>
              </div>

              <div class="card-actions">
                <button
                  @click="editPeriod(period)"
                  class="edit-button"
                  :disabled="period.is_completed"
                >
                  수정
                </button>
                <button
                  v-if="!period.is_completed && period.status === 'ended'"
                  @click="completePeriod(period.period_id)"
                  class="complete-button"
                >
                  완료 처리
                </button>
                <button
                  v-if="period.is_completed"
                  @click="reopenPeriod(period.period_id)"
                  class="reopen-button"
                >
                  재개
                </button>
                <button
                  @click="deletePeriod(period.period_id)"
                  class="delete-button"
                  :disabled="period.is_completed"
                >
                  삭제
                </button>
              </div>
            </div>
          </div>
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

        <RouterLink to="/admin/exceptions" class="outline-button">
          <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path
              d="M2.5 1a1 1 0 0 0-1 1v1a1 1 0 0 0 1 1H3v9a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V4h.5a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H10a1 1 0 0 0-1-1H7a1 1 0 0 0-1 1H2.5zm3 4a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 .5-.5zM8 5a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7A.5.5 0 0 1 8 5zm3 .5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 1 0z"
            />
          </svg>
          제외 설정
        </RouterLink>
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
                <th>제외 상태</th>
                <th>액션</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="record in paginatedRecords"
                :key="`${record.user_id}-${record.training_year}-${record.training_period}`"
              >
                <td>
                  <input
                    type="checkbox"
                    :value="record"
                    v-model="selectedRecords"
                    @change="updateSelectAll"
                  />
                </td>
                <td>{{ record.user_id }}</td>
                <td>{{ record.username }}</td>
                <td>{{ record.department }}</td>
                <td>{{ record.training_year }}</td>
                <td>
                  <span class="period-badge">
                    {{ record.training_period === 'first_half' ? '상반기' : '하반기' }}
                  </span>
                </td>
                <td>{{ record.user_email || '-' }}</td>
                <td>{{ formatDateTime(record.email_sent_time) }}</td>
                <td>{{ formatResponseTime(record.response_time_minutes) }}</td>
                <td>
                  <span v-if="record.log_type" class="log-type danger-text">
                    {{ record.log_type }}
                  </span>
                  <span v-else>-</span>
                </td>
                <td class="mail-type-cell">{{ record.mail_type || '-' }}</td>
                <td>{{ record.ip_address || '-' }}</td>
                <td>
                  <span
                    class="status-badge"
                    :class="{
                      success: record.training_result === 'pass',
                      danger: record.training_result === 'fail',
                      warning: record.training_result === 'pending',
                    }"
                  >
                    {{
                      record.training_result === 'pass'
                        ? '통과'
                        : record.training_result === 'fail'
                          ? '실패'
                          : '미실시'
                    }}
                  </span>
                </td>
                <td>
                  <button
                    @click="toggleExceptionStatus(record)"
                    class="exception-button"
                    :title="
                      record.exclude_from_scoring ? '점수 계산에서 제외됨' : '점수 계산에 포함됨'
                    "
                  >
                    <span
                      class="exception-status"
                      :class="record.exclude_from_scoring ? 'excluded' : 'included'"
                    >
                      {{ record.exclude_from_scoring ? '제외' : '포함' }}
                    </span>
                  </button>
                </td>
                <td>
                  <div class="action-buttons">
                    <button @click="editRecord(record)" class="edit-button" title="수정">
                      <svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                        <path
                          d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708L14.5 5.207l-3-3L12.146.146zM11.207 2.5L13.5 4.793 14.793 3.5 12.5 1.207 11.207 2.5zm1.586 3L10.5 3.207 4 9.707V10h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.293l6.5-6.5zm-9.761 5.175-.106.106-1.528 3.821 3.821-1.528.106-.106A.5.5 0 0 1 5 12.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.468-.325z"
                        />
                      </svg>
                    </button>
                    <button @click="deleteRecord(record)" class="delete-button" title="삭제">
                      <svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                        <path
                          d="M2.5 1a1 1 0 0 0-1 1v1a1 1 0 0 0 1 1H3v9a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V4h.5a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H10a1 1 0 0 0-1-1H7a1 1 0 0 0-1 1H2.5zm3 4a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 .5-.5zM8 5a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7A.5.5 0 0 1 8 5zm3 .5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 1 0z"
                        />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>

          <!-- 페이지네이션 -->
          <div class="pagination">
            <button @click="currentPage--" :disabled="currentPage <= 1" class="pagination-button">
              이전
            </button>

            <span class="pagination-info">
              {{ currentPage }} / {{ totalPages }} 페이지 (총 {{ filteredRecords.length }}건)
            </span>

            <button
              @click="currentPage++"
              :disabled="currentPage >= totalPages"
              class="pagination-button"
            >
              다음
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 기간 설정 모달 -->
    <div v-if="showPeriodModal" class="modal-overlay" @click="closePeriodModal">
      <div class="modal-content period-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ editingPeriod ? '기간 수정' : '기간 추가' }}</h3>
          <button @click="closePeriodModal" class="close-button">×</button>
        </div>

        <div class="modal-body">
          <form @submit.prevent="savePeriod">
            <div class="form-row">
              <div class="form-group">
                <label>연도 *</label>
                <input
                  type="number"
                  v-model.number="periodForm.training_year"
                  :disabled="editingPeriod"
                  min="2020"
                  max="2030"
                  required
                />
              </div>

              <div class="form-group">
                <label>기간 *</label>
                <select v-model="periodForm.training_period" :disabled="editingPeriod" required>
                  <option value="">선택하세요</option>
                  <option value="first_half">상반기</option>
                  <option value="second_half">하반기</option>
                </select>
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
                rows="3"
                placeholder="기간에 대한 설명을 입력하세요..."
              ></textarea>
            </div>

            <div class="form-actions">
              <button type="button" @click="closePeriodModal" class="cancel-button">취소</button>
              <button type="submit" class="save-button" :disabled="savingPeriod">
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
          <h3>모의훈련 데이터 일괄 업로드</h3>
          <button @click="closeBulkUploadModal" class="close-button">×</button>
        </div>

        <div class="modal-body">
          <div class="upload-section">
            <div class="upload-area" @drop="handleFileDrop" @dragover.prevent @dragenter.prevent>
              <div class="upload-icon">📁</div>
              <p>CSV 파일을 여기에 끌어다 놓거나 클릭하여 선택하세요</p>
              <input type="file" ref="fileInput" @change="handleFileSelect" accept=".csv" hidden />
              <button type="button" @click="$refs.fileInput.click()" class="browse-button">
                파일 선택
              </button>
            </div>

            <div class="upload-instructions">
              <h4>업로드 형식 안내</h4>
              <ul>
                <li>CSV 형식만 지원됩니다</li>
                <li>첫 번째 행은 헤더로 사용됩니다</li>
                <li>필수 필드: user_email, training_year, training_period</li>
                <li>
                  선택 필드: email_sent_time, action_time, log_type, mail_type, ip_address, notes
                </li>
              </ul>
              <button @click="downloadTemplate" class="secondary-button">템플릿 다운로드</button>
            </div>
          </div>

          <!-- 미리보기 -->
          <div v-if="uploadPreview.length > 0" class="preview-section">
            <h4>업로드 미리보기 (최대 5개 항목)</h4>
            <div class="preview-table">
              <table>
                <thead>
                  <tr>
                    <th v-for="header in Object.keys(uploadPreview[0])" :key="header">
                      {{ header }}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, index) in uploadPreview.slice(0, 5)" :key="index">
                    <td v-for="header in Object.keys(row)" :key="header">
                      {{ row[header] }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="modal-actions">
            <button @click="closeBulkUploadModal" class="cancel-button">취소</button>
            <button
              @click="uploadBulkData"
              :disabled="!selectedFile || uploading"
              class="upload-button"
            >
              {{ uploading ? '업로드 중...' : '업로드' }}
            </button>
          </div>
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
            <div class="form-row">
              <div class="form-group">
                <label>사용자 ID</label>
                <input type="text" v-model="editingRecord.user_id" disabled />
              </div>
              <div class="form-group">
                <label>사용자명</label>
                <input type="text" v-model="editingRecord.username" disabled />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>훈련 연도</label>
                <input type="number" v-model="editingRecord.training_year" disabled />
              </div>
              <div class="form-group">
                <label>훈련 기간</label>
                <select v-model="editingRecord.training_period" disabled>
                  <option value="first_half">상반기</option>
                  <option value="second_half">하반기</option>
                </select>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>메일 발송 시각</label>
                <input type="datetime-local" v-model="editingRecord.email_sent_time" step="1" />
              </div>
              <div class="form-group">
                <label>액션 시각</label>
                <input type="datetime-local" v-model="editingRecord.action_time" step="1" />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>로그 유형</label>
                <input type="text" v-model="editingRecord.log_type" />
              </div>
              <div class="form-group">
                <label>메일 유형</label>
                <input type="text" v-model="editingRecord.mail_type" />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>사용자 이메일</label>
                <input type="email" v-model="editingRecord.user_email" />
              </div>
              <div class="form-group">
                <label>IP 주소</label>
                <input type="text" v-model="editingRecord.ip_address" />
              </div>
            </div>

            <div class="form-group">
              <label>비고</label>
              <textarea v-model="editingRecord.notes" rows="3"></textarea>
            </div>

            <div class="modal-actions">
              <button type="button" @click="closeEditModal" class="cancel-button">취소</button>
              <button type="submit" :disabled="saving" class="save-button">
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

// AdminPhishingTrainingManagement.vue - Script Setup 부분
<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { RouterLink } from 'vue-router'

// 기존 반응형 데이터
const selectedYear = ref(new Date().getFullYear())
const selectedPeriod = ref('')
const selectedResult = ref('')
const searchQuery = ref('')
const trainingData = ref([])
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
const selectedFile = ref(null)
const uploadPreview = ref([])
const uploading = ref(false)
const editingRecord = ref({})
const saving = ref(false)

// 토스트
const showToast = ref(false)
const toastMessage = ref('')
const toastType = ref('success')

// 기간 관리 관련 데이터
const showPeriodModal = ref(false)
const editingPeriod = ref(null)
const savingPeriod = ref(false)
const periodStatus = ref({ periods: [] })

const periodForm = reactive({
  training_year: new Date().getFullYear(),
  training_period: '',
  start_date: '',
  end_date: '',
  description: '',
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

// 기간 관리 메서드
const loadPeriodStatus = async () => {
  try {
    const response = await fetch(
      `/api/phishing-training/periods/status?year=${selectedYear.value}`,
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      },
    )

    if (!response.ok) throw new Error('기간 상태 조회 실패')

    periodStatus.value = await response.json()
  } catch (err) {
    console.error('기간 상태 조회 오류:', err)
    displayToast('기간 상태 조회에 실패했습니다.', 'error')
  }
}

const openPeriodModal = () => {
  resetPeriodForm()
  showPeriodModal.value = true
}

const closePeriodModal = () => {
  showPeriodModal.value = false
  editingPeriod.value = null
  resetPeriodForm()
}

const resetPeriodForm = () => {
  periodForm.training_year = selectedYear.value
  periodForm.training_period = ''
  periodForm.start_date = ''
  periodForm.end_date = ''
  periodForm.description = ''
}

const editPeriod = (period) => {
  editingPeriod.value = period
  periodForm.training_year = period.training_year
  periodForm.training_period = period.training_period
  periodForm.start_date = period.start_date
  periodForm.end_date = period.end_date
  periodForm.description = period.description || ''
  showPeriodModal.value = true
}

const savePeriod = async () => {
  if (savingPeriod.value) return

  // 유효성 검사
  if (new Date(periodForm.start_date) >= new Date(periodForm.end_date)) {
    displayToast('종료일은 시작일보다 늦어야 합니다.', 'error')
    return
  }

  savingPeriod.value = true

  try {
    const url = editingPeriod.value
      ? `/api/phishing-training/periods/${editingPeriod.value.period_id}`
      : '/api/phishing-training/periods'

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

const completePeriod = async (periodId) => {
  if (!confirm('이 기간을 완료 처리하시겠습니까? 미실시 사용자들이 모두 성공으로 처리됩니다.')) {
    return
  }

  try {
    const response = await fetch(`/api/phishing-training/periods/${periodId}/complete`, {
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
    await loadTrainingData() // 테이블 데이터도 새로고침
  } catch (err) {
    console.error('완료 처리 오류:', err)
    displayToast(err.message, 'error')
  }
}

const reopenPeriod = async (periodId) => {
  if (!confirm('이 기간의 완료 상태를 취소하시겠습니까?')) {
    return
  }

  try {
    const response = await fetch(`/api/phishing-training/periods/${periodId}/reopen`, {
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
  } catch (err) {
    console.error('재개 처리 오류:', err)
    displayToast(err.message, 'error')
  }
}

const deletePeriod = async (periodId) => {
  if (!confirm('이 기간을 삭제하시겠습니까?')) {
    return
  }

  try {
    const response = await fetch(`/api/phishing-training/periods/${periodId}`, {
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
    console.error('삭제 오류:', err)
    displayToast(err.message, 'error')
  }
}

const getStatusText = (status) => {
  const statusMap = {
    upcoming: '예정',
    active: '진행중',
    ended: '종료',
    unknown: '알 수 없음',
  }
  return statusMap[status] || status
}

// 기존 메서드들
const loadTrainingData = async () => {
  loading.value = true
  error.value = ''

  try {
    const params = new URLSearchParams({
      year: selectedYear.value,
      ...(selectedPeriod.value && { period: selectedPeriod.value }),
      ...(selectedResult.value && { result: selectedResult.value }),
    })

    const response = await fetch(`/api/phishing-training/records?${params}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })

    if (!response.ok) throw new Error('데이터 조회 실패')

    const data = await response.json()
    trainingData.value = data
    applyFilters()
  } catch (err) {
    console.error('데이터 로딩 오류:', err)
    error.value = err.message
    displayToast('데이터 조회에 실패했습니다.', 'error')
  } finally {
    loading.value = false
  }
}

const searchTrainingData = () => {
  applyFilters()
}

const applyFilters = () => {
  let filtered = [...trainingData.value]

  // 검색어 필터
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    filtered = filtered.filter(
      (record) =>
        record.user_id?.toLowerCase().includes(query) ||
        record.username?.toLowerCase().includes(query) ||
        record.user_email?.toLowerCase().includes(query) ||
        record.department?.toLowerCase().includes(query),
    )
  }

  filteredRecords.value = filtered
  currentPage.value = 1 // 필터 변경 시 첫 페이지로
}

const toggleSelectAll = () => {
  if (selectAll.value) {
    selectedRecords.value = [...paginatedRecords.value]
  } else {
    selectedRecords.value = []
  }
}

const updateSelectAll = () => {
  selectAll.value =
    paginatedRecords.value.length > 0 &&
    selectedRecords.value.length === paginatedRecords.value.length
}

const editRecord = (record) => {
  editingRecord.value = { ...record }

  // datetime-local 형식으로 변환
  if (editingRecord.value.email_sent_time) {
    editingRecord.value.email_sent_time = formatDateTimeForInput(
      editingRecord.value.email_sent_time,
    )
  }
  if (editingRecord.value.action_time) {
    editingRecord.value.action_time = formatDateTimeForInput(editingRecord.value.action_time)
  }

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
    const response = await fetch('/api/phishing-training/update', {
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
    await loadTrainingData()
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
      `${record.username}의 ${record.training_year}년 ${record.training_period === 'first_half' ? '상반기' : '하반기'} 기록을 삭제하시겠습니까?`,
    )
  ) {
    return
  }

  try {
    const response = await fetch('/api/phishing-training/delete', {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({
        user_id: record.user_id,
        training_year: record.training_year,
        training_period: record.training_period,
      }),
    })

    const result = await response.json()

    if (!response.ok) {
      throw new Error(result.error || '삭제 실패')
    }

    displayToast(result.message, 'success')
    await loadTrainingData()
  } catch (err) {
    console.error('기록 삭제 오류:', err)
    displayToast(err.message, 'error')
  }
}

const toggleExceptionStatus = async (record) => {
  // 제외 상태 토글 로직 (기존 예외 관리 시스템과 연동)
  displayToast('제외 설정 기능은 제외 설정 페이지에서 관리할 수 있습니다.', 'info')
}

// 일괄 업로드 관련 메서드
const closeBulkUploadModal = () => {
  showBulkUploadModal.value = false
  selectedFile.value = null
  uploadPreview.value = []
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
    previewFile(file)
  }
}

const handleFileDrop = (event) => {
  event.preventDefault()
  const files = event.dataTransfer.files
  if (files.length > 0) {
    selectedFile.value = files[0]
    previewFile(files[0])
  }
}

const previewFile = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    const csv = e.target.result
    const lines = csv.split('\n')
    const headers = lines[0].split(',').map((h) => h.trim())

    const preview = []
    for (let i = 1; i < Math.min(6, lines.length); i++) {
      if (lines[i].trim()) {
        const values = lines[i].split(',').map((v) => v.trim())
        const row = {}
        headers.forEach((header, index) => {
          row[header] = values[index] || ''
        })
        preview.push(row)
      }
    }

    uploadPreview.value = preview
  }
  reader.readAsText(file)
}

const uploadBulkData = async () => {
  if (!selectedFile.value || uploading.value) return

  uploading.value = true

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const response = await fetch('/api/phishing-training/bulk-upload', {
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

    displayToast(`${result.success_count}건이 성공적으로 업로드되었습니다.`, 'success')

    if (result.error_count > 0) {
      displayToast(`${result.error_count}건의 오류가 있었습니다.`, 'warning')
    }

    closeBulkUploadModal()
    await loadTrainingData()
  } catch (err) {
    console.error('업로드 오류:', err)
    displayToast(err.message, 'error')
  } finally {
    uploading.value = false
  }
}

const downloadTemplate = async () => {
  try {
    const response = await fetch('/api/phishing-training/template/download', {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })

    if (!response.ok) throw new Error('템플릿 다운로드 실패')

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = '모의훈련_업로드_템플릿.csv'
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  } catch (err) {
    console.error('템플릿 다운로드 오류:', err)
    displayToast('템플릿 다운로드에 실패했습니다.', 'error')
  }
}

const exportTrainingData = async () => {
  try {
    const params = new URLSearchParams({
      year: selectedYear.value,
      ...(selectedPeriod.value && { period: selectedPeriod.value }),
      ...(selectedResult.value && { result: selectedResult.value }),
    })

    const response = await fetch(`/api/phishing-training/export?${params}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })

    if (!response.ok) throw new Error('내보내기 실패')

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `모의훈련_데이터_${selectedYear.value}.csv`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)

    displayToast('데이터가 성공적으로 내보내졌습니다.', 'success')
  } catch (err) {
    console.error('내보내기 오류:', err)
    displayToast('데이터 내보내기에 실패했습니다.', 'error')
  }
}

// 유틸리티 함수들
const formatDateTime = (dateTime) => {
  if (!dateTime) return '-'
  return new Date(dateTime).toLocaleString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

const formatDateTimeForInput = (dateTime) => {
  if (!dateTime) return ''
  const date = new Date(dateTime)
  return date.toISOString().slice(0, 19)
}

const formatResponseTime = (minutes) => {
  if (!minutes) return '-'

  if (minutes < 60) {
    return `${minutes}분`
  } else if (minutes < 1440) {
    const hours = Math.floor(minutes / 60)
    const remainingMinutes = minutes % 60
    return `${hours}시간 ${remainingMinutes}분`
  } else {
    const days = Math.floor(minutes / 1440)
    const hours = Math.floor((minutes % 1440) / 60)
    return `${days}일 ${hours}시간`
  }
}

const displayToast = (message, type = 'info') => {
  toastMessage.value = message
  toastType.value = type
  showToast.value = true

  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

// 워처
watch(selectedYear, () => {
  loadPeriodStatus()
})

watch(searchQuery, () => {
  applyFilters()
})

// 라이프사이클
onMounted(() => {
  loadTrainingData()
  loadPeriodStatus()
})
</script>

<style scoped>
@import '../styles/AdminPhishingTrainingManagement.css';
</style>
