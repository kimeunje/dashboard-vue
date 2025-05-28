<!-- components/ManualCheckModal.vue -->
<template>
  <div class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <h2>수시 점검 실행</h2>
        <button @click="$emit('close')" class="close-button">
          <svg width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
            <path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8 2.146 2.854Z"/>
          </svg>
        </button>
      </div>

      <div class="modal-content">
        <!-- 로딩 상태 -->
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>수시 점검 항목을 불러오는 중...</p>
        </div>

        <!-- 점검 항목 선택 -->
        <div v-else-if="!selectedItem" class="item-selection">
          <p class="selection-instruction">점검할 항목을 선택해주세요:</p>

          <div class="items-list">
            <div
              v-for="item in checkItems"
              :key="item.item_id"
              @click="selectItem(item)"
              class="item-card"
            >
              <div class="item-icon">
                <svg v-if="item.category === '물리적 보안'" width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M8 1a2 2 0 0 1 2 2v4H6V3a2 2 0 0 1 2-2zm3 6V3a3 3 0 0 0-6 0v4a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2z"/>
                </svg>
                <svg v-else-if="item.category === '악성코드 점검'" width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M6.5 1A1.5 1.5 0 0 0 5 2.5V3H1.5A1.5 1.5 0 0 0 0 4.5v8A1.5 1.5 0 0 0 1.5 14h13a1.5 1.5 0 0 0 1.5-1.5v-8A1.5 1.5 0 0 0 14.5 3H11v-.5A1.5 1.5 0 0 0 9.5 1h-3zm0 1h3a.5.5 0 0 1 .5.5V3H6v-.5a.5.5 0 0 1 .5-.5z"/>
                  <path d="M.5 4v8a.5.5 0 0 0 .5.5h13a.5.5 0 0 0 .5-.5V4a.5.5 0 0 0-.5-.5H1a.5.5 0 0 0-.5.5zm2.5 1.5v1a.5.5 0 0 0 1 0v-1a.5.5 0 0 0-1 0z"/>
                </svg>
                <svg v-else width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M1 2.5A1.5 1.5 0 0 1 2.5 1h3A1.5 1.5 0 0 1 7 2.5v3A1.5 1.5 0 0 1 5.5 7h-3A1.5 1.5 0 0 1 1 5.5v-3zM2.5 2a.5.5 0 0 0-.5.5v3a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5-.5v-3a.5.5 0 0 0-.5-.5h-3z"/>
                  <path d="M9.5 1a.5.5 0 0 1 .5.5v3a.5.5 0 0 1-.5.5h-3a.5.5 0 0 1-.5-.5v-3a.5.5 0 0 1 .5-.5h3z"/>
                </svg>
              </div>
              <div class="item-info">
                <h4>{{ item.name }}</h4>
                <p>{{ item.description }}</p>
                <span class="item-category">{{ item.category }}</span>
              </div>
              <div class="item-arrow">
                <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                  <path fill-rule="evenodd" d="M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z"/>
                </svg>
              </div>
            </div>
          </div>
        </div>

        <!-- 점검 실행 폼 -->
        <div v-else class="check-form">
          <div class="selected-item-info">
            <button @click="selectedItem = null" class="back-button">
              <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path fill-rule="evenodd" d="M15 8a.5.5 0 0 0-.5-.5H2.707l3.147-3.146a.5.5 0 1 0-.708-.708l-4 4a.5.5 0 0 0 0 .708l4 4a.5.5 0 0 0 .708-.708L2.707 8.5H14.5A.5.5 0 0 0 15 8z"/>
              </svg>
              뒤로 가기
            </button>
            <div class="item-header">
              <h3>{{ selectedItem.name }}</h3>
              <p>{{ selectedItem.description }}</p>
            </div>
          </div>

          <form @submit.prevent="submitCheck" class="check-form-content">
            <!-- PC 봉인씰 상태 확인 -->
            <div v-if="selectedItem.name.includes('봉인씰')" class="form-group">
              <label class="form-label">봉인씰 상태</label>
              <div class="radio-group">
                <label class="radio-option">
                  <input
                    type="radio"
                    v-model="formData.sealStatus"
                    value="intact"
                    name="sealStatus"
                  >
                  <span class="radio-label">정상 (훼손 없음)</span>
                </label>
                <label class="radio-option">
                  <input
                    type="radio"
                    v-model="formData.sealStatus"
                    value="damaged"
                    name="sealStatus"
                  >
                  <span class="radio-label">훼손됨</span>
                </label>
              </div>

              <div class="form-group">
                <label class="form-label">확인 날짜</label>
                <input
                  type="date"
                  v-model="formData.checkDate"
                  class="form-input"
                  :max="today"
                  required
                >
              </div>
            </div>

            <!-- 악성코드 탐지 이력 확인 -->
            <div v-else-if="selectedItem.name.includes('악성코드')" class="form-group">
              <label class="form-label">악성코드 탐지 여부</label>
              <div class="radio-group">
                <label class="radio-option">
                  <input
                    type="radio"
                    v-model="formData.malwareDetected"
                    :value="false"
                    name="malwareDetected"
                  >
                  <span class="radio-label">탐지되지 않음</span>
                </label>
                <label class="radio-option">
                  <input
                    type="radio"
                    v-model="formData.malwareDetected"
                    :value="true"
                    name="malwareDetected"
                  >
                  <span class="radio-label">탐지됨</span>
                </label>
              </div>

              <div v-if="formData.malwareDetected" class="form-group">
                <label class="form-label">탐지된 위협 수</label>
                <input
                  type="number"
                  v-model="formData.threatsFound"
                  class="form-input"
                  min="0"
                  placeholder="탐지된 위협의 개수를 입력하세요"
                >
              </div>

              <div class="form-group">
                <label class="form-label">마지막 검사 날짜</label>
                <input
                  type="date"
                  v-model="formData.lastScanDate"
                  class="form-input"
                  :max="today"
                  required
                >
              </div>
            </div>

            <!-- 개인정보 암호화 상태 확인 -->
            <div v-else-if="selectedItem.name.includes('암호화')" class="form-group">
              <div class="form-group">
                <label class="form-label">전체 파일 수</label>
                <input
                  type="number"
                  v-model="formData.totalFiles"
                  class="form-input"
                  min="0"
                  placeholder="검사한 전체 파일 수"
                  required
                >
              </div>

              <div class="form-group">
                <label class="form-label">암호화된 파일 수</label>
                <input
                  type="number"
                  v-model="formData.encryptedFiles"
                  class="form-input"
                  min="0"
                  :max="formData.totalFiles || 999"
                  placeholder="암호화된 파일 수"
                  required
                >
              </div>

              <div v-if="formData.totalFiles > 0" class="encryption-rate">
                <span class="rate-label">암호화율:</span>
                <span class="rate-value" :class="getEncryptionRateClass()">
                  {{ getEncryptionRate() }}%
                </span>
              </div>
            </div>

            <!-- 공통 메모 필드 -->
            <div class="form-group">
              <label class="form-label">메모 (선택사항)</label>
              <textarea
                v-model="formData.notes"
                class="form-textarea"
                rows="3"
                placeholder="추가적인 메모나 특이사항을 입력하세요..."
              ></textarea>
            </div>

            <!-- 결과 판정 -->
            <div class="result-section">
              <h4>점검 결과</h4>
              <div class="result-badge" :class="getResultClass()">
                {{ getResultText() }}
              </div>
              <p class="result-description">
                {{ getResultDescription() }}
              </p>
            </div>

            <!-- 제출 버튼 -->
            <div class="form-actions">
              <button type="button" @click="selectedItem = null" class="cancel-button">
                취소
              </button>
              <button
                type="submit"
                class="submit-button"
                :disabled="!isFormValid() || submitting"
              >
                <span v-if="submitting">
                  <div class="inline-spinner"></div>
                  저장 중...
                </span>
                <span v-else>점검 결과 저장</span>
              </button>
            </div>
          </form>
        </div>

        <!-- 에러 메시지 -->
        <div v-if="error" class="error-message">
          <svg width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
            <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM8 4a.905.905 0 0 0-.9.995l.35 3.507a.552.552 0 0 0 1.1 0l.35-3.507A.905.905 0 0 0 8 4zm.002 6a1 1 0 1 0 0 2 1 1 0 0 0 0-2z"/>
          </svg>
          {{ error }}
        </div>

        <!-- 성공 메시지 -->
        <div v-if="success" class="success-message">
          <svg width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
            <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.061L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/>
          </svg>
          {{ success }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'

// Props 및 Emits
const emit = defineEmits(['close', 'check-completed'])

// 반응형 데이터
const loading = ref(false)
const submitting = ref(false)
const error = ref('')
const success = ref('')
const checkItems = ref([])
const selectedItem = ref(null)

// 폼 데이터
const formData = ref({
  // PC 봉인씰 관련
  sealStatus: '',
  checkDate: '',

  // 악성코드 관련
  malwareDetected: null,
  threatsFound: 0,
  lastScanDate: '',

  // 암호화 관련
  totalFiles: 0,
  encryptedFiles: 0,

  // 공통
  notes: ''
})

// 계산된 속성
const today = computed(() => {
  return new Date().toISOString().split('T')[0]
})

// 메서드
const fetchCheckItems = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await fetch('/api/security-audit/manual-check-items', {
      credentials: 'include'
    })

    if (response.ok) {
      const data = await response.json()
      checkItems.value = data
    } else {
      throw new Error('수시 점검 항목을 불러올 수 없습니다.')
    }
  } catch (err) {
    error.value = err.message
    console.error('수시 점검 항목 로드 실패:', err)
  } finally {
    loading.value = false
  }
}

const selectItem = (item) => {
  selectedItem.value = item
  resetFormData()
  error.value = ''
  success.value = ''
}

const resetFormData = () => {
  formData.value = {
    sealStatus: '',
    checkDate: today.value,
    malwareDetected: null,
    threatsFound: 0,
    lastScanDate: today.value,
    totalFiles: 0,
    encryptedFiles: 0,
    notes: ''
  }
}

const getEncryptionRate = () => {
  if (formData.value.totalFiles === 0) return 0
  return Math.round((formData.value.encryptedFiles / formData.value.totalFiles) * 100)
}

const getEncryptionRateClass = () => {
  const rate = getEncryptionRate()
  if (rate >= 80) return 'excellent'
  if (rate >= 60) return 'good'
  return 'poor'
}

const getResultClass = () => {
  const passed = getCheckResult()
  return passed ? 'pass' : 'fail'
}

const getResultText = () => {
  const passed = getCheckResult()
  return passed ? '통과' : '실패'
}

const getCheckResult = () => {
  if (!selectedItem.value) return false

  if (selectedItem.value.name.includes('봉인씰')) {
    return formData.value.sealStatus === 'intact'
  } else if (selectedItem.value.name.includes('악성코드')) {
    return !formData.value.malwareDetected
  } else if (selectedItem.value.name.includes('암호화')) {
    return getEncryptionRate() >= 80
  }
  return false
}

const getResultDescription = () => {
  if (!selectedItem.value) return ''

  if (selectedItem.value.name.includes('봉인씰')) {
    return formData.value.sealStatus === 'intact'
      ? 'PC 봉인씰이 정상 상태입니다.'
      : 'PC 봉인씰이 훼손되어 조치가 필요합니다.'
  } else if (selectedItem.value.name.includes('악성코드')) {
    return !formData.value.malwareDetected
      ? '악성코드가 탐지되지 않았습니다.'
      : `${formData.value.threatsFound}개의 위협이 탐지되어 조치가 필요합니다.`
  } else if (selectedItem.value.name.includes('암호화')) {
    const rate = getEncryptionRate()
    if (rate >= 80) return '개인정보 암호화가 적절히 적용되어 있습니다.'
    return `암호화율이 ${rate}%로 기준(80%) 미달입니다. 추가 암호화가 필요합니다.`
  }
  return ''
}

const isFormValid = () => {
  if (!selectedItem.value) return false

  if (selectedItem.value.name.includes('봉인씰')) {
    return formData.value.sealStatus && formData.value.checkDate
  } else if (selectedItem.value.name.includes('악성코드')) {
    return formData.value.malwareDetected !== null && formData.value.lastScanDate
  } else if (selectedItem.value.name.includes('암호화')) {
    return formData.value.totalFiles >= 0 && formData.value.encryptedFiles >= 0
  }
  return false
}

const submitCheck = async () => {
  if (!isFormValid()) return

  submitting.value = true
  error.value = ''
  success.value = ''

  try {
    // 실제 값 구성
    let actualValue = {}

    if (selectedItem.value.name.includes('봉인씰')) {
      actualValue = {
        seal_status: formData.value.sealStatus,
        check_date: formData.value.checkDate
      }
    } else if (selectedItem.value.name.includes('악성코드')) {
      actualValue = {
        malware_detected: formData.value.malwareDetected,
        threats_found: formData.value.threatsFound,
        last_scan_date: formData.value.lastScanDate
      }
    } else if (selectedItem.value.name.includes('암호화')) {
      actualValue = {
        total_files: formData.value.totalFiles,
        encrypted_files: formData.value.encryptedFiles,
        encryption_rate: getEncryptionRate()
      }
    }

    const requestData = {
      item_id: selectedItem.value.item_id,
      actual_value: actualValue,
      passed: getCheckResult() ? 1 : 0,
      notes: formData.value.notes || getResultDescription()
    }

    const response = await fetch('/api/security-audit/manual-check', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify(requestData)
    })

    if (response.ok) {
      const result = await response.json()
      success.value = '수시 점검 결과가 성공적으로 저장되었습니다.'

      // 2초 후 모달 닫기
      setTimeout(() => {
        emit('check-completed')
        emit('close')
      }, 2000)
    } else {
      const errorData = await response.json()
      throw new Error(errorData.error || '점검 결과 저장에 실패했습니다.')
    }
  } catch (err) {
    error.value = err.message
    console.error('수시 점검 제출 실패:', err)
  } finally {
    submitting.value = false
  }
}

const handleOverlayClick = () => {
  if (!submitting.value) {
    emit('close')
  }
}

// 라이프사이클 훅
onMounted(() => {
  fetchCheckItems()
  formData.value.checkDate = today.value
  formData.value.lastScanDate = today.value
})
</script>

<style scoped>
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
  z-index: 2000;
  padding: 20px;
}

.modal-container {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 0 24px;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 24px;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--dark-blue);
}

.close-button {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.close-button:hover {
  background-color: #f3f4f6;
  color: #374151;
}

.modal-content {
  flex: 1;
  overflow-y: auto;
  padding: 0 24px 24px 24px;
}

/* 로딩 상태 */
.loading-state {
  text-align: center;
  padding: 40px 20px;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f4f6;
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 항목 선택 */
.selection-instruction {
  margin-bottom: 20px;
  color: #6b7280;
  font-size: 1rem;
}

.items-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.item-card {
  display: flex;
  align-items: center;
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.item-card:hover {
  border-color: var(--primary-color);
  background-color: #f8fafc;
}

.item-icon {
  margin-right: 16px;
  color: var(--primary-color);
  flex-shrink: 0;
}

.item-info {
  flex: 1;
}

.item-info h4 {
  margin: 0 0 4px 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--dark-blue);
}

.item-info p {
  margin: 0 0 8px 0;
  font-size: 0.875rem;
  color: #6b7280;
  line-height: 1.4;
}

.item-category {
  font-size: 0.75rem;
  color: var(--primary-color);
  background-color: var(--light-blue);
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: 500;
}

.item-arrow {
  color: #9ca3af;
  margin-left: 12px;
}

/* 점검 폼 */
.selected-item-info {
  margin-bottom: 24px;
}

.back-button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  color: var(--primary-color);
  cursor: pointer;
  font-size: 0.875rem;
  padding: 4px 0;
  margin-bottom: 16px;
}

.back-button:hover {
  text-decoration: underline;
}

.item-header h3 {
  margin: 0 0 8px 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--dark-blue);
}

.item-header p {
  margin: 0;
  color: #6b7280;
  line-height: 1.5;
}

.check-form-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-weight: 500;
  color: var(--dark-blue);
  font-size: 0.875rem;
}

.form-input,
.form-textarea {
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  transition: border-color 0.2s ease;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: background-color 0.2s ease;
}

.radio-option:hover {
  background-color: #f9fafb;
}

.radio-option input[type="radio"] {
  margin: 0;
}

.radio-label {
  font-size: 0.875rem;
  color: #374151;
}

.encryption-rate {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background-color: #f9fafb;
  border-radius: 6px;
}

.rate-label {
  font-size: 0.875rem;
  color: #6b7280;
}

.rate-value {
  font-weight: 600;
  font-size: 1rem;
}

.rate-value.excellent {
  color: #10b981;
}

.rate-value.good {
  color: #f59e0b;
}

.rate-value.poor {
  color: #ef4444;
}

.result-section {
  padding: 16px;
  background-color: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.result-section h4 {
  margin: 0 0 12px 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--dark-blue);
}
</style>
