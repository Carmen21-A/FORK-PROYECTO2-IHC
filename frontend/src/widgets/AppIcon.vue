<script setup>
// Icono de Material Symbols (equivale a Icon(Icons.xxx) de Flutter)
defineProps({
  name: { type: String, required: true },
  size: { type: Number, default: 24 },
  color: { type: String, default: null },
  filled: { type: Boolean, default: false },
})
</script>

<template>
  <span
    class="icon"
    aria-hidden="true"
    :style="{
      fontSize: `${size}px`,
      color,
      fontVariationSettings: filled ? `'FILL' 1` : null,
    }"
    >{{ name }}</span
  >
</template>
