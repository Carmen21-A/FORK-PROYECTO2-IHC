// Portado de lib/utils/presupuesto_categoria.dart (Tarea 5: presupuesto por categoría)
import { parseDouble } from './formato.js'

/// Enumerador que define los 4 posibles estados del presupuesto de una categoría
export const EstadoPresupuesto = Object.freeze({
  /// Representa que el usuario aún no ha fijado un monto límite para esta categoría
  sinPresupuesto: 'sinPresupuesto',

  /// Representa que el consumo va bien y el gasto está por debajo del 80%
  optimo: 'optimo',

  /// Representa una advertencia porque el gasto ya alcanzó o superó el 80% del presupuesto
  alerta: 'alerta',

  /// Representa que el gasto real ya superó el 100% del monto presupuestado
  excedido: 'excedido',
}) //fin del enumerador

/// Lista constante de las 5 categorías oficiales disponibles en la aplicación
export const categoriasApp = [
  //una constante categoriasApp es igual a una lista de textos con:
  'Transporte',
  'Comida',
  'Estudios',
  'Ocio',
  'Otros',
]

/// Función que valida el texto ingresado por el usuario al definir un presupuesto
/// Retorna un mensaje de error en texto si es inválido, o null si el valor es correcto
export function validarMontoPresupuesto(texto) {
  //una función llamada validarMontoPresupuesto, que recibe un texto opcional texto y devuelve un texto opcional
  /// Se verifica si el texto es nulo o si quitando espacios en blanco queda vacío
  if (texto === null || texto === undefined || texto.trim() === '') {
    /// Se retorna el mensaje de error indicando que no debe estar vacío
    return 'El presupuesto no debe estar vacío' //retorna "El presupuesto no debe estar vacío"
  }

  /// Intenta convertir el texto limpio a un número decimal; si contiene letras devuelve null
  const numero = parseDouble(texto.trim()) //constante numero == a intentar convertir texto sin espacios a decimal

  /// Si el resultado de la conversión es nulo, significa que el usuario escribió letras o símbolos inválidos
  if (numero === null) {
    return 'No se permiten letras, ingresa un número válido' //retorna "No se permiten letras, ingresa un número válido"
  }

  if (numero <= 0) {
    //si numero es menor o igual a 0
    return 'El presupuesto debe ser mayor a 0' //retorna "El presupuesto debe ser mayor a 0"
  }

  /// Si pasó todas las validaciones sin fallar, se retorna null indicando que el dato es completamente válido
  return null //retorna nulo
}

/// Indica si un movimiento es un gasto válido (no cancelado) de esa categoría en ese mes
function esGastoDeCategoria(m, mes, categoria) {
  /// Se obtiene la fecha, el tipo, el estado y la categoría como texto seguro (o vacío si es nulo)
  const fechaStr = String(m.fecha ?? '')
  const tipo = String(m.tipo ?? '')
  const estado = String(m.estado ?? '')
  const cat = String(m.categoria ?? '')

  /// Se comprueba que la fecha comience con el mes pedido, que sea de tipo 'gasto',
  /// que el estado no sea 'cancelado' y que pertenezca a la categoría solicitada
  return fechaStr.startsWith(mes) && tipo === 'gasto' && estado !== 'cancelado' && cat === categoria
}

/// Función que calcula la suma total de dinero gastado en una categoría durante un mes específico
export function calcularGastoCategoria({ movimientos, mes, categoria }) {
  /// Se inicializa el acumulador del monto total en 0.0 decimal
  let total = 0.0 //un decimal total es igual a 0.0

  /// Se recorre cada uno de los movimientos existentes en la lista
  for (const m of movimientos) {
    if (esGastoDeCategoria(m, mes, categoria)) {
      /// Se extrae el monto numérico del movimiento (o 0.0 si es nulo)
      const monto = Number(m.monto ?? 0.0)

      /// Se suma este monto al acumulador total de gastos de la categoría
      total += monto //total == a total más monto
    }
  }

  /// Se devuelve la suma total acumulada de gastos para esa categoría y mes
  return total
}

/// Función que cuenta cuántas transacciones de gasto válidas se realizaron en una categoría durante un mes
export function contarMovimientosCategoria({ movimientos, mes, categoria }) {
  /// Se inicializa el contador de movimientos en cero
  let count = 0 //un entero count es igual a 0

  /// Se recorre cada movimiento de la lista
  for (const m of movimientos) {
    /// Se verifica que coincida el mes, que sea gasto, que no esté cancelado y sea la categoría
    if (esGastoDeCategoria(m, mes, categoria)) {
      /// Se incrementa en 1 el contador de transacciones
      count++ //count aumenta en 1
    }
  }

  /// Se devuelve la cantidad total de transacciones encontradas
  return count
}

/// Función que calcula el porcentaje de consumo dividiendo el gasto real entre el límite presupuestado
export function calcularPorcentajeConsumo(presupuestado, consumido) {
  if (presupuestado <= 0) return 0.0 //si presupuestado es menor o igual a 0, retorna 0.0

  /// Se divide el dinero consumido entre el monto presupuestado y se devuelve el resultado decimal
  return consumido / presupuestado //retorna consumido dividido entre presupuestado
} //fin de la función calcularPorcentajeConsumo

/// Función que calcula el saldo disponible restando lo gastado del monto fijado
export function calcularSaldoRestante(presupuestado, consumido) {
  /// Se resta el monto presupuestado menos lo consumido; si da negativo representa exceso de gasto
  return presupuestado - consumido //retorna presupuestado menos consumido
}

/// Función que evalúa los montos y determina el estado visual del presupuesto (en orden, alerta o excedido)
export function obtenerEstadoPresupuesto({ presupuestado, consumido }) {
  /// Si el presupuesto fijado es cero o menor a cero, se marca como sin presupuesto
  if (presupuestado <= 0) {
    return EstadoPresupuesto.sinPresupuesto //retorna EstadoPresupuesto punto sinPresupuesto
  }

  /// Si lo consumido supera estrictamente el monto presupuestado (más del 100%)
  if (consumido > presupuestado) {
    /// Se retorna el estado excedido indicando que se pasó del límite
    return EstadoPresupuesto.excedido //retorna EstadoPresupuesto punto excedido
  }

  if (consumido / presupuestado >= 0.8) {
    //si consumido dividido entre presupuestado es mayor o igual a 0.8
    /// Se retorna el estado alerta advirtiendo que está cerca del tope
    return EstadoPresupuesto.alerta //retorna EstadoPresupuesto punto alerta
  }

  /// Si no se cumple ninguna de las anteriores, significa que está dentro del rango seguro
  return EstadoPresupuesto.optimo //retorna EstadoPresupuesto punto optimo
} //fin de la función obtenerEstadoPresupuesto

/// Objeto que contiene toda la información calculada de una categoría individual
/// (equivale a la clase ItemPresupuestoCategoria de Dart)
export function crearItemPresupuestoCategoria({
  categoria, /// Nombre de la categoría (ejemplo: 'Comida')
  presupuestado, /// Monto de dinero presupuestado fijado por el usuario
  consumido, /// Monto real gastado en el mes
  restante, /// Dinero disponible restante o saldo negativo si se excedió
  porcentaje, /// Porcentaje de avance de consumo expresado en decimal (ej: 0.75 para 75%)
  estado, /// Estado calculado (sinPresupuesto, optimo, alerta, excedido)
  cantidadMovimientos, /// Número de transacciones registradas en esta categoría
}) {
  return Object.freeze({
    categoria,
    presupuestado,
    consumido,
    restante,
    porcentaje,
    estado,
    cantidadMovimientos,
    /// Verdadero si la categoría tiene un presupuesto mayor a 0
    tienePresupuesto: presupuestado > 0,
    /// Verdadero si el estado actual es excedido
    estaExcedido: estado === EstadoPresupuesto.excedido,
    /// Verdadero si el estado actual es alerta
    estaEnAlerta: estado === EstadoPresupuesto.alerta,
  })
}

/// Función constructora que procesa los datos y arma el resumen mensual completo
/// (equivale a la clase ResumenPresupuestoMensual de Dart)
export function construirResumenMensual({
  mes, /// Mes a procesar (ej: '2026-10')
  presupuestosPorCategoria, /// Mapa con los presupuestos asignados a cada categoría { 'Comida': 400.0, ... }
  movimientos, /// Lista de movimientos del usuario leídos de la base de datos
}) {
  /// Se crea una lista vacía para almacenar el resultado de cada categoría
  const items = []

  /// Se inicializa la suma de todos los presupuestos en 0.0
  let totalPresupuestado = 0.0

  /// Se inicializa la suma de todos los gastos reales en 0.0
  let totalConsumido = 0.0

  /// Se itera sobre cada una de las 5 categorías oficiales de la app
  for (const cat of categoriasApp) {
    /// Se obtiene el presupuesto de la categoría o 0.0 si no fue fijado
    const presupuestado = presupuestosPorCategoria[cat] ?? 0.0

    /// Se calcula el gasto real sumando los movimientos de esa categoría en ese mes
    const consumido = calcularGastoCategoria({ movimientos, mes, categoria: cat })

    /// Se calcula el saldo restante (presupuesto - consumo)
    const restante = calcularSaldoRestante(presupuestado, consumido)

    /// Se calcula el porcentaje consumido
    const porcentaje = calcularPorcentajeConsumo(presupuestado, consumido)

    /// Se determina el estado de semáforo del presupuesto (óptimo, alerta, excedido o sin presupuesto)
    const estado = obtenerEstadoPresupuesto({ presupuestado, consumido })

    /// Se cuenta cuántos movimientos de gasto hubo en esa categoría
    const cantidadMovimientos = contarMovimientosCategoria({ movimientos, mes, categoria: cat })

    /// Si la categoría tiene presupuesto asignado mayor a cero, se acumula al total global presupuestado
    if (presupuestado > 0) {
      totalPresupuestado += presupuestado
    }

    /// Se acumula el dinero consumido al total global consumido
    totalConsumido += consumido

    /// Se crea el objeto de la categoría con todos sus cálculos y se agrega a la lista
    items.push(
      crearItemPresupuestoCategoria({
        categoria: cat,
        presupuestado,
        consumido,
        restante,
        porcentaje,
        estado,
        cantidadMovimientos,
      }),
    )
  }

  /// Se calcula el saldo total restante restando el consumo total del presupuesto total
  const totalRestante = totalPresupuestado - totalConsumido

  /// Se calcula el porcentaje total consumido (o 0.0 si no hay presupuesto)
  const porcentajeTotal = totalPresupuestado > 0 ? totalConsumido / totalPresupuestado : 0.0

  return Object.freeze({
    mes, /// Mes del resumen en formato 'YYYY-MM'
    items, /// Detalle procesado de cada una de las 5 categorías
    totalPresupuestado, /// Suma de todos los presupuestos fijados en el mes
    totalConsumido, /// Suma de todos los gastos consumidos en el mes
    totalRestante, /// Dinero restante total disponible en el mes
    porcentajeTotal, /// Porcentaje general de consumo de todo el mes
    /// Nombres de las categorías que superaron su presupuesto
    categoriasExcedidas: items.filter((i) => i.estaExcedido).map((i) => i.categoria),
    /// Nombres de las categorías que están en alerta (>= 80%)
    categoriasAlerta: items.filter((i) => i.estaEnAlerta).map((i) => i.categoria),
  })
}
