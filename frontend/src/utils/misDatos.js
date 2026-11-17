// Tarea 10 · Mis datos y salida honesta (lógica pura, se prueba con vitest)

// Columnas del CSV de movimientos, en el orden en que se descargan
export const COLUMNAS_CSV = [
  ['fecha', 'Fecha'],
  ['tipo', 'Tipo'],
  ['categoria', 'Categoría'],
  ['descripcion', 'Descripción'],
  ['monto', 'Monto (Bs)'],
  ['estado', 'Estado'],
  ['recurrencia', 'Se repite'],
]

// Un valor dentro del CSV: comillas si hace falta y sin fórmulas de Excel (=, +, -, @)
export function celdaCsv(valor) {
  if (valor === null || valor === undefined) return ''
  let texto = String(valor)
  if (typeof valor === 'string' && /^[=+\-@\t\r]/.test(texto)) texto = `'${texto}`
  if (/[",\n\r;]/.test(texto)) return `"${texto.replace(/"/g, '""')}"`
  return texto
}

// Movimientos -> texto CSV. Empieza con BOM para que Excel lea bien las tildes.
export function movimientosACsv(movimientos) {
  const cabecera = COLUMNAS_CSV.map(([, titulo]) => celdaCsv(titulo)).join(',')
  const filas = movimientos.map((m) => COLUMNAS_CSV.map(([campo]) => celdaCsv(m[campo])).join(','))
  return `﻿${[cabecera, ...filas].join('\r\n')}\r\n`
}

// presupuesto-estudiantil-movimientos-2026-11-15.csv
export function nombreArchivo(que, extension, fecha = new Date()) {
  const dia = [
    fecha.getFullYear(),
    String(fecha.getMonth() + 1).padStart(2, '0'),
    String(fecha.getDate()).padStart(2, '0'),
  ].join('-')
  return `presupuesto-estudiantil-${que}-${dia}.${extension}`
}

// Nombres legibles de cada tipo de dato (singular y plural)
export const NOMBRES_DATOS = {
  movimientos: ['movimiento', 'movimientos'],
  limites_mensuales: ['límite mensual', 'límites mensuales'],
  presupuestos_categoria: ['presupuesto por categoría', 'presupuestos por categoría'],
  metas_ahorro: ['meta de ahorro', 'metas de ahorro'],
  historial: ['registro del historial', 'registros del historial'],
}

export function cantidadCon(total, clave) {
  const [singular, plural] = NOMBRES_DATOS[clave]
  return `${total} ${total === 1 ? singular : plural}`
}

// Consecuencias de eliminar la cuenta, con los números reales de la persona.
// Solo lista lo que tiene (no asusta con cosas que no existen).
export function consecuenciasEliminar(resumen) {
  const lineas = Object.keys(NOMBRES_DATOS)
    .filter((clave) => (resumen?.[clave] ?? 0) > 0)
    .map((clave) => cantidadCon(resumen[clave], clave))
  return lineas
}

// Descarga un texto como archivo desde el navegador
export function descargarArchivo(contenido, nombre, tipo) {
  const blob = new Blob([contenido], { type: tipo })
  const url = URL.createObjectURL(blob)
  const enlace = document.createElement('a')
  enlace.href = url
  enlace.download = nombre
  document.body.appendChild(enlace)
  enlace.click()
  enlace.remove()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}
