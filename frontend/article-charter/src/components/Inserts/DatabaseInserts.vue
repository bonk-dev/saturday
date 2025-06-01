<template>
  <div class="card" style="max-width: 400px; margin: auto">
    <div class="form-group">
      <label class="form-label" for="search">Search Phrase</label>
      <input
        id="search"
        v-model="searchQuery"
        type="text"
        placeholder="Enter search phrase"
        class="form-input"
        :disabled="loading"
      />
    </div>

    <div class="flex flex-col gap-lg">
      <button class="btn btn-primary" @click="sendToAll" :disabled="loading || !searchQuery">
        Send to all
      </button>
      <button
        class="btn btn-secondary"
        @click="() => sendTo('http://localhost:5000/gscholar/search')"
        :disabled="loading || !searchQuery"
      >
        Find in google scholar
      </button>
      <button
        class="btn btn-secondary"
        @click="() => sendTo('http://localhost:5000/scopus-api/search')"
        :disabled="loading || !searchQuery"
      >
        Find in Scopus API
      </button>
      <button
        class="btn btn-secondary"
        @click="() => sendTo('http://localhost:5000/scopus-batch/search')"
        :disabled="loading || !searchQuery"
      >
        Find in Scopus Scraper
      </button>
    </div>

    <div v-if="results.length" class="mt-lg">
      <h3>Results:</h3>
      <ul>
        <li v-for="(res, index) in results" :key="index" class="card-description">
          <strong>{{ getEndpointName(res.endpoint) }}:&nbsp;</strong>
          <span v-if="res.error" style="color: var(--error)">Błąd:&nbsp; {{ res.error }}</span>
          <span v-else>Query:&nbsp; "{{ res.search_query }}", Count:&nbsp; {{ res.count }}</span>
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
.btn {
  padding: 0.5rem 1rem;
}
</style>
