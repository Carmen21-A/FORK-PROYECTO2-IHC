// Portado de lib/utils/estado_movimiento.dart (Tareas 2 y 3)

export function siguienteEstado(estadoActual) {
  if (estadoActual === 'pendiente') {
    return 'pagado'
  }
  if (estadoActual === 'pagado') {
    return 'cancelado'
  }
  return null
}

export function esTransicionValida(actual, nuevo) {
  return siguienteEstado(actual) === nuevo
}

export function puedeEditarMonto(estado) {
  return estado !== 'pagado'
}
