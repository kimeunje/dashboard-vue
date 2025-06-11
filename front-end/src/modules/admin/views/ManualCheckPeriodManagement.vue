<!-- ManualCheckPeriodManagement.vue -->
<template>
  <div class="period-management">
    <!-- 헤더 -->
    <div class="section-header">
      <h3>🗓️ 점검 기간 관리</h3>
      <div class="header-actions">
        <select v-model="selectedYear" @change="loadPeriodStatus" class="year-selector">
          <option v-for="year in availableYears" :key="year" :value="year">{{ year }}년</option>
        </select>
        <button @click="openPeriodModal" class="primary-button">
          <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
          </svg>
          기간 추가
        </button>
      </div>
    </div>

    <!-- 점검 유형별 기간 현황 -->
    <div class="check-types-container" v-if="periodStatus.check_types">
      <div
        v-for="(typeData, checkType) in periodStatus.check_types"
        :key="checkType"
        class="check-type-section"
      >
        <div class="type-header">
          <h4>{{ typeData.type_name }} 점검</h4>
          <div class="type-stats">
            <span class="stat-item">
              총 기간: {{ typeData.periods.length }}개
            </span>
            <span class="stat-item">
              완료: {{ typeData.periods.filter(p => p.is_completed).length }}개
            </span>
          </div>
        </div>

        <!-- 기간 카드들 -->
        <div class="period-cards">
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
              <div class="period-dates">
                <span class="date-range">
                  {{ formatDate(period.start_date) }} ~ {{ formatDate(period.end_date) }}
                </span>
                <span class="status-badge" :class="period.status">
                  {{ getStatusText(period.status) }}
                </span>
              </div>

              <div class="period-stats" v-if="period.total_users > 0">
                <div class="stats-row">
                  <span class="stat-label">참여자:</span>
                  <span class="stat-value">{{ period.total_users }}명</span>
                </div>
                <div class="stats-row">
                  <span class="stat-label">통과:</span>
                  <span class="stat-value success">{{ period.pass_count }}명</span>
                </div>
                <div class="stats-row">
                  <span class="stat-label">실패:</span>
                  <span class="stat-value danger">{{ period.fail_count }}명</span>
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
                <span v-else-if="period.status === 'active'" class="active-indicator">
                  🟢 진행 중
                </span>
                <span v-else-if="period.status === 'upcoming'" class="upcoming-indicator">
                  ⏱️ 예정
                </span>
              </div>
            </div>
          </div>

          <!-- 기간이 없는 경우 -->
          <div v-if="typeData.periods.length === 0" class="no-periods">
            <span>{{ selectedYear }}년 {{ typeData.type_name }} 점검 기간이 설정되지 않았습니다.</span>
            <button @click="openPeriodModal(checkType)" class="add-period-button">
              기간 추가하기
            </button>
          </div>
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
              <select
                v-model="periodForm.check_type"
                :disabled="editingPeriod"
                required
              >
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
                  <option v-for="year in availableYears" :key="year" :value="year">{{ year }}</option>
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
                <input
                  type="date"
                  v-model="periodForm.start_date"
                  required
                />
              </div>

              <div class="form-group">
                <label>종료일 *</label>
                <input
                  type="date"
                  v-model="periodForm.end_date"
                  required
                />
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
                <input
                  type="checkbox"
                  v-model="periodForm.auto_pass_setting"
                />
                기간 종료 시 자동 통과 처리
              </label>
              <small class="help-text">
                체크 시 기간 종료 후 완료 처리할 때 미실시 사용자들을 자동으로 통과 처리합니다.
              </small>
            </div>

            <div class="modal-footer">
              <button type="button" @click="closePeriodModal" class="secondary-button">
                취소
              </button>
              <button type="submit" class="primary-button" :disabled="savingPeriod">
                {{ savingPeriod ? '저장 중...' : '저장' }}
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

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'

// 반응형 데이터
const selectedYear = ref(new Date().getFullYear())
const periodStatus = ref({ check_types: {} })
const loading = ref(false)
const completing = ref(false)

// 모달 상태
const showPeriodModal = ref(false)
const editingPeriod = ref(null)
const savingPeriod = ref(false)

// 폼 데이터
const periodForm = reactive({
  check_type: '',
  period_year: new Date().getFullYear(),
  period_name: '',
  start_date: '',
  end_date: '',
  description: '',
  auto_pass_setting: true
})

// 토스트
const showToast = ref(false)
const toastMessage = ref('')
const toastType = ref('success')

// 계산된 속성
const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: 11 }, (_, i) => currentYear - 5 + i)
})

// 메서드
const loadPeriodStatus = async () => {
  try {
    loading.value = true
    const response = await fetch(
      `/api/manual-check/periods/status?year=${selectedYear.value}`,
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      }
    )

    if (!response.ok) throw new Error('기간 상태 조회 실패')

    const result = await response.json()
    periodStatus.value = result.data
  } catch (err) {
    console.error('기간 상태 조회 오류:', err)
    displayToast('기간 상태 조회에 실패했습니다.', 'error')
  } finally {
    loading.value = false
  }
}

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
        Authorization: `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(periodForm)
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

const deletePeriod = async (period) => {
  if (!confirm(`${period.period_name} 기간을 삭제하시겠습니까?`)) return

  try {
    const response = await fetch(`/api/manual-check/periods/${period.period_id}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
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
  if (!confirm(
    `${period.period_name} 기간을 완료 처리하시겠습니까?\n\n` +
    `자동 통과 설정이 켜져있어 미실시 사용자들이 자동으로 통과 처리됩니다.`
  )) return

  completing.value = true

  try {
    const response = await fetch(`/api/manual-check/periods/${period.period_id}/complete`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    })

    const result = await response.json()

    if (!response.ok) {
      throw new Error(result.error || '완료 처리 실패')
    }

    displayToast(result.message, 'success')
    await loadPeriodStatus()
  } catch (err) {
    console.error('완료 처리 오류:', err)
    displayToast(err.message, 'error')
  } finally {
    completing.value = false
  }
}

const displayToast = (message, type = 'success') => {
  toastMessage.value = message
  toastType.value = type
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('ko-KR')
}

const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return ''
  return new Date(dateTimeString).toLocaleString('ko-KR')
}

const getStatusText = (status) => {
  const statusTexts = {
    active: '진행 중',
    upcoming: '예정',
    ended: '종료'
  }
  return statusTexts[status] || status
}

// 생명주기
onMounted(() => {
  loadPeriodStatus()
})
</script>

<style scoped>
.period-management {
  padding: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e0e0e0;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.year-selector {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.check-types-container {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.check-type-section {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 24px;
}

.type-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.type-header h4 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.type-stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  font-size: 14px;
  color: #666;
  background: white;
  padding: 4px 8px;
  border-radius: 4px;
}

.period-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.period-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #ddd;
  transition: all 0.3s ease;
}

.period-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.period-card.status-active {
  border-left-color: #28a745;
}

.period-card.status-upcoming {
  border-left-color: #ffc107;
}

.period-card.status-ended {
  border-left-color: #6c757d;
}

.period-card.completed {
  border-left-color: #007bff;
  background: #f8f9ff;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.card-header h5 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.icon-button {
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  border-radius: 4px;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.icon-button:hover:not(:disabled) {
  opacity: 1;
  background: #f0f0f0;
}

.icon-button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.card-content {
  margin-bottom: 16px;
}

.period-dates {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.date-range {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background: #d4edda;
  color: #155724;
}

.status-badge.upcoming {
  background: #fff3cd;
  color: #856404;
}

.status-badge.ended {
  background: #f8d7da;
  color: #721c24;
}

.period-stats {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stats-row {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.stat-label {
  color: #666;
}

.stat-value {
  font-weight: 500;
}

.stat-value.success {
  color: #28a745;
}

.stat-value.danger {
  color: #dc3545;
}

.no-data {
  color: #999;
  font-style: italic;
  font-size: 14px;
}

.card-footer {
  border-top: 1px solid #e9ecef;
  padding-top: 12px;
}

.completion-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.completed-badge {
  color: #007bff;
  font-weight: 500;
  font-size: 14px;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
}

.complete-button {
  background: #28a745;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}

.complete-button:hover:not(:disabled) {
  background: #218838;
}

.complete-button:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.active-indicator,
.upcoming-indicator {
  font-size: 14px;
  font-weight: 500;
}

.no-periods {
  grid-column: 1 / -1;
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

.add-period-button {
  margin-top: 12px;
  background: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.add-period-button:hover {
  background: #0056b3;
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
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.2s;
}

.close-button:hover {
  background: #f0f0f0;
}

.modal-body {
  padding: 24px;
}

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
  color: #333;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
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
  color: #666;
  font-size: 13px;
  margin-top: 4px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e9ecef;
}

.primary-button,
.secondary-button {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.primary-button {
  background: #007bff;
  color: white;
}

.primary-button:hover:not(:disabled) {
  background: #0056b3;
}

.primary-button:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.secondary-button {
  background: #6c757d;
  color: white;
}

.secondary-button:hover {
  background: #5a6268;
}

/* 토스트 */
.toast-message {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 24px;
  border-radius: 6px;
  font-weight: 500;
  z-index: 1100;
  animation: slideIn 0.3s ease;
}

.toast-message.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.toast-message.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
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
</style>
