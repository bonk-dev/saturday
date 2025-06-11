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

  const { style = {} } = props.chartPayload;

  const ctx = canvas.value.getContext('2d');

  // Optional: set canvas background color
  if (style.backgroundColor) {
    canvas.value.style.backgroundColor = style.backgroundColor;
  }

  chartInstance = new Chart(ctx, {
    type: props.chartPayload.chart_type || 'bar',
    data: props.chartPayload.data,
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: style.legendPosition || 'top',
          labels: {
            color: style.fontColor || '#666',
            font: {
              family: style.fontFamily || 'sans-serif',
              size: style.fontSize || 12,
            },
          },
        },
        title: {
          display: true,
          text: props.chartNames.value.title || 'Wykres danych',
          color: style.titleFontColor || '#000',
          font: {
            size: style.titleFontSize || 16,
            family: style.fontFamily || 'sans-serif',
          },
        },
      },
      scales: {
        x: {
          grid: {
            color: style.gridColor || '#e5e5e5',
          },
          title: {
            display: true,
            text: props.chartNames.value.xtitle || '',
            color: style.fontColor || '#666',
            font: {
              size: style.fontSize || 12,
              family: style.fontFamily || 'sans-serif',
            },
          },
          ticks: {
            color: style.fontColor || '#666',
            font: {
              size: style.fontSize || 12,
              family: style.fontFamily || 'sans-serif',
            },
            callback: function (value, index, ticks) {
              const originalLabel = props.chartPayload.data.labels?.[index] ?? String(value);
              return originalLabel.length > 40 ? originalLabel.slice(0, 40) + '...' : originalLabel;
            },
          },
        },
        y: {
          beginAtZero: true,
          grid: {
            color: style.gridColor || '#e5e5e5',
          },
          title: {
            display: true,
            text: props.chartNames.value.ytitle || '',
            color: style.fontColor || '#666',
            font: {
              size: style.fontSize || 12,
              family: style.fontFamily || 'sans-serif',
            },
          },
          ticks: {
            color: style.fontColor || '#666',
            font: {
              size: style.fontSize || 12,
              family: style.fontFamily || 'sans-serif',
            },
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
