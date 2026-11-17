<script setup>
// TextFormField de contraseña con el boton del ojito para mostrar/ocultar
import AppIcon from './AppIcon.vue'

const valor = defineModel({ type: String, default: '' })
const oculto = defineModel('oculto', { type: Boolean, default: true })
defineProps({
  id: { type: String, required: true },
  placeholder: { type: String, default: 'password123' },
  error: { type: String, default: null },
  label: { type: String, default: null },
  autocomplete: { type: String, default: 'current-password' }, // 'new-password' al crear una cuenta
})
</script>

<template>
  <div class="input-wrap">
    <input
      :id="id"
      v-model="valor"
      class="input has-suffix"
      :class="{ invalid: error }"
      :type="oculto ? 'password' : 'text'"
      :placeholder="placeholder"
      :aria-label="label ?? undefined"
      :aria-invalid="error ? 'true' : 'false'"
      :autocomplete="autocomplete"
    />
    <button
      type="button"
      class="icon-btn input-suffix"
      :aria-label="oculto ? 'Mostrar contraseña' : 'Ocultar contraseña'"
      @click="oculto = !oculto"
    >
      <AppIcon :name="oculto ? 'visibility_off' : 'visibility'" />
    </button>
  </div>
  <span v-if="error" class="field-error">{{ error }}</span>
</template>
