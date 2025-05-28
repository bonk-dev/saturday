<template>
  <MainComponent></MainComponent>
</template>

<script setup>
import MainComponent from './components/MainComponent.vue';
</script>

<style>
/* Universal Dark Theme CSS Stylesheet */

/* CSS Variables for Dark Theme */
:root {
  /* Colors */
  --primary: #3b82f6;
  --primary-hover: #2563eb;
  --primary-light: #60a5fa;
  --secondary: #6366f1;
  --accent: #10b981;
  --warning: #f59e0b;
  --error: #ef4444;
  --success: #22c55e;

  /* Dark Theme Background Colors */
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --bg-tertiary: #334155;
  --bg-card: #1e293b;
  --bg-hover: #475569;
  --bg-input: #334155;

  /* Text Colors */
  --text-primary: #f8fafc;
  --text-secondary: #cbd5e1;
  --text-muted: #94a3b8;
  --text-disabled: #64748b;

  /* Border Colors */
  --border-primary: #334155;
  --border-secondary: #475569;
  --border-focus: #3b82f6;

  /* Shadow */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -1px rgba(0, 0, 0, 0.3);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -2px rgba(0, 0, 0, 0.3);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 10px 10px -5px rgba(0, 0, 0, 0.3);

  /* Spacing */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;
  --space-xl: 2rem;
  --space-2xl: 3rem;

  /* Border Radius */
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;

  /* Typography */
  --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    sans-serif;
  --font-mono: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;

  /* Transitions */
  --transition-fast: 150ms ease-in-out;
  --transition-normal: 250ms ease-in-out;
  --transition-slow: 350ms ease-in-out;
}

/* Reset and Base Styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  font-size: 16px;
  scroll-behavior: smooth;
}

body {
  font-family: var(--font-family);
  background-color: var(--bg-primary);
  color: var(--text-primary);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  min-height: 100vh;
}

/* Typography */
h1,
h2,
h3,
h4,
h5,
h6 {
  font-weight: 600;
  line-height: 1.3;
  margin-bottom: var(--space-md);
  color: var(--text-primary);
}

h1 {
  font-size: 2.5rem;
}
h2 {
  font-size: 2rem;
}
h3 {
  font-size: 1.75rem;
}
h4 {
  font-size: 1.5rem;
}
h5 {
  font-size: 1.25rem;
}
h6 {
  font-size: 1.125rem;
}

p {
  margin-bottom: var(--space-md);
  color: var(--text-secondary);
}

a {
  color: var(--primary);
  text-decoration: none;
  transition: color var(--transition-fast);
}

a:hover {
  color: var(--primary-light);
  text-decoration: underline;
}

code {
  font-family: var(--font-mono);
  background-color: var(--bg-tertiary);
  padding: 0.125rem 0.25rem;
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  color: var(--text-primary);
}

pre {
  background-color: var(--bg-secondary);
  padding: var(--space-md);
  border-radius: var(--radius-md);
  overflow-x: auto;
  margin-bottom: var(--space-md);
  border-left: 4px solid var(--primary);
}

pre code {
  background: none;
  padding: 0;
}

/* Layout Components */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-md);
}

.grid {
  display: grid;
  gap: var(--space-md);
}

.flex {
  display: flex;
  gap: var(--space-md);
}

.flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

.flex-between {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* Cards */
.card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  box-shadow: var(--shadow-md);
  transition: all var(--transition-normal);
}

.card:hover {
  border-color: var(--border-secondary);
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.card-header {
  margin-bottom: var(--space-lg);
  padding-bottom: var(--space-md);
  border-bottom: 1px solid var(--border-primary);
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--space-xs);
}

.card-description {
  color: var(--text-muted);
  font-size: 0.875rem;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs);
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  text-decoration: none;
  min-height: 44px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background-color: var(--primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-secondary {
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-primary);
}

.btn-secondary:hover:not(:disabled) {
  background-color: var(--bg-tertiary);
  border-color: var(--border-secondary);
}

.btn-ghost {
  background-color: transparent;
  color: var(--text-secondary);
}

.btn-ghost:hover:not(:disabled) {
  background-color: var(--bg-hover);
  color: var(--text-primary);
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.75rem;
  min-height: 36px;
}

.btn-lg {
  padding: 1rem 2rem;
  font-size: 1rem;
  min-height: 52px;
}

/* Form Elements */
.form-group {
  margin-bottom: var(--space-lg);
}

.form-label {
  display: block;
  margin-bottom: var(--space-sm);
  font-weight: 500;
  color: var(--text-primary);
  font-size: 0.875rem;
}

.form-input,
.form-textarea,
.form-select {
  width: 100%;
  padding: 0.75rem;
  background-color: var(--bg-input);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 0.875rem;
  transition: all var(--transition-fast);
  min-height: 44px;
}

.form-input:focus,
.form-textarea:focus,
.form-select:focus {
  outline: none;
  border-color: var(--border-focus);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input::placeholder,
.form-textarea::placeholder {
  color: var(--text-muted);
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.form-error {
  color: var(--error);
  font-size: 0.75rem;
  margin-top: var(--space-xs);
}

/* Navigation */
.nav {
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-primary);
  padding: var(--space-md) 0;
}

.nav-list {
  display: flex;
  gap: var(--space-lg);
  list-style: none;
  align-items: center;
}

.nav-link {
  color: var(--text-secondary);
  font-weight: 500;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.nav-link:hover,
.nav-link.active {
  color: var(--text-primary);
  background-color: var(--bg-hover);
  text-decoration: none;
}

/* Tables */
.table {
  width: 100%;
  border-collapse: collapse;
  background-color: var(--bg-card);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-md);
}

.table th,
.table td {
  padding: var(--space-md);
  text-align: left;
  border-bottom: 1px solid var(--border-primary);
}

.table th {
  background-color: var(--bg-secondary);
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.table td {
  color: var(--text-secondary);
}

.table tbody tr:hover {
  background-color: var(--bg-hover);
}

.table tbody tr:last-child td {
  border-bottom: none;
}

/* Alerts */
.alert {
  padding: var(--space-md);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-md);
  border-left: 4px solid;
}

.alert-info {
  background-color: rgba(59, 130, 246, 0.1);
  border-color: var(--primary);
  color: var(--primary-light);
}

.alert-success {
  background-color: rgba(34, 197, 94, 0.1);
  border-color: var(--success);
  color: var(--success);
}

.alert-warning {
  background-color: rgba(245, 158, 11, 0.1);
  border-color: var(--warning);
  color: var(--warning);
}

.alert-error {
  background-color: rgba(239, 68, 68, 0.1);
  border-color: var(--error);
  color: var(--error);
}

/* Modal */
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

.modal {
  background-color: var(--bg-card);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  padding: var(--space-lg);
  border-bottom: 1px solid var(--border-primary);
}

.modal-content {
  padding: var(--space-lg);
}

.modal-footer {
  padding: var(--space-lg);
  border-top: 1px solid var(--border-primary);
  display: flex;
  gap: var(--space-md);
  justify-content: flex-end;
}

/* Loading */
.loading {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-primary);
  border-radius: 50%;
  border-top-color: var(--primary);
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Utility Classes */
.text-center {
  text-align: center;
}
.text-left {
  text-align: left;
}
.text-right {
  text-align: right;
}

.w-full {
  width: 100%;
}
.h-full {
  height: 100%;
}

.hidden {
  display: none;
}
.visible {
  display: block;
}

.opacity-50 {
  opacity: 0.5;
}
.opacity-75 {
  opacity: 0.75;
}

.rounded {
  border-radius: var(--radius-md);
}
.rounded-lg {
  border-radius: var(--radius-lg);
}
.rounded-full {
  border-radius: 9999px;
}

.shadow {
  box-shadow: var(--shadow-md);
}
.shadow-lg {
  box-shadow: var(--shadow-lg);
}

/* Responsive Design */
@media (max-width: 768px) {
  .container {
    padding: 0 var(--space-sm);
  }

  .flex {
    flex-direction: column;
  }

  .nav-list {
    flex-direction: column;
    gap: var(--space-sm);
  }

  .modal {
    width: 95%;
  }

  h1 {
    font-size: 2rem;
  }
  h2 {
    font-size: 1.75rem;
  }
  h3 {
    font-size: 1.5rem;
  }

  .btn {
    width: 100%;
  }

  .table {
    font-size: 0.875rem;
  }

  .table th,
  .table td {
    padding: var(--space-sm);
  }
}

@media (max-width: 480px) {
  html {
    font-size: 14px;
  }

  .card {
    padding: var(--space-md);
  }

  .modal-header,
  .modal-content,
  .modal-footer {
    padding: var(--space-md);
  }
}
</style>
