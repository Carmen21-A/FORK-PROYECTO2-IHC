// Portado de lib/services/auth_service.dart
import { api } from './api.js'
import { borrarSesion, guardarSesion, sesionActual } from './sesion.js'

export const AuthService = {
  // registrar usuario
  async signUp({ nombre, email, password }) {
    const sesion = await api('/auth/register', { method: 'POST', body: { nombre, email, password } })
    guardarSesion(sesion)
    return sesion
  },

  // iniciar sesion
  async signInWithPassword({ email, password }) {
    const sesion = await api('/auth/login', { method: 'POST', body: { email, password } })
    guardarSesion(sesion)
    return sesion
  },

  // cerrar sesión
  async signOut() {
    borrarSesion()
  },

  // actualizar contraseña
  async updatePassword(newPassword) {
    await api('/auth/password', { method: 'PATCH', body: { password: newPassword } })
  },

  // recuperar contraseña, paso 1: manda un código de 4 dígitos al correo
  async resetPasswordForEmail(email) {
    return api('/auth/password/recover', { method: 'POST', body: { email } })
  },

  // paso 2: revisa el código (todavía no lo gasta)
  async verifyRecoveryCode(email, codigo) {
    return api('/auth/password/verify', { method: 'POST', body: { email, codigo } })
  },

  // paso 3: guarda la contraseña nueva con el código y abre la sesión
  async resetPasswordWithCode({ email, codigo, password }) {
    const sesion = await api('/auth/password/reset', { method: 'POST', body: { email, codigo, password } })
    guardarSesion(sesion)
    return sesion
  },

  // usuario actual
  get currentUser() {
    return sesionActual.value?.user ?? null
  },
}
