<template>
  <div class="card mb-4">
    <div class="form-group">
      <div class="card-header">
        <h2 class="card-title">X axis</h2>
      </div>
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
      <label class="form-label">Field Name</label>
      <input v-model="state.alias" placeholder="Enter field name" class="form-input" />
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
      alias: '',
    }),
  },
});

const emit = defineEmits(['update:modelValue']);

const state = reactive({
  table: props.modelValue.table || '', // string
  field: props.modelValue.field || '', // string
  alias: props.modelValue.label || '',
});

watch(
  () => ({ ...state }),
  (newVal) => {
    emit('update:modelValue', {
      table: newVal.table || '',
      field: newVal.field || '',
      alias: newVal.alias || '',
    });
  },
  { deep: true }
);

watch(
  () => state.table,
  (newTable) => {
    state.field = '';
  },
  { immediate: true }
);
</script>
