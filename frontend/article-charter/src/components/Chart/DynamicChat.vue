<template>
  <canvas ref="canvas"></canvas>
</template>

<script>
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

export default {
  name: 'ChartRenderer',
  props: {
    chartPayload: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      chartInstance: null,
    };
  },
  mounted() {
    this.renderChart();
  },
  watch: {
    chartPayload: {
      handler() {
        this.updateChart();
      },
      deep: true,
    },
  },
  methods: {
    renderChart() {
      if (!this.chartPayload.success) {
        console.warn('Chart payload was not successful');
        return;
      }

      const ctx = this.$refs.canvas.getContext('2d');
      this.chartInstance = new Chart(ctx, {
        type: this.chartPayload.chart_type || 'bar',
        data: this.chartPayload.data,
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: 'top',
            },
            title: {
              display: true,
              text: 'Wykres danych',
            },
          },
          scales: {
            y: {
              beginAtZero: true,
            },
          },
        },
      });
    },
    updateChart() {
      if (this.chartInstance) {
        this.chartInstance.destroy();
      }
      this.renderChart();
    },
  },
  beforeUnmount() {
    if (this.chartInstance) {
      this.chartInstance.destroy();
    }
  },
};
</script>

<style scoped>
canvas {
  max-width: 100%;
}
</style>
