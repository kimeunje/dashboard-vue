<!-- components/PageNavigation.vue -->
<template>
  <div class="pagination">
    <button @click="goToPrevious" :disabled="!prevItem" :class="{ disabled: !prevItem }">
      {{ prevItem ? `이전: ${prevItem.title}` : '이전' }}
    </button>

    <button @click="goToNext" :disabled="!nextItem" :class="{ disabled: !nextItem }">
      {{ nextItem ? `다음: ${nextItem.title}` : '다음' }}
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { getPreviousMenuItem, getNextMenuItem } from '@/data/security-audit-config'

// Props 정의
const props = defineProps({
  currentPath: {
    type: String,
    required: true,
  },
})

// Vue Router
const router = useRouter()

// 계산된 속성
const prevItem = computed(() => getPreviousMenuItem(props.currentPath))
const nextItem = computed(() => getNextMenuItem(props.currentPath))

// 메서드
const goToPrevious = () => {
  if (prevItem.value) {
    router.push(prevItem.value.path)
  }
}

const goToNext = () => {
  if (nextItem.value) {
    router.push(nextItem.value.path)
  }
}
</script>

<style scoped>
.pagination {
  display: flex;
  justify-content: space-between;
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid var(--light-blue);
}

.pagination button {
  background-color: var(--primary-color);
  color: var(--white);
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.pagination button:hover:not(.disabled) {
  background-color: var(--dark-blue);
  transform: translateY(-1px);
}

.pagination button.disabled {
  background-color: var(--gray);
  cursor: not-allowed;
  opacity: 0.6;
}

.pagination button:active:not(.disabled) {
  transform: translateY(0);
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .pagination {
    flex-direction: column;
    gap: 10px;
  }

  .pagination button {
    width: 100%;
    padding: 12px 16px;
  }
}
</style>
