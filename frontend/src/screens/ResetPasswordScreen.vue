<script setup>
// Portado de lib/screens/reset_password_screen.dart
// Recuperar la contraseña en 3 pasos, sin salir de esta pantalla:
//   1. el correo  ->  2. el código de 4 dígitos que llega al correo  ->  3. la contraseña nueva
// Antes se mandaba un enlace que apuntaba a la app en la computadora (localhost): abierto desde
// el celular no funcionaba. El código se lee en cualquier dispositivo y se escribe aquí.
import { computed, nextTick, ref } from 'vue'
import { useRouter } from 'vue-router'
import { AuthService } from '../services/authService.js'
import { ApiError } from '../services/api.js'
import { showSnackBar } from '../widgets/snackbar.js'
import BarraPublica from '../widgets/BarraPublica.vue'
import PasswordField from '../widgets/PasswordField.vue'
import '../theme/paginasPublicas.css'

const router = useRouter()
const paso = ref('correo') // 'correo' | 'codigo' | 'nueva'
const numeroDePaso = computed(() => ({ correo: 1, codigo: 2, nueva: 3 })[paso.value])
const enviando = ref(false) // evita mandar dos veces mientras espera al servidor

const email = ref('')
const codigo = ref('')
const minutos = ref(15) // el servidor dice cuánto sirve el código
const password = ref('')
const password2 = ref('')
const oculta = ref(true)
const oculta2 = ref(true)
const error = ref(null) // error del campo principal del paso
const error2 = ref(null) // error de «Confirmar contraseña»

const campoCorreo = ref(null)
const campoCodigo = ref(null)

function mensaje(e, porDefecto) {
  return e instanceof ApiError ? e.message : porDefecto
}

// Al cambiar de paso, el cursor queda en el campo que hay que llenar
async function irA(nuevoPaso) {
  paso.value = nuevoPaso
  error.value = null
  error2.value = null
  await nextTick()
  if (nuevoPaso === 'correo') campoCorreo.value?.focus()
  if (nuevoPaso === 'codigo') campoCodigo.value?.focus()
  if (nuevoPaso === 'nueva') document.getElementById('password')?.focus()
}

// Solo números y como máximo 4 (también al pegar «12 34» o «1234.»)
function limpiarCodigo() {
  codigo.value = codigo.value.replace(/\D/g, '').slice(0, 4)
}

async function pedirCodigo({ reenviar = false } = {}) {
  error.value = email.value.trim() === '' ? 'Ingresa tu correo' : null
  if (error.value || enviando.value) return
  enviando.value = true
  try {
    const respuesta = await AuthService.resetPasswordForEmail(email.value.trim())
    minutos.value = respuesta.minutos ?? minutos.value
    codigo.value = ''
    if (reenviar) showSnackBar('Te enviamos un código nuevo. El anterior ya no sirve.')
    await irA('codigo')
  } catch (e) {
    error.value = mensaje(e, 'No se pudo enviar el código. Revisa tu conexión e intenta de nuevo.')
  } finally {
    enviando.value = false
  }
}

async function verificarCodigo() {
  error.value = codigo.value.length !== 4 ? 'Escribe los 4 números del código' : null
  if (error.value || enviando.value) return
  enviando.value = true
  try {
    await AuthService.verifyRecoveryCode(email.value.trim(), codigo.value)
    await irA('nueva')
  } catch (e) {
    error.value = mensaje(e, 'No se pudo revisar el código. Revisa tu conexión e intenta de nuevo.')
  } finally {
    enviando.value = false
  }
}

async function guardarPassword() {
  error.value = password.value.length < 6 ? 'Mínimo 6 caracteres' : null
  error2.value = password2.value !== password.value ? 'Las contraseñas no coinciden' : null
  if (error.value || error2.value || enviando.value) return
  enviando.value = true
  try {
    await AuthService.resetPasswordWithCode({
      email: email.value.trim(),
      codigo: codigo.value,
      password: password.value.trim(),
    })
    showSnackBar('Listo, tu contraseña se cambió.')
    router.push('/movements')
  } catch (e) {
    // Si el código venció mientras escribía la contraseña, vuelve al paso del código y lo dice ahí
    if (e instanceof ApiError && e.status === 400) {
      await irA('codigo')
      error.value = e.message
    } else {
      showSnackBar(mensaje(e, 'No se pudo guardar la contraseña. Intenta de nuevo.'), 'var(--color-error)')
    }
  } finally {
    enviando.value = false
  }
}
</script>

<template>
  <div class="publico">
    <BarraPublica pagina="recuperar" />
    <main class="auth-fondo">
      <div class="pub-contenedor">
        <div class="recuperar-tarjeta">
          <!-- Paso 1: el correo -->
          <form v-if="paso === 'correo'" class="auth-formulario" novalidate @submit.prevent="pedirCodigo()">
            <div>
              <p class="recuperar-paso">Paso {{ numeroDePaso }} de 3</p>
              <h1 class="auth-titulo">Recuperar contraseña</h1>
              <p id="ayuda-correo" class="auth-subtitulo">
                Escribe el correo de tu cuenta y te enviaremos un código de 4 dígitos.
              </p>
            </div>
            <div class="field">
              <label class="field-label" for="email">Correo electrónico</label>
              <input
                id="email"
                ref="campoCorreo"
                v-model="email"
                class="input"
                :class="{ invalid: error }"
                type="email"
                placeholder="Ingresa tu correo registrado"
                autocomplete="email"
                aria-describedby="ayuda-correo"
                :aria-invalid="error ? 'true' : 'false'"
              />
              <span v-if="error" class="field-error" role="alert">{{ error }}</span>
            </div>
            <button type="submit" class="pub-btn pub-btn-primario pub-btn-bloque" :disabled="enviando">
              {{ enviando ? 'Enviando…' : 'Enviar código' }}
            </button>
            <p class="auth-pie">
              ¿Ya la recordaste?
              <button type="button" class="auth-enlace" @click="router.push('/login')">Inicia sesión</button>
            </p>
          </form>

          <!-- Paso 2: el código que llegó al correo -->
          <form v-else-if="paso === 'codigo'" class="auth-formulario" novalidate @submit.prevent="verificarCodigo">
            <div>
              <p class="recuperar-paso">Paso {{ numeroDePaso }} de 3</p>
              <h1 class="auth-titulo">Revisa tu correo</h1>
              <p id="ayuda-codigo" class="auth-subtitulo">
                Si <strong class="recuperar-correo">{{ email.trim() }}</strong> está registrado, te enviamos un
                código de 4 dígitos. Sirve por {{ minutos }} minutos. Si no lo ves, revisa la carpeta de spam.
              </p>
            </div>
            <div class="field">
              <label class="field-label" for="codigo">Código de 4 dígitos</label>
              <input
                id="codigo"
                ref="campoCodigo"
                v-model="codigo"
                class="input recuperar-codigo"
                :class="{ invalid: error }"
                type="text"
                inputmode="numeric"
                autocomplete="one-time-code"
                maxlength="4"
                placeholder="0000"
                aria-describedby="ayuda-codigo"
                :aria-invalid="error ? 'true' : 'false'"
                @input="limpiarCodigo"
              />
              <span v-if="error" class="field-error" role="alert">{{ error }}</span>
            </div>
            <button type="submit" class="pub-btn pub-btn-primario pub-btn-bloque" :disabled="enviando">
              {{ enviando ? 'Revisando…' : 'Verificar código' }}
            </button>
            <div class="recuperar-acciones">
              <button type="button" class="auth-enlace" :disabled="enviando" @click="pedirCodigo({ reenviar: true })">
                Reenviar código
              </button>
              <button type="button" class="auth-enlace" @click="irA('correo')">Usar otro correo</button>
            </div>
          </form>

          <!-- Paso 3: la contraseña nueva -->
          <form v-else class="auth-formulario" novalidate @submit.prevent="guardarPassword">
            <div>
              <p class="recuperar-paso">Paso {{ numeroDePaso }} de 3</p>
              <h1 class="auth-titulo">Crea tu contraseña nueva</h1>
              <p class="auth-subtitulo">El código es correcto. Elige una contraseña de al menos 6 caracteres.</p>
            </div>
            <div class="field">
              <label class="field-label" for="password">Contraseña nueva</label>
              <PasswordField
                id="password"
                v-model="password"
                v-model:oculto="oculta"
                placeholder="Mínimo 6 caracteres"
                autocomplete="new-password"
                :error="error"
              />
            </div>
            <div class="field">
              <label class="field-label" for="password2">Confirmar contraseña</label>
              <PasswordField
                id="password2"
                v-model="password2"
                v-model:oculto="oculta2"
                placeholder="Repite tu contraseña"
                autocomplete="new-password"
                :error="error2"
              />
            </div>
            <button type="submit" class="pub-btn pub-btn-primario pub-btn-bloque" :disabled="enviando">
              {{ enviando ? 'Guardando…' : 'Guardar contraseña' }}
            </button>
          </form>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.recuperar-tarjeta {
  width: 100%;
  max-width: 480px;
  margin: 0 auto;
  border-radius: 28px;
  background: var(--color-superficie);
  box-shadow: var(--sombra-publica);
}

.recuperar-paso {
  margin-bottom: 4px;
  color: var(--color-publico-accion);
  font-size: 15px;
  font-weight: 600;
}

.recuperar-correo {
  color: var(--color-publico-titulo);
  overflow-wrap: anywhere;
}

/* Código grande y espaciado: se lee de un vistazo al copiarlo del correo */
.recuperar-codigo {
  font-size: 28px;
  font-weight: 600;
  letter-spacing: 0.5em;
  text-indent: 0.5em; /* compensa el espacio que letter-spacing deja después del último número */
  text-align: center;
  font-variant-numeric: tabular-nums;
}

.recuperar-acciones {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
}

.recuperar-acciones .auth-enlace {
  align-self: auto;
}

.pub-btn:disabled {
  cursor: wait;
  opacity: 0.75;
}
</style>
