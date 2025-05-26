<!-- views/SecurityAuditSolutions.vue -->
<template>
  <div>
    <h1 class="page-title">보안 감사 조치방법</h1>

    <div class="section">
      <h2 class="section-title">조치방법 개요</h2>
      <p>
        이 페이지에서는 정보보안 감사에서 확인해야 할 주요 항목에 대한 조치방법을 안내합니다. 모든
        가이드는 조직의 보안 정책을 준수하기 위한 기본적인 설정 방법과 점검 사항을 제공합니다.
      </p>
    </div>

    <div class="section">
      <h2 class="section-title">항목별 상세 가이드</h2>
      <div class="solutions-grid">
        <RouterLink
          v-for="(item, index) in solutionItems"
          :key="index"
          :to="item.path"
          class="solution-card-link"
        >
          <div class="solution-card" @mouseenter="handleMouseEnter" @mouseleave="handleMouseLeave">
            <div class="solution-icon">
              <component :is="getIconComponent(item.id)" />
            </div>
            <h3 class="solution-title">{{ item.title }}</h3>
            <p class="solution-description">{{ item.description }}</p>
            <div class="solution-arrow">
              <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path
                  fill-rule="evenodd"
                  d="M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z"
                />
              </svg>
            </div>
          </div>
        </RouterLink>
      </div>
    </div>

    <!-- 추가 도움말 섹션 -->
    <div class="section">
      <h2 class="section-title">추가 도움말</h2>
      <div class="help-grid">
        <div class="help-card">
          <div class="help-icon">
            <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
              <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
              <path
                d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"
              />
            </svg>
          </div>
          <h3>일반적인 문제 해결</h3>
          <p>자주 발생하는 보안 설정 문제와 해결 방법을 안내합니다.</p>
        </div>

        <div class="help-card">
          <div class="help-icon">
            <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M3 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1H3zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"
              />
            </svg>
          </div>
          <h3>관리자 문의</h3>
          <p>추가적인 도움이 필요한 경우 IT 보안팀에 문의하세요.</p>
        </div>

        <div class="help-card">
          <div class="help-icon">
            <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
              <path
                d="M14 1a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H4.414A2 2 0 0 0 3 11.586l-2 2V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v12.793a.5.5 0 0 0 .854.353l2.853-2.853A1 1 0 0 1 4.414 12H14a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z"
              />
              <path
                d="M3 3.5a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9a.5.5 0 0 1-.5-.5zM3 6a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9A.5.5 0 0 1 3 6zm0 2.5a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5z"
              />
            </svg>
          </div>
          <h3>정책 문서</h3>
          <p>회사의 보안 정책 및 가이드라인을 확인하세요.</p>
        </div>
      </div>
    </div>

    <!-- 공통 페이지 네비게이션 컴포넌트 사용 -->
    <PageNavigation :current-path="route.path" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import PageNavigation from '@/components/PageNavigation.vue'

// Vue Router
const route = useRoute()

// 솔루션 항목 데이터
const solutionItems = [
  {
    id: 'screen-saver',
    title: '화면보호기 사용',
    path: '/security-audit/solutions/screen-saver',
    description: '화면보호기 10분 이내 설정 및 암호화 적용',
  },
  {
    id: 'auto-run',
    title: '이동매체 자동실행 제한',
    path: '/security-audit/solutions/auto-run',
    description: 'USB 및 외부 저장장치 자동실행 기능 비활성화',
  },
  {
    id: 'antivirus',
    title: '백신 상태 확인',
    path: '/security-audit/solutions/antivirus',
    description: '바이러스 백신 설치, 실시간 보호, 최신 업데이트 확인',
  },
  {
    id: 'password-policy',
    title: '패스워드 길이 및 복잡도',
    path: '/security-audit/solutions/password-policy',
    description: '8자 이상 강력한 패스워드 정책 적용 및 정기적 변경',
  },
  {
    id: 'shared-folder',
    title: '공유폴더 확인',
    path: '/security-audit/solutions/shared-folder',
    description: '불필요한 공유폴더 제거 및 접근 권한 관리',
  },
  {
    id: 'remote-desktop',
    title: '원격데스크톱 제한',
    path: '/security-audit/solutions/remote-desktop',
    description: '원격 접속 비활성화 또는 승인된 사용자로 제한',
  },
  {
    id: 'firewall',
    title: '방화벽 활성화 확인',
    path: '/security-audit/solutions/firewall',
    description: '모든 네트워크 프로필에 방화벽 적용 상태 점검',
  },
]

// 메서드
const getIconComponent = (itemId) => {
  // 실제 아이콘 컴포넌트 대신 SVG를 직접 반환
  const icons = {
    'screen-saver': 'ScreenIcon',
    'auto-run': 'UsbIcon',
    antivirus: 'ShieldIcon',
    'password-policy': 'KeyIcon',
    'shared-folder': 'FolderIcon',
    'remote-desktop': 'MonitorIcon',
    firewall: 'FirewallIcon',
  }

  return icons[itemId] || 'DefaultIcon'
}

const handleMouseEnter = (event) => {
  event.currentTarget.style.transform = 'translateY(-5px)'
  event.currentTarget.style.boxShadow = '0 5px 15px rgba(0,0,0,0.1)'
}

const handleMouseLeave = (event) => {
  event.currentTarget.style.transform = 'translateY(0)'
  event.currentTarget.style.boxShadow = 'none'
}
</script>

<style scoped>
.solutions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 15px;
}

.solution-card-link {
  text-decoration: none;
  color: inherit;
}

.solution-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 24px;
  background-color: #f9f9f9;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  height: 100%;
  box-sizing: border-box;
  position: relative;
  display: flex;
  flex-direction: column;
}

.solution-card:hover {
  border-color: var(--primary-color);
  background-color: white;
}

.solution-icon {
  width: 48px;
  height: 48px;
  margin-bottom: 16px;
  color: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--subtle-blue);
  border-radius: 8px;
}

.solution-title {
  margin: 0 0 12px 0;
  color: #2c5282;
  font-size: 1.1rem;
  font-weight: 600;
}

.solution-description {
  font-size: 0.9rem;
  color: #4a5568;
  line-height: 1.5;
  margin: 0;
  flex-grow: 1;
}

.solution-arrow {
  position: absolute;
  top: 20px;
  right: 20px;
  color: #cbd5e0;
  transition: all 0.3s ease;
}

.solution-card:hover .solution-arrow {
  color: var(--primary-color);
  transform: translateX(4px);
}

.help-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 15px;
}

.help-card {
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  transition: all 0.3s ease;
}

.help-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.help-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 16px;
  color: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--subtle-blue);
  border-radius: 50%;
}

.help-card h3 {
  margin: 0 0 12px 0;
  color: var(--dark-blue);
  font-size: 1rem;
  font-weight: 600;
}

.help-card p {
  font-size: 0.875rem;
  color: #6b7280;
  line-height: 1.5;
  margin: 0;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .solutions-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .help-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .solution-card {
    padding: 20px;
  }

  .help-card {
    padding: 16px;
  }
}

@media (max-width: 480px) {
  .solution-card {
    padding: 16px;
  }

  .solution-title {
    font-size: 1rem;
  }

  .solution-description {
    font-size: 0.875rem;
  }
}
</style>
