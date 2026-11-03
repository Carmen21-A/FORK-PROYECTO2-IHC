# Portado de lib/utils/estado_movimiento.dart (Tarea 2 y 3: estados del movimiento)
# Flujo permitido: pendiente -> pagado -> cancelado


def siguiente_estado(estado_actual: str) -> str | None:  # función que retorna el siguiente estado válido en el ciclo de vida
    if estado_actual == "pendiente":  # si el estado actual es 'pendiente'
        return "pagado"  # avanza a 'pagado'
    if estado_actual == "pagado":  # si el estado actual ya es 'pagado'
        return "cancelado"  # avanza a 'cancelado'
    return None  # si está cancelado o en otro estado no tiene siguiente estado


def es_transicion_valida(actual: str, nuevo: str) -> bool:  # función que verifica si cambiar de estado actual a nuevo es válido
    return siguiente_estado(actual) == nuevo  # retorna verdadero si el nuevo estado coincide exactamente con el siguiente permitido


def puede_editar_monto(estado: str) -> bool:  # función que comprueba si las reglas de negocio permiten editar el monto
    return estado != "pagado"  # retorna verdadero solo si el estado no es 'pagado' (un gasto pagado no se puede modificar)
