# Lógica pura de la analítica de interacción (Clase 21)
# Regla de privacidad: se registra la acción, no a la persona. Cada evento solo acepta
# las propiedades que la pregunta necesita; cualquier otra (email, descripción, monto) se rechaza.

TIPOS = {"gasto", "ingreso"}  # valores permitidos para la propiedad tipo
CATEGORIAS = {"Transporte", "Comida", "Estudios", "Ocio", "Otros"}  # lista fija de categorías permitidas

EVENTOS_PERMITIDOS: dict[str, set[str]] = {  # nombre del evento -> propiedades que acepta
    "movimiento_iniciado": set(),  # inicio: se abre el formulario de nuevo movimiento (no necesita propiedades)
    "movimiento_guardado": {"tipo", "categoria"},  # éxito: el movimiento se guardó en la base de datos
}  # fin de eventos permitidos


def validar_evento(evento: str, props: dict) -> None:  # verifica nombre y propiedades de un evento antes de guardarlo
    if evento not in EVENTOS_PERMITIDOS:  # si el evento no está definido
        raise ValueError(f"Evento desconocido: {evento}")  # se rechaza
    sobrantes = set(props) - EVENTOS_PERMITIDOS[evento]  # propiedades que no fueron definidas para este evento
    if sobrantes:  # si llegó algún dato que la pregunta no necesita
        raise ValueError(f"Propiedades no permitidas: {', '.join(sorted(sobrantes))}")  # se rechaza (privacidad)
    if "tipo" in props and props["tipo"] not in TIPOS:  # si el tipo no es gasto ni ingreso
        raise ValueError("tipo debe ser gasto o ingreso")  # se rechaza
    if "categoria" in props and props["categoria"] not in CATEGORIAS:  # si la categoría no es de la lista fija
        raise ValueError("categoria no está en la lista permitida")  # se rechaza (evita texto libre del usuario)


def porcentaje_terminan(iniciados: int, guardados: int) -> int:  # calcula qué % de los que empiezan terminan
    if iniciados <= 0:  # si nadie empezó todavía
        return 0  # evita dividir entre cero
    return int(guardados * 100 / iniciados + 0.5)  # porcentaje redondeado a entero (.5 sube, como Math.round)
