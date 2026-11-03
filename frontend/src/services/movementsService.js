// Portado de lib/services/movements_service.dart
// (el historial de cada accion lo registra el backend)
import { api } from './api.js'
import { fechaISO } from '../utils/formato.js'

export const MovementsService = {
  async getAll() {
    return api('/movimientos')
  },

  async create({ tipo, monto, categoria, fecha, descripcion, recurrencia = null }) {
    return api('/movimientos', {
      method: 'POST',
      body: { tipo, monto, categoria, descripcion, fecha: fechaISO(fecha), recurrencia },
    })
  },

  async delete(id) {
    await api(`/movimientos/${id}`, { method: 'DELETE' })
  },

  // Si se paga un gasto recurrente, la respuesta trae el `siguiente` o un `aviso`
  async cambiarEstado(id, nuevoEstado) {
    return api(`/movimientos/${id}/estado`, { method: 'PATCH', body: { estado: nuevoEstado } })
  },

  async update({ id, tipo, monto, categoria, fecha, descripcion, recurrencia = null }) {
    return api(`/movimientos/${id}`, {
      method: 'PUT',
      body: { tipo, monto, categoria, descripcion, fecha: fechaISO(fecha), recurrencia },
    })
  },

  // Combina busqueda y filtros en una sola consulta a la API
  async buscarConFiltros({ texto, tipo, categoria, estado, desde, hasta } = {}) {
    return api('/movimientos', {
      params: {
        texto: texto?.trim() || null,
        tipo,
        categoria,
        estado,
        desde: desde ? fechaISO(desde) : null,
        hasta: hasta ? fechaISO(hasta) : null,
      },
    })
  },
}
