// manualCheckService.js - API 호출 서비스

const API_BASE = '/api/manual-check'

const getAuthHeaders = () => {
  const token = localStorage.getItem('token')
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
}

export const manualCheckService = {
  // 템플릿 다운로드
  async downloadTemplate() {
    const token = localStorage.getItem('token')
    const response = await fetch(`${API_BASE}/template`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    if (!response.ok) throw new Error('템플릿 다운로드 실패')
    return response.blob()
  },

  // 일괄 업로드
  async bulkUpload(file) {
    const token = localStorage.getItem('token')
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(`${API_BASE}/bulk-upload`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || '업로드 실패')
    }

    return response.json()
  },

  // 점검 결과 조회
  async getResults(params = {}) {
    const queryParams = new URLSearchParams(params)
    const response = await fetch(`${API_BASE}/results?${queryParams}`, {
      headers: getAuthHeaders()
    })

    if (!response.ok) throw new Error('결과 조회 실패')
    return response.json()
  },

  // 점검 결과 수정
  async updateResult(checkId, data) {
    const response = await fetch(`${API_BASE}/results/${checkId}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    })

    if (!response.ok) throw new Error('결과 수정 실패')
    return response.json()
  },

  // 점검 결과 삭제
  async deleteResult(checkId) {
    const response = await fetch(`${API_BASE}/results/${checkId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    })

    if (!response.ok) throw new Error('결과 삭제 실패')
    return response.json()
  },

  // 통계 조회
  async getStatistics(params = {}) {
    const queryParams = new URLSearchParams(params)
    const response = await fetch(`${API_BASE}/stats?${queryParams}`, {
      headers: getAuthHeaders()
    })

    if (!response.ok) throw new Error('통계 조회 실패')
    return response.json()
  },

  // 결과 내보내기
  async exportResults(params = {}) {
    const queryParams = new URLSearchParams(params)
    const token = localStorage.getItem('token')
    const response = await fetch(`${API_BASE}/export?${queryParams}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    if (!response.ok) throw new Error('내보내기 실패')
    return response.blob()
  }
}
