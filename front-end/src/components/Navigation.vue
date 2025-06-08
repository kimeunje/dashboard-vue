<!-- components/Navigation.vue -->
<template>
  <nav class="navigation">
    <!-- 데스크톱 네비게이션 -->
    <ul class="nav-links desktop-nav">
      <li v-for="item in navItems" :key="item.path">
        <RouterLink :to="item.path">{{ item.name }}</RouterLink>
      </li>
    </ul>

    <!-- 모바일 햄버거 버튼 -->
    <button class="mobile-menu-toggle" @click="toggleMobileMenu" aria-label="메뉴 열기">
      <span :class="['hamburger-line', { active: isMobileMenuOpen }]"></span>
      <span :class="['hamburger-line', { active: isMobileMenuOpen }]"></span>
      <span :class="['hamburger-line', { active: isMobileMenuOpen }]"></span>
    </button>

    <!-- 모바일 메뉴 -->
    <div :class="['mobile-menu', { open: isMobileMenuOpen }]">
      <ul class="mobile-nav-links">
        <li v-for="item in navItems" :key="item.path">
          <RouterLink :to="item.path" @click="closeMobileMenu">
            {{ item.name }}
          </RouterLink>
        </li>
      </ul>
    </div>

    <!-- 모바일 메뉴 오버레이 -->
    <div v-if="isMobileMenuOpen" class="mobile-menu-overlay" @click="closeMobileMenu"></div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

// 네비게이션 메뉴 항목
const navItems = [
  { name: '정보보안 감사 현황', path: '/security-audit' },
  { name: '악성메일 모의훈련 현황', path: '/phishing-training' },
  { name: '정보보호 교육 현황', path: '/security-education' },
  { name: '문의사항', path: '/contact' },
]

// 반응형 데이터
const isMobileMenuOpen = ref(false)

// 모바일 메뉴 토글
const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

// 모바일 메뉴 닫기
const closeMobileMenu = () => {
  isMobileMenuOpen.value = false
}
</script>

<!-- CSS는 외부 파일에서 import -->
<style>
@import './styles/Navigation.css';
</style>
