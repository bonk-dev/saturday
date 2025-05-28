<template>
  <div class="filter-form card">
    <div class="form-group">
      <label class="form-label">Table</label>
      <DbSelect
        v-model="state.table"
        options-endpoint="http://127.0.0.1:5000/filter-options/tableList"
        :options-payload="{}"
        :multiple="false"
        :disabled="false"
        placeholder="Select table"
      />
    </div>

    <div class="form-group">
      <label class="form-label">Field</label>
      <DbSelect
        v-model="state.field"
        options-endpoint="http://127.0.0.1:5000/filter-options/columnList"
        :options-payload="{ table_name: state.table || '' }"
        :multiple="false"
        placeholder="Select field"
        :disabled="!state.table"
      />
    </div>

    <div class="form-group">
      <label class="form-label">Operator</label>
      <DbSelect
        v-model="state.operator"
        options-endpoint="http://127.0.0.1:5000/filter-options/operator"
        :options-payload="{}"
        :multiple="false"
        placeholder="Select operator"
        :disabled="!state.table || !state.field"
      />
    </div>

    <div class="form-group">
      <label class="form-label">Value</label>
      <DbSelect
        v-if="state.operator === 'IN'"
        v-model="state.value"
        options-endpoint="http://127.0.0.1:5000/filter-options/uniqueValues"
        :options-payload="{
          table_name: state.table || '',
          column_name: state.field || '',
        }"
        :multiple="true"
        placeholder="Select value(s)"
        :disabled="!state.table || !state.field"
      />
      <input
        v-else
        v-model="state.value"
        type="text"
        placeholder="Enter value"
        class="form-input"
        :disabled="!state.table || !state.field"
      />
    </div>
  </div>
</template>

<script setup>
import DbSelect from '../Shared/DbSelect.vue';

import { reactive, watch } from 'vue';

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({
      table: '',
      field: '',
      value: [],
      operator: '',
    }),
  },
});

const emit = defineEmits(['update:modelValue']);

const state = reactive({
  table: props.modelValue.table || '', // string
  field: props.modelValue.field || '', // string
  value: props.modelValue.value || [], // tablica
  operator: props.modelValue.operator || '',
});

watch(
  () => state.table,
  (newTable) => {
    state.field = '';
    state.operator = '';
    state.value = newTable ? (state.operator === 'IN' ? [] : '') : '';
  },
  { immediate: true }
);

watch(
  () => state.field,
  (newField) => {
    state.operator = '';
    state.value = newField ? (state.operator === 'IN' ? [] : '') : '';
  },
  { immediate: true }
);

watch(
  () => state.operator,
  (newOp) => {
    // Resetuj wartość tylko jeśli typ operatora się zmienia
    state.value = newOp === 'IN' ? [] : '';
  }
);

watch(
  () => ({ ...state }),
  (newVal) => {
    emit('update:modelValue', newVal);
  },
  { deep: true }
);
</script>
