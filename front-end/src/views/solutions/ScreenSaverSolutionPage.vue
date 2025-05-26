<!-- views/solutions/ScreenSaverSolution.vue -->
<template>
  <div>
    <h1 class="page-title">화면보호기 사용 확인</h1>

    <div class="section">
      <h2 class="section-title">개요</h2>
      <p>
        화면보호기는 컴퓨터를 일정 시간 사용하지 않을 때 자동으로 잠금 상태로 전환하여 무단 접근을
        방지하는 중요한 보안 기능입니다. 적절히 구성된 화면보호기는 사용자가 자리를 비운 동안 정보
        유출을 방지하는 데 중요한 역할을 합니다.
      </p>
    </div>

    <div class="section">
      <h2 class="section-title">화면보호기 보안 정책 요구사항</h2>
      <p>다음 화면보호기 보안 정책이 반드시 적용되어 있어야 합니다:</p>
      <ul class="requirement-list">
        <li>
          <div class="requirement-item">
            <div class="requirement-icon success">
              <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path
                  d="M13.854 3.646a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 10.293l6.646-6.647a.5.5 0 0 1 .708 0z"
                />
              </svg>
            </div>
            <div class="requirement-content">
              <strong>화면보호기 활성화:</strong> 화면보호기가 활성화되어 있어야 함
            </div>
          </div>
        </li>
        <li>
          <div class="requirement-item">
            <div class="requirement-icon success">
              <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path
                  d="M8 3.5a.5.5 0 0 0-1 0V9a.5.5 0 0 0 .252.434l3.5 2a.5.5 0 0 0 .496-.868L8 8.71V3.5z"
                />
                <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm7-8A7 7 0 1 1 1 8a7 7 0 0 1 14 0z" />
              </svg>
            </div>
            <div class="requirement-content">
              <strong>대기 시간 설정:</strong> 10분(600초) 이내에 화면보호기가 작동하도록 설정
            </div>
          </div>
        </li>
        <li>
          <div class="requirement-item">
            <div class="requirement-icon success">
              <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path
                  d="M3.5 11.5a3.5 3.5 0 1 1 3.163-5H14L15.5 8 14 9.5l-1-1-1 1-1-1-1 1-1-1-1 1H6.663a3.5 3.5 0 0 1-3.163 2zM2.5 9a1 1 0 1 0 0-2 1 1 0 0 0 0 2z"
                />
              </svg>
            </div>
            <div class="requirement-content">
              <strong>재개 시 암호 요구:</strong> 화면보호기에서 복귀 시 암호 입력 필요
            </div>
          </div>
        </li>
      </ul>
    </div>

    <div class="section">
      <h2 class="section-title">화면보호기 설정 확인 방법 (Windows)</h2>
      <div class="step-container">
        <div class="step-item">
          <div class="step-number">1</div>
          <div class="step-content">
            <h3>화면보호기 설정 열기:</h3>
            <ol class="sub-steps">
              <li>바탕 화면에서 마우스 오른쪽 버튼을 클릭하고 "개인 설정"을 선택합니다.</li>
              <li>왼쪽 메뉴에서 "잠금 화면"을 클릭합니다.</li>
              <li>"화면 보호기 설정"을 클릭합니다.</li>
            </ol>
          </div>
        </div>

        <div class="step-item">
          <div class="step-number">2</div>
          <div class="step-content">
            <h3>화면보호기 설정 확인:</h3>
            <ol class="sub-steps">
              <li>
                화면 보호기 드롭다운 메뉴에서 "없음" 이외의 옵션이 선택되어 있는지 확인합니다.
              </li>
              <li>"대기" 필드가 10분(600초) 이하로 설정되어 있는지 확인합니다.</li>
              <li>"다시 시작할 때 로그온 화면 표시" 체크박스가 선택되어 있는지 확인합니다.</li>
            </ol>
          </div>
        </div>
      </div>
    </div>

    <div class="section">
      <h2 class="section-title">명령줄을 통한 화면보호기 설정 확인</h2>
      <p>다음 명령을 사용하여 현재 화면보호기 설정을 확인할 수 있습니다:</p>

      <!-- <div class="command-section">
        <h4>화면보호기 활성화 상태 확인:</h4>
        <div class="code-block">
          <code>reg query "HKCU\\Control Panel\\Desktop" /v ScreenSaveActive</code>
          <button @click="copyToClipboard('reg query \"HKCU\\\\Control Panel\\\\Desktop\" /v ScreenSaveActive')" class="copy-button" title="클립보드에 복사">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path d="M4 1.5H3a2 2 0 0 0-2 2V14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V3.5a2 2 0 0 0-2-2h-1v1h1a1 1 0 0 1 1 1V14a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V3.5a1 1 0 0 1 1-1h1v-1z"/>
              <path d="M9.5 1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-3a.5.5 0 0 1-.5-.5v-1a.5.5 0 0 1 .5-.5h3zm-3-1A1.5 1.5 0 0 0 5 1.5v1A1.5 1.5 0 0 0 6.5 4h3A1.5 1.5 0 0 0 11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3z"/>
            </svg>
          </button>
        </div>
        <p class="code-description">
          결과값이 1이면 화면보호기가 활성화된 것이고, 0이면 비활성화된 것입니다.
        </p>
      </div>

      <div class="command-section">
        <h4>화면보호기 대기 시간 확인:</h4>
        <div class="code-block">
          <code>reg query "HKCU\\Control Panel\\Desktop" /v ScreenSaveTimeOut</code>
          <button @click="copyToClipboard('reg query \"HKCU\\\\Control Panel\\\\Desktop\" /v ScreenSaveTimeOut')" class="copy-button" title="클립보드에 복사">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path d="M4 1.5H3a2 2 0 0 0-2 2V14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V3.5a2 2 0 0 0-2-2h-1v1h1a1 1 0 0 1 1 1V14a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V3.5a1 1 0 0 1 1-1h1v-1z"/>
              <path d="M9.5 1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-3a.5.5 0 0 1-.5-.5v-1a.5.5 0 0 1 .5-.5h3zm-3-1A1.5 1.5 0 0 0 5 1.5v1A1.5 1.5 0 0 0 6.5 4h3A1.5 1.5 0 0 0 11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3z"/>
            </svg>
          </button>
        </div>
      </div>

      <div class="command-section">
        <h4>암호 보호 설정 확인:</h4>
        <div class="code-block">
          <code>reg query "HKCU\\Control Panel\\Desktop" /v ScreenSaverIsSecure</code>
          <button @click="copyToClipboard('reg query \"HKCU\\\\Control Panel\\\\Desktop\" /v ScreenSaverIsSecure')" class="copy-button" title="클립보드에 복사">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path d="M4 1.5H3a2 2 0 0 0-2 2V14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V3.5a2 2 0 0 0-2-2h-1v1h1a1 1 0 0 1 1 1V14a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V3.5a1 1 0 0 1 1-1h1v-1z"/>
              <path d="M9.5 1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-3a.5.5 0 0 1-.5-.5v-1a.5.5 0 0 1 .5-.5h3zm-3-1A1.5 1.5 0 0 0 5 1.5v1A1.5 1.5 0 0 0 6.5 4h3A1.5 1.5 0 0 0 11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3z"/>
            </svg>
          </button>
        </div>
      </div>
    </div> -->

      <div class="section">
        <h2 class="section-title">화면보호기 설정 변경 방법</h2>
        <div class="step-container">
          <div class="step-item">
            <div class="step-number">1</div>
            <div class="step-content">
              <h3>화면보호기 활성화:</h3>
              <ol class="sub-steps">
                <li>화면 보호기 설정 창에서 화면 보호기 드롭다운 메뉴를 클릭합니다.</li>
                <li>"없음" 이외의 옵션을 선택합니다 (예: "빈 화면").</li>
              </ol>
            </div>
          </div>

          <div class="step-item">
            <div class="step-number">2</div>
            <div class="step-content">
              <h3>대기 시간 설정:</h3>
              <ol class="sub-steps">
                <li>"대기" 필드에 10 이하의 숫자를 입력합니다 (이 값은 분 단위임).</li>
              </ol>
            </div>
          </div>

          <div class="step-item">
            <div class="step-number">3</div>
            <div class="step-content">
              <h3>암호 보호 활성화:</h3>
              <ol class="sub-steps">
                <li>"다시 시작할 때 로그온 화면 표시" 체크박스를 선택합니다.</li>
                <li>"적용" 버튼을 클릭하여 설정을 저장합니다.</li>
              </ol>
            </div>
          </div>
        </div>
      </div>

      <div class="section">
        <h2 class="section-title">화면보호기 보안 모범 사례</h2>
        <div class="best-practices">
          <div class="practice-item">
            <div class="practice-icon">
              <svg width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                <path
                  d="M8 3.5a.5.5 0 0 0-1 0V9a.5.5 0 0 0 .252.434l3.5 2a.5.5 0 0 0 .496-.868L8 8.71V3.5z"
                />
                <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm7-8A7 7 0 1 1 1 8a7 7 0 0 1 14 0z" />
              </svg>
            </div>
            <div class="practice-content">
              <h4>시간 설정 최적화</h4>
              <p>화면보호기 대기 시간을 5분으로 설정하여 보안 강화</p>
            </div>
          </div>

          <div class="practice-item">
            <div class="practice-icon">
              <svg width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                <path
                  d="M8 4.754a3.246 3.246 0 1 0 0 6.492 3.246 3.246 0 0 0 0-6.492zM5.754 8a2.246 2.246 0 1 1 4.492 0 2.246 2.246 0 0 1-4.492 0z"
                />
                <path
                  d="M9.796 1.343c-.527-1.79-3.065-1.79-3.592 0l-.094.319a.873.873 0 0 1-1.255.52l-.292-.16c-1.64-.892-3.433.902-2.54 2.541l.159.292a.873.873 0 0 1-.52 1.255l-.319.094c-1.79.527-1.79 3.065 0 3.592l.319.094a.873.873 0 0 1 .52 1.255l-.16.292c-.892 1.64.901 3.434 2.541 2.54l.292-.159a.873.873 0 0 1 1.255.52l.094.319c.527 1.79 3.065 1.79 3.592 0l.094-.319a.873.873 0 0 1 1.255-.52l.292.16c1.64.893 3.434-.902 2.54-2.541l-.159-.292a.873.873 0 0 1 .52-1.255l.319-.094c1.79-.527 1.79-3.065 0-3.592l-.319-.094a.873.873 0 0 1-.52-1.255l.16-.292c.893-1.64-.902-3.433-2.541-2.54l-.292.159a.873.873 0 0 1-1.255-.52l-.094-.319z"
                />
              </svg>
            </div>
            <div class="practice-content">
              <h4>간단한 화면보호기 사용</h4>
              <p>빈 화면 또는 간단한 화면보호기 사용(복잡한 화면보호기는 시스템 리소스를 소모)</p>
            </div>
          </div>

          <div class="practice-item">
            <div class="practice-icon">
              <svg width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                <path
                  d="M1 2.828c.885-.37 2.154-.769 3.388-.893 1.33-.134 2.458.063 3.112.752v9.746c-.935-.53-2.12-.603-3.213-.493-1.18.12-2.37.461-3.287.811V2.828zm7.5-.141c.654-.689 1.782-.886 3.112-.752 1.234.124 2.503.523 3.388.893v9.923c-.918-.35-2.107-.692-3.287-.81-1.094-.111-2.278-.039-3.213.492V2.687zM8 1.783C7.015.936 5.587.81 4.287.94c-1.514.153-3.042.672-3.994 1.105A.5.5 0 0 0 0 2.5v11a.5.5 0 0 0 .707.455c.882-.4 2.303-.881 3.68-1.02 1.409-.142 2.59.087 3.223.877a.5.5 0 0 0 .78 0c.633-.79 1.814-1.019 3.222-.877 1.378.139 2.8.62 3.681 1.02A.5.5 0 0 0 16 13.5v-11a.5.5 0 0 0-.293-.455c-.952-.433-2.48-.952-3.994-1.105C10.413.809 8.985.936 8 1.783z"
                />
              </svg>
            </div>
            <div class="practice-content">
              <h4>정책 일관성</h4>
              <p>모든 회사 컴퓨터에 일관된 화면보호기 정책 적용</p>
            </div>
          </div>

          <div class="practice-item">
            <div class="practice-icon">
              <svg width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                <path d="M11 6a3 3 0 1 1-6 0 3 3 0 0 1 6 0z" />
                <path
                  fill-rule="evenodd"
                  d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8zm8-7a7 7 0 0 0-5.468 11.37C3.242 11.226 4.805 10 8 10s4.757 1.225 5.468 2.37A7 7 0 0 0 8 1z"
                />
              </svg>
            </div>
            <div class="practice-content">
              <h4>수동 잠금 습관</h4>
              <p>
                화면보호기와 함께 Windows + L 단축키를 사용하여 자리를 비울 때 수동으로 컴퓨터 잠금
                습관 기르기
              </p>
            </div>
          </div>
        </div>
      </div>

      <div class="section">
        <h2 class="section-title">관리자 연락처</h2>
        <p>화면보호기 설정에 문제가 있는 경우 아래 담당자에게 문의하세요:</p>
        <p><strong>보안관리팀:</strong> 내선 1234 또는 security@example.com</p>
      </div>

      <!-- 토스트 메시지 -->
      <div v-if="showToast" class="toast-message">클립보드에 복사되었습니다!</div>

      <!-- 공통 페이지 네비게이션 컴포넌트 사용 -->
      <PageNavigation :current-path="route.path" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import PageNavigation from '@/components/PageNavigation.vue'

// Vue Router
const route = useRoute()

// 반응형 데이터
const showToast = ref(false)

// 메서드
const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    showToast.value = true

    // 3초 후 토스트 메시지 숨기기
    setTimeout(() => {
      showToast.value = false
    }, 3000)
  } catch (err) {
    console.error('클립보드 복사 실패:', err)
    // 브라우저가 clipboard API를 지원하지 않는 경우 대체 방법
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
      showToast.value = true
      setTimeout(() => {
        showToast.value = false
      }, 3000)
    }
  } catch (err) {
    console.error('Fallback: 클립보드 복사 실패', err)
  }

  document.body.removeChild(textArea)
}
</script>

<style scoped>
.requirement-list {
  list-style: none;
  padding: 0;
  margin: 16px 0;
}

.requirement-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 16px;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #4caf50;
}

.requirement-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  flex-shrink: 0;
}

.requirement-icon.success {
  background-color: #4caf50;
  color: white;
}

.requirement-content {
  flex: 1;
  line-height: 1.5;
}

.step-container {
  margin-top: 20px;
}

.step-item {
  display: flex;
  margin-bottom: 24px;
  padding: 20px;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.step-number {
  width: 40px;
  height: 40px;
  background-color: var(--primary-color);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-right: 20px;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
}

.step-content h3 {
  margin: 0 0 12px 0;
  color: var(--dark-blue);
  font-size: 1.1rem;
}

.sub-steps {
  margin: 12px 0 0 20px;
  padding: 0;
}

.sub-steps li {
  margin-bottom: 8px;
  line-height: 1.5;
}

.command-section {
  margin-bottom: 24px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid var(--primary-color);
}

.command-section h4 {
  margin: 0 0 12px 0;
  color: var(--dark-blue);
  font-size: 1rem;
}

.code-block {
  position: relative;
  background-color: #2d3748;
  color: #f7fafc;
  padding: 12px 50px 12px 16px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  margin: 8px 0;
  overflow-x: auto;
}

.copy-button {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: #f7fafc;
  padding: 6px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.copy-button:hover {
  background: rgba(255, 255, 255, 0.2);
}

.code-description {
  margin: 8px 0 0 0;
  font-size: 0.875rem;
  color: #6b7280;
  font-style: italic;
}

.best-practices {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 16px;
}

.practice-item {
  display: flex;
  align-items: flex-start;
  padding: 16px;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.practice-item:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.practice-icon {
  width: 40px;
  height: 40px;
  background-color: var(--subtle-blue);
  color: var(--primary-color);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  flex-shrink: 0;
}

.practice-content h4 {
  margin: 0 0 8px 0;
  color: var(--dark-blue);
  font-size: 1rem;
  font-weight: 600;
}

.practice-content p {
  margin: 0;
  font-size: 0.875rem;
  color: #6b7280;
  line-height: 1.5;
}

.toast-message {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background-color: #4caf50;
  color: white;
  padding: 12px 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  animation: slideIn 0.3s ease;
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
  .step-item {
    flex-direction: column;
  }

  .step-number {
    margin-right: 0;
    margin-bottom: 16px;
  }

  .best-practices {
    grid-template-columns: 1fr;
  }

  .practice-item {
    flex-direction: column;
    text-align: center;
  }

  .practice-icon {
    margin-right: 0;
    margin-bottom: 12px;
  }
}
</style>
