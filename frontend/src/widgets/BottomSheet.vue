<script setup>
// Equivale a showModalBottomSheet(...)
import { onBeforeUnmount, onMounted } from 'vue'

const emit = defineEmits(['cerrar'])
// Nombre del dialogo para lectores de pantalla (y para encontrarlo por rol en las pruebas)
defineProps({ titulo: { type: String, required: true } })

function alPresionarTecla(evento) {
  if (evento.key === 'Escape') emit('cerrar')
}

onMounted(() => document.addEventListener('keydown', alPresionarTecla))
onBeforeUnmount(() => document.removeEventListener('keydown', alPresionarTecla))
</script>

<template>
  <Teleport to="body">
    <div class="overlay bottom" @click.self="emit('cerrar')">
      <div class="sheet" role="dialog" aria-modal="true" :aria-label="titulo">
        <div class="sheet-handle" />
        <slot />
      </div>
    </div>
  </Teleport>
</template>
