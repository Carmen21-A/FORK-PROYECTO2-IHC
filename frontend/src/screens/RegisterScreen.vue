<script setup>
// Portado de lib/screens/register_screen.dart
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { AuthService } from '../services/authService.js'
import { ApiError } from '../services/api.js'
import { showSnackBar } from '../widgets/snackbar.js'
import AppScaffold from '../widgets/AppScaffold.vue'
import PasswordField from '../widgets/PasswordField.vue'

const router = useRouter()
const email = ref('')
const password = ref('')
const mostrarPassword = ref(false) // igual que en Flutter: empieza visible
const errores = reactive({ email: null, password: null })

function validar() {
  errores.email = email.value === '' ? 'Ingresa tu correo' : null
  errores.password = password.value.length < 6 ? 'Mínimo 6 caracteres' : null
  return !errores.email && !errores.password
}

async function handleRegister() {
  if (!validar()) return

  try {
    await AuthService.signUp({
      email: email.value.trim(),
      password: password.value.trim(),
    })
    router.push('/movements')
  } catch (e) {
    showSnackBar(
      e instanceof ApiError ? e.message : 'Error al crear la cuenta, intenta nuevamente.',
      'var(--error-default)',
    )
  }
}
</script>

<template>
  <AppScaffold titulo="Crear Cuenta" con-atras>
    <main class="page centered">
      <form class="stack" novalidate @submit.prevent="handleRegister">
        <div class="field">
          <label class="field-label" for="email">Correo electrónico</label>
          <input
            id="email"
            v-model="email"
            class="input"
            :class="{ invalid: errores.email }"
            type="email"
            placeholder="ejemplo@gmail.com"
            autocomplete="email"
          />
          <span v-if="errores.email" class="field-error">{{ errores.email }}</span>
        </div>
        <div class="field">
          <label class="field-label" for="password">Contraseña</label>
          <PasswordField
            id="password"
            v-model="password"
            v-model:oculto="mostrarPassword"
            :error="errores.password"
          />
        </div>
        <button type="submit" class="btn btn-elevated btn-block">Registrarse</button>
      </form>
    </main>
  </AppScaffold>
</template>
