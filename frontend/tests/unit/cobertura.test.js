// Casos que faltaban para llegar al 100 % de cobertura de src/utils (entrega final)
import { afterEach, describe, expect, it, vi } from 'vitest'
import { claveMes, dartNum, fixed } from '../../src/utils/formato.js'
import { getMensajesErrorLimiteMensual } from '../../src/utils/limiteMensual.js'
import { calcularPorcentajeMeta, diasRestantes, validarMontoOperacion } from '../../src/utils/metas.js'
import { descargarArchivo } from '../../src/utils/misDatos.js'

describe('formato', () => {
  it('muestra los números como Dart: 150 -> "150.0" y 25.5 -> "25.5"', () => {
    expect(dartNum(150)).toBe('150.0')
    expect(dartNum('25.5')).toBe('25.5')
  })

  it('fija decimales (2 por defecto)', () => {
    expect(fixed(3)).toBe('3.00')
    expect(fixed('2.456', 1)).toBe('2.5')
  })

  it('arma la clave de mes YYYY-MM con cero a la izquierda', () => {
    expect(claveMes(new Date(2026, 0, 15))).toBe('2026-01')
    expect(claveMes(new Date(2026, 10, 1))).toBe('2026-11')
  })
})

describe('mensajes del límite mensual al editar', () => {
  it('avisa si el gasto editado supera el límite', () => {
    expect(getMensajesErrorLimiteMensual({ nuevoMonto: 600, gastoActual: 100, limite: 500 })).toContain('se excedera el limite mensual')
  })

  it('avisa si el nuevo límite queda por debajo de lo ya gastado', () => {
    expect(getMensajesErrorLimiteMensual({ nuevoMonto: 50, gastoActual: 100, limite: 1000 })).toContain('no se puede poner limite menor')
  })

  it('no dice nada cuando todo está bien', () => {
    expect(getMensajesErrorLimiteMensual({ nuevoMonto: 50, gastoActual: 10, limite: 1000 })).toBeNull()
  })
})

describe('metas de ahorro', () => {
  it('valida el monto: vacío, letras, cero y negativo', () => {
    expect(validarMontoOperacion('')).toBe('El campo no puede estar vacío')
    expect(validarMontoOperacion(null)).toBe('El campo no puede estar vacío')
    expect(validarMontoOperacion('abc')).toBe('Formato numérico inválido')
    expect(validarMontoOperacion('0')).toBe('El monto debe ser mayor a 0')
  })

  it('explica el motivo cuando el monto supera lo permitido, según la operación', () => {
    expect(validarMontoOperacion('200', 100, 'asignar')).toBe('Fondos insuficientes: el saldo disponible es de 100.0 Bs')
    expect(validarMontoOperacion('200', 100, 'retirar')).toBe('Fondos insuficientes en la meta: cuenta con 100.0 Bs')
    expect(validarMontoOperacion('200', 100, 'transferir')).toBe('Fondos insuficientes en la meta: cuenta con 100.0 Bs')
    expect(validarMontoOperacion('200', 100, 'otra')).toBe('Supera el límite máximo permitido de 100.0 Bs')
  })

  it('acepta un monto dentro del máximo', () => {
    expect(validarMontoOperacion('50', 100)).toBeNull()
    expect(validarMontoOperacion('50')).toBeNull()
  })

  it('calcula el porcentaje, sin pasar de 100 y con 0 si no hay objetivo', () => {
    expect(calcularPorcentajeMeta(250, 1000)).toBe(25)
    expect(calcularPorcentajeMeta(1500, 1000)).toBe(100)
    expect(calcularPorcentajeMeta(10, 0)).toBe(0)
    expect(calcularPorcentajeMeta(undefined, undefined)).toBe(0)
  })

  it('cuenta los días que faltan hasta la fecha límite', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2026, 10, 18, 15, 0))
    expect(diasRestantes('2026-11-28')).toBe(10)
    expect(diasRestantes('2026-11-18')).toBe(0)
    expect(diasRestantes(null)).toBeNull()
    vi.useRealTimers()
  })
})

describe('descargar archivo', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
    vi.useRealTimers()
  })

  it('crea un enlace temporal, lo pulsa y libera la URL después', () => {
    vi.useFakeTimers()
    const enlace = { click: vi.fn(), remove: vi.fn() }
    const appendChild = vi.fn()
    vi.stubGlobal('document', { createElement: vi.fn(() => enlace), body: { appendChild } })
    const revoke = vi.fn()
    vi.stubGlobal('URL', { createObjectURL: vi.fn(() => 'blob:prueba'), revokeObjectURL: revoke })

    descargarArchivo('a;b', 'mis-datos.csv', 'text/csv')

    expect(enlace.href).toBe('blob:prueba')
    expect(enlace.download).toBe('mis-datos.csv')
    expect(appendChild).toHaveBeenCalledWith(enlace)
    expect(enlace.click).toHaveBeenCalled()
    expect(enlace.remove).toHaveBeenCalled()
    vi.advanceTimersByTime(1000)
    expect(revoke).toHaveBeenCalledWith('blob:prueba')
  })
})
