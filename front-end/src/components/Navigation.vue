<!-- Navigation.vue 수정 사항 -->

<script setup>
import { ref, computed } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const authStore = useAuthStore()

// 관리자 메뉴 표시 여부
const isAdmin = computed(() => {
  return authStore.user?.role === 'admin' || authStore.user?.username === 'admin'
})

// 관리자 메뉴 확장/축소 상태
const adminMenuExpanded = ref(false)

// 네비게이션 메뉴 아이템들
const menuItems = computed(() => {
  const baseItems = [
    {
      name: 'SecurityAudit',
      path: '/security-audit',
      title: '정보보안 감사',
      icon: 'shield-check',
    },
    {
      name: 'SecurityScore',
      path: '/security-score',
      title: '종합 보안 점수',
      icon: 'trophy',
    },
    {
      name: 'SecurityEducation',
      path: '/security-education',
      title: '정보보호 교육',
      icon: 'book',
    },
    {
      name: 'PhishingTraining',
      path: '/phishing-training',
      title: '악성메일 모의훈련',
      icon: 'mail',
    },
    {
      name: 'Contact',
      path: '/contact',
      title: '문의하기',
      icon: 'message-circle',
    },
  ]

  // 관리자인 경우 관리자 메뉴 추가
  if (isAdmin.value) {
    baseItems.push({
      name: 'AdminMenu',
      title: '관리자 메뉴',
      icon: 'settings',
      isDropdown: true,
      expanded: adminMenuExpanded.value,
      children: [
        {
          name: 'AdminDashboard',
          path: '/admin/dashboard',
          title: '대시보드',
          icon: 'dashboard',
        },
        {
          name: 'AdminUserManagement',
          path: '/admin/users',
          title: '사용자 관리',
          icon: 'users',
        },
        {
          name: 'AdminPhishingTrainingManagement',
          path: '/admin/training',
          title: '모의훈련 관리',
          icon: 'training',
        },
        {
          name: 'AdminExceptionManagement',
          path: '/admin/exceptions',
          title: '예외 관리',
          icon: 'exception',
        },
        {
          name: 'AdminManualCheck',
          path: '/admin/manual-check',
          title: '수시 점검 관리',
          icon: 'check-circle',
        },
      ],
    })
  }

  return baseItems
})

// 현재 라우트 확인
const isCurrentRoute = (routeName) => {
  return route.name === routeName
}

// 현재 라우트가 관리자 페이지인지 확인
const isAdminRoute = computed(() => {
  return route.path.startsWith('/admin')
})

// 관리자 메뉴 토글
const toggleAdminMenu = () => {
  adminMenuExpanded.value = !adminMenuExpanded.value
}

// 자동으로 관리자 메뉴 확장 (관리자 페이지 접근 시)
if (isAdminRoute.value) {
  adminMenuExpanded.value = true
}
</script>

<template>
  <nav class="navigation">
    <div class="nav-container">
      <ul class="nav-menu">
        <li
          v-for="item in menuItems"
          :key="item.name"
          class="nav-item"
          :class="{
            dropdown: item.isDropdown,
            expanded: item.expanded,
            active: isCurrentRoute(item.name) || (item.isDropdown && isAdminRoute),
          }"
        >
          <!-- 일반 메뉴 아이템 -->
          <RouterLink
            v-if="!item.isDropdown"
            :to="item.path"
            class="nav-link"
            :class="{ active: isCurrentRoute(item.name) }"
          >
            <Icon :name="item.icon" />
            <span>{{ item.title }}</span>
          </RouterLink>

          <!-- 드롭다운 메뉴 아이템 (관리자 메뉴) -->
          <div v-else class="dropdown-toggle" @click="toggleAdminMenu">
            <div class="nav-link" :class="{ active: isAdminRoute }">
              <Icon :name="item.icon" />
              <span>{{ item.title }}</span>
              <Icon name="chevron-down" class="dropdown-icon" :class="{ rotated: item.expanded }" />
            </div>
          </div>

          <!-- 드롭다운 메뉴 내용 -->
          <ul v-if="item.isDropdown && item.expanded" class="dropdown-menu">
            <li v-for="child in item.children" :key="child.name" class="dropdown-item">
              <RouterLink
                :to="child.path"
                class="dropdown-link"
                :class="{ active: isCurrentRoute(child.name) }"
              >
                <Icon :name="child.icon" />
                <span>{{ child.title }}</span>
              </RouterLink>
            </li>
          </ul>
        </li>
      </ul>
    </div>
  </nav>
</template>

<style scoped>
/* 네비게이션 기본 스타일 */
.navigation {
  background-color: var(--primary-color);
  color: white;
  position: sticky;
  top: 0;
  z-index: 1000;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.nav-menu {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  align-items: center;
}

.nav-item {
  position: relative;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  transition: all 0.3s ease;
  white-space: nowrap;
  font-weight: 500;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-link.active {
  background-color: var(--dark-blue);
  color: white;
  border-bottom: 2px solid white;
}

/* 드롭다운 스타일 */
.dropdown-toggle {
  cursor: pointer;
}

.dropdown-icon {
  margin-left: auto;
  transition: transform 0.3s ease;
}

.dropdown-icon.rotated {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  min-width: 200px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  overflow: hidden;
  z-index: 1001;
  list-style: none;
  margin: 0;
  padding: 8px 0;
}

.dropdown-item {
  margin: 0;
}

.dropdown-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  color: #374151;
  text-decoration: none;
  transition: all 0.2s ease;
  font-weight: 500;
}

.dropdown-link:hover {
  background-color: #f3f4f6;
  color: var(--primary-color);
}

.dropdown-link.active {
  background-color: var(--light-blue);
  color: var(--primary-color);
  border-left: 3px solid var(--primary-color);
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .nav-menu {
    flex-direction: column;
    align-items: stretch;
  }

  .nav-item {
    width: 100%;
  }

  .nav-link {
    justify-content: center;
    padding: 10px;
  }

  .dropdown-menu {
    position: static;
    box-shadow: none;
    background-color: rgba(255, 255, 255, 0.1);
    margin: 0;
  }

  .dropdown-link {
    color: rgba(255, 255, 255, 0.9);
    padding-left: 32px;
  }

  .dropdown-link:hover {
    background-color: rgba(255, 255, 255, 0.1);
    color: white;
  }

  .dropdown-link.active {
    background-color: rgba(255, 255, 255, 0.2);
    color: white;
    border-left: 3px solid white;
  }
}
</style>
