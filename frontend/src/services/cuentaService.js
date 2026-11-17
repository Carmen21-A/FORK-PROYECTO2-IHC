// Tarea 10 · Mis datos y salida honesta
import { api } from './api.js'
import { borrarSesion } from './sesion.js'

export const CuentaService = {
  // Todo lo que la app guarda de la persona (cuenta, movimientos, límites, presupuestos, metas, historial)
  async misDatos() {
    return api('/cuenta/datos')
  },

  // Elimina la cuenta y todos sus datos. Después cierra la sesión en el navegador.
  async eliminarCuenta() {
    const resultado = await api('/cuenta', { method: 'DELETE', body: { confirmar: true } })
    borrarSesion()
    return resultado
  },
}
