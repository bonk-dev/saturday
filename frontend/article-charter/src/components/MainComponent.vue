<template>
  <div class="layout">
    <div class="chart-panel">
      <DynamicChat v-if="chartData" :chartPayload="chartData" :chartNames="chartNames" />
      <TableBuilder v-if="chartData" :table="chartData.table" :fullPayload="request" />
    </div>
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
import TableBuilder from './Chart/TableBuilder.vue';

const chartData = ref(null);
const chartNames = ref(null);
const request = ref(null);

function handleQueryResult(payload) {
  chartData.value = payload.result;
  chartNames.value = payload.chart_names;
  request.value = payload.form;
}

const tabs = [
  {
    label: 'Query Builder',
    component: QueryBuilder,
    props: {
      onSubmit: handleQueryResult,
    },
  },
  { label: 'Fetch data', component: DatabaseInserts },
];
</script>

<style scoped>
.layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.chart-panel {
  flex: 2;
  padding: 20px;
  overflow-y: auto;
}

.builder-panel {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}
</style>
