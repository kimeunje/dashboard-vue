<!-- views/LoginPage.vue - IP 인증으로 수정 -->
<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>정보보안 감사 시스템</h1>
        <p v-if="loginStep === 'ip_check'">IP 기반 자동 인증</p>
        <p v-else-if="loginStep === 'verification'">이메일 인증</p>
      </div>

      <div v-if="error" class="error-message">{{ error }}</div>
      <div v-if="message" class="success-message">{{ message }}</div>

      <!-- IP 인증 단계 -->
      <div v-if="loginStep === 'ip_check'" class="login-form">
        <div class="ip-info-card">
          <div class="ip-icon">
            <svg width="32" height="32" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8zm7.5-6.923c-.67.204-1.335.82-1.887 1.855A7.97 7.97 0 0 0 5.145 4H7.5V1.077zM4.09 4a9.267 9.267 0 0 1 .64-1.539 6.7 6.7 0 0 1 .597-.933A7.025 7.025 0 0 0 2.255 4H4.09zm-.582 3.5c.03-.877.138-1.718.312-2.5H1.674a6.958 6.958 0 0 0-.656 2.5h2.49zM4.847 5a12.5 12.5 0 0 0-.338 2.5H7.5V5H4.847zM8.5 5v2.5h2.99a12.495 12.495 0 0 0-.337-2.5H8.5zM4.51 8.5a12.5 12.5 0 0 0 .337 2.5H7.5V8.5H4.51zm3.99 0V11h2.653c.187-.765.306-1.608.338-2.5H8.5zM5.145 12c.138.386.295.744.468 1.068.552 1.035 1.218 1.65 1.887 1.855V12H5.145zm.182 2.472a6.696 6.696 0 0 1-.597-.933A9.268 9.268 0 0 1 4.09 12H2.255a7.024 7.024 0 0 0 3.072 2.472zM3.82 11a13.652 13.652 0 0 1-.312-2.5h-2.49c.062.89.291 1.733.656 2.5H3.82zm6.853 3.472A7.024 7.024 0 0 0 13.745 12H11.91a9.27 9.27 0 0 1-.64 1.539 6.688 6.688 0 0 1-.597.933zM8.5 12v2.923c.67-.204 1.335-.82 1.887-1.855.173-.324.33-.682.468-1.068H8.5zm3.68-1h2.146c.365-.767.594-1.61.656-2.5h-2.49a13.65 13.65 0 0 1-.312 2.5zm2.802-3.5a6.959 6.959 0 0 0-.656-2.5H12.18c.174.782.282 1.623.312 2.5h2.49zM11.27 2.461c.247.464.462.98.64 1.539h1.835a7.024 7.024 0 0 0-3.072-2.472c.218.284.418.598.597.933zM10.855 4a7.966 7.966 0 0 0-.468-1.068C9.835 1.897 9.17 1.282 8.5 1.077V4h2.355z"
              />
            </svg>
          </div>
          <div class="ip-info">
            <h3>자동 IP 인증</h3>
            <p>
              현재 IP: <strong>{{ currentIp || '확인 중...' }}</strong>
            </p>
            <p class="ip-description">사설망 환경에서 IP 주소로 자동 사용자 인증을 진행합니다.</p>
          </div>
        </div>

        <button @click="handleIpAuthentication" class="login-button" :disabled="loading">
          {{ loading ? 'IP 인증 중...' : 'IP 인증 시작' }}
        </button>

        <div class="ip-help">
          <div class="help-item">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
              <path
                d="M5.255 5.786a.237.237 0 0 0 .241.247h.825c.138 0 .248-.113.266-.25.09-.656.54-1.134 1.342-1.134.686 0 1.314.343 1.314 1.168 0 .635-.374.927-.965 1.371-.673.489-1.206 1.06-1.168 1.987l.003.217a.25.25 0 0 0 .25.246h.811a.25.25 0 0 0 .25-.25v-.105c0-.718.273-.927 1.01-1.486.609-.463 1.244-.977 1.244-2.056 0-1.511-1.276-2.241-2.673-2.241-1.267 0-2.655.59-2.75 2.286zm1.557 5.763c0 .533.425.927 1.01.927.609 0 1.028-.394 1.028-.927 0-.552-.42-.94-1.029-.94-.584 0-1.009.388-1.009.94z"
              />
            </svg>
            <p class="help-text">이 시스템은 IP 주소 기반 자동 인증을 사용합니다.</p>
          </div>
          <div class="help-item">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M8.47 2.47a.75.75 0 0 1 1.06 0l4.5 4.5a.75.75 0 0 1-1.06 1.06L9.75 4.81V15a.75.75 0 0 1-1.5 0V4.81L5.03 8.03a.75.75 0 0 1-1.06-1.06l4.5-4.5Z"
              />
            </svg>
            <p class="help-text">접근이 거부될 경우 운영실(내선 2533)에 문의하세요.</p>
          </div>
        </div>
      </div>

      <!-- 이메일 인증 단계 (기존 유지) -->
      <form
        v-if="loginStep === 'verification'"
        @submit.prevent="handleVerificationSubmit"
        class="login-form"
      >
        <div class="verification-info">
          <p>
            <strong>{{ verificationEmail }}</strong
            >으로 전송된 인증 코드를 입력해주세요.
          </p>
          <div class="user-info">
            <p>
              인증된 사용자: <strong>{{ authenticatedUser.name }}</strong> ({{
                authenticatedUser.dept
              }})
            </p>
            <p class="ip-info-small">접속 IP: {{ authenticatedUser.client_ip }}</p>
          </div>
        </div>

        <div class="form-group">
          <label for="verification-code">인증 코드</label>
          <input
            type="text"
            id="verification-code"
            v-model="verificationCode"
            required
            placeholder="인증 코드 6자리를 입력하세요"
            maxlength="6"
            pattern="[0-9]{6}"
            style="letter-spacing: 2px; font-weight: 600; text-align: center"
          />
        </div>

        <div class="verification-options">
          <button type="button" class="text-button" @click="handleBackToCredentials">
            이전으로 돌아가기
          </button>
          <button type="button" class="text-button" @click="handleResendCode" :disabled="loading">
            인증 코드 재발송
          </button>
        </div>

        <button type="submit" class="login-button" :disabled="loading">
          {{ loading ? '인증 중...' : '인증 및 로그인' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Vue Router
const router = useRouter()
const route = useRoute()

// Pinia Store
const authStore = useAuthStore()

// 반응형 데이터
const authenticatedUser = ref({
  username: '',
  name: '',
  dept: '',
  email: '',
  client_ip: '',
})

const verificationEmail = ref('')
const verificationCode = ref('')
const error = ref('')
const message = ref('')
const loading = ref(false)
const loginStep = ref('ip_check') // 'ip_check' → 'verification' → 'complete'
const currentIp = ref('')

// 현재 IP 정보 가져오기
const getCurrentIp = async () => {
  try {
    const response = await fetch('/api/auth/ip-info', {
      credentials: 'include',
    })

    if (response.ok) {
      const data = await response.json()
      currentIp.value = data.client_ip
    }
  } catch (err) {
    console.warn('IP 정보 조회 실패:', err)
    currentIp.value = '확인 불가'
  }
}

// IP 인증 처리
const handleIpAuthentication = async () => {
  loading.value = true
  error.value = ''
  message.value = ''

  try {
    console.log('IP 인증 시작...')

    // IP 기반 인증 요청
    const response = await authStore.checkIpAuthentication()

    if (!response.success) {
      throw new Error(response.message || 'IP 인증에 실패했습니다.')
    }

    // 인증된 사용자 정보 저장
    authenticatedUser.value = {
      username: response.username,
      name: response.name,
      dept: response.dept,
      email: response.email,
      client_ip: response.client_ip,
    }

    // 이메일 주소 설정
    verificationEmail.value = response.email

    // 이메일 인증 코드 요청
    const verificationData = await authStore.requestVerificationCode(verificationEmail.value)

    if (!verificationData.success) {
      throw new Error(verificationData.message || '인증 코드 발송에 실패했습니다.')
    }

    // 인증 단계로 전환
    message.value = `${authenticatedUser.value.name}님, 이메일로 인증 코드가 발송되었습니다.`
    loginStep.value = 'verification'
  } catch (err) {
    console.error('IP 인증 오류:', err)
    error.value = err.message

    // 특정 오류에 대한 추가 안내
    if (
      err.message.includes('허용되지 않은') ||
      err.message.includes('등록된 사용자를 찾을 수 없습니다')
    ) {
      error.value += ' 운영실에 IP 등록을 요청하세요.'
    }
  } finally {
    loading.value = false
  }
}

// 이메일 인증 코드 확인 및 최종 로그인 (기존 유지)
const handleVerificationSubmit = async () => {
  loading.value = true
  error.value = ''
  message.value = ''

  try {
    const result = await authStore.verifyAndLogin(
      verificationEmail.value,
      verificationCode.value,
      authenticatedUser.value.username,
    )

    if (!result.success) {
      throw new Error(result.error || '인증에 실패했습니다.')
    }

    loginStep.value = 'complete'

    // 리디렉션 처리
    const redirectPath = route.query.redirect || '/'
    router.push(redirectPath)
  } catch (err) {
    console.error('이메일 인증 오류:', err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// 이메일 재발송 처리 (기존 유지)
const handleResendCode = async () => {
  loading.value = true
  message.value = ''

  try {
    const response = await authStore.requestVerificationCode(verificationEmail.value)

    if (response.success) {
      message.value = '인증 코드가 이메일로 재발송되었습니다.'
    } else {
      throw new Error(response.message || '인증 코드 재발송에 실패했습니다.')
    }
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// 처음으로 돌아가기
const handleBackToCredentials = () => {
  loginStep.value = 'ip_check'
  error.value = ''
  message.value = ''
  verificationCode.value = ''
}

// 라이프사이클 훅
onMounted(() => {
  getCurrentIp()
})
</script>

<style scoped>
/* 기존 스타일 유지 + IP 인증 관련 스타일 추가 */

/* IP 인증 카드 스타일 */
.ip-info-card {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, var(--subtle-blue), #f0f7ff);
  border: 1px solid #e0e4e9;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
}

.ip-icon {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, var(--primary-color), var(--dark-blue));
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-right: 20px;
  flex-shrink: 0;
}

.ip-info h3 {
  margin: 0 0 8px 0;
  color: var(--dark-blue);
  font-size: 1.25rem;
  font-weight: 600;
}

.ip-info p {
  margin: 4px 0;
  color: #5a6a7e;
  font-size: 0.95rem;
  line-height: 1.4;
}

.ip-description {
  font-size: 0.875rem !important;
  opacity: 0.8;
}

.ip-help {
  margin-top: 20px;
  padding: 16px;
  background-color: #f8fafc;
  border-radius: 8px;
  border-left: 4px solid var(--primary-color);
}

.help-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 8px;
}

.help-item:last-child {
  margin-bottom: 0;
}

.help-item svg {
  margin-top: 2px;
  color: var(--primary-color);
  flex-shrink: 0;
}

.help-text {
  font-size: 0.875rem;
  color: #5a6a7e;
  margin: 0;
  line-height: 1.4;
}

.user-info {
  background-color: #f0f7ff;
  padding: 12px;
  border-radius: 8px;
  margin: 12px 0;
  border-left: 4px solid var(--primary-color);
}

.user-info p {
  margin: 4px 0;
  font-size: 0.875rem;
  color: var(--dark-blue);
}

.ip-info-small {
  font-size: 0.8rem !important;
  color: #6b7280 !important;
  font-family: monospace;
}

/* 기존 로그인 스타일들 */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 65px);
  padding: 20px;
  box-sizing: border-box;
  background-color: var(--bright-bg);
  width: 100%;
}

.login-card {
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 420px;
  padding: 40px 30px;
  max-height: calc(100vh - 105px);
  overflow-y: auto;
  border: 1px solid #e0e4e9;
  transition: transform 0.3s ease;
}

.login-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: var(--dark-blue);
  margin-bottom: 8px;
}

.login-header p {
  font-size: 16px;
  color: #5a6a7e;
}

.error-message {
  background-color: #fef2f2;
  color: #b91c1c;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 20px;
  font-size: 14px;
}

.success-message {
  background-color: #ecfdf5;
  color: #047857;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 20px;
  font-size: 14px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: var(--dark-blue);
}

.form-group input {
  padding: 12px 16px;
  border: 1px solid #e0e4e9;
  border-radius: 6px;
  font-size: 15px;
  transition: all 0.3s ease;
  background-color: var(--subtle-blue);
}

.form-group input:focus {
  border-color: var(--primary-color);
  outline: none;
  box-shadow: 0 0 0 2px rgba(64, 86, 183, 0.2);
  background-color: white;
}

.verification-info {
  background-color: var(--subtle-blue);
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 20px;
}

.verification-info p {
  font-size: 14px;
  color: #5a6a7e;
  margin: 0;
}

.verification-info strong {
  color: var(--dark-blue);
}

.verification-options {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.text-button {
  background: none;
  border: none;
  color: var(--primary-color);
  font-size: 14px;
  cursor: pointer;
  padding: 0;
  font-weight: 500;
  transition: color 0.2s;
}

.text-button:hover {
  color: var(--dark-blue);
  text-decoration: underline;
}

.text-button:disabled {
  color: var(--gray);
  cursor: not-allowed;
  text-decoration: none;
}

.login-button {
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 14px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.login-button:hover {
  background-color: var(--dark-blue);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.login-button:disabled {
  background-color: #a0aec0;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 반응형 디자인 */
@media (max-width: 480px) {
  .ip-info-card {
    flex-direction: column;
    text-align: center;
  }

  .ip-icon {
    margin-right: 0;
    margin-bottom: 16px;
  }
}
</style>
