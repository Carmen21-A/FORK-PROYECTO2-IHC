// Portado de lib/utils/limite_mensual.dart (Tarea 4: limite mensual)
import { calcularMontoTotalMovimientos } from './movimientosFiltros.js'
import { parseDouble } from './formato.js'

export function validarMontoLimite(texto) {
  if (texto === null || texto === undefined || texto.trim() === '') {
    return 'El límite no debe estar vacío'
  }

  // Si es letra devolvera null
  const numero = parseDouble(texto)
  if (numero === null) {
    return 'No se permite letras, ingresa un número válido'
  }

  if (numero <= 0) {
    return 'El monto tiene que ser mayor a 0'
  }

  return null
}

export function esLimiteMenorAGasto(nuevoLimite, gastoActualMes) {
  return nuevoLimite < gastoActualMes
}

export function superaLimiteMensual({ gastoActualDelMes, nuevoGasto, limite }) {
  const nuevoTotal = gastoActualDelMes + nuevoGasto
  return nuevoTotal > limite
}

export function getMensajesErrorLimiteMensual({ nuevoMonto, gastoActual, limite }) {
  const supera = superaLimiteMensual({
    gastoActualDelMes: gastoActual,
    nuevoGasto: nuevoMonto,
    limite,
  })
  const esMenorAGasto = esLimiteMenorAGasto(nuevoMonto, gastoActual)

  if (supera) {
    return `al editar se excedera el limite mensual de ${limite}, el gasto actual es ${gastoActual}`
  } else if (esMenorAGasto) {
    return `al editar se reduce el limite mensual a ${nuevoMonto}, no se puede poner limite menor al gasto actual de ${gastoActual}`
  } else {
    return null
  }
}

export function calcularGastoTotalMes(movimientos, mes) {
  // No admite cancelados
  const movimientosMes = movimientos.filter(
    (m) => String(m.fecha).startsWith(mes) && m.tipo === 'gasto' && m.estado !== 'cancelado',
  )

  return calcularMontoTotalMovimientos(movimientosMes)
}
