// Portado de lib/utils/historial.dart

// Texto legible de un evento del historial
export function armarDetalleEvento({ tipo, monto, categoria, descripcion }) {
  const tipoTexto = tipo === 'gasto' ? 'Gasto' : 'Ingreso'
  const textoDescripcion =
    descripcion === null || descripcion === undefined || descripcion.trim() === ''
      ? ''
      : ` · ${descripcion.trim()}`
  return `${tipoTexto} ${monto} Bs · ${categoria}${textoDescripcion}`
}

export function filtrarHistorial(eventos, busqueda) {
  const query = busqueda.trim().toLowerCase()
  if (query === '') return eventos

  return eventos.filter((evento) => {
    const detalle = String(evento.detalle ?? '').toLowerCase()
    const accion = String(evento.accion ?? '').toLowerCase()

    return detalle.includes(query) || accion.includes(query)
  })
}

// Ordena los eventos del mas reciente al mas viejo
export function ordenarRecientePrimero(eventos) {
  const copia = [...eventos]
  copia.sort((a, b) => {
    const fechaA = Date.parse(a.created_at)
    const fechaB = Date.parse(b.created_at)
    if (Number.isNaN(fechaA) || Number.isNaN(fechaB)) return 0
    return fechaB - fechaA
  })
  return copia
}
