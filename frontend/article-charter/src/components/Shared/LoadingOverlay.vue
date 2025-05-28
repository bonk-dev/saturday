<template>
  <teleport to="body">
    <div v-if="visible" class="modal-overlay">
      <div class="loading"></div>
    </div>
  </teleport>
</template>

<script setup>
import { defineProps } from 'vue';
const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
});
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.loading {
  display: inline-block;
  width: 50px;
  height: 50px;
  border: 4px solid #334155;
  border-radius: 50%;
  border-top-color: #3b82f6;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
