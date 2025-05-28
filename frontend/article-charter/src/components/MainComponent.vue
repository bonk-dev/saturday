<template>
  <div class="layout">
    <!-- Wykres: lewa strona, bez scrolla -->
    <div class="chart-panel">
      <DynamicChat v-if="chartData" :chartPayload="chartData" />
    </div>

    <!-- Formularz: prawa strona, z własnym scrollowaniem -->
    <div class="builder-panel">
      <TabsComponent :tabs="tabs" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import DynamicChat from './Chart/DynamicChat.vue';
import QueryBuilder from './Chart/QueryBuilder.vue';
import TabsComponent from './TabsComponent.vue';
import DatabaseInserts from './Inserts/DatabaseInserts.vue';

const chartData = ref(null);

function handleQueryResult(payload) {
  chartData.value = payload;
}

const tabs = [
  {
    label: 'QueryBuilder',
    component: QueryBuilder,
    props: {
      onSubmit: handleQueryResult,
    },
  },
  { label: 'DatabaseInsert', component: DatabaseInserts },
];
</script>

<style scoped>
.layout {
  display: flex;
  height: 100vh; /* pełna wysokość ekranu */
  overflow: hidden;
}

/* Lewy panel z wykresem */
.chart-panel {
  flex: 2;
  padding: 20px;
  overflow: hidden; /* brak scrolla */
}

/* Prawy panel z formularzem */
.builder-panel {
  flex: 1;
  padding: 20px;
  overflow-y: auto; /* scroll tylko w pionie */
}
</style>
