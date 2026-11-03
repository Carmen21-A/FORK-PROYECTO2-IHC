// Portado de test/historial_test.dart
import { describe, expect, test } from 'vitest'
import {
  armarDetalleEvento,
  filtrarHistorial,
  ordenarRecientePrimero,
} from '../../src/utils/historial.js'

describe('1. Detalle del evento', () => {
  test('arma el detalle de un gasto con descripcion', () => {
    const detalle = armarDetalleEvento({
      tipo: 'gasto',
      monto: 50,
      categoria: 'Comida',
      descripcion: 'Almuerzo',
    })

    expect(detalle).toBe('Gasto 50 Bs · Comida · Almuerzo')
  })

  test('arma el detalle de un ingreso sin descripcion', () => {
    const detalle = armarDetalleEvento({
      tipo: 'ingreso',
      monto: 200,
      categoria: 'Otros',
      descripcion: '',
    })

    expect(detalle).toBe('Ingreso 200 Bs · Otros')
  })

  test('ignora descripcion vacia o con espacios', () => {
    const detalle = armarDetalleEvento({
      tipo: 'gasto',
      monto: 10,
      categoria: 'Transporte',
      descripcion: '   ',
    })

    expect(detalle).toBe('Gasto 10 Bs · Transporte')
  })
})

describe('2. Orden reciente primero', () => {
  test('ordena los eventos del mas nuevo al mas viejo', () => {
    const eventos = [
      { id: 'a', created_at: '2026-10-15T10:00:00Z' },
      { id: 'c', created_at: '2026-10-17T09:30:00Z' },
      { id: 'b', created_at: '2026-10-16T12:00:00Z' },
    ]

    const ordenados = ordenarRecientePrimero(eventos)

    expect(ordenados.map((e) => e.id)).toEqual(['c', 'b', 'a'])
  })
})

describe('3. Caso vacio', () => {
  test('devuelve lista vacia cuando no hay eventos', () => {
    const ordenados = ordenarRecientePrimero([])

    expect(ordenados).toEqual([])
  })
})

describe('4. Filtrar historial', () => {
  const eventosPrueba = [
    { id: '1', accion: 'creado', detalle: 'Gasto 50 Bs · Comida · Almuerzo' },
    { id: '2', accion: 'editado', detalle: 'Gasto 20 Bs · Transporte · Micro' },
    { id: '3', accion: 'eliminado', detalle: 'Ingreso 100 Bs · Otros' },
  ]

  test('filtra por texto en detalle ignorando mayusculas', () => {
    const resultado = filtrarHistorial(eventosPrueba, 'comida')

    expect(resultado.length).toBe(1)
    expect(resultado[0].id).toBe('1')
  })

  test('filtra por accion', () => {
    const resultado = filtrarHistorial(eventosPrueba, 'eliminado')

    expect(resultado.length).toBe(1)
    expect(resultado[0].id).toBe('3')
  })

  test('devuelve lista vacia cuando nada coincide', () => {
    const resultado = filtrarHistorial(eventosPrueba, 'cine')

    expect(resultado).toEqual([])
  })

  test('devuelve todos los eventos si la busqueda esta vacia', () => {
    const resultado = filtrarHistorial(eventosPrueba, '   ')

    expect(resultado.length).toBe(3)
  })
})
