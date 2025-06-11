<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import ResultDetailModal from '../components/modals/ResultDetailModal.vue'
import ResultEditModal from '../components/modals/ResultEditModal.vue'
import BatchDetailModal from '../components/modals/BatchDetailModal.vue'

const router = useRouter()

// 반응형 데이터
const activeTab = ref('upload')
const loading = ref(false)
const error = ref('')
const success = ref('')

// 업로드 관련
const uploadCheckType = ref('')
const selectedFile = ref(null)
const isUploading = ref(false)
const isDragOver = ref(false)
const uploadProgress = ref(null)

// 결과 관리 관련
const selectedYear = ref(new Date().getFullYear())
const selectedCheckType = ref('')
const selectedResult = ref('')
const selectedDepartment = ref('')
const checkResults = ref([])
const currentPage = ref(1)
const totalPages = ref(1)
const totalCount = ref(0)
const pageSize = ref(20)

// 통계 관련
const statsYear = ref(new Date().getFullYear())
const statsPeriod = ref('')
const statistics = ref(null)

// 업로드 이력 관련
const historyCheckType = ref('')
const uploadHistory = ref([])

// 모달 관련
const showDetailModal = ref(false)
const showEditModal = ref(false)
const showBatchModal = ref(false)
const selectedCheckId = ref(null)
const selectedBatchId = ref(null)

// 기본 데이터
const availableYears = ref([])
const departments = ref([])

// 점검 유형별 한국어 이름 맵핑
const checkTypeNames = {
  'seal_check': 'PC 봉인씰 확인',
  'malware_scan': '악성코드 전체 검사',
  'file_encryption': '개인정보 파일 암호화'
}

// 컴포넌트 마운트 시 초기화
onMounted(async () => {
  await initializeData()
})

// 초기 데이터 로드
const initializeData = async () => {
  loading.value = true
  try {
    // 연도 목록 생성 (현재년도 기준 ±2년)
    const currentYear = new Date().getFullYear()
    availableYears.value = [currentYear - 2, currentYear - 1, currentYear, currentYear + 1]

    // 부서 목록 로드
    await loadDepartments()

    // 기본 탭 데이터 로드
    if (activeTab.value === 'results') {
      await loadResults()
    } else if (activeTab.value === 'statistics') {
      await loadStatistics()
    } else if (activeTab.value === 'history') {
      await loadUploadHistory()
    }
  } catch (err) {
    error.value = '초기 데이터 로드에 실패했습니다.'
    console.error('초기화 실패:', err)
  } finally {
    loading.value = false
  }
}

// 부서 목록 로드
const loadDepartments = async () => {
  try {
    const response = await fetch('/api/users/departments', {
      credentials: 'include'
    })
    if (response.ok) {
      const data = await response.json()
      departments.value = data.departments || []
    }
  } catch (err) {
    console.error('부서 목록 로드 실패:', err)
  }
}

// 엑셀 업로드 관련 메서드
const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
    validateFile(file)
  }
}

const handleFileDrop = (event) => {
  event.preventDefault()
  isDragOver.value = false

  const files = event.dataTransfer.files
  if (files.length > 0) {
    selectedFile.value = files[0]
    validateFile(files[0])
  }
}

const validateFile = (file) => {
  const maxSize = 16 * 1024 * 1024 // 16MB
  const allowedTypes = [
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-excel',
    'text/csv'
  ]

  if (file.size > maxSize) {
    error.value = '파일 크기가 16MB를 초과할 수 없습니다.'
    selectedFile.value = null
    return false
  }

  if (!allowedTypes.includes(file.type) && !file.name.match(/\.(xlsx|xls|csv)$/i)) {
    error.value = '지원하지 않는 파일 형식입니다. (.xlsx, .xls, .csv만 지원)'
    selectedFile.value = null
    return false
  }

  error.value = ''
  return true
}

const clearSelection = () => {
  selectedFile.value = null
  uploadProgress.value = null
  error.value = ''
  success.value = ''
}

const downloadTemplate = async () => {
  if (!uploadCheckType.value) return

  try {
    const response = await fetch(`/api/manual-check/template/${uploadCheckType.value}`, {
      credentials: 'include'
    })

    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${checkTypeNames[uploadCheckType.value]}_template.csv`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    } else {
      throw new Error('템플릿 다운로드에 실패했습니다.')
    }
  } catch (err) {
    error.value = err.message
  }
}

const uploadFile = async () => {
  if (!selectedFile.value || !uploadCheckType.value) return

  isUploading.value = true
  uploadProgress.value = { message: '파일 업로드 중...' }
  error.value = ''
  success.value = ''

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('check_type', uploadCheckType.value)

    const response = await fetch('/api/manual-check/upload', {
      method: 'POST',
      body: formData,
      credentials: 'include'
    })

    const result = await response.json()

    if (response.ok) {
      uploadProgress.value = {
        message: '업로드가 완료되었습니다.',
        result: result.data
      }
      success.value = '파일이 성공적으로 업로드되었습니다.'

      // 업로드 이력 새로고침
      if (activeTab.value === 'history') {
        await loadUploadHistory()
      }
    } else {
      throw new Error(result.error || '업로드에 실패했습니다.')
    }
  } catch (err) {
    error.value = err.message
    uploadProgress.value = null
  } finally {
    isUploading.value = false
  }
}

// 점검 결과 관련 메서드
const loadResults = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      year: selectedYear.value,
      page: currentPage.value,
      size: pageSize.value
    })

    if (selectedCheckType.value) params.append('check_type', selectedCheckType.value)
    if (selectedResult.value) params.append('result', selectedResult.value)
    if (selectedDepartment.value) params.append('department', selectedDepartment.value)

    const response = await fetch(`/api/manual-check/results?${params}`, {
      credentials: 'include'
    })

    if (response.ok) {
      const data = await response.json()
      checkResults.value = data.data.results || []
      totalCount.value = data.data.total || 0
      totalPages.value = Math.ceil(totalCount.value / pageSize.value)
    } else {
      throw new Error('점검 결과 조회에 실패했습니다.')
    }
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    loadResults()
  }
}

const viewDetail = (checkId) => {
  selectedCheckId.value = checkId
  showDetailModal.value = true
}

const editResult = (checkId) => {
  selectedCheckId.value = checkId
  showEditModal.value = true
}

const deleteResult = async (checkId) => {
  if (!confirm('정말로 이 점검 결과를 삭제하시겠습니까?')) return

  try {
    const response = await fetch(`/api/manual-check/results/${checkId}`, {
      method: 'DELETE',
      credentials: 'include'
    })

    if (response.ok) {
      success.value = '점검 결과가 삭제되었습니다.'
      await loadResults()
    } else {
      const data = await response.json()
      throw new Error(data.error || '삭제에 실패했습니다.')
    }
  } catch (err) {
    error.value = err.message
  }
}

const exportResults = async () => {
  try {
    const params = new URLSearchParams({
      year: selectedYear.value
    })

    if (selectedDepartment.value) params.append('department', selectedDepartment.value)

    const response = await fetch(`/api/manual-check/export/csv?${params}`, {
      credentials: 'include'
    })

    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `manual_check_results_${selectedYear.value}.csv`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
      success.value = 'CSV 파일이 다운로드되었습니다.'
    } else {
      throw new Error('내보내기에 실패했습니다.')
    }
  } catch (err) {
    error.value = err.message
  }
}

const handleResultUpdated = () => {
  showEditModal.value = false
  loadResults()
  success.value = '점검 결과가 수정되었습니다.'
}

// 통계 관련 메서드
const loadStatistics = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      year: statsYear.value
    })

    if (statsPeriod.value) params.append('period', statsPeriod.value)

    const response = await fetch(`/api/manual-check/statistics?${params}`, {
      credentials: 'include'
    })

    if (response.ok) {
      const data = await response.json()
      statistics.value = data.data
    } else {
      throw new Error('통계 조회에 실패했습니다.')
    }
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// 업로드 이력 관련 메서드
const loadUploadHistory = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()

    if (historyCheckType.value) params.append('check_type', historyCheckType.value)

    const response = await fetch(`/api/manual-check/upload/history?${params}`, {
      credentials: 'include'
    })

    if (response.ok) {
      const data = await response.json()
      uploadHistory.value = data.data || []
    } else {
      throw new Error('업로드 이력 조회에 실패했습니다.')
    }
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const viewBatchDetail = (batchId) => {
  selectedBatchId.value = batchId
  showBatchModal.value = true
}

// 유틸리티 함수들
const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatSealStatus = (status) => {
  const statusMap = {
    'normal': '정상',
    'damaged': '훼손',
    'missing': '미부착',
    'replacement_needed': '교체필요'
  }
  return statusMap[status] || status || '-'
}

const formatMalwareStatus = (status) => {
  const statusMap = {
    'clean': '정상',
    'infected': '감염',
    'scan_failed': '검사실패',
    'not_performed': '미실시'
  }
  return statusMap[status] || status || '-'
}

const formatEncryptionStatus = (status) => {
  const statusMap = {
    'fully_encrypted': '완전암호화',
    'not_encrypted': '미암호화',
    'partially_encrypted': '부분암호화',
    'not_applicable': '해당없음'
  }
  return statusMap[status] || status || '-'
}

const formatOverallResult = (result) => {
  const resultMap = {
    'pass': '통과',
    'fail': '실패',
    'partial': '부분통과'
  }
  return resultMap[result] || result || '-'
}

const formatUploadStatus = (status) => {
  const statusMap = {
    'processing': '처리중',
    'completed': '완료',
    'failed': '실패'
  }
  return statusMap[status] || status || '-'
}

const getCheckTypeKorean = (checkType) => {
  return checkTypeNames[checkType] || checkType
}

const getStatusClass = (status) => {
  if (!status) return ''

  const successStatuses = ['normal', 'clean', 'fully_encrypted']
  const warningStatuses = ['partially_encrypted']
  const errorStatuses = ['damaged', 'missing', 'infected', 'not_encrypted']

  if (successStatuses.includes(status)) return 'success'
  if (warningStatuses.includes(status)) return 'warning'
  if (errorStatuses.includes(status)) return 'error'

  return ''
}

const getPercentage = (value, total) => {
  if (!total || total === 0) return 0
  return Math.round((value / total) * 100)
}
</script>

<template>
  <div class="admin-manual-check">
    <div class="admin-header">
      <h1>수시 점검 관리</h1>
      <div class="admin-nav">
        <RouterLink to="/admin/training" class="nav-item">모의훈련 관리</RouterLink>
        <RouterLink to="/admin/manual-check" class="nav-item active">점검 관리</RouterLink>
        <RouterLink to="/admin/exceptions" class="nav-item">제외 설정</RouterLink>
      </div>
    </div>

    <!-- 알림 메시지 -->
    <div v-if="error" class="alert alert-error">
      {{ error }}
      <button @click="error = ''" class="alert-close">&times;</button>
    </div>

    <div v-if="success" class="alert alert-success">
      {{ success }}
      <button @click="success = ''" class="alert-close">&times;</button>
    </div>

    <div class="management-content">
      <!-- 탭 메뉴 -->
      <div class="tab-menu">
        <button
          class="tab-button"
          :class="{ active: activeTab === 'upload' }"
          @click="activeTab = 'upload'"
        >
          엑셀 업로드
        </button>
        <button
          class="tab-button"
          :class="{ active: activeTab === 'results' }"
          @click="activeTab = 'results'; loadResults()"
        >
          점검 결과
        </button>
        <button
          class="tab-button"
          :class="{ active: activeTab === 'statistics' }"
          @click="activeTab = 'statistics'; loadStatistics()"
        >
          통계 현황
        </button>
        <button
          class="tab-button"
          :class="{ active: activeTab === 'history' }"
          @click="activeTab = 'history'; loadUploadHistory()"
        >
          업로드 이력
        </button>
      </div>

      <!-- 엑셀 업로드 탭 -->
      <div v-if="activeTab === 'upload'" class="tab-content">
        <div class="upload-section">
          <h2>엑셀 파일 업로드</h2>

          <div class="upload-options">
            <div class="check-type-selector">
              <label>점검 유형 선택:</label>
              <select v-model="uploadCheckType">
                <option value="">점검 유형을 선택하세요</option>
                <option value="seal_check">PC 봉인씰 확인</option>
                <option value="malware_scan">악성코드 전체 검사</option>
                <option value="file_encryption">개인정보 파일 암호화</option>
              </select>
            </div>

            <div class="template-download">
              <button
                class="btn-secondary"
                @click="downloadTemplate"
                :disabled="!uploadCheckType"
              >
                템플릿 다운로드
              </button>
            </div>
          </div>

          <div class="file-upload-area" :class="{ 'drag-over': isDragOver }">
            <input
              type="file"
              ref="fileInput"
              @change="handleFileSelect"
              accept=".xlsx,.xls,.csv"
              style="display: none"
            >

            <div
              class="drop-zone"
              @drop="handleFileDrop"
              @dragover.prevent="isDragOver = true"
              @dragleave="isDragOver = false"
              @click="$refs.fileInput.click()"
            >
              <div class="drop-zone-content">
                <div class="upload-icon">📁</div>
                <p v-if="!selectedFile">파일을 드래그하거나 클릭해서 선택하세요</p>
                <p v-else class="selected-file">{{ selectedFile.name }}</p>
                <small>지원 형식: .xlsx, .xls, .csv (최대 16MB)</small>
              </div>
            </div>
          </div>

          <div class="upload-actions">
            <button
              class="btn-primary"
              @click="uploadFile"
              :disabled="!selectedFile || !uploadCheckType || isUploading"
            >
              <span v-if="isUploading">업로드 중...</span>
              <span v-else>업로드 시작</span>
            </button>
            <button
              class="btn-secondary"
              @click="clearSelection"
              :disabled="isUploading"
            >
              선택 해제
            </button>
          </div>

          <!-- 업로드 진행 상태 -->
          <div v-if="uploadProgress" class="upload-progress">
            <div class="progress-info">
              <h3>업로드 진행 상황</h3>
              <p>{{ uploadProgress.message }}</p>
            </div>
            <div v-if="uploadProgress.result" class="upload-result">
              <div class="result-summary">
                <div class="result-item success">
                  <span>성공:</span>
                  <strong>{{ uploadProgress.result.success_records }}건</strong>
                </div>
                <div class="result-item error" v-if="uploadProgress.result.failed_records > 0">
                  <span>실패:</span>
                  <strong>{{ uploadProgress.result.failed_records }}건</strong>
                </div>
                <div class="result-item total">
                  <span>전체:</span>
                  <strong>{{ uploadProgress.result.total_records }}건</strong>
                </div>
              </div>

              <div v-if="uploadProgress.result.errors && uploadProgress.result.errors.length > 0" class="error-details">
                <h4>오류 상세:</h4>
                <ul>
                  <li v-for="error in uploadProgress.result.errors.slice(0, 5)" :key="error">
                    {{ error }}
                  </li>
                  <li v-if="uploadProgress.result.errors.length > 5">
                    ... 외 {{ uploadProgress.result.errors.length - 5 }}개 오류
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 점검 결과 탭 -->
      <div v-if="activeTab === 'results'" class="tab-content">
        <div class="results-section">
          <div class="results-header">
            <h2>점검 결과 관리</h2>
            <div class="results-actions">
              <button class="btn-secondary" @click="exportResults">
                CSV 내보내기
              </button>
              <button class="btn-primary" @click="loadResults">
                새로고침
              </button>
            </div>
          </div>

          <!-- 필터 -->
          <div class="filter-section">
            <div class="filter-group">
              <label>연도:</label>
              <select v-model="selectedYear" @change="loadResults">
                <option v-for="year in availableYears" :key="year" :value="year">{{ year }}년</option>
              </select>
            </div>

            <div class="filter-group">
              <label>점검 유형:</label>
              <select v-model="selectedCheckType" @change="loadResults">
                <option value="">전체</option>
                <option value="seal_check">PC 봉인씰 확인</option>
                <option value="malware_scan">악성코드 전체 검사</option>
                <option value="file_encryption">개인정보 파일 암호화</option>
              </select>
            </div>

            <div class="filter-group">
              <label>결과:</label>
              <select v-model="selectedResult" @change="loadResults">
                <option value="">전체</option>
                <option value="pass">통과</option>
                <option value="fail">실패</option>
                <option value="partial">부분통과</option>
              </select>
            </div>

            <div class="filter-group">
              <label>부서:</label>
              <select v-model="selectedDepartment" @change="loadResults">
                <option value="">전체</option>
                <option v-for="dept in departments" :key="dept" :value="dept">{{ dept }}</option>
              </select>
            </div>
          </div>

          <!-- 결과 테이블 -->
          <div class="results-table-container">
            <div v-if="loading" class="loading">데이터를 불러오는 중...</div>

            <table v-else class="results-table">
              <thead>
                <tr>
                  <th>점검일시</th>
                  <th>사용자</th>
                  <th>부서</th>
                  <th>점검자</th>
                  <th>봉인씰</th>
                  <th>악성코드</th>
                  <th>암호화</th>
                  <th>종합결과</th>
                  <th>점수</th>
                  <th>관리</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="result in checkResults" :key="result.check_id">
                  <td>{{ formatDateTime(result.check_date) }}</td>
                  <td>{{ result.username }}</td>
                  <td>{{ result.department }}</td>
                  <td>{{ result.checker_name }}</td>
                  <td>
                    <span class="status-badge" :class="getStatusClass(result.seal_status)">
                      {{ formatSealStatus(result.seal_status) }}
                    </span>
                  </td>
                  <td>
                    <span class="status-badge" :class="getStatusClass(result.malware_scan_result)">
                      {{ formatMalwareStatus(result.malware_scan_result) }}
                    </span>
                  </td>
                  <td>
                    <span class="status-badge" :class="getStatusClass(result.encryption_status)">
                      {{ formatEncryptionStatus(result.encryption_status) }}
                    </span>
                  </td>
                  <td>
                    <span class="result-badge" :class="result.overall_result">
                      {{ formatOverallResult(result.overall_result) }}
                    </span>
                  </td>
                  <td class="score">{{ result.total_score }}</td>
                  <td class="actions">
                    <button class="btn-small" @click="viewDetail(result.check_id)">
                      상세
                    </button>
                    <button class="btn-small btn-edit" @click="editResult(result.check_id)">
                      수정
                    </button>
                    <button class="btn-small btn-delete" @click="deleteResult(result.check_id)">
                      삭제
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>

            <div v-if="checkResults.length === 0 && !loading" class="no-data">
              점검 결과가 없습니다.
            </div>
          </div>

          <!-- 페이지네이션 -->
          <div class="pagination" v-if="totalPages > 1">
            <button
              @click="changePage(currentPage - 1)"
              :disabled="currentPage <= 1"
              class="btn-page"
            >
              이전
            </button>

            <span class="page-info">
              {{ currentPage }} / {{ totalPages }} 페이지 (총 {{ totalCount }}건)
            </span>

            <button
              @click="changePage(currentPage + 1)"
              :disabled="currentPage >= totalPages"
              class="btn-page"
            >
              다음
            </button>
          </div>
        </div>
      </div>

      <!-- 통계 현황 탭 -->
      <div v-if="activeTab === 'statistics'" class="tab-content">
        <div class="statistics-section">
          <h2>점검 통계 현황</h2>

          <div class="stats-filters">
            <div class="filter-group">
              <label>연도:</label>
              <select v-model="statsYear" @change="loadStatistics">
                <option v-for="year in availableYears" :key="year" :value="year">{{ year }}년</option>
              </select>
            </div>
            <div class="filter-group">
              <label>기간:</label>
              <select v-model="statsPeriod" @change="loadStatistics">
                <option value="">전체</option>
                <option value="Q1">1분기</option>
                <option value="Q2">2분기</option>
                <option value="Q3">3분기</option>
                <option value="Q4">4분기</option>
              </select>
            </div>
          </div>

          <div v-if="loading" class="loading">통계를 불러오는 중...</div>

          <div v-else-if="statistics" class="stats-container">
            <!-- 전체 통계 -->
            <div class="stats-overview">
              <div class="stat-card">
                <h3>전체 점검</h3>
                <div class="stat-number">{{ statistics.basic_stats.total_checks }}</div>
              </div>
              <div class="stat-card success">
                <h3>통과</h3>
                <div class="stat-number">{{ statistics.basic_stats.pass_count }}</div>
                <div class="stat-percent">
                  {{ getPercentage(statistics.basic_stats.pass_count, statistics.basic_stats.total_checks) }}%
                </div>
              </div>
              <div class="stat-card warning">
                <h3>부분통과</h3>
                <div class="stat-number">{{ statistics.basic_stats.partial_count }}</div>
                <div class="stat-percent">
                  {{ getPercentage(statistics.basic_stats.partial_count, statistics.basic_stats.total_checks) }}%
                </div>
              </div>
              <div class="stat-card error">
                <h3>실패</h3>
                <div class="stat-number">{{ statistics.basic_stats.fail_count }}</div>
                <div class="stat-percent">
                  {{ getPercentage(statistics.basic_stats.fail_count, statistics.basic_stats.total_checks) }}%
                </div>
              </div>
            </div>

            <!-- 부서별 통계 -->
            <div class="department-stats">
              <h3>부서별 현황</h3>
              <div class="dept-stats-table">
                <table>
                  <thead>
                    <tr>
                      <th>부서</th>
                      <th>전체</th>
                      <th>통과</th>
                      <th>통과율</th>
                      <th>평균점수</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="dept in statistics.department_stats" :key="dept.department">
                      <td>{{ dept.department }}</td>
                      <td>{{ dept.dept_total }}</td>
                      <td>{{ dept.dept_pass }}</td>
                      <td class="percentage">
                        {{ getPercentage(dept.dept_pass, dept.dept_total) }}%
                      </td>
                      <td class="score">{{ dept.dept_avg_score?.toFixed(1) || '0.0' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div v-else class="no-data">
            통계 데이터가 없습니다.
          </div>
        </div>
      </div>

      <!-- 업로드 이력 탭 -->
      <div v-if="activeTab === 'history'" class="tab-content">
        <div class="history-section">
          <h2>업로드 이력</h2>

          <div class="history-filters">
            <div class="filter-group">
              <label>점검 유형:</label>
              <select v-model="historyCheckType" @change="loadUploadHistory">
                <option value="">전체</option>
                <option value="seal_check">PC 봉인씰 확인</option>
                <option value="malware_scan">악성코드 전체 검사</option>
                <option value="file_encryption">개인정보 파일 암호화</option>
              </select>
            </div>
          </div>

          <div class="history-table-container">
            <div v-if="loading" class="loading">이력을 불러오는 중...</div>

            <table v-else class="history-table">
              <thead>
                <tr>
                  <th>업로드일시</th>
                  <th>점검유형</th>
                  <th>파일명</th>
                  <th>업로드자</th>
                  <th>전체</th>
                  <th>성공</th>
                  <th>실패</th>
                  <th>상태</th>
                  <th>관리</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="history in uploadHistory" :key="history.batch_id">
                  <td>{{ formatDateTime(history.upload_date) }}</td>
                  <td>{{ getCheckTypeKorean(history.check_type) }}</td>
                  <td>{{ history.filename }}</td>
                  <td>{{ history.uploaded_by }}</td>
                  <td>{{ history.total_records }}</td>
                  <td class="success">{{ history.success_records }}</td>
                  <td class="error">{{ history.failed_records }}</td>
                  <td>
                    <span class="status-badge" :class="history.status">
                      {{ formatUploadStatus(history.status) }}
                    </span>
                  </td>
                  <td class="actions">
                    <button class="btn-small" @click="viewBatchDetail(history.batch_id)">
                      상세보기
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>

            <div v-if="uploadHistory.length === 0 && !loading" class="no-data">
              업로드 이력이 없습니다.
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 모달들 -->
    <ResultDetailModal
      v-if="showDetailModal"
      :check-id="selectedCheckId"
      @close="showDetailModal = false"
    />

    <ResultEditModal
      v-if="showEditModal"
      :check-id="selectedCheckId"
      @close="showEditModal = false"
      @updated="handleResultUpdated"
    />

    <BatchDetailModal
      v-if="showBatchModal"
      :batch-id="selectedBatchId"
      @close="showBatchModal = false"
    />
  </div>
</template>

<style scoped>
.admin-manual-check {
  min-height: 100vh;
  background-color: #f8fafc;
}

.admin-header {
  background: white;
  border-bottom: 1px solid #e2e8f0;
  padding: 1.5rem 2rem;
  margin-bottom: 2rem;
}

.admin-header h1 {
  color: #1a202c;
  font-size: 1.875rem;
  font-weight: 700;
  margin: 0 0 1rem 0;
}

.admin-nav {
  display: flex;
  gap: 0.5rem;
}

.nav-item {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  text-decoration: none;
  color: #64748b;
  font-weight: 500;
  transition: all 0.2s;
}

.nav-item:hover {
  background-color: #f1f5f9;
  color: #334155;
}

.nav-item.active {
  background-color: #3b82f6;
  color: white;
}

/* 알림 메시지 */
.alert {
  margin: 0 2rem 1rem 2rem;
  padding: 1rem;
  border-radius: 0.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.alert-error {
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
}

.alert-success {
  background-color: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #16a34a;
}

.alert-close {
  background: none;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  color: inherit;
  opacity: 0.7;
}

.alert-close:hover {
  opacity: 1;
}

.management-content {
  padding: 0 2rem;
}

/* 탭 메뉴 */
.tab-menu {
  display: flex;
  background: white;
  border-radius: 0.5rem;
  padding: 0.25rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.tab-button {
  flex: 1;
  padding: 0.75rem 1rem;
  border: none;
  background: none;
  border-radius: 0.375rem;
  font-weight: 500;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-button:hover {
  background-color: #f1f5f9;
  color: #334155;
}

.tab-button.active {
  background-color: #3b82f6;
  color: white;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* 탭 컨텐츠 */
.tab-content {
  background: white;
  border-radius: 0.5rem;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.tab-content h2 {
  color: #1a202c;
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
}

/* 엑셀 업로드 스타일 */
.upload-options {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
  align-items: end;
}

.check-type-selector label,
.template-download {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
}

.check-type-selector select {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  min-width: 200px;
}

.file-upload-area {
  margin-bottom: 2rem;
}

.drop-zone {
  border: 2px dashed #d1d5db;
  border-radius: 0.5rem;
  padding: 3rem 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background-color: #fafafa;
}

.drop-zone:hover,
.file-upload-area.drag-over .drop-zone {
  border-color: #3b82f6;
  background-color: #eff6ff;
}

.drop-zone-content {
  pointer-events: none;
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.selected-file {
  color: #3b82f6;
  font-weight: 500;
}

.upload-actions {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.upload-progress {
  background-color: #f8fafc;
  border-radius: 0.5rem;
  padding: 1.5rem;
  border: 1px solid #e2e8f0;
}

.progress-info h3 {
  color: #1a202c;
  font-size: 1.125rem;
  margin-bottom: 0.5rem;
}

.upload-result {
  margin-top: 1rem;
}

.result-summary {
  display: flex;
  gap: 2rem;
  margin-bottom: 1rem;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.result-item.success strong {
  color: #16a34a;
}

.result-item.error strong {
  color: #dc2626;
}

.result-item.total strong {
  color: #374151;
}

.error-details {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #fef2f2;
  border-radius: 0.375rem;
  border: 1px solid #fecaca;
}

.error-details h4 {
  color: #dc2626;
  margin-bottom: 0.5rem;
}

.error-details ul {
  margin: 0;
  padding-left: 1.5rem;
}

.error-details li {
  color: #7f1d1d;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

/* 점검 결과 스타일 */
.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.results-actions {
  display: flex;
  gap: 1rem;
}

.filter-section {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  min-width: 150px;
}

.filter-group label {
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.filter-group select {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.results-table-container {
  overflow-x: auto;
  margin-bottom: 2rem;
}

.results-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.results-table th,
.results-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.results-table th {
  background-color: #f9fafb;
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
}

.results-table td {
  font-size: 0.875rem;
  color: #6b7280;
}

.status-badge,
.result-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.status-badge.success,
.result-badge.pass {
  background-color: #d1fae5;
  color: #065f46;
}

.status-badge.warning,
.result-badge.partial {
  background-color: #fef3c7;
  color: #92400e;
}

.status-badge.error,
.result-badge.fail {
  background-color: #fee2e2;
  color: #991b1b;
}

.status-badge.processing {
  background-color: #dbeafe;
  color: #1e40af;
}

.status-badge.completed {
  background-color: #d1fae5;
  color: #065f46;
}

.status-badge.failed {
  background-color: #fee2e2;
  color: #991b1b;
}

.score {
  font-weight: 600;
  color: #374151;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}

.btn-page {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-page:hover:not(:disabled) {
  background-color: #f9fafb;
}

.btn-page:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 0.875rem;
  color: #6b7280;
}

/* 통계 스타일 */
.stats-filters {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.stat-card h3 {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.stat-percent {
  font-size: 0.875rem;
  font-weight: 500;
}

.stat-card.success .stat-number,
.stat-card.success .stat-percent {
  color: #16a34a;
}

.stat-card.warning .stat-number,
.stat-card.warning .stat-percent {
  color: #d97706;
}

.stat-card.error .stat-number,
.stat-card.error .stat-percent {
  color: #dc2626;
}

.department-stats h3 {
  color: #1a202c;
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.dept-stats-table table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 0.5rem;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.dept-stats-table th,
.dept-stats-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.dept-stats-table th {
  background-color: #f9fafb;
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
}

.dept-stats-table td {
  font-size: 0.875rem;
  color: #6b7280;
}

.percentage {
  font-weight: 600;
}

/* 업로드 이력 스타일 */
.history-filters {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
}

.history-table-container {
  overflow-x: auto;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.history-table th,
.history-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.history-table th {
  background-color: #f9fafb;
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
}

.history-table td {
  font-size: 0.875rem;
  color: #6b7280;
}

.history-table .success {
  color: #16a34a;
  font-weight: 600;
}

.history-table .error {
  color: #dc2626;
  font-weight: 600;
}

/* 공통 버튼 스타일 */
.btn-primary {
  background-color: #3b82f6;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #f8fafc;
  color: #374151;
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #f1f5f9;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-small {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-small:hover {
  background-color: #f9fafb;
}

.btn-edit {
  color: #3b82f6;
  border-color: #3b82f6;
}

.btn-edit:hover {
  background-color: #eff6ff;
}

.btn-delete {
  color: #dc2626;
  border-color: #dc2626;
}

.btn-delete:hover {
  background-color: #fef2f2;
}

/* 로딩 및 데이터 없음 스타일 */
.loading {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
  font-style: italic;
}

.no-data {
  text-align: center;
  padding: 3rem;
  color: #9ca3af;
  font-style: italic;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .admin-header {
    padding: 1rem;
  }

  .management-content {
    padding: 0 1rem;
  }

  .tab-content {
    padding: 1rem;
  }

  .upload-options,
  .filter-section,
  .stats-filters,
  .history-filters {
    flex-direction: column;
    gap: 1rem;
  }

  .results-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .results-actions {
    justify-content: center;
  }

  .stats-overview {
    grid-template-columns: 1fr;
  }

  .result-summary {
    flex-direction: column;
    gap: 0.5rem;
  }

  .results-table,
  .history-table,
  .dept-stats-table table {
    font-size: 0.75rem;
  }

  .results-table th,
  .results-table td,
  .history-table th,
  .history-table td,
  .dept-stats-table th,
  .dept-stats-table td {
    padding: 0.5rem 0.25rem;
  }

  .actions {
    flex-direction: column;
    gap: 0.25rem;
  }

  .btn-small {
    font-size: 0.625rem;
    padding: 0.125rem 0.25rem;
  }
}

@media (max-width: 480px) {
  .admin-header h1 {
    font-size: 1.5rem;
  }

  .tab-menu {
    flex-direction: column;
  }

  .pagination {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>
