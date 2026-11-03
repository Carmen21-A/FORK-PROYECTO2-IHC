// Portado de lib/utils/movimientos_filtros.dart (Tarea 4: busqueda y filtros)
import { parseFecha } from './formato.js'

export function calcularMontoTotalMovimientos(movimientos) {
  let montoTotal = 0.0
  for (let i = 0; i < movimientos.length; i++) {
    const montoActual = Number(movimientos[i].monto)
    montoTotal = montoTotal + montoActual
  }
  return montoTotal
}

// Suma solo los gastos no cancelados de la lista
export function calcularTotalGastos(movimientos) {
  const gastos = movimientos.filter((m) => m.tipo === 'gasto' && m.estado !== 'cancelado')
  return calcularMontoTotalMovimientos(gastos)
}

// Suma solo los ingresos no cancelados de la lista
export function calcularTotalIngresos(movimientos) {
  const ingresos = movimientos.filter((m) => m.tipo === 'ingreso' && m.estado !== 'cancelado')
  return calcularMontoTotalMovimientos(ingresos)
}

// Aplica busqueda y filtros sobre una lista de movimientos
export function filtrarMovimientos(
  movimientos,
  { texto = null, tipo = null, categoria = null, estado = null, desde = null, hasta = null } = {},
) {
  return movimientos.filter((m) => {
    // Busqueda por descripcion con coincidencia parcial
    if (texto !== null && texto.trim() !== '') {
      const descripcion = String(m.descripcion ?? '').toLowerCase()
      if (!descripcion.includes(texto.trim().toLowerCase())) {
        return false
      }
    }
    if (tipo !== null && m.tipo !== tipo) return false
    if (categoria !== null && m.categoria !== categoria) return false
    if (estado !== null && m.estado !== estado) return false

    if (desde !== null || hasta !== null) {
      const fecha = parseFecha(m.fecha)
      if (desde !== null && fecha < desde) return false
      if (hasta !== null && fecha > hasta) return false
    }

    return true
  })
}
