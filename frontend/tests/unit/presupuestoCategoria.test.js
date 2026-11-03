// Portado de test/presupuesto_categoria_test.dart
import { describe, expect, test } from 'vitest'
import {
  EstadoPresupuesto,
  calcularGastoCategoria,
  calcularPorcentajeConsumo,
  calcularSaldoRestante,
  construirResumenMensual,
  contarMovimientosCategoria,
  obtenerEstadoPresupuesto,
  validarMontoPresupuesto,
} from '../../src/utils/presupuestoCategoria.js'

/// Agrupación de pruebas para verificar la validación del texto ingresado
describe('1. Validación de monto de presupuesto por categoría', () => {
  test('Acepta montos numéricos válidos mayores a cero', () => {
    /// Se comprueba que '350' devuelva null (es decir, que no haya error)
    expect(validarMontoPresupuesto('350')).toBeNull()

    /// Se comprueba que un decimal como '150.50' devuelva null
    expect(validarMontoPresupuesto('150.50')).toBeNull()

    /// Se comprueba que un número con espacios alrededor como '  500  ' se limpie y sea válido
    expect(validarMontoPresupuesto('  500  ')).toBeNull()
  })

  test('Rechaza entradas vacías o nulas', () => {
    expect(validarMontoPresupuesto('')).toBe('El presupuesto no debe estar vacío')
    expect(validarMontoPresupuesto('   ')).toBe('El presupuesto no debe estar vacío')
    expect(validarMontoPresupuesto(null)).toBe('El presupuesto no debe estar vacío')
  })

  test('Rechaza letras o caracteres no numéricos', () => {
    expect(validarMontoPresupuesto('abc')).toBe('No se permiten letras, ingresa un número válido')
    expect(validarMontoPresupuesto('100Bs')).toBe('No se permiten letras, ingresa un número válido')
  })

  test('Rechaza montos iguales o menores a 0', () => {
    expect(validarMontoPresupuesto('0')).toBe('El presupuesto debe ser mayor a 0')
    expect(validarMontoPresupuesto('-20')).toBe('El presupuesto debe ser mayor a 0')
  })
})

/// Agrupación de pruebas para verificar el cálculo del dinero consumido por categoría
describe('2. Cálculo de consumo de gastos por categoría', () => {
  /// Lista simulada de movimientos para las pruebas
  const movimientos = [
    /// Movimiento 1: Gasto en Comida del mes 10 por 50 Bs (debe sumarse)
    { fecha: '2026-10-02', tipo: 'gasto', categoria: 'Comida', estado: 'pagado', monto: 50.0 },
    /// Movimiento 2: Gasto en Comida del mes 10 por 75 Bs en estado pendiente (debe sumarse)
    { fecha: '2026-10-05', tipo: 'gasto', categoria: 'Comida', estado: 'pendiente', monto: 75.0 },
    /// Movimiento 3: Gasto cancelado por 100 Bs (NO debe sumarse porque fue cancelado)
    { fecha: '2026-10-08', tipo: 'gasto', categoria: 'Comida', estado: 'cancelado', monto: 100.0 },
    /// Movimiento 4: Ingreso de dinero por 500 Bs (NO debe sumarse porque no es gasto)
    { fecha: '2026-10-10', tipo: 'ingreso', categoria: 'Comida', estado: 'pagado', monto: 500.0 },
    /// Movimiento 5: Gasto de Transporte por 30 Bs (pertenece a otra categoría)
    { fecha: '2026-10-12', tipo: 'gasto', categoria: 'Transporte', estado: 'pagado', monto: 30.0 },
    /// Movimiento 6: Gasto de septiembre (NO debe sumarse porque es de otro mes)
    { fecha: '2026-09-20', tipo: 'gasto', categoria: 'Comida', estado: 'pagado', monto: 200.0 },
  ]

  test('Calcula correctamente el consumo de una categoría en el mes', () => {
    const gastoComida = calcularGastoCategoria({ movimientos, mes: '2026-10', categoria: 'Comida' })
    /// Se verifica que la suma sea exactamente 50.0 + 75.0 = 125.0
    expect(gastoComida).toBe(125.0)
  })

  test('Calcula correctamente el consumo de Transporte', () => {
    const gastoTransporte = calcularGastoCategoria({ movimientos, mes: '2026-10', categoria: 'Transporte' })
    expect(gastoTransporte).toBe(30.0)
  })

  test('Devuelve 0 si no hay gastos en la categoría', () => {
    const gastoEstudios = calcularGastoCategoria({ movimientos, mes: '2026-10', categoria: 'Estudios' })
    expect(gastoEstudios).toBe(0.0)
  })

  test('Cuenta cantidad de movimientos válidos de la categoría', () => {
    const count = contarMovimientosCategoria({ movimientos, mes: '2026-10', categoria: 'Comida' })
    /// Se comprueba que fueron exactamente 2 movimientos (50 Bs y 75 Bs)
    expect(count).toBe(2)
  })
})

/// Agrupación de pruebas para porcentajes, saldos y estados de semáforo
describe('3. Estado y porcentaje de consumo del presupuesto', () => {
  test('Calcula porcentaje correctamente', () => {
    expect(calcularPorcentajeConsumo(500.0, 250.0)).toBe(0.5)
    expect(calcularPorcentajeConsumo(0.0, 100.0)).toBe(0.0)
    expect(calcularPorcentajeConsumo(200.0, 300.0)).toBe(1.5)
  })

  test('Calcula saldo restante positivo y negativo (exceso)', () => {
    expect(calcularSaldoRestante(500.0, 200.0)).toBe(300.0)
    expect(calcularSaldoRestante(200.0, 250.0)).toBe(-50.0)
  })

  test('Determina EstadoPresupuesto.sinPresupuesto', () => {
    const estado = obtenerEstadoPresupuesto({ presupuestado: 0.0, consumido: 50.0 })
    expect(estado).toBe(EstadoPresupuesto.sinPresupuesto)
  })

  test('Determina EstadoPresupuesto.optimo cuando gasto < 80%', () => {
    /// Gasto de 350 sobre 500 representa un 70% (< 80%)
    const estado = obtenerEstadoPresupuesto({ presupuestado: 500.0, consumido: 350.0 })
    expect(estado).toBe(EstadoPresupuesto.optimo)
  })

  test('Determina EstadoPresupuesto.alerta cuando gasto está entre 80% y 100%', () => {
    /// Gasto de 420 sobre 500 representa un 84% (>= 80% y <= 100%)
    const estado = obtenerEstadoPresupuesto({ presupuestado: 500.0, consumido: 420.0 })
    expect(estado).toBe(EstadoPresupuesto.alerta)
  })

  test('Determina EstadoPresupuesto.excedido cuando gasto > 100%', () => {
    /// Gasto de 550 sobre 500 representa un 110% (> 100%)
    const estado = obtenerEstadoPresupuesto({ presupuestado: 500.0, consumido: 550.0 })
    expect(estado).toBe(EstadoPresupuesto.excedido)
  })
})

/// Agrupación de pruebas para el resumen mensual consolidado
describe('4. Resumen general mensual por categorías', () => {
  /// Movimientos de prueba con distintas categorías
  const movimientos = [
    { fecha: '2026-10-01', tipo: 'gasto', categoria: 'Transporte', estado: 'pagado', monto: 120.0 },
    { fecha: '2026-10-02', tipo: 'gasto', categoria: 'Comida', estado: 'pagado', monto: 450.0 },
    { fecha: '2026-10-03', tipo: 'gasto', categoria: 'Estudios', estado: 'pagado', monto: 160.0 },
  ]

  /// Presupuestos configurados
  const presupuestos = {
    Transporte: 100.0, // Consumido 120 -> EXCEDIDO (120%)
    Comida: 500.0, // Consumido 450 -> ALERTA (90%)
    Estudios: 300.0, // Consumido 160 -> OPTIMO (53.3%)
    Ocio: 150.0, // Consumido 0   -> OPTIMO (0%)
  }

  test('Construye resumen completo con totales y alertas', () => {
    const resumen = construirResumenMensual({
      mes: '2026-10',
      presupuestosPorCategoria: presupuestos,
      movimientos,
    })

    /// Se verifica el total presupuestado: 100 + 500 + 300 + 150 = 1050.0
    expect(resumen.totalPresupuestado).toBe(1050.0)

    /// Se verifica el total consumido: 120 + 450 + 160 = 730.0
    expect(resumen.totalConsumido).toBe(730.0)

    /// Se verifica el restante: 1050 - 730 = 320.0
    expect(resumen.totalRestante).toBe(320.0)

    /// Se verifica que Transporte esté listada entre las categorías excedidas
    expect(resumen.categoriasExcedidas).toContain('Transporte')

    /// Se verifica que Comida esté listada entre las categorías en alerta
    expect(resumen.categoriasAlerta).toContain('Comida')
  })
})
