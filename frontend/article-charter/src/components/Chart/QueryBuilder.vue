<template>
  <div class="container">
    <h1 class="text-center mb-6">Query Builder</h1>

    <!-- x_axis -->
    <div class="form-group">
      <XAxis v-model="form.x_axis" />
    </div>

    <!-- y_axis_datasets -->
    <div class="card mb-6">
      <div class="card-header">
        <h2 class="card-title">Y axis</h2>
      </div>
      <div class="card-content grid gap-4">
        <div v-for="(dataset, i) in form.y_axis_datasets" :key="i" class="border rounded p-4 card">
          <YAxisDatasetItem v-model="form.y_axis_datasets[i]" />

          <div class="flex-center mt-4" v-if="form.y_axis_datasets.length > 1">
            <button class="btn btn-secondary btn-sm remove-btn" @click="removeYAxisDataset(i)">
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
          <button class="btn btn-secondary btn-sm remove-btn" @click="removeFilter(i)">
            × Remove
          </button>
        </div>
        <button class="btn btn-secondary mt-2" @click="addFilter">+ Add Filter</button>
      </div>
    </div>

    <!-- HAVING Filters -->
    <div class="card mb-6">
      <div class="card-header">
        <h2 class="card-title">Aggregated Filters</h2>
      </div>
      <div class="card-content grid">
        <HavingFilterItem
          v-for="(filter, i) in form.having_filters"
          :key="i"
          v-model="form.having_filters[i]"
          :field-options="havingFieldOptions"
        />
        <div class="flex-center mt-4" v-if="form.having_filters.length > 0">
          <button class="btn btn-secondary btn-sm remove-btn" @click="removeHavingFilter(i)">
            × Remove
          </button>
        </div>
        <button class="btn btn-secondary mt-2" @click="addHavingFilter">
          + Add Aggregated Filter
        </button>
      </div>
    </div>

    <!-- Order By -->
    <div class="card mb-6">
      <div class="card-header">
        <h2 class="card-title">Order By</h2>
      </div>
      <div class="card-content grid">
        <OrderByItem
          v-for="(filter, i) in form.order_by"
          :key="i"
          v-model="form.order_by[i]"
          :field-options="havingFieldOptions"
        />
        <div class="flex-center mt-4" v-if="form.order_by.length > 0">
          <button class="btn btn-secondary btn-sm remove-btn" @click="removeOrderBy(i)">
            × Remove
          </button>
        </div>
        <button class="btn btn-secondary mt-2" @click="addOrderBy">+ Add Ordering</button>
      </div>
    </div>

    <!-- Chart type -->
    <div class="card mb-6">
      <div class="card-header">
        <h2 class="card-title">Chart type</h2>
      </div>
      <div class="card-content grid">
        <DbSelect
          v-model="form.chart_type"
          options-endpoint="http://127.0.0.1:5000/filter-options/chart-type"
          :options-payload="{}"
          :multiple="false"
          placeholder="Chart type"
        />
      </div>
    </div>

    <!-- Limit -->
    <div class="card mb-6">
      <div class="card-header">
        <h2 class="card-title">Limit</h2>
      </div>
      <div class="card-content grid">
        <input
          v-model="form.limit"
          type="number"
          placeholder="Enter value (0 or empty = no limit)"
          class="form-input"
        />
      </div>
    </div>

    <!-- Chart Name -->
    <div class="card mb-6">
      <div class="card-header">
        <h2 class="card-title">Chart Name</h2>
      </div>
      <div class="card-content grid">
        <input v-model="chart_name" type="text" placeholder="Enter value" class="form-input" />
      </div>
    </div>

    <!-- Chart Colors -->
    <div class="card mb-6">
      <div class="card-header">
        <h2 class="card-title">Chart Colors</h2>
      </div>
      <div class="card-content">
        <div>
          <label class="block mb-1">Background Color</label>
          <ColorPicker v-model="form.style.backgroundColor" />
        </div>
        <div>
          <label class="block mb-1">Font Color</label>
          <ColorPicker v-model="form.style.fontColor" />
        </div>
        <div>
          <label class="block mb-1">Title Font Color</label>
          <ColorPicker v-model="form.style.titleFontColor" />
        </div>
        <div>
          <label class="block mb-1">Grid Color</label>
          <ColorPicker v-model="form.style.gridColor" />
        </div>
      </div>
    </div>

    <!-- Chart Style Options -->
    <div class="card mb-6">
      <div class="card-header">
        <h2 class="card-title">Chart Style Options</h2>
      </div>
      <div class="card-content">
        <!-- Font Family -->
        <div>
          <label class="block mb-1">Font Family</label>
          <DbSelect
            v-model="form.style.fontFamily"
            :options-endpoint="'http://127.0.0.1:5000/filter-options/fonts'"
            :options-payload="{}"
            :multiple="false"
            placeholder="Choose font"
          />
        </div>

        <!-- Font Size -->
        <div>
          <label class="block mb-1">Font Size (px)</label>
          <input
            type="number"
            v-model="form.style.fontSize"
            class="form-input"
            placeholder="Font size"
            min="8"
          />
        </div>

        <!-- Legend Position -->
        <div>
          <label class="block mb-1">Legend Position</label>
          <DbSelect
            v-model="form.style.legendPosition"
            :options-endpoint="'http://127.0.0.1:5000/filter-options/legend-position'"
            :options-payload="{}"
            :multiple="false"
            placeholder="Legend position"
          />
        </div>

        <!-- Title Font Size -->
        <div>
          <label class="block mb-1">Title Font Size (px)</label>
          <input
            type="number"
            v-model="form.style.titleFontSize"
            class="form-input"
            placeholder="Title font size"
            min="10"
          />
        </div>
      </div>
    </div>
    <!-- Submit -->
    <div class="text-center mt-6">
      <button class="btn btn-primary" @click="submitQuery">Submit Query</button>
      <div v-if="formErrors.length" class="error-box">
        <strong class="block mb-2">Please fix the following errors:</strong>
        <ul>
          <li v-for="(error, index) in formErrors" :key="index">{{ error }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import XAxis from './XAxis.vue';
import YAxisDatasetItem from './YAxisDatasetItem.vue';
import FilterItem from './FilterItem.vue';
import HavingFilterItem from './HavingFilterItem.vue';
import DbSelect from '../Shared/DbSelect.vue';
import { ref, defineEmits, computed, watch } from 'vue';
import OrderByItem from './OrderByItem.vue';
import ColorPicker from '../Shared/ColorPicker.vue';
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
      background_color: '#3b82f6',
    },
  ],
  filters: [],
  having_filters: [],
  order_by: [],
  limit: null,
  chart_type: '',
  style: {
    backgroundColor: '#0f172a',
    fontFamily: '',
    fontSize: 14,
    fontColor: '#f8fafc',
    legendPosition: '',
    titleFontSize: 18,
    titleFontColor: '#f8fafc',
    gridColor: '#94a3b8',
  },
});

const chart_name = ref('');
const chart_names = ref({
  title: '',
  xtitle: '',
  ytitle: '',
});

function addYAxisDataset() {
  form.value.y_axis_datasets.push({
    table: '',
    field: '',
    method: '',
    name: '',
    label: '',
    background_color: '#3b82f6',
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

function addHavingFilter() {
  form.value.having_filters.push({ field: '', operator: '', value: null });
}

function removeHavingFilter(index) {
  form.value.having_filters.splice(index, 1);
}

const havingFieldOptions = computed(() => {
  return form.value.y_axis_datasets.map((dataset) => dataset.name).filter((name) => !!name);
});

function addOrderBy() {
  form.value.order_by.push({ field: '', direction: 'ASC' });
}

function removeOrderBy(index) {
  form.value.order_by.splice(index, 1);
}

const formErrors = ref([]);

function validateForm() {
  const errors = [];

  const { x_axis, y_axis_datasets, filters, having_filters, order_by, chart_type } = form.value;

  // Helper function to check if string is a valid SQL field/alias name
  function isValidSQLFieldName(str) {
    return /^[a-zA-Z_][a-zA-Z0-9_]*$/.test(str);
  }

  // X axis
  if (!x_axis.table || !x_axis.field || !x_axis.alias) {
    errors.push('X axis table, field, and Field name are required.');
  } else if (!isValidSQLFieldName(x_axis.alias)) {
    errors.push(
      'X axis Field name must be a valid SQL field name (letters, digits, underscores; cannot start with a digit).'
    );
  }

  // Y axis datasets
  if (y_axis_datasets.length === 0) {
    errors.push('At least one Y axis dataset is required.');
  } else {
    y_axis_datasets.forEach((ds, i) => {
      if (!ds.table || !ds.field || !ds.method || !ds.name || !ds.label) {
        errors.push(`Y axis dataset ${i + 1} is missing required fields.`);
      } else {
        if (!isValidSQLFieldName(ds.name)) {
          errors.push(`Y axis dataset ${i + 1} Field name must be a valid SQL field name.`);
        }
        if (!isValidSQLFieldName(ds.label)) {
          errors.push(`Y axis dataset ${i + 1} label must be a valid SQL field name.`);
        }
      }
    });
  }

  // Unique aliases
  const aliasSet = new Set();
  aliasSet.add(x_axis.alias);
  y_axis_datasets.forEach((ds) => aliasSet.add(ds.name));
  if (aliasSet.size !== 1 + y_axis_datasets.length) {
    errors.push('X axis Field name and Y axis dataset Field names must be unique.');
  }

  // Filters
  filters.forEach((filter, i) => {
    if (
      !filter.table ||
      !filter.field ||
      !filter.operator ||
      !filter.value ||
      filter.value.length === 0
    ) {
      errors.push(`Filter ${i + 1} is missing required fields.`);
    }
  });

  // Having filters
  having_filters.forEach((filter, i) => {
    if (!filter.field || !filter.operator || filter.value === null || filter.value === '') {
      errors.push(`Having filter ${i + 1} is missing required fields.`);
    }
  });

  // Order By
  order_by.forEach((order, i) => {
    if (!order.field || !order.direction) {
      errors.push(`Order by item ${i + 1} is missing required fields.`);
    }
  });

  // Chart type
  if (!chart_type) {
    errors.push('Chart type is required.');
  }

  formErrors.value = errors;
  return errors.length === 0;
}

async function submitQuery() {
  if (!validateForm()) return;

  form.value.limit = form.value.limit || 0;

  try {
    const response = await fetch('http://127.0.0.1:5000/dynamic-chart/data', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value),
    });
    const result = await response.json();
    emit('submit', { form: form.value, result, chart_names });
    console.log('Response:', result);
  } catch (error) {
    console.error('Error submitting query:', error);
  }
}

watch(
  [form, chart_names],
  () => {
    chart_names.value.title = chart_name.value;
    chart_names.value.xtitle = form.value.x_axis.alias;
    chart_names.value.ytitle = form.value.y_axis_datasets
      .map((ds) => ds.name)
      .filter((name) => !!name)
      .join(' ');
  },
  { deep: true, immediate: true }
);
</script>
<style scoped>
.remove-btn {
  margin-top: var(--space-md);
  color: var(--error);
  border-color: var(--error);
  background-color: transparent;
  transition: all var(--transition-fast);
}

.remove-btn:hover {
  background-color: rgba(239, 68, 68, 0.1);
  border-color: var(--error);
  color: var(--text-primary);
}

.error-box {
  background-color: rgba(239, 68, 68, 0.05);
  border: 1px solid var(--error);
  color: var(--error);
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
  transition: all var(--transition-fast);
}

.error-box ul {
  margin: 0.5rem 0 0;
  padding-left: 0;
  list-style: none;
}

.error-box li {
  margin-bottom: 0.25rem;
}
</style>
