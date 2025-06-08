<!-- components/Header.vue -->
<template>
  <header class="header" id="header">
    <RouterLink :to="getLinkPath()" class="logo-container scale-hover">
      <svg width="24" height="24" fill="white" viewBox="0 0 16 16">
        <path
          d="M8 0a8 8 0 0 0-2.916 15.462c-.074-.534-.144-1.343.03-1.918.159-.533.528-1.707.528-1.707s-.135-.271-.135-.674c0-.631.366-1.102.819-1.102.386 0 .573.29.573.636 0 .388-.246.973-.375 1.515-.107.452.224.816.67.816.805 0 1.347-.847 1.347-1.85 0-.969-.654-1.693-1.846-1.693-1.347 0-2.185 1.007-2.185 2.133 0 .388.129.663.332.872.035.044.078.126.063.158-.066.252-.214.796-.243.907-.35.135-.185.055-.421-.144-.593-.659-.859-1.537-.859-2.401 0-2.028 1.714-4.464 5.106-4.464 2.724 0 4.508 1.97 4.508 4.089 0 2.803-1.56 4.897-3.858 4.897-.771 0-1.5-.418-1.752-.894 0 0-.416 1.65-.507 1.97-.152.553-.501 1.11-.802 1.55 1.009.293 2.077.336 3.144.068 1.068-.285 2.062-.794 2.902-1.493a8 8 0 0 0-1.066-15.789z"
        />
      </svg>
      <div class="logo">{{ scrolled ? getPageTitle() : '나이스디앤비' }}</div>
    </RouterLink>

    <div class="user-controls">
      <div v-if="user" class="user-menu">
        <div class="user-info tablet-hidden">
          <span class="user-name">{{ user.name || user.username }}</span>
          <span class="user-role">
            {{ getUserRoleText(user.role) }}
          </span>
        </div>
        <div class="user-actions">
          <button @click="handleLogout" class="btn btn-transparent logout-button">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path
                fill-rule="evenodd"
                d="M10 12.5a.5.5 0 0 1-.5.5h-8a.5.5 0 0 1-.5-.5v-9a.5.5 0 0 1 .5-.5h8a.5.5 0 0 1 .5.5v2a.5.5 0 0 0 1 0v-2A1.5 1.5 0 0 0 9.5 2h-8A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h8a1.5 1.5 0 0 0 1.5-1.5v-2a.5.5 0 0 0-1 0v2z"
              />
              <path
                fill-rule="evenodd"
                d="M15.854 8.354a.5.5 0 0 0 0-.708l-3-3a.5.5 0 0 0-.708.708L14.293 7.5H5.5a.5.5 0 0 0 0 1h8.793l-2.147 2.146a.5.5 0 0 0 .708.708l3-3z"
              />
            </svg>
            로그아웃
          </button>
        </div>
      </div>
      <RouterLink v-else to="/login" class="btn btn-primary login-link">
        <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
          <path
            fill-rule="evenodd"
            d="M6 12.5a.5.5 0 0 0 .5.5h8a.5.5 0 0 0 .5-.5v-9a.5.5 0 0 0-.5-.5h-8a.5.5 0 0 0-.5.5v2a.5.5 0 0 1-1 0v-2A1.5 1.5 0 0 1 6.5 2h8A1.5 1.5 0 0 1 16 3.5v9a1.5 1.5 0 0 1-1.5 1.5h-8A1.5 1.5 0 0 1 5 12.5v-2a.5.5 0 0 1 1 0v2z"
          />
          <path
            fill-rule="evenodd"
            d="M.146 8.354a.5.5 0 0 1 0-.708l3-3a.5.5 0 1 1 .708.708L1.707 7.5H10.5a.5.5 0 0 1 0 1H1.707l2.147 2.146a.5.5 0 0 1-.708.708l-3-3z"
          />
        </svg>
        로그인
      </RouterLink>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'

defineProps({
  user: {
    type: Object,
    default: null,
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['logout'])

const scrolled = ref(false)

const route = useRoute()

// 현재 경로에 따른 페이지 제목 설정
const getPageTitle = () => {
  const routes = [
    { path: '/', title: '정보보안 감사 현황' },
    { path: '/security-audit', title: '정보보안 감사 현황' },
    { path: '/login', title: '로그인' },
    { path: '/phishing-training', title: '악성메일 모의훈련 현황' },
    { path: '/security-education', title: '정보보호 교육 현황' },
    { path: '/contact', title: '문의사항' },
  ]

  const matchedRoute = routes.find(
    (routeItem) =>
      route.path === routeItem.path ||
      (route.path.startsWith(routeItem.path) && routeItem.path !== '/'),
  )

  return matchedRoute ? matchedRoute.title : '나이스디앤비'
}

// 현재 경로에 따른 링크 경로 결정
const getLinkPath = () => {
  if (!scrolled.value || route.path === '/') {
    return '/'
  }
  return route.path
}

// 사용자 역할 텍스트 변환
const getUserRoleText = (role) => {
  const roleMap = {
    admin: '관리자',
    user: '사용자',
    manager: '관리자',
    employee: '직원',
  }
  return roleMap[role] || '사용자'
}

// 스크롤 이벤트 처리
const handleScroll = () => {
  scrolled.value = window.scrollY > 50
}

// 로그아웃 처리 함수
const handleLogout = (e) => {
  e.preventDefault()
  emit('logout')
}

// 라이프사이클 훅
onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<!-- CSS는 외부 파일에서 import -->
<style scoped>
@import './styles/Header.css';
</style>
