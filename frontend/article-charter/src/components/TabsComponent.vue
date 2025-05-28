<template>
  <div class="tabs-container card">
    <div class="tab-headers flex">
      <button
        v-for="(tab, index) in tabs"
        :key="index"
        :class="['btn btn-ghost tab-button', { active: selectedTab === index }]"
        @click="selectedTab = index"
        type="button"
      >
        {{ tab.label }}
      </button>
    </div>

    <div class="tab-content mt-4">
      <component :is="tabs[selectedTab]?.component" v-bind="tabs[selectedTab]?.props || {}" />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, defineProps } from 'vue';

const props = defineProps({
  tabs: {
    type: Array,
    required: true,
    // Każdy element: { label: String, component: Component }
  },
});

const selectedTab = ref(0);

// Opcjonalnie możesz nasłuchiwać na zmianę tabs i resetować selectedTab
watch(
  () => props.tabs,
  () => {
    selectedTab.value = 0;
  }
);
</script>

<style scoped>
.tab-headers {
  width: 100%;
  gap: var(--space-sm);
}

.tab-headers.flex > button.tab-button {
  flex: 1 1 0;
  border-radius: var(--radius-md);
  font-weight: 600;
  transition: all var(--transition-fast);
  text-align: center;
  padding-left: var(--space-md);
  padding-right: var(--space-md);
}

.tab-headers button.active {
  background-color: var(--primary);
  color: var(--text-primary);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.tab-headers button:hover:not(.active) {
  background-color: var(--bg-hover);
  color: var(--text-primary);
}

.tab-content {
  color: var(--text-secondary);
}
</style>
