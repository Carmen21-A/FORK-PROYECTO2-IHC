<script setup>
// Portado de lib/screens/register_screen.dart
// Diseño basado en el mockup de registro: fondo celeste con ondas, tarjeta blanca con el estudiante
// a la izquierda y el formulario a la derecha.
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { AuthService } from '../services/authService.js'
import { ApiError } from '../services/api.js'
import { showSnackBar } from '../widgets/snackbar.js'
import BarraPublica from '../widgets/BarraPublica.vue'
import PasswordField from '../widgets/PasswordField.vue'
import estudiante from '../assets/inicio/estudiante-registro.jpg'
import '../theme/paginasPublicas.css'

const router = useRouter()
const nombre = ref('')
const email = ref('')
const password = ref('')
const password2 = ref('')
const mostrarPassword = ref(false) // igual que en Flutter: empieza visible
const mostrarPassword2 = ref(true)
const errores = reactive({ nombre: null, email: null, password: null, password2: null })

function validar() {
  errores.nombre = nombre.value.trim() === '' ? 'Ingresa tu nombre completo' : null
  errores.email = email.value === '' ? 'Ingresa tu correo' : null
  errores.password = password.value.length < 6 ? 'Mínimo 6 caracteres' : null
  // Confirmar la contraseña evita crear la cuenta con un error de tipeo que no se ve
  errores.password2 = password2.value !== password.value ? 'Las contraseñas no coinciden' : null
  return !errores.nombre && !errores.email && !errores.password && !errores.password2
}

async function handleRegister() {
  if (!validar()) return

  try {
    await AuthService.signUp({
      nombre: nombre.value.trim(),
      email: email.value.trim(),
      password: password.value.trim(),
    })
    router.push('/movements')
  } catch (e) {
    showSnackBar(
      e instanceof ApiError ? e.message : 'Error al crear la cuenta, intenta nuevamente.',
      'var(--color-error)',
    )
  }
}
</script>

<template>
  <div class="publico registro-pagina">
    <BarraPublica pagina="registro" transparente solo-marca />
    <main class="registro-main">
      <div class="pub-contenedor">
        <div class="registro-tarjeta">
          <div class="registro-encabezado">
            <h1 class="registro-titulo">Crear Cuenta</h1>
            <p class="registro-sub">
              ¿Ya tienes una cuenta?
              <button type="button" class="auth-enlace registro-enlace" @click="router.push('/login')">
                Inicia sesión
              </button>
            </p>
          </div>

          <div class="registro-cuerpo">
            <img class="registro-estudiante" :src="estudiante" alt="" width="760" height="689" />

            <form class="registro-form" novalidate @submit.prevent="handleRegister">
              <div class="field">
                <label class="field-label" for="nombre">Nombre completo</label>
                <input
                  id="nombre"
                  v-model="nombre"
                  class="input"
                  :class="{ invalid: errores.nombre }"
                  type="text"
                  placeholder="Tu nombre"
                  autocomplete="name"
                  maxlength="100"
                />
                <span v-if="errores.nombre" class="field-error">{{ errores.nombre }}</span>
              </div>
              <div class="field">
                <label class="field-label" for="email">Correo electrónico</label>
                <input
                  id="email"
                  v-model="email"
                  class="input"
                  :class="{ invalid: errores.email }"
                  type="email"
                  placeholder="ejemplo@correo.com"
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
                  placeholder="Mínimo 6 caracteres"
                  autocomplete="new-password"
                  :error="errores.password"
                />
              </div>
              <div class="field">
                <label class="field-label" for="password2">Confirmar contraseña</label>
                <PasswordField
                  id="password2"
                  v-model="password2"
                  v-model:oculto="mostrarPassword2"
                  placeholder="Repite tu contraseña"
                  autocomplete="new-password"
                  :error="errores.password2"
                />
              </div>
              <button type="submit" class="pub-btn pub-btn-primario pub-btn-bloque registro-boton">Registrarse</button>
            </form>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.registro-pagina {
  background: var(--color-publico-fondo-registro) url('../assets/inicio/fondo-registro.jpg') center / cover no-repeat;
}

.registro-main {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 8px 0 48px;
}

.registro-tarjeta {
  padding: 36px 48px 44px;
  border-radius: 28px;
  background: var(--color-superficie);
  box-shadow: var(--sombra-publica);
}

.registro-encabezado {
  text-align: center;
}

.registro-titulo {
  color: var(--color-publico-titulo);
  font-size: 44px;
  font-weight: 700;
  line-height: 1.15;
}

.registro-sub {
  margin-top: 6px;
  color: var(--color-publico-texto);
  font-size: 19px;
}

.registro-enlace {
  font-size: 19px;
}

.registro-cuerpo {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  align-items: center;
  gap: 48px;
  margin-top: 16px;
}

.registro-estudiante {
  width: 100%;
  max-width: 520px;
  height: auto;
  justify-self: center;
  /* el fondo casi blanco de la imagen se funde con el blanco de la tarjeta */
  mix-blend-mode: multiply;
}

.registro-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.registro-form :deep(.field-label) {
  color: var(--color-publico-titulo);
  font-size: 16px;
  font-weight: 500;
}

.registro-form :deep(.input) {
  border: 1.5px solid var(--color-publico-borde-campo);
  border-radius: 12px;
}

.registro-form :deep(.input:focus) {
  border: 2px solid var(--color-publico-accion);
}

.registro-form :deep(.field-error) {
  color: var(--color-error);
}

.registro-boton {
  margin-top: 8px;
}

@media (max-width: 900px) {
  .registro-tarjeta {
    max-width: 560px;
    margin: 0 auto;
    padding: 28px 20px 32px;
  }

  .registro-titulo {
    font-size: 32px;
  }

  .registro-cuerpo {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .registro-estudiante {
    max-width: 240px;
  }
}
</style>
