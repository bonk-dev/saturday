<template>
  <div class="form-group">
    <input type="color" v-model="localValue" class="form-input custom-color-picker" />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  modelValue: {
    type: String,
    default: '#000000',
  },
});

const emit = defineEmits(['update:modelValue']);

const localValue = ref(props.modelValue);

watch(
  () => localValue.value,
  (newVal) => {
    emit('update:modelValue', newVal);
  }
);

watch(
  () => props.modelValue,
  (newVal) => {
    if (newVal !== localValue.value) {
      localValue.value = newVal;
    }
  },
  { immediate: true }
);
</script>

<style scoped>
.custom-color-picker {
  width: 100%;
  height: 2.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 0;
}
</style>
