<script setup>
import { snackbars } from './snackbar.js'
</script>

<template>
  <div class="snackbar-host" role="status" aria-live="polite">
    <div
      v-for="s in snackbars"
      :key="s.id"
      class="snackbar"
      :style="s.color ? { background: s.color } : null"
    >
      {{ s.texto }}
    </div>
  </div>
</template>
