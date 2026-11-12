// Clase 21: si no hay prueba, no sabemos si el evento existe. Una prueba por evento.
import { beforeEach, describe, expect, test, vi } from 'vitest'
import {
  MOVIMIENTO_GUARDADO,
  MOVIMIENTO_INICIADO,
  configurarEnvio,
  eventos,
  guardarMovimientoConTrack,
  iniciarMovimientoConTrack,
} from '../../src/services/analitica.js'

const DATOS = {
  tipo: 'gasto',
  monto: 123.5,
  categoria: 'Transporte',
  descripcion: 'taxi a casa de Juan',
  fecha: new Date('2026-11-10'),
}

// Palabras que delatarían un dato personal o innecesario dentro del registro
const PROHIBIDOS = ['monto', 'descripcion', 'email', 'nombre', '123.5', 'taxi a casa de Juan']

beforeEach(() => {
  eventos.length = 0
  configurarEnvio(() => Promise.resolve())
  vi.spyOn(console, 'log').mockImplementation(() => {})
})

describe('movimiento_iniciado', () => {
  test('se registra una vez, sin propiedades ni datos personales', () => {
    iniciarMovimientoConTrack()

    expect(eventos).toHaveLength(1)
    expect(eventos[0].evento).toBe(MOVIMIENTO_INICIADO)
    expect(eventos[0].props).toEqual({})
    expect(Number.isNaN(Date.parse(eventos[0].fecha))).toBe(false)
  })
})

describe('movimiento_guardado', () => {
  test('se registra una vez, con tipo y categoría y ninguna propiedad más', async () => {
    await guardarMovimientoConTrack(DATOS, async () => ({ id: 'x' }))

    expect(eventos).toHaveLength(1)
    expect(eventos[0].evento).toBe(MOVIMIENTO_GUARDADO)
    expect(eventos[0].props).toEqual({ tipo: 'gasto', categoria: 'Transporte' })
  })

  test('no aparece ningún dato personal en el registro', async () => {
    await guardarMovimientoConTrack(DATOS, async () => ({ id: 'x' }))

    const texto = JSON.stringify(eventos[0])
    for (const prohibido of PROHIBIDOS) expect(texto).not.toContain(prohibido)
  })

  test('si el guardado falla, no se registra (solo se dispara después de guardar)', async () => {
    const fallar = async () => {
      throw new Error('No se puede registrar, porque supera tu límite mensual')
    }

    await expect(guardarMovimientoConTrack(DATOS, fallar)).rejects.toThrow()
    expect(eventos).toHaveLength(0)
  })

  test('el registro se envía a la tabla eventos', async () => {
    const enviados = []
    configurarEnvio(async (registro) => enviados.push(registro))

    await guardarMovimientoConTrack(DATOS, async () => ({ id: 'x' }))
    await new Promise((r) => setTimeout(r, 0))

    expect(enviados).toHaveLength(1)
    expect(enviados[0].evento).toBe(MOVIMIENTO_GUARDADO)
  })
})

// ---------- Tarea 9 · Parte A: errores con motivo de lista fija y búsquedas ----------
import {
  EVENTOS,
  motivoMontoMovimiento,
  motivoPresupuesto,
  motivoRechazoServidor,
  track,
  trackBusqueda,
} from '../../src/services/analitica.js'

describe('Tarea 9 · motivos de una lista fija', () => {
  test('el mensaje de error se traduce a un código, nunca se envía el texto', () => {
    expect(motivoMontoMovimiento('El campo no puede estar vacío')).toBe('monto_vacio')
    expect(motivoMontoMovimiento('Formato numérico inválido')).toBe('monto_invalido')
    expect(motivoPresupuesto('El presupuesto no debe estar vacío')).toBe('vacio')
    expect(motivoPresupuesto('No se permiten letras, ingresa un número válido')).toBe('letras')
    expect(motivoPresupuesto('El presupuesto debe ser mayor a 0')).toBe('menor_o_igual_a_cero')
  })

  test('un pago rechazado por dinero reservado en metas tiene su propio motivo', () => {
    const error = { status: 409, message: 'Fondos insuficientes: tienes 280.00 Bs reservados en tus metas de ahorro' }
    expect(motivoRechazoServidor(error)).toBe('fondos_reservados_en_metas')
    expect(motivoRechazoServidor({ status: 500, message: 'x' })).toBe('rechazado_por_servidor')
  })

  test('movimiento_rechazado se registra una vez, solo con el motivo', () => {
    track(EVENTOS.MOVIMIENTO_RECHAZADO, { motivo: motivoMontoMovimiento('El campo no puede estar vacío') })

    expect(eventos).toHaveLength(1)
    expect(eventos[0].props).toEqual({ motivo: 'monto_vacio' })
  })
})

describe('Tarea 9 · búsquedas sin resultados', () => {
  test('una búsqueda sin resultados registra dos eventos, sin el texto buscado', () => {
    trackBusqueda({ conTexto: true, conFiltros: false, sinResultados: true })

    expect(eventos.map((e) => e.evento)).toEqual([EVENTOS.BUSQUEDA_REALIZADA, EVENTOS.BUSQUEDA_SIN_RESULTADOS])
    expect(eventos[1].props).toEqual({ con_texto: true, con_filtros: false })
  })

  test('una búsqueda con resultados solo registra busqueda_realizada', () => {
    trackBusqueda({ conTexto: false, conFiltros: true, sinResultados: false })

    expect(eventos).toHaveLength(1)
    expect(eventos[0].evento).toBe(EVENTOS.BUSQUEDA_REALIZADA)
  })
})
