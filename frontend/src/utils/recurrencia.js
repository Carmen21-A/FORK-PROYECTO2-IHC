// Tarea 6: gastos recurrentes (misma regla que backend/app/logica/recurrencia.py)

// Opciones del selector "Repetir" ('' = no se repite)
export const OPCIONES_RECURRENCIA = [
  { valor: '', texto: 'No se repite' },
  { valor: 'semanal', texto: 'Cada semana' },
  { valor: 'mensual', texto: 'Cada mes' },
]

export const TEXTO_RECURRENCIA = { semanal: 'cada semana', mensual: 'cada mes' }

export function siguienteFecha(fecha, recurrencia) {
  // Semanal: 7 dias despues
  if (recurrencia === 'semanal') {
    return new Date(fecha.getFullYear(), fecha.getMonth(), fecha.getDate() + 7)
  }
  // Mensual: el mismo dia del mes siguiente; si no existe (31 de enero), el ultimo dia (28 de febrero)
  const ultimoDia = new Date(fecha.getFullYear(), fecha.getMonth() + 2, 0).getDate()
  return new Date(fecha.getFullYear(), fecha.getMonth() + 1, Math.min(fecha.getDate(), ultimoDia))
}
