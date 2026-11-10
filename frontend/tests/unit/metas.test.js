import { describe, expect, test } from 'vitest'
import { calcularPorcentajeMeta, validarMontoOperacion } from '../../src/utils/metas.js'

describe('Metas de Ahorro y Fondos Disponibles (Tarea 8)', () => {
  test('porcentaje de la meta no excede 100% y maneja división por cero', () => {
    expect(calcularPorcentajeMeta(50, 200)).toBe(25)
    expect(calcularPorcentajeMeta(200, 200)).toBe(100)
    expect(calcularPorcentajeMeta(300, 200)).toBe(100)
    expect(calcularPorcentajeMeta(50, 0)).toBe(0)
  })

  test('valida monto de operación correctamente', () => {
    expect(validarMontoOperacion('')).toBe('El campo no puede estar vacío')
    expect(validarMontoOperacion('abc')).toBe('Formato numérico inválido')
    expect(validarMontoOperacion('0')).toBe('El monto debe ser mayor a 0')
    expect(validarMontoOperacion('-10')).toBe('El monto debe ser mayor a 0')
    expect(validarMontoOperacion('50', 100, 'asignar')).toBe(null)
    expect(validarMontoOperacion('150', 100, 'asignar')).toContain('Fondos insuficientes')
    expect(validarMontoOperacion('80', 50, 'retirar')).toContain('Fondos insuficientes en la meta')
  })
})
