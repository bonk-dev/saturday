<template>
  <div class="container">
    <h1 class="text-center mb-6">Query Builder</h1>

    <!-- x_axis -->
    <div class="form-group">
      <XAxis v-model="form.x_axis" />
    </div>

    <!-- y_axis_datasets -->
    <!-- y_axis_datasets -->
    <div class="card mb-6">
      <div class="card-header">
        <h2 class="card-title">Y axis</h2>
      </div>
      <div class="card-content grid gap-4">
        <div v-for="(dataset, i) in form.y_axis_datasets" :key="i" class="border rounded p-4 card">
          <YAxisDatasetItem v-model="form.y_axis_datasets[i]" />

          <div class="flex-center mt-4" v-if="form.y_axis_datasets.length > 1">
            <button
              class="btn btn-secondary btn-sm remove-y-axis-btn"
              @click="removeYAxisDataset(i)"
            >
              × Remove
            </button>
          </div>
        </div>
        <button class="btn btn-secondary mt-2" @click="addYAxisDataset">+ Add Dataset</button>
      </div>
    </div>
    <!-- filters -->
    <div class="card mb-6">
      <div class="card-header">
        <h2 class="card-title">Filters</h2>
      </div>
      <div class="card-content grid">
        <FilterItem v-for="(filter, i) in form.filters" :key="i" v-model="form.filters[i]" />
        <div class="flex-center mt-4" v-if="form.filters.length > 0">
          <button class="btn btn-secondary btn-sm remove-y-axis-btn" @click="removeFilter(i)">
            × Remove
          </button>
        </div>
        <button class="btn btn-secondary mt-2" @click="addFilter">+ Add Filter</button>
      </div>
    </div>
    <div class="card mb-4">
      <div class="form-group">
        <div class="card-header">
          <h2 class="card-title">Chart type</h2>
        </div>
        <DbSelect
          v-model="form.chart_type"
          options-endpoint="http://127.0.0.1:5000/filter-options/chart-type"
          :options-payload="{}"
          :multiple="false"
          placeholder="Chart type"
        />
      </div>
    </div>

    <!-- Submit -->
    <div class="text-center mt-6">
      <button class="btn btn-primary" @click="submitQuery">Submit Query</button>
    </div>
  </div>
</template>

<script setup>
import XAxis from './XAxis.vue';
import YAxisDatasetItem from './YAxisDatasetItem.vue';
import FilterItem from './FilterItem.vue';
import DbSelect from '../Shared/DbSelect.vue';
import { ref, defineEmits } from 'vue';

const emit = defineEmits(['submit']);

const form = ref({
  x_axis: { table: '', field: '', alias: '' },
  y_axis_datasets: [
    {
      table: '',
      field: '',
      method: '',
      name: '',
      label: '',
    },
  ],
  filters: [],
  chart_type: '',
});

function addYAxisDataset() {
  form.value.y_axis_datasets.push({
    table: '',
    field: '',
    method: '',
    name: '',
    label: '',
  });
}

function removeYAxisDataset(index) {
  if (form.value.y_axis_datasets.length > 1) {
    form.value.y_axis_datasets.splice(index, 1);
  }
}

function addFilter() {
  form.value.filters.push({ table: '', field: '', value: [], operator: '' });
}

function removeFilter(index) {
  form.value.filters.splice(index, 1);
}
async function submitQuery() {
  try {
    const response = await fetch('http://127.0.0.1:5000/dynamic-chart/data', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value),
    });
    const result = await response.json();
    emit('submit', result);
    console.log('Response:', result);
  } catch (error) {
    console.error('Error submitting query:', error);
  }
}
</script>
<style scoped>
.remove-y-axis-btn {
  margin-top: var(--space-md);
  color: var(--error);
  border-color: var(--error);
  background-color: transparent;
  transition: all var(--transition-fast);
}

.remove-y-axis-btn:hover {
  background-color: rgba(239, 68, 68, 0.1);
  border-color: var(--error);
  color: var(--text-primary);
}
</style>
