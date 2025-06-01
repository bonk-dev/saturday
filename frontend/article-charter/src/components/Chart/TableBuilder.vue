<template>
  <div>
    <table class="table">
      <thead>
        <tr>
          <th
            v-for="header in headers"
            :key="header.key"
            @click="sortBy(header.key)"
            class="sortable"
          >
            {{ header.label }}
            <span>
              {{ sortKey === header.key ? (sortAsc ? '▲' : '▼') : '' }}
            </span>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, index) in sortedRows" :key="index">
          <td v-for="header in headers" :key="header.key">
            {{ row[header.key] }}
          </td>
        </tr>
      </tbody>
    </table>

    <div class="flex gap-4 mt-4">
      <button class="btn btn-primary" @click="downloadFile('json')" :disabled="downloading">
        Download JSON
      </button>
      <button class="btn btn-primary" @click="downloadFile('csv')" :disabled="downloading">
        Download CSV
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';

const props = defineProps({
  table: {
    type: Object,
    required: true,
  },
  fullPayload: {
    type: Object,
    required: true,
  },
});

const headers = ref(props.table.headers);
const rows = ref(props.table.rows);

const sortKey = ref('');
const sortAsc = ref(true);

const sortBy = (key) => {
  if (sortKey.value === key) {
    sortAsc.value = !sortAsc.value;
  } else {
    sortKey.value = key;
    sortAsc.value = true;
  }
};

const sortedRows = computed(() => {
  if (!sortKey.value) return rows.value;

  return [...rows.value].sort((a, b) => {
    const aVal = a[sortKey.value];
    const bVal = b[sortKey.value];

    if (typeof aVal === 'string' && typeof bVal === 'string') {
      return sortAsc.value ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
    } else {
      return sortAsc.value ? aVal - bVal : bVal - aVal;
    }
  });
});

watch(
  () => props.table,
  (newTable) => {
    headers.value = newTable.headers;
    rows.value = newTable.rows;
    sortKey.value = '';
    sortAsc.value = true;
  }
);

const downloading = ref(false);

async function downloadFile(format) {
  if (downloading.value) return;
  downloading.value = true;

  const url = `http://127.0.0.1:5000/dynamic-chart/export/${format}`;

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(props.fullPayload),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const json = await response.json();

    let fileContent;
    let blobType;
    if (format === 'json') {
      fileContent = JSON.stringify(json.content || json, null, 2);
      blobType = 'application/json';
    } else if (format === 'csv') {
      fileContent = json.content;
      blobType = 'text/csv';
    } else {
      throw new Error('Unsupported format');
    }

    const fileBlob = new Blob([fileContent], { type: blobType });

    const link = document.createElement('a');
    link.href = URL.createObjectURL(fileBlob);
    link.download = `export.${format}`;
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (error) {
    console.error('Download failed:', error);
    alert('Download failed. See console for details.');
  } finally {
    downloading.value = false;
  }
}
</script>

<style scoped>
.table {
  width: 100%;
  border-collapse: collapse;
  background-color: var(--bg-card);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-md);
  font-size: 0.875rem;
}

.table th,
.table td {
  padding: var(--space-md);
  text-align: left;
  border-bottom: 1px solid var(--border-primary);
  color: var(--text-secondary);
  user-select: none;
}

.table thead th {
  background-color: var(--bg-secondary);
  font-weight: 600;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: default;
  transition: color var(--transition-fast);
}

.table thead th.sortable {
  cursor: pointer;
}

.table thead th.sortable:hover {
  color: var(--primary-light);
}

.table tbody tr:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
}

.table tbody tr:last-child td {
  border-bottom: none;
}

.mt-4 {
  margin-top: 1rem;
}
.flex {
  display: flex;
}
.gap-4 {
  gap: 1rem;
}
</style>
