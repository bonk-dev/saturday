<template>
  <div class="form-group">
    <Multiselect
      v-model="localValue"
      :options="options"
      :multiple="multiple"
      :placeholder="placeholder"
      :disabled="disabled"
      :close-on-select="!multiple"
      class="form-input custom-multiselect"
    />
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import Multiselect from 'vue-multiselect';

const props = defineProps({
  modelValue: {
    type: [Array, String, Object, null],
    default: () => [],
  },
  optionsEndpoint: String,
  optionsPayload: Object,
  multiple: Boolean,
  placeholder: String,
  disabled: Boolean,
});

const emit = defineEmits(['update:modelValue']);

const localValue = ref(
  props.multiple ? (Array.isArray(props.modelValue) ? [...props.modelValue] : []) : props.modelValue
);

// Fetch options
async function fetchOptions() {
  try {
    if (!props.optionsEndpoint) return;
    const response = await fetch(props.optionsEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(props.optionsPayload),
    });

    const data = await response.json();
    options.value = Array.isArray(data?.values) ? data.values : [];
  } catch (error) {
    console.error('Error fetching options:', error);
    options.value = [];
  }
}

const options = ref([]);

watch(
  () => localValue.value,
  (newVal) => {
    emit('update:modelValue', newVal);
  }
);

watch(
  () => [props.optionsPayload, props.disabled],
  ([newPayload, newDisabled]) => {
    if (!newDisabled) {
      fetchOptions();
    } else {
      options.value = [];
    }
  },
  { immediate: true, deep: true }
);

watch(
  () => props.modelValue,
  (newVal) => {
    const normalizedNewVal = props.multiple ? (Array.isArray(newVal) ? [...newVal] : []) : newVal;

    if (JSON.stringify(normalizedNewVal) !== JSON.stringify(localValue.value)) {
      localValue.value = normalizedNewVal;
    }
  },
  { immediate: true }
);

onMounted(() => {
  if (!props.disabled) {
    fetchOptions();
  }
});
</script>

<style scoped>
.form-group :deep(.custom-multiselect.multiselect) {
  --tag-bg: var(--primary);
  --tag-hover: var(--primary-hover);
  --tag-text: white;
  --tag-radius: var(--radius-sm);
  --tag-padding: 0.25rem 0.5rem;

  min-height: 44px;
  border-radius: var(--radius-md);
  background: var(--bg-input);
  border: 1px solid var(--border-primary);
  transition: all var(--transition-fast);
}

/* Stan disabled - wyraźny wskaźnik */
.form-group :deep(.custom-multiselect.multiselect--disabled) {
  opacity: 0.7;
  cursor: not-allowed;
  background-color: rgba(51, 65, 85, 0.5);
}

.form-group :deep(.custom-multiselect.multiselect--disabled .multiselect__select) {
  background: transparent;
}

.form-group :deep(.custom-multiselect.multiselect--disabled .multiselect__tags) {
  background-color: rgba(51, 65, 85, 0.5);
}

.form-group :deep(.custom-multiselect.multiselect--disabled .multiselect__placeholder) {
  color: var(--text-disabled);
}

/* Stan aktywny/focus */
.form-group :deep(.custom-multiselect.multiselect--active) {
  border-color: var(--border-focus);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Kontener tagów */
.form-group :deep(.custom-multiselect .multiselect__tags) {
  min-height: 44px;
  padding: 0.75rem 1rem;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: nowrap;
  overflow-x: auto;
  scrollbar-width: thin;
  scrollbar-color: var(--primary) var(--bg-input);
}

/* Scrollbar dla kontenera tagów */
.form-group :deep(.custom-multiselect .multiselect__tags::-webkit-scrollbar) {
  height: 4px;
}

.form-group :deep(.custom-multiselect .multiselect__tags::-webkit-scrollbar-thumb) {
  background-color: var(--primary);
  border-radius: 2px;
}

/* Pojedynczy tag */
.form-group :deep(.custom-multiselect .multiselect__tag) {
  background: var(--tag-bg);
  color: var(--tag-text);
  border-radius: var(--tag-radius);
  padding: var(--tag-padding);
  margin: 0;
  display: flex;
  align-items: center;
  max-width: 100%;
  overflow: hidden;
  flex-shrink: 0;
}

/* Tekst w tagu - ograniczenie długości */
.form-group :deep(.custom-multiselect .multiselect__tag span) {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
  display: inline-block;
}

/* Ikona usuwania tagu */
.form-group :deep(.custom-multiselect .multiselect__tag-icon) {
  background: transparent;
  color: var(--tag-text);
  opacity: 0.7;
  transition: opacity var(--transition-fast);
  line-height: 1;
}

.form-group :deep(.custom-multiselect .multiselect__tag-icon:hover) {
  background: transparent;
  opacity: 1;
}

/* Pole input */
.form-group :deep(.custom-multiselect .multiselect__input) {
  background: transparent;
  color: var(--text-primary);
  padding: 0;
  margin: 0;
  min-height: auto;
  border: none !important;
  max-width: 100%;
}

.form-group :deep(.custom-multiselect .multiselect__input::placeholder) {
  color: var(--text-muted);
}

/* Placeholder */
.form-group :deep(.custom-multiselect .multiselect__placeholder) {
  color: var(--text-muted);
  padding-top: 0;
  margin-bottom: 0;
}

/* Lista rozwijana - FIX CENTROWANIA */
.form-group :deep(.custom-multiselect .multiselect__content-wrapper) {
  background: var(--bg-card);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  margin-top: 0.25rem;
  max-height: 300px;
  overflow-y: auto;
  display: flex;
  justify-content: center;
}

/* Kontener opcji - FIX CENTROWANIA */
.form-group :deep(.custom-multiselect .multiselect__content) {
  width: 100%;
  max-width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.5rem 0;
}

/* Pojedyncza opcja - FIX CENTROWANIA */
.form-group :deep(.custom-multiselect .multiselect__option) {
  padding: 0.75rem 1rem;
  color: var(--text-secondary);
  background: transparent;
  transition: all var(--transition-fast);
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  max-width: 100%;
  text-align: center;
}

/* Długie teksty w opcjach - zawijanie */
.form-group :deep(.custom-multiselect .multiselect__option span) {
  display: block;
  white-space: normal;
  word-break: break-word;
  line-height: 1.4;
  width: 100%;
  text-align: center;
}

/* Aktywna opcja */
.form-group :deep(.custom-multiselect .multiselect__option--highlight) {
  background: var(--bg-hover);
  color: var(--text-primary);
}

/* Wybrana opcja */
.form-group :deep(.custom-multiselect .multiselect__option--selected) {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  font-weight: 600;
}

/* Czerwone podświetlenie dla zaznaczonej opcji przy najechaniu */
.form-group :deep(.custom-multiselect .multiselect__option--selected:hover) {
  background-color: var(--error) !important;
  color: white !important;
}

/* Tryb pojedynczego wyboru - centrowanie */
.form-group :deep(.custom-multiselect .multiselect__single) {
  background: transparent;
  color: var(--text-primary);
  margin: 0;
  padding: 0;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: center;
  width: 100%;
  display: flex;
  justify-content: center;
}

/* Ikona rozwijania */
.form-group :deep(.custom-multiselect .multiselect__select) {
  background: transparent;
  width: 40px;
  padding: 0;
}

.form-group :deep(.custom-multiselect .multiselect__select:before) {
  border-color: var(--text-muted) transparent transparent;
  border-width: 6px 6px 0;
}

/* Loading spinner */
.form-group :deep(.custom-multiselect .multiselect__spinner) {
  background: transparent;
  border-color: var(--border-primary) var(--border-primary) var(--primary);
}
</style>
