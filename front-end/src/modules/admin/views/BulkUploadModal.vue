<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-content bulk-upload-modal" @click.stop>
      <div class="modal-header">
        <h3>수시 점검 결과 일괄 등록</h3>
        <button @click="$emit('close')" class="close-button">×</button>
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
              <button @click="$refs.fileInput.click()" class="select-file-button">파일 선택</button>
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
              <li>필수 컬럼: 사용자ID, 점검일시, 봉인씰상태, 악성코드검사결과, 암호화상태</li>
              <li>첫 번째 행은 헤더로 처리됩니다</li>
              <li>템플릿을 다운로드하여 양식을 확인하세요</li>
            </ul>
          </div>
        </div>

        <div v-if="uploadPreview.length > 0" class="preview-section">
          <h4>미리보기 (처음 3개 레코드)</h4>
          <div class="preview-table">
            <table>
              <thead>
                <tr>
                  <th>사용자ID</th>
                  <th>점검일시</th>
                  <th>봉인씰</th>
                  <th>악성코드</th>
                  <th>암호화</th>
                  <th>종합결과</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(record, index) in uploadPreview.slice(0, 3)" :key="index">
                  <td>{{ record.user_id || '-' }}</td>
                  <td>{{ record.check_date || '-' }}</td>
                  <td>{{ record.seal_status || '-' }}</td>
                  <td>{{ record.malware_scan_result || '-' }}</td>
                  <td>{{ record.encryption_status || '-' }}</td>
                  <td>{{ record.overall_result || '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p class="preview-note">총 {{ uploadPreview.length }}개 레코드가 파싱되었습니다.</p>
        </div>
      </div>

      <div class="modal-footer">
        <button @click="$emit('close')" class="cancel-button">취소</button>
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
</template>

<script>
import { ref } from 'vue'
import { manualCheckService } from '../services/manualCheckService.js'
import Papa from 'papaparse'

export default {
  name: 'BulkUploadModal',
  emits: ['close', 'upload-success'],
  setup(props, { emit }) {
    const selectedFile = ref(null)
    const uploadPreview = ref([])
    const uploading = ref(false)

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
      try {
        const fileName = file.name.toLowerCase()

        if (fileName.endsWith('.csv')) {
          const text = await file.text()
          const results = Papa.parse(text, {
            header: true,
            dynamicTyping: true,
            skipEmptyLines: true,
            encoding: 'utf-8',
          })
          uploadPreview.value = results.data.slice(0, 10) // 미리보기용 제한
        } else if (fileName.endsWith('.xlsx') || fileName.endsWith('.xls')) {
          // Excel 처리는 실제 업로드시 서버에서 처리
          uploadPreview.value = [
            {
              user_id: 'Excel 파일 감지됨',
              check_date: '서버에서 처리됩니다',
              seal_status: '-',
              malware_scan_result: '-',
              encryption_status: '-',
              overall_result: '-',
            },
          ]
        } else {
          throw new Error('지원하지 않는 파일 형식입니다.')
        }
      } catch (err) {
        console.error('파일 파싱 실패:', err)
        alert(`파일 파싱에 실패했습니다: ${err.message}`)
        uploadPreview.value = []
      }
    }

    const processBulkUpload = async () => {
      if (!selectedFile.value) return

      try {
        uploading.value = true
        const result = await manualCheckService.bulkUpload(selectedFile.value)
        emit('upload-success', result)
      } catch (error) {
        console.error('업로드 실패:', error)
        alert(error.message || '업로드 중 오류가 발생했습니다.')
      } finally {
        uploading.value = false
      }
    }

    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    return {
      selectedFile,
      uploadPreview,
      uploading,
      handleFileSelect,
      handleFileDrop,
      removeSelectedFile,
      processBulkUpload,
      formatFileSize,
    }
  },
}
</script>

<style scoped>
/* 모달 기본 스타일 */
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
}

.bulk-upload-modal {
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

/* 업로드 섹션 */
.upload-section {
  margin-bottom: 30px;
}

.upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  transition: all 0.3s ease;
  cursor: pointer;
  background: #fafbfc;
}

.upload-area:hover {
  border-color: #667eea;
  background: #f0f4ff;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.upload-icon {
  font-size: 3rem;
  color: #9ca3af;
}

.upload-placeholder p {
  margin: 0;
  color: #6b7280;
  font-size: 16px;
}

.select-file-button {
  background: #667eea;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.select-file-button:hover {
  background: #5a67d8;
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

/* 파일 선택됨 상태 */
.file-selected {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  border-radius: 8px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.file-icon {
  font-size: 2rem;
  color: #059669;
}

.file-name {
  font-weight: 600;
  color: #064e3b;
  margin-bottom: 4px;
}

.file-size {
  font-size: 14px;
  color: #6b7280;
}

.remove-file-button {
  background: #fee2e2;
  color: #dc2626;
  border: none;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  transition: all 0.2s ease;
}

.remove-file-button:hover {
  background: #fecaca;
}

/* 업로드 안내 */
.upload-instructions {
  margin-top: 25px;
  padding: 20px;
  background: #f0f9ff;
  border-radius: 8px;
  border-left: 4px solid #0ea5e9;
}

.upload-instructions h4 {
  margin: 0 0 15px 0;
  color: #0c4a6e;
  font-size: 16px;
}

.upload-instructions ul {
  margin: 0;
  padding-left: 20px;
}

.upload-instructions li {
  color: #075985;
  margin-bottom: 8px;
  line-height: 1.5;
}

/* 미리보기 섹션 */
.preview-section {
  margin-top: 30px;
  padding: 25px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.preview-section h4 {
  margin: 0 0 20px 0;
  color: #374151;
  font-size: 16px;
}

.preview-table {
  overflow-x: auto;
  margin-bottom: 15px;
}

.preview-table table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  background: white;
  border-radius: 6px;
  overflow: hidden;
}

.preview-table th,
.preview-table td {
  padding: 10px 8px;
  border-bottom: 1px solid #e5e7eb;
  text-align: left;
}

.preview-table th {
  background: #f3f4f6;
  font-weight: 600;
  color: #374151;
}

.preview-table td {
  color: #6b7280;
}

.preview-note {
  margin: 0;
  font-size: 14px;
  color: #059669;
  font-weight: 500;
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

/* 반응형 디자인 */
@media (max-width: 768px) {
  .modal-overlay {
    padding: 10px;
  }

  .modal-content {
    max-width: 100%;
  }

  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 20px;
  }

  .upload-area {
    padding: 30px 20px;
  }

  .file-selected {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }

  .modal-footer {
    flex-direction: column;
  }

  .cancel-button,
  .upload-button {
    width: 100%;
  }
}
</style>
