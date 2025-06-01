<template>
  <canvas ref="canvas"></canvas>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

const props = defineProps({
  chartPayload: {
    type: Object,
    required: true,
  },
  chartNames: {
    type: Object,
    required: true,
  },
});

const canvas = ref(null);
let chartInstance = null;

function renderChart() {
  if (!props.chartPayload.success) {
    console.warn('Chart payload was not successful');
    return;
  }

  const ctx = canvas.value.getContext('2d');

  chartInstance = new Chart(ctx, {
    type: props.chartPayload.chart_type || 'bar',
    data: props.chartPayload.data,
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'top',
        },
        title: {
          display: true,
          text: props.chartNames.value.title || 'Wykres danych',
        },
      },
      scales: {
        x: {
          title: {
            display: true,
            text: props.chartNames.value.xtitle || '',
          },
        },
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: props.chartNames.value.ytitle || '',
          },
        },
      },
    },
  });
}

function updateChart() {
  if (chartInstance) {
    chartInstance.destroy();
  }
  renderChart();
}

onMounted(() => {
  renderChart();
});

watch(
  () => props.chartPayload,
  () => {
    updateChart();
  },
  { deep: true }
);

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.destroy();
  }
});
</script>

<style scoped>
canvas {
  max-width: 100%;
}
</style>
