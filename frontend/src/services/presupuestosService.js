// Portado de lib/services/presupuestos_service.dart
import { api } from './api.js'
import { construirResumenMensual } from '../utils/presupuestoCategoria.js'

export const PresupuestosService = {
  /// Obtiene todos los presupuestos asignados por categoría para un mes (formato 'YYYY-MM')
  /// Retorna un mapa con { 'Comida': 400.0, 'Transporte': 150.0, ... }
  async getPresupuestosMes(mes) {
    const filas = await api(`/presupuestos/${mes}`)
    const resultado = {}
    for (const fila of filas) {
      resultado[fila.categoria] = Number(fila.monto)
    }
    return resultado
  },

  /// Guarda o actualiza el presupuesto de una categoría para un mes
  async savePresupuestoCategoria({ mes, categoria, monto }) {
    await api(`/presupuestos/${mes}/${encodeURIComponent(categoria)}`, {
      method: 'PUT',
      body: { monto },
    })
  },

  /// Elimina el presupuesto de una categoría para un mes específico
  async deletePresupuestoCategoria({ mes, categoria }) {
    await api(`/presupuestos/${mes}/${encodeURIComponent(categoria)}`, { method: 'DELETE' })
  },

  /// Construye el resumen de presupuesto vs consumo combinando la base de datos y movimientos
  async getResumenMensual({ mes, movimientos }) {
    const presupuestos = await this.getPresupuestosMes(mes)
    return construirResumenMensual({ mes, presupuestosPorCategoria: presupuestos, movimientos })
  },
}
