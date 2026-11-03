// Portado de test/limite_mensual_test.dart
import { describe, expect, test } from 'vitest'
import {
  calcularGastoTotalMes,
  esLimiteMenorAGasto,
  getMensajesErrorLimiteMensual,
  superaLimiteMensual,
  validarMontoLimite,
} from '../../src/utils/limiteMensual.js'

describe('1. Validacion del texto del limite', () => {
  test('Tiene que retornar null (valido) para montos correctos', () => {
    expect(validarMontoLimite('500')).toBeNull()
    expect(validarMontoLimite('100.5')).toBeNull()
  })

  test('No debe dejar pasar cadenas vacias o nulas', () => {
    expect(validarMontoLimite('')).toBe('El límite no debe estar vacío')
    expect(validarMontoLimite(null)).toBe('El límite no debe estar vacío')
  })

  test('No debe dejar pasar letras o textos mezclados con numeros', () => {
    expect(validarMontoLimite('abcasdasdsad')).toBe('No se permite letras, ingresa un número válido')
    expect(validarMontoLimite('abcasd123213')).toBe('No se permite letras, ingresa un número válido')
  })

  test('No debe dejar pasar ceros o numeros negativos', () => {
    expect(validarMontoLimite('0')).toBe('El monto tiene que ser mayor a 0')
    expect(validarMontoLimite('-50')).toBe('El monto tiene que ser mayor a 0')
  })
})

describe('2. Limite menor a lo ya gastado', () => {
  test('Debe devolver true si el nuevo limite es menor al gasto actual', () => {
    expect(esLimiteMenorAGasto(200.0, 300.0)).toBe(true)
  })

  test('Debe devolver false si el nuevo limite es mayor o igual al gasto actual', () => {
    expect(esLimiteMenorAGasto(500.0, 300.0)).toBe(false)
  })
})

describe('3. Para no superar el limite mensual', () => {
  test('Debe devolver true si al agregar el nuevo gasto se supera el limite', () => {
    const supera = superaLimiteMensual({ gastoActualDelMes: 400.0, nuevoGasto: 150.0, limite: 500.0 })
    expect(supera).toBe(true)
  })

  test('Debe devolver false si el gasto entra dentro del limite permitido', () => {
    const supera = superaLimiteMensual({ gastoActualDelMes: 400.0, nuevoGasto: 50.0, limite: 500.0 })
    expect(supera).toBe(false)
  })

  test('Debe devolver el mensaje de error al exceder el limite', () => {
    const mensaje = getMensajesErrorLimiteMensual({
      nuevoMonto: 150.0,
      gastoActual: 400.0,
      limite: 500.0,
    })
    expect(mensaje).toContain('al editar se excedera el limite mensual')
  })
})

describe('4. Calcular el gasto total del mes', () => {
  const movimientosMock = [
    { fecha: '2026-10-01', tipo: 'gasto', estado: 'pagado', monto: 100.0 },
    { fecha: '2026-10-05', tipo: 'gasto', estado: 'pendiente', monto: 50.0 },
    { fecha: '2026-10-10', tipo: 'gasto', estado: 'cancelado', monto: 200.0 },
    { fecha: '2026-10-12', tipo: 'ingreso', estado: 'pagado', monto: 1000.0 },
    { fecha: '2026-09-15', tipo: 'gasto', estado: 'pagado', monto: 300.0 },
  ]

  test('Debe sumar solo los gastos validos del mes y excluir cancelados e ingresos', () => {
    const totalOctubre = calcularGastoTotalMes(movimientosMock, '2026-10')

    // Solo deberia sumar 100.0 + 50.0 = 150.0
    expect(totalOctubre).toBe(150.0)
  })
})
