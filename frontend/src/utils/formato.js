// Ayudas para mostrar numeros y fechas igual que en la app Flutter

// double.tryParse de Dart: acepta espacios alrededor y rechaza letras ('100Bs' -> null)
export function parseDouble(texto) {
  if (texto === null || texto === undefined) return null
  const limpio = String(texto).trim()
  if (!/^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$/.test(limpio)) return null
  return Number(limpio)
}

// toString() de un double en Dart: 150 -> "150.0", 25.5 -> "25.5"
export function dartNum(valor) {
  const n = Number(valor)
  return Number.isInteger(n) ? n.toFixed(1) : String(n)
}

// toStringAsFixed de Dart
export function fixed(valor, decimales = 2) {
  return Number(valor).toFixed(decimales)
}

export const MESES = [
  'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
  'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
]

// Fecha local en formato 'YYYY-MM-DD' (sin pasar por UTC)
export function fechaISO(fecha) {
  const mes = String(fecha.getMonth() + 1).padStart(2, '0')
  const dia = String(fecha.getDate()).padStart(2, '0')
  return `${fecha.getFullYear()}-${mes}-${dia}`
}

// 'YYYY-MM-DD' -> Date local
export function parseFecha(iso) {
  const [anio, mes, dia] = String(iso).slice(0, 10).split('-').map(Number)
  return new Date(anio, mes - 1, dia)
}

// Clave de mes 'YYYY-MM'
export function claveMes(fecha) {
  return `${fecha.getFullYear()}-${String(fecha.getMonth() + 1).padStart(2, '0')}`
}
