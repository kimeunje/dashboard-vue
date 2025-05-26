<!-- views/LoginPage.vue -->
<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>상시보안감사</h1>
        <p v-if="loginStep === 'credentials'">계정에 로그인하세요</p>
        <p v-else-if="loginStep === 'verification'">이메일 인증</p>
      </div>

      <div v-if="error" class="error-message">{{ error }}</div>
      <div v-if="message" class="success-message">{{ message }}</div>

      <!-- 자격증명 입력 단계 -->
      <form
        v-if="loginStep === 'credentials'"
        @submit.prevent="handleCredentialsSubmit"
        class="login-form"
      >
        <div class="form-group">
          <label for="username">사용자 ID</label>
          <input
            type="text"
            id="username"
            v-model="credentials.username"
            required
            placeholder="사용자 ID를 입력하세요"
          />
        </div>

        <div class="form-group">
          <label for="password">비밀번호</label>
          <input
            type="password"
            id="password"
            v-model="credentials.password"
            required
            placeholder="비밀번호를 입력하세요"
          />
        </div>

        <button type="submit" class="login-button" :disabled="loading">
          {{ loading ? '처리 중...' : '다음' }}
        </button>
      </form>

      <!-- 이메일 인증 단계 -->
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
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Vue Router
const router = useRouter()
const route = useRoute()

// Pinia Store
const authStore = useAuthStore()

// 반응형 데이터
const credentials = ref({
  username: '',
  password: '',
})

const verificationEmail = ref('')
const verificationCode = ref('')
const error = ref('')
const message = ref('')
const loading = ref(false)
const loginStep = ref('credentials') // 'credentials' → 'verification' → 'complete'

// 자격증명 확인 및 이메일 인증 코드 요청
const handleCredentialsSubmit = async () => {
  loading.value = true
  error.value = ''
  message.value = ''

  try {
    // 먼저 자격증명(아이디/비밀번호)을 검증
    const credentialData = await authStore.checkCredentials(
      credentials.value.username,
      credentials.value.password,
    )

    if (!credentialData.success) {
      throw new Error(credentialData.message || '아이디 또는 비밀번호가 올바르지 않습니다.')
    }

    // 이메일 주소 설정
    verificationEmail.value = credentialData.email || `${credentials.value.username}@example.com`

    // 이메일 인증 코드 요청
    const verificationData = await authStore.requestVerificationCode(verificationEmail.value)

    if (!verificationData.success) {
      throw new Error(verificationData.message || '인증 코드 발송에 실패했습니다.')
    }

    // 인증 단계로 전환
    message.value = '이메일로 인증 코드가 발송되었습니다. 메일함을 확인해주세요.'
    loginStep.value = 'verification'
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// 이메일 인증 코드 확인 및 최종 로그인
const handleVerificationSubmit = async () => {
  loading.value = true
  error.value = ''
  message.value = ''

  try {
    // 인증 코드 확인 및 로그인 요청
    const result = await authStore.verifyAndLogin(
      verificationEmail.value,
      verificationCode.value,
      credentials.value.username,
      credentials.value.password,
    )

    if (!result.success) {
      throw new Error(result.error || '인증에 실패했습니다.')
    }

    loginStep.value = 'complete'

    // 리디렉션 처리
    const redirectPath = route.query.redirect || '/'
    router.push(redirectPath)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// 이메일 재발송 처리
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
  loginStep.value = 'credentials'
  error.value = ''
  message.value = ''
}
</script>

<style scoped>
/* 로그인 페이지 스타일 */
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
</style>
