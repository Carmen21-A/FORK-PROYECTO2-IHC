// Tarea 10 · Mis datos y salida honesta
import { describe, expect, it } from 'vitest'
import { celdaCsv, consecuenciasEliminar, movimientosACsv, nombreArchivo } from '../../src/utils/misDatos.js'

describe('CSV de movimientos', () => {
  const movimientos = [
    { fecha: '2026-11-15', tipo: 'gasto', categoria: 'Transporte', descripcion: 'Pasaje de micro', monto: 40, estado: 'pendiente', recurrencia: null },
    { fecha: '2026-11-15', tipo: 'ingreso', categoria: 'Otros', descripcion: 'Mesada, de mamá', monto: 300, estado: 'pagado', recurrencia: 'mensual' },
  ]

  it('tiene cabecera en español y una fila por movimiento', () => {
    const lineas = movimientosACsv(movimientos).replace('﻿', '').trim().split('\r\n')
    expect(lineas[0]).toBe('Fecha,Tipo,Categoría,Descripción,Monto (Bs),Estado,Se repite')
    expect(lineas[1]).toBe('2026-11-15,gasto,Transporte,Pasaje de micro,40,pendiente,')
    expect(lineas).toHaveLength(3)
  })

  it('pone comillas a los textos con comas para no partir la columna', () => {
    expect(movimientosACsv(movimientos)).toContain('"Mesada, de mamá"')
    expect(celdaCsv('dijo "hola"')).toBe('"dijo ""hola"""')
    expect(celdaCsv('a,"b"')).toBe('"a,""b"""')
  })

  it('empieza con BOM para que Excel lea bien las tildes', () => {
    expect(movimientosACsv([]).startsWith('﻿')).toBe(true)
  })

  it('no deja que una descripción se ejecute como fórmula en Excel', () => {
    expect(celdaCsv('=HYPERLINK("x")')).toBe(`"'=HYPERLINK(""x"")"`)
    expect(celdaCsv('-5')).toBe("'-5")
    expect(celdaCsv(-5)).toBe('-5') // los números sí se dejan tal cual
  })
})

describe('nombre del archivo', () => {
  it('lleva qué es y la fecha del día', () => {
    expect(nombreArchivo('movimientos', 'csv', new Date(2026, 10, 5))).toBe('presupuesto-estudiantil-movimientos-2026-11-05.csv')
  })
})

describe('consecuencias de eliminar la cuenta', () => {
  it('dice exactamente qué se borra, con los números reales', () => {
    const resumen = { movimientos: 2, limites_mensuales: 1, presupuestos_categoria: 1, metas_ahorro: 0, historial: 2 }
    expect(consecuenciasEliminar(resumen)).toEqual([
      '2 movimientos',
      '1 límite mensual',
      '1 presupuesto por categoría',
      '2 registros del historial',
    ])
  })

  it('una cuenta sin datos no muestra una lista que asuste', () => {
    expect(consecuenciasEliminar({ movimientos: 0 })).toEqual([])
  })
})
