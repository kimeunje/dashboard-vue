<template>
  <div class="stats-card">
    <h3 class="stats-title">{{ title }}</h3>
    <p class="stats-value" :class="getColorClass">
      {{ value }}
    </p>
    <p class="stats-subtitle">{{ subtitle }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  value: {
    type: [String, Number],
    required: true,
  },
  subtitle: {
    type: String,
    default: '',
  },
  valueColor: {
    type: String,
    default: '',
  },
})

const getColorClass = computed(() => {
  switch (props.valueColor) {
    case 'green':
      return 'color-green'
    case 'red':
      return 'color-red'
    case 'blue':
      return 'color-blue'
    default:
      return 'color-default'
  }
})
</script>

<style scoped>
.stats-card {
  background-color: white;
  border-radius: 4px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stats-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.stats-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: #666;
  margin: 0 0 8px 0;
}

.stats-value {
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0 0 8px 0;
}

.stats-value.color-green {
  color: #4caf50;
}

.stats-value.color-red {
  color: #f44336;
}

.stats-value.color-blue {
  color: #2196f3;
}

.stats-value.color-default {
  color: #333;
}

.stats-subtitle {
  font-size: 0.875rem;
  color: #666;
  margin: 0;
}

@media (max-width: 768px) {
  .stats-card {
    padding: 12px;
  }

  .stats-value {
    font-size: 1.3rem;
  }

  .stats-title,
  .stats-subtitle {
    font-size: 0.8rem;
  }
}
</style>
