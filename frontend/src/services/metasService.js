// Servicio para Metas de Ahorro y Gestión de Fondos Disponibles (Tarea 8)
import { api } from './api.js'

export const MetasService = {
  /// Obtiene todas las metas de ahorro del usuario
  async getAll() {
    return await api('/metas')
  },

  /// Obtiene el balance detallado de fondos (total, gastos, ingresos, reservados, disponible)
  async getResumenFondos() {
    return await api('/metas/resumen-fondos')
  },

  /// Crea una nueva meta de ahorro
  async create({ nombre, monto_objetivo, fecha_limite }) {
    return await api('/metas', {
      method: 'POST',
      body: { nombre, monto_objetivo, fecha_limite },
    })
  },

  /// Actualiza datos básicos de la meta
  async update(id, datos) {
    return await api(`/metas/${id}`, {
      method: 'PUT',
      body: datos,
    })
  },

  /// Elimina una meta de ahorro (libera sus fondos al disponible)
  async delete(id) {
    await api(`/metas/${id}`, { method: 'DELETE' })
  },

  /// Asigna dinero del saldo disponible hacia la meta
  async asignar(id, monto) {
    return await api(`/metas/${id}/asignar`, {
      method: 'POST',
      body: { monto },
    })
  },

  /// Retira dinero de la meta y lo devuelve al saldo disponible
  async retirar(id, monto) {
    return await api(`/metas/${id}/retirar`, {
      method: 'POST',
      body: { monto },
    })
  },

  /// Transfiere fondos de una meta hacia otra meta
  async transferir(id, meta_destino_id, monto) {
    return await api(`/metas/${id}/transferir`, {
      method: 'POST',
      body: { meta_destino_id, monto },
    })
  },
}
