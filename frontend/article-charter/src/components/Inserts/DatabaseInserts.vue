<template>
  <div class="card" style="max-width: 400px; margin: auto">
    <div class="form-group">
      <label class="form-label" for="search">Search Query</label>
      <input
        id="search"
        v-model="searchQuery"
        type="text"
        placeholder="Wpisz zapytanie"
        class="form-input"
        :disabled="loading"
      />
    </div>

    <div class="flex flex-col gap-lg">
      <button class="btn btn-primary" @click="sendToAll" :disabled="loading || !searchQuery">
        Wyślij do wszystkich
      </button>
      <button
        class="btn btn-secondary"
        @click="() => sendTo('http://localhost:5000/gscholar/search')"
        :disabled="loading || !searchQuery"
      >
        Wyślij do GScholar
      </button>
      <button
        class="btn btn-secondary"
        @click="() => sendTo('http://localhost:5000/scopus-api/search')"
        :disabled="loading || !searchQuery"
      >
        Wyślij do Scopus API
      </button>
      <button
        class="btn btn-secondary"
        @click="() => sendTo('http://localhost:5000/scopus-batch/search')"
        :disabled="loading || !searchQuery"
      >
        Wyślij do Scopus Batch
      </button>
    </div>

    <div v-if="results.length" class="mt-lg">
      <h3>Wyniki:</h3>
      <ul>
        <li v-for="(res, index) in results" :key="index" class="card-description">
          <strong>{{ getEndpointName(res.endpoint) }}:</strong>
          <span v-if="res.error" style="color: var(--error)">Błąd: {{ res.error }}</span>
          <span v-else>Query: "{{ res.search_query }}", Count: {{ res.count }}</span>
        </li>
      </ul>
    </div>

    <LoadingOverlay :visible="loading" />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import LoadingOverlay from '../Shared/LoadingOverlay.vue';

const searchQuery = ref('');
const loading = ref(false);
const results = ref([]);

const endpoints = [
  'http://localhost:5000/gscholar/search',
  'http://localhost:5000/scopus-api/search',
  'http://localhost:5000/scopus-batch/search',
];

function getEndpointName(url) {
  if (url.includes('gscholar')) return 'Google Scholar';
  if (url.includes('scopus-api')) return 'Scopus API';
  if (url.includes('scopus-batch')) return 'Scopus Batch';
  return url;
}

async function sendTo(url) {
  if (!searchQuery.value) return;
  loading.value = true;
  results.value = [];
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ search_query: searchQuery.value }),
    });
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    const data = await res.json();
    results.value = [{ endpoint: url, ...data }];
  } catch (e) {
    results.value = [{ endpoint: url, error: e.message }];
  } finally {
    loading.value = false;
  }
}

async function sendToAll() {
  if (!searchQuery.value) return;
  loading.value = true;
  results.value = [];

  const allResults = [];
  for (const url of endpoints) {
    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ search_query: searchQuery.value }),
      });
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      const data = await res.json();
      allResults.push({ endpoint: url, ...data });
    } catch (e) {
      allResults.push({ endpoint: url, error: e.message });
    }
  }

  results.value = allResults;
  loading.value = false;
}
</script>

<style scoped>
.mt-lg {
  margin-top: var(--space-lg);
}
</style>
