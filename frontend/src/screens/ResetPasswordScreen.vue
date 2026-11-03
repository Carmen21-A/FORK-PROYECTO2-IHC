<script setup>
// Portado de lib/screens/reset_password_screen.dart
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { AuthService } from '../services/authService.js'
import { showSnackBar } from '../widgets/snackbar.js'
import AppScaffold from '../widgets/AppScaffold.vue'

const router = useRouter()
const email = ref('')
const error = ref(null)

async function handleResetPassword() {
  error.value = email.value === '' ? 'Ingresa tu correo' : null
  if (error.value) return

  try {
    const respuesta = await AuthService.resetPasswordForEmail(email.value.trim())
    showSnackBar(respuesta.message)
    router.push('/login')
  } catch (e) {
    email.value = ''
    showSnackBar(e.message, 'var(--error-default)')
  }
}
</script>

<template>
  <AppScaffold titulo="Recuperar Contraseña" con-atras>
    <main class="page centered">
      <form class="stack" novalidate @submit.prevent="handleResetPassword">
        <div class="field">
          <label class="field-label" for="email">Correo electrónico</label>
          <input
            id="email"
            v-model="email"
            class="input"
            :class="{ invalid: error }"
            type="email"
            placeholder="Ingresa tu correo registrado"
            autocomplete="email"
          />
          <span v-if="error" class="field-error">{{ error }}</span>
        </div>
        <button type="submit" class="btn btn-elevated btn-block">Enviar Solicitud</button>
      </form>
    </main>
  </AppScaffold>
</template>
