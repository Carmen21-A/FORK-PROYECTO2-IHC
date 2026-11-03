<script setup>
// Portado de lib/screens/change_password_screen.dart
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { AuthService } from '../services/authService.js'
import { showSnackBar } from '../widgets/snackbar.js'
import AppScaffold from '../widgets/AppScaffold.vue'
import PasswordField from '../widgets/PasswordField.vue'

const router = useRouter()
const password1 = ref('')
const password2 = ref('')
const mostrarPassword1 = ref(false)
const mostrarPassword2 = ref(false)
const errores = reactive({ password1: null, password2: null })

function validar() {
  errores.password1 = password1.value.length < 6 ? 'Mínimo 6 caracteres' : null
  if (password2.value.length < 6) {
    errores.password2 = 'Mínimo 6 caracteres'
  } else if (password2.value !== password1.value) {
    errores.password2 = 'Las contraseñas no coinciden'
  } else {
    errores.password2 = null
  }
  return !errores.password1 && !errores.password2
}

async function handleChangePassword() {
  if (!validar()) return

  try {
    await AuthService.updatePassword(password1.value.trim())
    showSnackBar('Contraseña actualizada', 'var(--success-dark)')
    router.push('/movements')
  } catch (e) {
    password1.value = ''
    password2.value = ''
    showSnackBar(e.message, 'var(--error-default)')
  }
}
</script>

<template>
  <AppScaffold titulo="Cambiar Contraseña" con-drawer>
    <main class="page centered">
      <form class="stack" novalidate @submit.prevent="handleChangePassword">
        <label class="field-label" for="password1">Ingresa tu nueva contraseña</label>
        <div class="field">
          <PasswordField
            id="password1"
            v-model="password1"
            v-model:oculto="mostrarPassword1"
            :error="errores.password1"
            label="Nueva contraseña"
          />
        </div>
        <div class="field">
          <PasswordField
            id="password2"
            v-model="password2"
            v-model:oculto="mostrarPassword2"
            :error="errores.password2"
            label="Repite la nueva contraseña"
          />
        </div>
        <button type="submit" class="btn btn-elevated btn-block">Actualizar Contraseña</button>
      </form>
    </main>
  </AppScaffold>
</template>
