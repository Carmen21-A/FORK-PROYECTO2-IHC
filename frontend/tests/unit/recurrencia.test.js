// Tarea 6: gastos recurrentes (mismos casos que backend/tests/test_logica.py)
import { describe, expect, test } from 'vitest'
import { siguienteFecha } from '../../src/utils/recurrencia.js'
import { fechaISO } from '../../src/utils/formato.js'

const siguiente = (y, m, d, recurrencia) => fechaISO(siguienteFecha(new Date(y, m - 1, d), recurrencia))

describe('Siguiente ocurrencia de un gasto recurrente', () => {
  test('semanal: 7 días después, aunque cambie de mes', () => {
    expect(siguiente(2026, 11, 3, 'semanal')).toBe('2026-11-10')
    expect(siguiente(2026, 11, 28, 'semanal')).toBe('2026-12-05')
  })

  test('mensual: el mismo día del mes siguiente, aunque cambie de año', () => {
    expect(siguiente(2026, 11, 3, 'mensual')).toBe('2026-12-03')
    expect(siguiente(2026, 12, 15, 'mensual')).toBe('2027-01-15')
  })

  test('mensual: si el día no existe, usa el último día del mes', () => {
    expect(siguiente(2026, 1, 31, 'mensual')).toBe('2026-02-28')
    expect(siguiente(2028, 1, 31, 'mensual')).toBe('2028-02-29')
  })
})
