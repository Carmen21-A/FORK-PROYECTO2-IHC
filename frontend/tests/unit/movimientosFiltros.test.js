// Portado de test/movimientos_filtros_test.dart
import { describe, expect, test } from 'vitest'
import {
  calcularMontoTotalMovimientos,
  calcularTotalGastos,
  calcularTotalIngresos,
  filtrarMovimientos,
} from '../../src/utils/movimientosFiltros.js'

const movimientos = [
  {
    fecha: '2026-10-01',
    tipo: 'gasto',
    categoria: 'Comida',
    estado: 'pagado',
    monto: 100.0,
    descripcion: 'Almuerzo universidad',
  },
  {
    fecha: '2026-10-05',
    tipo: 'gasto',
    categoria: 'Transporte',
    estado: 'pendiente',
    monto: 50.0,
    descripcion: 'Pasaje bus',
  },
  {
    fecha: '2026-10-10',
    tipo: 'ingreso',
    categoria: 'Otros',
    estado: 'pagado',
    monto: 1000.0,
    descripcion: 'Beca',
  },
  {
    fecha: '2026-09-20',
    tipo: 'gasto',
    categoria: 'Comida',
    estado: 'pagado',
    monto: 30.0,
    descripcion: 'Cena',
  },
]

describe('1. Casos con resultados', () => {
  test('filtra por coincidencia parcial en la descripcion', () => {
    const filtrados = filtrarMovimientos(movimientos, { texto: 'almu' })

    expect(filtrados.length).toBe(1)
    expect(filtrados[0].descripcion).toBe('Almuerzo universidad')
  })

  test('filtra por tipo', () => {
    const filtrados = filtrarMovimientos(movimientos, { tipo: 'ingreso' })

    expect(filtrados.length).toBe(1)
    expect(filtrados[0].descripcion).toBe('Beca')
  })
})

describe('2. Caso sin resultados', () => {
  test('devuelve lista vacia cuando nada coincide', () => {
    const filtrados = filtrarMovimientos(movimientos, { texto: 'zzzz' })

    expect(filtrados).toEqual([])
  })
})

describe('3. Combinacion de varios filtros', () => {
  test('combina tipo, categoria y estado', () => {
    const filtrados = filtrarMovimientos(movimientos, {
      tipo: 'gasto',
      categoria: 'Comida',
      estado: 'pagado',
    })

    // Octubre y septiembre
    expect(filtrados.length).toBe(2)
  })

  test('combina texto, tipo y rango de fechas', () => {
    const filtrados = filtrarMovimientos(movimientos, {
      texto: 'pasaje',
      tipo: 'gasto',
      desde: new Date(2026, 9, 1),
      hasta: new Date(2026, 9, 31),
    })

    expect(filtrados.length).toBe(1)
    expect(filtrados[0].descripcion).toBe('Pasaje bus')
  })
})

describe('4. Total coincide con la suma de los filtrados', () => {
  test('el total es la suma de los montos filtrados', () => {
    const filtrados = filtrarMovimientos(movimientos, { tipo: 'gasto', categoria: 'Comida' })
    const total = calcularMontoTotalMovimientos(filtrados)

    // 100 + 30
    expect(total).toBe(130.0)

    const sumaManual = filtrados.reduce((sum, m) => sum + Number(m.monto), 0.0)
    expect(total).toBe(sumaManual)
  })
})

describe('5. Totales separados por tipo', () => {
  const conCancelado = [
    { fecha: '2026-10-01', tipo: 'gasto', categoria: 'Comida', estado: 'pagado', monto: 100.0, descripcion: 'Almuerzo' },
    { fecha: '2026-10-02', tipo: 'gasto', categoria: 'Ocio', estado: 'cancelado', monto: 200.0, descripcion: 'Cine' },
    { fecha: '2026-10-03', tipo: 'ingreso', categoria: 'Otros', estado: 'pagado', monto: 500.0, descripcion: 'Beca' },
  ]

  test('el total de gastos no incluye cancelados', () => {
    expect(calcularTotalGastos(conCancelado)).toBe(100.0)
  })

  test('el total de ingresos no incluye cancelados', () => {
    expect(calcularTotalIngresos(conCancelado)).toBe(500.0)
  })
})
