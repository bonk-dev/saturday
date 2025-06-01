<template>
  <div class="mb-4">
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
      <label class="form-label">Method</label>
      <DbSelect
        v-model="state.method"
        options-endpoint="http://127.0.0.1:5000/filter-options/methods"
        :options-payload="{}"
        :multiple="false"
        placeholder="Select method"
        :disabled="!state.table || !state.field"
      />
    </div>

    <div class="form-group">
      <label class="form-label">Field Name</label>
      <input v-model="state.name" placeholder="Enter field name" class="form-input" />
    </div>

    <div class="form-group">
      <label class="form-label">Label</label>
      <input v-model="state.label" placeholder="Enter label" class="form-input" />
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
      method: '',
      name: '',
      label: '',
    }),
  },
});

const emit = defineEmits(['update:modelValue']);

const state = reactive({
  table: props.modelValue.table || '',
  field: props.modelValue.field || '',
  method: props.modelValue.method || '',
  name: props.modelValue.name || '',
  label: props.modelValue.label || '',
});

watch(
  () => ({ ...state }),
  (newVal) => {
    emit('update:modelValue', { ...newVal });
  },
  { deep: true }
);

watch(
  () => state.table,
  (newTable, oldTable) => {
    if (newTable !== oldTable) {
      state.field = '';
      state.method = '';
    }
  }
);

watch(
  () => state.field,
  (newField, oldField) => {
    if (newField !== oldField) {
      state.method = '';
    }
  }
);
</script>
