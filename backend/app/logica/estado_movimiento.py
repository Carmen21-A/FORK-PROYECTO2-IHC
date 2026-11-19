# Portado de lib/utils/estado_movimiento.dart (Tarea 2 y 3: estados del movimiento)
# Flujo permitido: pendiente -> pagado -> cancelado


def siguiente_estado(estado_actual: str) -> str | None: 
    if estado_actual == "pendiente": 
        return "pagado"  
    if estado_actual == "pagado":  
        return "cancelado"  
    return None  


def es_transicion_valida(actual: str, nuevo: str) -> bool:  
    return siguiente_estado(actual) == nuevo  


def puede_editar_monto(estado: str) -> bool:  
    return estado != "pagado" 
