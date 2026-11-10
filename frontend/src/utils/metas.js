// Utilidades para cálculo y validación de Metas de Ahorro (Tarea 8)
import { parseDouble } from './formato.js'

// El saldo disponible lo calcula el backend (GET /api/metas/resumen-fondos)

export function validarMontoOperacion(montoTexto, maximoPermitido = null, operacion = 'asignar') {
  if (montoTexto === undefined || montoTexto === null || String(montoTexto).trim() === '') {
    return 'El campo no puede estar vacío'
  }
  const n = parseDouble(montoTexto)
  if (n === null) return 'Formato numérico inválido'
  if (n <= 0) return 'El monto debe ser mayor a 0'

  if (maximoPermitido !== null) {
    const max = Number(maximoPermitido)
    if (n > max) {
      if (operacion === 'asignar') {
        return `Fondos insuficientes: el saldo disponible es de ${max.toFixed(1)} Bs`
      }
      if (operacion === 'retirar' || operacion === 'transferir') {
        return `Fondos insuficientes en la meta: cuenta con ${max.toFixed(1)} Bs`
      }
      return `Supera el límite máximo permitido de ${max.toFixed(1)} Bs`
    }
  }

  return null
}

export function calcularPorcentajeMeta(montoAhorrado, montoObjetivo) {
  const obj = Number(montoObjetivo) || 0
  const ahorr = Number(montoAhorrado) || 0
  if (obj <= 0) return 0
  const pct = (ahorr / obj) * 100
  return Math.min(Math.round(pct * 10) / 10, 100)
}

export function diasRestantes(fechaLimiteIso) {
  if (!fechaLimiteIso) return null
  const limite = new Date(fechaLimiteIso + 'T00:00:00')
  const hoy = new Date()
  hoy.setHours(0, 0, 0, 0)
  const diffTime = limite.getTime() - hoy.getTime()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays
}
