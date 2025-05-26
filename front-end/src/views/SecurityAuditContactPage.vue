<!-- views/SecurityAuditContact.vue -->
<template>
  <div class="security-audit-layout">
    <!-- 모바일 메뉴 토글 버튼 -->
    <button
      v-if="sidebarRef?.isMobile"
      @click="sidebarRef?.toggleSidebar()"
      class="mobile-menu-toggle"
    >
      <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
        <path
          fill-rule="evenodd"
          d="M2.5 12a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5z"
        />
      </svg>
    </button>

    <!-- 사이드바 -->
    <Sidebar ref="sidebarRef" />

    <main class="main-content">
      <h1 class="page-title">문의하세요</h1>

      <!-- 개요 섹션 -->
      <div class="section">
        <h2 class="section-title">보안 감사 관련 문의</h2>
        <p>
          상시보안감사 시스템 사용 중 궁금한 사항이나 기술적 문제가 있으시면 언제든지 IT 보안팀으로
          연락 주시기 바랍니다. 신속하고 정확한 답변을 드리도록 하겠습니다.
        </p>
      </div>

      <!-- 연락처 정보 -->
      <div class="section">
        <h2 class="section-title">연락처 정보</h2>
        <div class="contact-grid">
          <div class="contact-card">
            <div class="contact-icon phone">
              <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                <path
                  d="M3.654 1.328a.678.678 0 0 0-1.015-.063L1.605 2.3c-.483.484-.661 1.169-.45 1.77a17.568 17.568 0 0 0 4.168 6.608 17.569 17.569 0 0 0 6.608 4.168c.601.211 1.286.033 1.77-.45l1.034-1.034a.678.678 0 0 0-.063-1.015l-2.307-1.794a.678.678 0 0 0-.58-.122L9.98 10.97a.68.68 0 0 1-.673-.38 9.344 9.344 0 0 1-1.062-2.227.678.678 0 0 1 .122-.58l1.794-2.307a.678.678 0 0 0-.063-1.015L7.793 2.654a.678.678 0 0 0-.58-.122L5.408 3.566a.678.678 0 0 1-.673-.38z"
                />
              </svg>
            </div>
            <div class="contact-content">
              <h3>전화 문의</h3>
              <p class="contact-detail">내선 <strong>5678</strong></p>
              <p class="contact-description">평일 09:00 - 18:00</p>
              <button @click="copyToClipboard('5678')" class="copy-button small">
                <svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M4 1.5H3a2 2 0 0 0-2 2V14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V3.5a2 2 0 0 0-2-2h-1v1h1a1 1 0 0 1 1 1V14a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V3.5a1 1 0 0 1 1-1h1v-1z"
                  />
                  <path
                    d="M9.5 1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-3a.5.5 0 0 1-.5-.5v-1a.5.5 0 0 1 .5-.5h3zm-3-1A1.5 1.5 0 0 0 5 1.5v1A1.5 1.5 0 0 0 6.5 4h3A1.5 1.5 0 0 0 11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3z"
                  />
                </svg>
                복사
              </button>
            </div>
          </div>

          <div class="contact-card">
            <div class="contact-icon email">
              <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                <path
                  d="M2 2A2 2 0 0 0 0 4v.217l8 4.157 8-4.157V4a2 2 0 0 0-2-2H2zm13 2.383-4.758 2.475L16 8.32V4.383zm-.034 6.876-5.64-3.471L8 8.583l-1.326-.795-5.64 3.47A2 2 0 0 0 2 14h12a2 2 0 0 0 1.966-1.741z"
                />
              </svg>
            </div>
            <div class="contact-content">
              <h3>이메일 문의</h3>
              <p class="contact-detail">
                <a href="mailto:security-audit@example.com" class="email-link">
                  security-audit@example.com
                </a>
              </p>
              <p class="contact-description">24시간 접수 가능</p>
              <button
                @click="copyToClipboard('security-audit@example.com')"
                class="copy-button small"
              >
                <svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    d="M4 1.5H3a2 2 0 0 0-2 2V14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V3.5a2 2 0 0 0-2-2h-1v1h1a1 1 0 0 1 1 1V14a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V3.5a1 1 0 0 1 1-1h1v-1z"
                  />
                  <path
                    d="M9.5 1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-3a.5.5 0 0 1-.5-.5v-1a.5.5 0 0 1 .5-.5h3zm-3-1A1.5 1.5 0 0 0 5 1.5v1A1.5 1.5 0 0 0 6.5 4h3A1.5 1.5 0 0 0 11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3z"
                  />
                </svg>
                복사
              </button>
            </div>
          </div>

          <div class="contact-card">
            <div class="contact-icon location">
              <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                <path
                  d="M8 16s6-5.686 6-10A6 6 0 0 0 2 6c0 4.314 6 10 6 10zm0-7a3 3 0 1 1 0-6 3 3 0 0 1 0 6z"
                />
              </svg>
            </div>
            <div class="contact-content">
              <h3>방문 문의</h3>
              <p class="contact-detail">IT보안팀 사무실</p>
              <p class="contact-description">본사 3층 IT보안팀</p>
              <p class="contact-note">사전 예약 필수</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 자주 묻는 질문 -->
      <div class="section">
        <h2 class="section-title">자주 묻는 질문</h2>
        <div class="faq-container">
          <div v-for="(faq, index) in faqList" :key="index" class="faq-item">
            <button
              @click="toggleFaq(index)"
              :class="['faq-question', { active: activeFaq === index }]"
            >
              <span class="faq-question-text">{{ faq.question }}</span>
              <span class="faq-toggle-icon">
                <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                  <path
                    fill-rule="evenodd"
                    d="M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z"
                  />
                </svg>
              </span>
            </button>
            <Transition name="faq">
              <div v-if="activeFaq === index" class="faq-answer">
                <div class="faq-answer-content">
                  <p v-html="faq.answer"></p>
                </div>
              </div>
            </Transition>
          </div>
        </div>
      </div>

      <!-- 문의 양식 -->
      <div class="section">
        <h2 class="section-title">온라인 문의</h2>
        <div class="contact-form-container">
          <form @submit.prevent="submitForm" class="contact-form">
            <div class="form-row">
              <div class="form-group">
                <label for="name">이름 *</label>
                <input
                  type="text"
                  id="name"
                  v-model="form.name"
                  required
                  placeholder="이름을 입력하세요"
                />
              </div>
              <div class="form-group">
                <label for="department">부서</label>
                <input
                  type="text"
                  id="department"
                  v-model="form.department"
                  placeholder="소속 부서를 입력하세요"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="email">이메일 *</label>
                <input
                  type="email"
                  id="email"
                  v-model="form.email"
                  required
                  placeholder="이메일 주소를 입력하세요"
                />
              </div>
              <div class="form-group">
                <label for="phone">연락처</label>
                <input
                  type="tel"
                  id="phone"
                  v-model="form.phone"
                  placeholder="연락처를 입력하세요"
                />
              </div>
            </div>

            <div class="form-group">
              <label for="category">문의 유형 *</label>
              <select id="category" v-model="form.category" required>
                <option value="">문의 유형을 선택하세요</option>
                <option value="technical">기술적 문제</option>
                <option value="policy">보안 정책 관련</option>
                <option value="result">감사 결과 관련</option>
                <option value="solution">조치방법 관련</option>
                <option value="system">시스템 사용법</option>
                <option value="other">기타</option>
              </select>
            </div>

            <div class="form-group">
              <label for="subject">제목 *</label>
              <input
                type="text"
                id="subject"
                v-model="form.subject"
                required
                placeholder="문의 제목을 입력하세요"
              />
            </div>

            <div class="form-group">
              <label for="message">문의 내용 *</label>
              <textarea
                id="message"
                v-model="form.message"
                required
                rows="6"
                placeholder="구체적인 문의 내용을 작성해 주세요"
              ></textarea>
            </div>

            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="form.agreePrivacy" required />
                <span class="checkbox-text">
                  개인정보 수집 및 이용에 동의합니다 *
                  <a href="#" @click.prevent="showPrivacyPolicy" class="privacy-link">
                    (상세보기)
                  </a>
                </span>
              </label>
            </div>

            <div class="form-actions">
              <button type="button" @click="resetForm" class="reset-button">초기화</button>
              <button type="submit" :disabled="isSubmitting" class="submit-button">
                <span v-if="isSubmitting" class="loading-spinner"></span>
                {{ isSubmitting ? '전송 중...' : '문의하기' }}
              </button>
            </div>
          </form>

          <!-- 문의 안내 -->
          <div class="contact-info">
            <div class="info-card">
              <h3>문의 처리 안내</h3>
              <ul>
                <li>일반 문의: 1-2 영업일 내 답변</li>
                <li>긴급 문의: 당일 답변</li>
                <li>기술 지원: 즉시 대응</li>
              </ul>
            </div>

            <div class="info-card">
              <h3>문의 시 참고사항</h3>
              <ul>
                <li>구체적인 문제 상황을 기재해 주세요</li>
                <li>스크린샷이 있으면 첨부해 주세요</li>
                <li>재현 방법을 상세히 적어주세요</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- 토스트 메시지 -->
      <div v-if="showToast" :class="['toast-message', toastType]">
        {{ toastMessage }}
      </div>

      <!-- 공통 페이지 네비게이션 -->
      <PageNavigation :current-path="route.path" />
    </main>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRoute } from 'vue-router'
import PageNavigation from '@/components/PageNavigation.vue'
import Sidebar from '@/components/Sidebar.vue'

// Vue Router
const route = useRoute()

// 반응형 데이터
const activeFaq = ref(null)
const showToast = ref(false)
const toastMessage = ref('')
const toastType = ref('success')
const isSubmitting = ref(false)
// Sidebar ref 추가
const sidebarRef = ref(null)

// 폼 데이터
const form = reactive({
  name: '',
  department: '',
  email: '',
  phone: '',
  category: '',
  subject: '',
  message: '',
  agreePrivacy: false,
})

// FAQ 데이터
const faqList = [
  {
    question: '보안 감사는 얼마나 자주 실시되나요?',
    answer:
      '정기 보안 감사는 매월 첫째 주에 실시되며, 필요에 따라 수시 감사도 진행됩니다. 시스템을 통해 언제든지 현재 상태를 확인하실 수 있습니다.',
  },
  {
    question: '감사 결과에서 실패 항목이 있을 때 어떻게 해야 하나요?',
    answer:
      '<strong>조치방법</strong> 페이지에서 각 항목별 상세한 해결 방법을 확인하실 수 있습니다. 기술적 도움이 필요한 경우 IT 보안팀으로 연락주시기 바랍니다.',
  },
  {
    question: '시스템 접속에 문제가 있어요.',
    answer:
      '로그인 문제의 경우 먼저 브라우저 캐시를 삭제하고 다시 시도해 보세요. 문제가 지속되면 IT 보안팀(내선 5678)으로 연락 주시기 바랍니다.',
  },
  {
    question: '보안 정책이 변경되었다고 하는데 어디서 확인할 수 있나요?',
    answer:
      '변경된 보안 정책은 <strong>조치방법</strong> 페이지에서 최신 정보를 확인하실 수 있습니다. 중요한 변경사항은 이메일로도 안내드립니다.',
  },
  {
    question: '개인 PC에서도 보안 감사를 받아야 하나요?',
    answer:
      '회사 네트워크에 연결된 모든 PC는 보안 정책 준수 대상입니다. 개인 소유 장비라도 업무용으로 사용하는 경우 보안 감사 대상에 포함됩니다.',
  },
]

// 메서드
const toggleFaq = (index) => {
  activeFaq.value = activeFaq.value === index ? null : index
}

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    showToastMessage('클립보드에 복사되었습니다!', 'success')
  } catch (err) {
    console.error('클립보드 복사 실패:', err)
    fallbackCopyTextToClipboard(text)
  }
}

const fallbackCopyTextToClipboard = (text) => {
  const textArea = document.createElement('textarea')
  textArea.value = text
  textArea.style.top = '0'
  textArea.style.left = '0'
  textArea.style.position = 'fixed'

  document.body.appendChild(textArea)
  textArea.focus()
  textArea.select()

  try {
    const successful = document.execCommand('copy')
    if (successful) {
      showToastMessage('클립보드에 복사되었습니다!', 'success')
    }
  } catch (err) {
    console.error('Fallback: 클립보드 복사 실패', err)
    showToastMessage('복사에 실패했습니다.', 'error')
  }

  document.body.removeChild(textArea)
}

const showToastMessage = (message, type = 'success') => {
  toastMessage.value = message
  toastType.value = type
  showToast.value = true

  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

const submitForm = async () => {
  isSubmitting.value = true

  try {
    // 실제 API 호출 시뮬레이션
    await new Promise((resolve) => setTimeout(resolve, 2000))

    // TODO: 실제 API 호출
    console.log('문의 양식 제출:', form)

    showToastMessage('문의가 성공적으로 접수되었습니다!', 'success')
    resetForm()
  } catch (error) {
    console.error('문의 제출 실패:', error)
    showToastMessage('문의 제출 중 오류가 발생했습니다.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

const resetForm = () => {
  Object.keys(form).forEach((key) => {
    if (typeof form[key] === 'boolean') {
      form[key] = false
    } else {
      form[key] = ''
    }
  })
}

const showPrivacyPolicy = () => {
  alert('개인정보 수집 및 이용 방침에 대한 상세 내용을 별도 창에서 확인하실 수 있습니다.')
}
</script>

<style scoped>
.contact-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
  margin-top: 20px;
}

.contact-card {
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
  transition: all 0.3s ease;
  position: relative;
}

.contact-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.contact-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  color: white;
}

.contact-icon.phone {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
}

.contact-icon.email {
  background: linear-gradient(135deg, #10b981, #059669);
}

.contact-icon.location {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.contact-content h3 {
  margin: 0 0 8px 0;
  color: var(--dark-blue);
  font-size: 1.125rem;
  font-weight: 600;
}

.contact-detail {
  margin: 0 0 4px 0;
  font-size: 1rem;
  font-weight: 500;
  color: #374151;
}

.contact-description {
  margin: 0 0 12px 0;
  font-size: 0.875rem;
  color: #6b7280;
}

.contact-note {
  margin: 8px 0 0 0;
  font-size: 0.75rem;
  color: #f59e0b;
  font-style: italic;
}

.email-link {
  color: var(--primary-color);
  text-decoration: none;
}

.email-link:hover {
  text-decoration: underline;
}

.copy-button {
  background: none;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  padding: 4px 8px;
  cursor: pointer;
  color: #6b7280;
  font-size: 0.75rem;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s ease;
}

.copy-button:hover {
  background-color: #f3f4f6;
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.copy-button.small {
  padding: 2px 6px;
  font-size: 0.7rem;
}

.faq-container {
  margin-top: 20px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.faq-item {
  border-bottom: 1px solid #e5e7eb;
}

.faq-item:last-child {
  border-bottom: none;
}

.faq-question {
  width: 100%;
  background: none;
  border: none;
  padding: 20px;
  text-align: left;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background-color 0.2s ease;
}

.faq-question:hover {
  background-color: #f9fafb;
}

.faq-question.active {
  background-color: var(--subtle-blue);
}

.faq-question-text {
  font-size: 1rem;
  font-weight: 500;
  color: #374151;
}

.faq-toggle-icon {
  transition: transform 0.2s ease;
  color: #6b7280;
}

.faq-question.active .faq-toggle-icon {
  transform: rotate(90deg);
}

.faq-answer {
  overflow: hidden;
}

.faq-answer-content {
  padding: 0 20px 20px 20px;
  color: #6b7280;
  line-height: 1.6;
}

.faq-enter-active,
.faq-leave-active {
  transition: all 0.3s ease;
}

.faq-enter-from,
.faq-leave-to {
  max-height: 0;
  opacity: 0;
}

.contact-form-container {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 40px;
  margin-top: 20px;
}

.contact-form {
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 32px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  transition: border-color 0.2s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(64, 86, 183, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 120px;
}

.checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  cursor: pointer;
}

.checkbox-text {
  font-size: 0.875rem;
  color: #374151;
  line-height: 1.4;
}

.privacy-link {
  color: var(--primary-color);
  text-decoration: none;
}

.privacy-link:hover {
  text-decoration: underline;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-top: 24px;
}

.reset-button,
.submit-button {
  padding: 12px 24px;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.reset-button {
  background: none;
  border: 1px solid #d1d5db;
  color: #6b7280;
}

.reset-button:hover {
  background-color: #f9fafb;
  border-color: #9ca3af;
}

.submit-button {
  background-color: var(--primary-color);
  border: 1px solid var(--primary-color);
  color: white;
}

.submit-button:hover:not(:disabled) {
  background-color: var(--dark-blue);
}

.submit-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-card {
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
}

.info-card h3 {
  margin: 0 0 12px 0;
  color: var(--dark-blue);
  font-size: 1rem;
  font-weight: 600;
}

.info-card ul {
  margin: 0;
  padding-left: 16px;
  color: #6b7280;
  font-size: 0.875rem;
}

.info-card li {
  margin-bottom: 6px;
  line-height: 1.4;
}

.toast-message {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 8px;
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
  z-index: 1000;
  animation: slideIn 0.3s ease;
}

.toast-message.success {
  background-color: #10b981;
}

.toast-message.error {
  background-color: #ef4444;
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
  .contact-grid {
    grid-template-columns: 1fr;
  }

  .contact-form-container {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .form-row {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .contact-form {
    padding: 24px;
  }

  .form-actions {
    flex-direction: column;
  }

  .reset-button,
  .submit-button {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .contact-card {
    padding: 16px;
  }

  .contact-form {
    padding: 16px;
  }

  .faq-question {
    padding: 16px;
  }

  .faq-answer-content {
    padding: 0 16px 16px 16px;
  }
}

/* SecurityAuditContactPage.vue 스타일 맨 위에 추가 */

.security-audit-layout {
  display: flex;
  background-color: var(--bright-bg);
  min-height: calc(100vh - 114px);
}

.main-content {
  flex: 1;
  padding: 30px;
  background-color: var(--content-bg);
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  margin: 20px;
}

.mobile-menu-toggle {
  position: fixed;
  top: 20px;
  left: 20px;
  z-index: 1001;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.2s ease;
}

.mobile-menu-toggle:hover {
  background-color: var(--dark-blue);
  transform: scale(1.05);
}

@media (min-width: 769px) {
  .mobile-menu-toggle {
    display: none;
  }
}

@media (max-width: 1024px) {
  .security-audit-layout {
    flex-direction: column;
  }

  .main-content {
    margin: 20px;
  }
}

@media (max-width: 768px) {
  .main-content {
    padding: 20px;
    margin: 10px;
  }
}

/* 기존의 모든 CSS는 그대로 유지 */
</style>
