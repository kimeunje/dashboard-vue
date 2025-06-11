<template>
  <div class="manual-check-management">
    <!-- 헤더 -->
    <div class="admin-header">
      <h1>수시 점검 관리</h1>
      <div class="admin-nav">
        <button
          @click="activeTab = 'results'"
          :class="['nav-item', { active: activeTab === 'results' }]"
        >
          점검 결과 관리
        </button>
        <button
          @click="activeTab = 'statistics'"
          :class="['nav-item', { active: activeTab === 'statistics' }]"
        >
          점검 통계
        </button>
      </div>
    </div>

    <!-- 점검 결과 관리 탭 -->
    <div v-if="activeTab === 'results'" class="tab-content">
      <!-- 필터 및 검색 -->
      <div class="filter-section">
        <div class="filter-group">
          <label>연도:</label>
          <select v-model="selectedYear" @change="loadCheckResults">
            <option v-for="year in availableYears" :key="year" :value="year">{{ year }}년</option>
          </select>
        </div>

        <div class="filter-group">
          <label>기간:</label>
          <select v-model="selectedPeriod" @change="loadCheckResults">
            <option value="">전체</option>
            <option value="first_half">상반기</option>
            <option value="second_half">하반기</option>
          </select>
        </div>

        <div class="filter-group">
          <label>결과:</label>
          <select v-model="selectedResult" @change="loadCheckResults">
            <option value="">전체</option>
            <option value="pass">통과</option>
            <option value="fail">실패</option>
            <option value="partial">부분통과</option>
          </select>
        </div>

        <div class="search-group">
          <input
            type="text"
            v-model="searchQuery"
            @input="searchCheckResults"
            placeholder="사용자명, ID 또는 부서 검색..."
            class="search-input"
          />
        </div>
      </div>

      <!-- 액션 버튼 -->
      <div class="action-section">
        <button @click="downloadTemplate" class="secondary-button">📄 템플릿 다운로드</button>
        <button @click="openBulkUploadModal" class="primary-button">📤 일괄 업로드</button>
        <button @click="exportResults" class="secondary-button">📊 결과 내보내기</button>
      </div>

      <!-- 로딩 상태 -->
      <div v-if="loading" class="loading-spinner">
        <div class="spinner"></div>
        <p>데이터를 불러오는 중...</p>
      </div>

      <!-- 결과 테이블 -->
      <div v-else class="results-table-container">
        <table class="results-table">
          <thead>
            <tr>
              <th>사용자ID</th>
              <th>사용자명</th>
              <th>부서</th>
              <th>점검일시</th>
              <th>봉인씰</th>
              <th>악성코드</th>
              <th>암호화</th>
              <th>종합결과</th>
              <th>총점</th>
              <th>액션</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="checkResults.length === 0">
              <td colspan="10" class="no-data">검색 결과가 없습니다.</td>
            </tr>
            <tr v-for="result in checkResults" :key="result.check_id">
              <td>{{ result.user_id }}</td>
              <td>{{ result.username }}</td>
              <td>{{ result.department }}</td>
              <td>{{ formatDateTime(result.check_date) }}</td>
              <td>
                <span :class="['status-badge', getStatusClass(result.seal_status)]">
                  {{ getSealStatusText(result.seal_status) }}
                </span>
              </td>
              <td>
                <span :class="['status-badge', getStatusClass(result.malware_scan_result)]">
                  {{ getMalwareStatusText(result.malware_scan_result) }}
                </span>
              </td>
              <td>
                <span :class="['status-badge', getStatusClass(result.encryption_status)]">
                  {{ getEncryptionStatusText(result.encryption_status) }}
                </span>
              </td>
              <td>
                <span :class="['result-badge', result.overall_result]">
                  {{ getResultText(result.overall_result) }}
                </span>
              </td>
              <!-- <td class="score-cell">{{ result.total_score?.toFixed(1) || '-' }}</td> -->
              <td>
                <div class="action-buttons">
                  <button @click="editResult(result)" class="edit-btn" title="수정">✏️</button>
                  <button @click="deleteResult(result.check_id)" class="delete-btn" title="삭제">
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
        <button @click="changePage(currentPage - 1)" :disabled="currentPage === 1" class="page-btn">
          이전
        </button>

        <span class="page-info">
          {{ currentPage }} / {{ totalPages }} (총 {{ totalCount }}건)
        </span>

        <button
          @click="changePage(currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="page-btn"
        >
          다음
        </button>
      </div>
    </div>

    <!-- 점검 통계 탭 -->
    <div v-if="activeTab === 'statistics'" class="tab-content">
      <div class="statistics-section">
        <h3>📊 점검 통계</h3>

        <!-- 통계 필터 -->
        <div class="stats-filter">
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
              <option value="first_half">상반기</option>
              <option value="second_half">하반기</option>
            </select>
          </div>
        </div>

        <!-- 전체 통계 카드 -->
        <div class="stats-cards" v-if="statistics.basic_stats">
          <div class="stat-card">
            <div class="stat-value">{{ statistics.basic_stats.total_checks }}</div>
            <div class="stat-label">총 점검 건수</div>
          </div>
          <div class="stat-card success">
            <div class="stat-value">{{ statistics.basic_stats.pass_count }}</div>
            <div class="stat-label">통과</div>
          </div>
          <div class="stat-card warning">
            <div class="stat-value">{{ statistics.basic_stats.partial_count }}</div>
            <div class="stat-label">부분통과</div>
          </div>
          <div class="stat-card danger">
            <div class="stat-value">{{ statistics.basic_stats.fail_count }}</div>
            <div class="stat-label">실패</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ statistics.basic_stats.avg_score?.toFixed(1) }}점</div>
            <div class="stat-label">평균 점수</div>
          </div>
        </div>

        <!-- 부서별 통계 -->
        <div
          class="department-stats"
          v-if="statistics.department_stats && statistics.department_stats.length > 0"
        >
          <h4>부서별 통계</h4>
          <div class="stats-table">
            <table>
              <thead>
                <tr>
                  <th>부서</th>
                  <th>총 점검</th>
                  <th>통과</th>
                  <th>통과율</th>
                  <th>평균 점수</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="dept in statistics.department_stats" :key="dept.department">
                  <td>{{ dept.department }}</td>
                  <td>{{ dept.dept_total }}</td>
                  <td>{{ dept.dept_pass }}</td>
                  <td>{{ ((dept.dept_pass / dept.dept_total) * 100).toFixed(1) }}%</td>
                  <td>{{ dept.dept_avg_score?.toFixed(1) }}점</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- 일괄 업로드 모달 -->
    <BulkUploadModal
      v-if="showBulkUploadModal"
      @close="closeBulkUploadModal"
      @upload-success="handleUploadSuccess"
    />

    <!-- 토스트 메시지 -->
    <div v-if="toastMessage" :class="['toast', toastType]">
      {{ toastMessage }}
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { manualCheckService } from '../services/manualCheckService.js'
import BulkUploadModal from './BulkUploadModal.vue'

export default {
  name: 'ManualCheckManagement',
  components: {
    BulkUploadModal,
  },
  setup() {
    // 반응형 데이터
    const activeTab = ref('results')
    const loading = ref(false)

    // 필터 및 검색
    const selectedYear = ref(new Date().getFullYear())
    const selectedPeriod = ref('')
    const selectedResult = ref('')
    const searchQuery = ref('')

    // 통계용 필터
    const statsYear = ref(new Date().getFullYear())
    const statsPeriod = ref('')

    // 데이터
    const checkResults = ref([])
    const statistics = ref({})

    // 페이지네이션
    const currentPage = ref(1)
    const pageSize = ref(20)
    const totalCount = ref(0)

    // 모달 상태
    const showBulkUploadModal = ref(false)

    // 토스트 메시지
    const toastMessage = ref('')
    const toastType = ref('info')

    // 연도 목록
    const availableYears = computed(() => {
      const currentYear = new Date().getFullYear()
      return Array.from({ length: 5 }, (_, i) => currentYear - i)
    })

    // 총 페이지 수
    const totalPages = computed(() => {
      return Math.ceil(totalCount.value / pageSize.value)
    })

    // 토스트 메시지 표시
    const showToast = (message, type = 'info') => {
      toastMessage.value = message
      toastType.value = type
      setTimeout(() => {
        toastMessage.value = ''
      }, 3000)
    }

    // 점검 결과 로드
    const loadCheckResults = async () => {
      try {
        loading.value = true
        const params = {
          year: selectedYear.value,
          page: currentPage.value,
          size: pageSize.value,
        }

        if (selectedPeriod.value) params.period = selectedPeriod.value
        if (selectedResult.value) params.result = selectedResult.value
        if (searchQuery.value) params.search = searchQuery.value

        const data = await manualCheckService.getResults(params)
        checkResults.value = data.results || []
        totalCount.value = data.total || 0
      } catch (error) {
        console.error('점검 결과 로드 실패:', error)
        showToast('결과를 불러오는데 실패했습니다.', 'error')
      } finally {
        loading.value = false
      }
    }

    // 검색 (디바운싱)
    let searchTimeout
    const searchCheckResults = () => {
      clearTimeout(searchTimeout)
      searchTimeout = setTimeout(() => {
        currentPage.value = 1
        loadCheckResults()
      }, 300)
    }

    // 템플릿 다운로드
    const downloadTemplate = async () => {
      try {
        const blob = await manualCheckService.downloadTemplate()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'manual_check_template.csv'
        a.click()
        window.URL.revokeObjectURL(url)
        showToast('템플릿이 다운로드되었습니다.', 'success')
      } catch (error) {
        console.error('템플릿 다운로드 실패:', error)
        showToast('템플릿 다운로드에 실패했습니다.', 'error')
      }
    }

    // 일괄 업로드 모달
    const openBulkUploadModal = () => {
      showBulkUploadModal.value = true
    }

    const closeBulkUploadModal = () => {
      showBulkUploadModal.value = false
    }

    const handleUploadSuccess = (result) => {
      showToast(
        `업로드 완료: 성공 ${result.successful_records}건, 실패 ${result.failed_records}건`,
        result.failed_records > 0 ? 'warning' : 'success',
      )
      closeBulkUploadModal()
      loadCheckResults()
    }

    // 결과 수정
    const editResult = (result) => {
      // 간단한 프롬프트로 구현 (나중에 모달로 개선 가능)
      const newNotes = prompt('비고를 수정하세요:', result.notes || '')
      if (newNotes !== null) {
        updateResult(result.check_id, { ...result, notes: newNotes })
      }
    }

    const updateResult = async (checkId, data) => {
      try {
        await manualCheckService.updateResult(checkId, data)
        showToast('결과가 수정되었습니다.', 'success')
        loadCheckResults()
      } catch (error) {
        console.error('결과 수정 실패:', error)
        showToast('결과 수정에 실패했습니다.', 'error')
      }
    }

    // 결과 삭제
    const deleteResult = async (checkId) => {
      if (!confirm('정말로 이 결과를 삭제하시겠습니까?')) return

      try {
        await manualCheckService.deleteResult(checkId)
        showToast('결과가 삭제되었습니다.', 'success')
        loadCheckResults()
      } catch (error) {
        console.error('결과 삭제 실패:', error)
        showToast('결과 삭제에 실패했습니다.', 'error')
      }
    }

    // 통계 로드
    const loadStatistics = async () => {
      try {
        const params = { year: statsYear.value }
        if (statsPeriod.value) params.period = statsPeriod.value

        const data = await manualCheckService.getStatistics(params)
        statistics.value = data
      } catch (error) {
        console.error('통계 로드 실패:', error)
        showToast('통계를 불러오는데 실패했습니다.', 'error')
      }
    }

    // 결과 내보내기
    const exportResults = async () => {
      try {
        const params = { year: selectedYear.value }
        if (selectedPeriod.value) params.period = selectedPeriod.value

        const blob = await manualCheckService.exportResults(params)
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `manual_check_results_${selectedYear.value}_${selectedPeriod.value || 'all'}.csv`
        a.click()
        window.URL.revokeObjectURL(url)
        showToast('결과가 내보내기되었습니다.', 'success')
      } catch (error) {
        console.error('내보내기 실패:', error)
        showToast('내보내기에 실패했습니다.', 'error')
      }
    }

    // 페이지 변경
    const changePage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        loadCheckResults()
      }
    }

    // 유틸리티 함수들
    const getSealStatusText = (status) => {
      const statusTexts = {
        normal: '정상',
        damaged: '손상',
        missing: '미부착',
        replacement_needed: '교체필요',
      }
      return statusTexts[status] || status || '-'
    }

    const getMalwareStatusText = (status) => {
      const statusTexts = {
        clean: '정상',
        infected: '감염발견',
        scan_failed: '검사실패',
        not_performed: '미실시',
      }
      return statusTexts[status] || status || '-'
    }

    const getEncryptionStatusText = (status) => {
      const statusTexts = {
        fully_encrypted: '완전암호화',
        not_encrypted: '미암호화',
        partially_encrypted: '부분암호화',
        not_applicable: '해당없음',
      }
      return statusTexts[status] || status || '-'
    }

    const getResultText = (result) => {
      const resultTexts = {
        pass: '통과',
        fail: '실패',
        partial: '부분통과',
      }
      return resultTexts[result] || result || '-'
    }

    const getStatusClass = (status) => {
      if (!status) return 'unknown'

      const successStatuses = ['normal', 'clean', 'fully_encrypted']
      const warningStatuses = [
        'damaged',
        'scan_failed',
        'partially_encrypted',
        'replacement_needed',
      ]
      const dangerStatuses = ['missing', 'infected', 'not_encrypted']

      if (successStatuses.includes(status)) return 'success'
      if (warningStatuses.includes(status)) return 'warning'
      if (dangerStatuses.includes(status)) return 'danger'
      return 'info'
    }

    const formatDateTime = (dateString) => {
      if (!dateString) return '-'
      try {
        return new Date(dateString).toLocaleString('ko-KR', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
        })
      } catch {
        return dateString
      }
    }

    // 라이프사이클
    onMounted(() => {
      loadCheckResults()
      loadStatistics()
    })

    return {
      // 반응형 데이터
      activeTab,
      loading,
      selectedYear,
      selectedPeriod,
      selectedResult,
      searchQuery,
      statsYear,
      statsPeriod,
      checkResults,
      statistics,
      currentPage,
      totalPages,
      totalCount,
      showBulkUploadModal,
      toastMessage,
      toastType,
      availableYears,

      // 함수들
      loadCheckResults,
      searchCheckResults,
      downloadTemplate,
      openBulkUploadModal,
      closeBulkUploadModal,
      handleUploadSuccess,
      editResult,
      deleteResult,
      loadStatistics,
      exportResults,
      changePage,

      // 유틸리티 함수들
      getSealStatusText,
      getMalwareStatusText,
      getEncryptionStatusText,
      getResultText,
      getStatusClass,
      formatDateTime,
    }
  },
}
</script>

<style scoped>
.manual-check-management {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 헤더 스타일 */
.admin-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px;
  border-radius: 12px;
  margin-bottom: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.admin-header h1 {
  margin: 0 0 20px 0;
  font-size: 2.2rem;
  font-weight: 600;
}

.admin-nav {
  display: flex;
  gap: 10px;
}

.nav-item {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.3);
}

.nav-item.active {
  background: rgba(255, 255, 255, 0.9);
  color: #667eea;
}

/* 필터 섹션 */
.filter-section {
  display: flex;
  gap: 20px;
  align-items: center;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-weight: 500;
  color: #374151;
  white-space: nowrap;
}

.filter-group select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background: white;
  min-width: 120px;
}

.search-group {
  flex: 1;
  min-width: 200px;
}

.search-input {
  width: 100%;
  padding: 10px 15px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* 액션 버튼 섹션 */
.action-section {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.primary-button,
.secondary-button {
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.primary-button {
  background: #667eea;
  color: white;
}

.primary-button:hover {
  background: #5a67d8;
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.secondary-button {
  background: #f7fafc;
  color: #4a5568;
  border: 1px solid #e2e8f0;
}

.secondary-button:hover {
  background: #edf2f7;
  transform: translateY(-1px);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

/* 로딩 스피너 */
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: #6b7280;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-left: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* 테이블 스타일 */
.results-table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
}

.results-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.results-table th {
  background: #f8fafc;
  padding: 16px 12px;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 2px solid #e5e7eb;
  white-space: nowrap;
}

.results-table td {
  padding: 14px 12px;
  border-bottom: 1px solid #f3f4f6;
  vertical-align: middle;
}

.results-table tr:hover {
  background: #f9fafb;
}

.no-data {
  text-align: center;
  color: #6b7280;
  font-style: italic;
  padding: 40px !important;
}

/* 상태 배지 */
.status-badge,
.result-badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  text-align: center;
  white-space: nowrap;
}

.status-badge.success {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.warning {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.danger {
  background: #fee2e2;
  color: #991b1b;
}

.status-badge.info {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge.unknown {
  background: #f3f4f6;
  color: #6b7280;
}

.result-badge.pass {
  background: #d1fae5;
  color: #065f46;
}

.result-badge.fail {
  background: #fee2e2;
  color: #991b1b;
}

.result-badge.partial {
  background: #fef3c7;
  color: #92400e;
}

/* 점수 셀 */
.score-cell {
  font-weight: 600;
  color: #374151;
}

/* 액션 버튼 */
.action-buttons {
  display: flex;
  gap: 6px;
}

.edit-btn,
.delete-btn {
  padding: 6px 8px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.edit-btn {
  background: #e0f2fe;
  color: #0277bd;
}

.edit-btn:hover {
  background: #b3e5fc;
}

.delete-btn {
  background: #ffebee;
  color: #c62828;
}

.delete-btn:hover {
  background: #ffcdd2;
}

/* 페이지네이션 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.page-btn:hover:not(:disabled) {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

/* 통계 섹션 */
.statistics-section h3 {
  color: #374151;
  margin-bottom: 20px;
  font-size: 1.5rem;
}

.stats-filter {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 25px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  border-left: 4px solid #e5e7eb;
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-card.success {
  border-left-color: #10b981;
}

.stat-card.warning {
  border-left-color: #f59e0b;
}

.stat-card.danger {
  border-left-color: #ef4444;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

/* 부서별 통계 */
.department-stats {
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.department-stats h4 {
  margin-bottom: 20px;
  color: #374151;
  font-size: 1.2rem;
}

.stats-table table {
  width: 100%;
  border-collapse: collapse;
}

.stats-table th,
.stats-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.stats-table th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
}

/* 토스트 메시지 */
.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 15px 20px;
  border-radius: 8px;
  color: white;
  font-weight: 500;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  animation: slideIn 0.3s ease;
}

.toast.success {
  background: #10b981;
}

.toast.error {
  background: #ef4444;
}

.toast.warning {
  background: #f59e0b;
}

.toast.info {
  background: #3b82f6;
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
  .manual-check-management {
    padding: 10px;
  }

  .filter-section {
    flex-direction: column;
    align-items: stretch;
  }

  .action-section {
    flex-direction: column;
  }

  .results-table-container {
    overflow-x: auto;
  }

  .results-table {
    min-width: 800px;
  }

  .stats-cards {
    grid-template-columns: 1fr;
  }

  .admin-header h1 {
    font-size: 1.8rem;
  }

  .admin-nav {
    flex-direction: column;
  }
}
</style>
