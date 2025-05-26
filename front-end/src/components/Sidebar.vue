<!-- src/components/Sidebar.vue -->
<!-- Sidebar.vue 템플릿을 다음과 같이 수정 -->
<template>
  <!-- 데스크톱에서는 항상 표시, 모바일에서는 조건부 표시 -->
  <aside v-show="!isMobile || isOpen" :class="['sidebar', { 'mobile-open': isMobile && isOpen }]">
    <div class="sidebar-title">상시보안감사</div>
    <ul class="sidebar-menu">
      <li v-for="mainItem in MENU_STRUCTURE" :key="mainItem.id" class="sidebar-main-item">
        <RouterLink
          :to="mainItem.path"
          :class="{ active: isParentPath(mainItem.path) }"
          @click="isMobile && closeSidebar()"
        >
          {{ mainItem.title }}
        </RouterLink>

        <!-- 하위 메뉴가 있고, 현재 항목이 활성화되어 있으면 하위 메뉴 표시 -->
        <ul
          v-if="mainItem.subItems.length > 0 && isParentPath(mainItem.path)"
          class="sidebar-submenu"
        >
          <li v-for="subItem in mainItem.subItems" :key="subItem.id">
            <RouterLink
              :to="subItem.path"
              :class="{ active: isPathActive(subItem.path) }"
              @click="isMobile && closeSidebar()"
            >
              {{ subItem.title }}
            </RouterLink>
          </li>
        </ul>
      </li>
    </ul>
  </aside>

  <!-- 모바일 오버레이 -->
  <div v-if="isMobile && isOpen" class="sidebar-overlay" @click="closeSidebar"></div>
</template>

<script setup>
// src/components/Sidebar.vue의 <script setup> 부분에 추가

import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { MENU_STRUCTURE } from '@/data/security-audit-config'

// Vue Router
const route = useRoute()

// 반응형 데이터 추가
const isMobile = ref(false)
const isOpen = ref(false)

// 기존 메서드들...
const isPathActive = (path) => {
  return route.path === path
}

const isParentPath = (path) => {
  if (route.path === path) return true
  return route.path.startsWith(`${path}/`)
}

// 새로 추가할 메서드들
const checkScreenSize = () => {
  isMobile.value = window.innerWidth <= 768
  if (!isMobile.value) {
    isOpen.value = false
  }
}

const toggleSidebar = () => {
  isOpen.value = !isOpen.value
}

const closeSidebar = () => {
  isOpen.value = false
}

// 라이프사이클 훅
onMounted(() => {
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
})

// 외부에서 사용할 수 있도록 expose
defineExpose({
  toggleSidebar,
  isOpen,
  isMobile,
})
</script>

<style scoped>
.sidebar {
  width: 250px;
  background-color: white;
  padding: 20px 0;
  border-right: 1px solid #e0e4e9;
  border-radius: 8px;
  margin: 20px 0 20px 20px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.sidebar-title {
  font-size: 18px;
  font-weight: bold;
  color: var(--dark-blue);
  padding: 0 20px 15px 20px;
  border-bottom: 1px solid #e0e4e9;
}

.sidebar-menu {
  list-style: none;
  margin-top: 20px;
  padding: 0;
}

.sidebar-menu li {
  padding: 8px 20px;
}

.sidebar-main-item {
  margin-bottom: 5px;
}

.sidebar-menu a {
  color: var(--dark-gray);
  display: block;
  transition: all 0.3s;
  padding: 8px 12px;
  border-radius: 4px;
  text-decoration: none;
}

.sidebar-menu a:hover,
.sidebar-menu a.active {
  color: var(--primary-color);
  font-weight: bold;
  background-color: var(--light-blue);
}

.sidebar-submenu {
  list-style: none;
  margin-top: 5px;
  margin-bottom: 10px;
  padding-left: 15px;
}

.sidebar-submenu li {
  padding: 5px 0;
}

.sidebar-submenu a {
  font-size: 0.9em;
  color: var(--dark-gray);
}

.sidebar-submenu a:hover,
.sidebar-submenu a.active {
  color: var(--primary-color);
  font-weight: bold;
  background-color: var(--light-blue);
}

/* 반응형 디자인 */
@media (max-width: 1024px) {
  .sidebar {
    position: fixed;
    left: -250px;
    top: 0;
    height: 100vh;
    z-index: 1000;
    transition: left 0.3s ease;
    margin: 0;
    border-radius: 0;
  }

  .sidebar.open {
    left: 0;
  }

  .sidebar-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 999;
  }
}

@media (max-width: 768px) {
  .sidebar {
    width: 280px;
  }
}

/* 기존 CSS는 그대로 두고, 반응형 부분만 다음과 같이 수정 */

/* 반응형 디자인 - 768px 이하에서 사이드바 숨김 */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: -250px;
    top: 0;
    height: 100vh;
    z-index: 1000;
    transition: left 0.3s ease;
    margin: 0;
    border-radius: 0;
    border-right: 1px solid #e0e4e9;
    width: 280px;
  }

  .sidebar.mobile-open {
    left: 0;
  }
}

/* 사이드바 오버레이 */
.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 999;
}
</style>
