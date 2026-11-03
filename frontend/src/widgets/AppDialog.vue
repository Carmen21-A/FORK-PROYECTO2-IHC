<script setup>
// Equivale a showDialog(... AlertDialog ...)
import { onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps({
  titulo: { type: String, default: '' },
  dismissible: { type: Boolean, default: true },
})
const emit = defineEmits(['cerrar'])
const dialogo = ref(null)

function alPresionarTecla(evento) {
  if (evento.key === 'Escape' && props.dismissible) emit('cerrar')
}

onMounted(() => {
  document.addEventListener('keydown', alPresionarTecla)
  dialogo.value?.querySelector('input, select, button')?.focus()
})
onBeforeUnmount(() => document.removeEventListener('keydown', alPresionarTecla))
</script>

<template>
  <Teleport to="body">
    <div class="overlay" @click.self="dismissible && emit('cerrar')">
      <div ref="dialogo" class="dialog" role="dialog" aria-modal="true" :aria-label="titulo">
        <div v-if="titulo || $slots.titulo" class="dialog-title">
          <slot name="titulo">{{ titulo }}</slot>
        </div>
        <slot />
        <div v-if="$slots.acciones" class="dialog-actions">
          <slot name="acciones" />
        </div>
      </div>
    </div>
  </Teleport>
</template>
