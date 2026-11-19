<script setup>
// Portado de lib/screens/login_screen.dart
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { AuthService } from '../services/authService.js'
import { ApiError } from '../services/api.js'
import { showSnackBar } from '../widgets/snackbar.js'
import BarraPublica from '../widgets/BarraPublica.vue'
import '../theme/paginasPublicas.css'
import PasswordField from '../widgets/PasswordField.vue'

const router = useRouter()
const email = ref('')
const password = ref('')
const mostrarPassword = ref(true) // true = oculta
const errores = reactive({ email: null, password: null })

function validar() {
  errores.email = email.value === '' ? 'Ingresa tu correo' : null
  errores.password = password.value.length < 6 ? 'Mínimo 6 caracteres' : null
  return !errores.email && !errores.password
}

async function handleLogin() {
  if (!validar()) return
  try {
    await AuthService.signInWithPassword({
      email: email.value.trim(),
      password: password.value.trim(),
    })
    router.push('/movements')
  } catch (e) {
    showSnackBar(
      e instanceof ApiError
        ? e.message
        : 'Ha ocurrido un error de conexion, intenta de nuevo.',
      'var(--color-error)',
    )
  }
}
</script>

<template>
  <div class="publico login-pagina">
    <BarraPublica pagina="login" transparente sin-marca />
    <main class="login-main">
      <div class="pub-contenedor login-fila">
        <div class="login-tarjeta">
          <form class="auth-formulario" novalidate @submit.prevent="handleLogin">
            <div>
              <h1 class="auth-titulo">Iniciar Sesión</h1>
              <p class="auth-subtitulo">Qué bueno verte de nuevo. Entra para revisar tus cuentas.</p>
            </div>
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

            <button type="button" class="auth-enlace" @click="router.push('/reset-password')">
              ¿Olvidaste tu contraseña?
            </button>

            <button type="submit" class="pub-btn pub-btn-primario pub-btn-bloque">Iniciar Sesión</button>
            <p class="auth-pie">
              ¿Aún no tienes cuenta?
              <button type="button" class="auth-enlace" @click="router.push('/register')">Regístrate aquí</button>
            </p>
          </form>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* Fondo del login: la imagen ya trae el logo y al estudiante a la izquierda; el formulario va a la derecha */
.login-pagina {
  background: url('../assets/inicio/fondo-login.jpg') left top / cover no-repeat, var(--degradado-publico);
}

.login-main {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 24px 0 48px;
}

.login-fila {
  display: flex;
  justify-content: flex-end;
}

.login-tarjeta {
  width: 100%;
  max-width: 460px;
  border-radius: 28px;
  background: var(--color-publico-tarjeta-translucida);
  box-shadow: var(--sombra-publica);
}

@media (max-width: 900px) {
  /* En celular la imagen se recortaría (y su logo quedaría tapado): fondo de color y logo en la barra */
  .login-pagina {
    background: var(--degradado-publico);
  }

  .login-fila {
    justify-content: center;
  }
}
</style>
