// Portado de lib/services/auth_service.dart
import { api } from './api.js'
import { borrarSesion, guardarSesion, sesionActual } from './sesion.js'

export const AuthService = {
  // registrar usuario
  async signUp({ email, password }) {
    const sesion = await api('/auth/register', { method: 'POST', body: { email, password } })
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

  // recuperar contraseña x correo
  async resetPasswordForEmail(email) {
    return api('/auth/password/recover', { method: 'POST', body: { email } })
  },

  // abre sesion con el enlace del correo (verifyOTP de Supabase)
  async verifyRecovery(tokenHash) {
    const sesion = await api('/auth/password/verify', {
      method: 'POST',
      body: { token_hash: tokenHash },
    })
    guardarSesion(sesion)
    return sesion
  },

  // usuario actual
  get currentUser() {
    return sesionActual.value?.user ?? null
  },
}
