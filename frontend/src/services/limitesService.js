// Portado de lib/services/limites_service.dart
import { api } from './api.js'

export const LimitesService = {
  async getLimit(mes) {
    const respuesta = await api(`/limites/${mes}`)
    return respuesta.limite
  },

  async saveMonthLimit({ mes, limite }) {
    await api(`/limites/${mes}`, { method: 'PUT', body: { limite } })
  },
}
