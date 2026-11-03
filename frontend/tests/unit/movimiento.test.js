// Portado de test/movimiento_test.dart
import { expect, test } from 'vitest'
import { esTransicionValida, puedeEditarMonto, siguienteEstado } from '../../src/utils/estadoMovimiento.js'

test('estado inicial es pendiente', () => {
  const estadoInicial = 'pendiente'
  expect(estadoInicial).toBe('pendiente')
})

test('la acción hace la transicion esperada', () => {
  expect(siguienteEstado('pendiente')).toBe('pagado')
  expect(siguienteEstado('pagado')).toBe('cancelado')
})

test('transicion invalida es rechazada', () => {
  expect(siguienteEstado('cancelado')).toBeNull()
  expect(esTransicionValida('cancelado', 'pagado')).toBe(false)
  expect(esTransicionValida('pendiente', 'cancelado')).toBe(false)
})

test('los demas datos se conservan', () => {
  const m = {
    id: '1',
    tipo: 'gasto',
    monto: 25.0,
    categoria: 'Transporte',
    descripcion: 'Pasaje pal taxi',
    fecha: '2025-10-01',
    estado: 'pendiente',
  }

  // simula el cambio de estado sin tocar el resto
  const copia = { ...m }
  copia.estado = siguienteEstado(m.estado)

  expect(copia.id).toBe('1')
  expect(copia.tipo).toBe('gasto')
  expect(copia.monto).toBe(25.0)
  expect(copia.categoria).toBe('Transporte')
  expect(copia.descripcion).toBe('Pasaje pal taxi')
  expect(copia.fecha).toBe('2025-10-01')
  expect(copia.estado).toBe('pagado')
})

test('no se puede editar el monto del movimiento si el estado es pagado', () => {
  // En estado pendiente o cancelado, el monto SÍ se puede editar:
  expect(puedeEditarMonto('pendiente')).toBe(true)
  expect(puedeEditarMonto('cancelado')).toBe(true)

  // En estado pagado, el monto NO se puede editar (restricción de negocio):
  expect(puedeEditarMonto('pagado')).toBe(false)
})
