# Lógica pura de la analítica de interacción (Clase 21 y Tarea 9 Parte A)
# Regla de privacidad: se registra la acción, no a la persona. Cada evento solo acepta
# las propiedades que su pregunta necesita, y cada propiedad solo acepta valores de una lista fija.
# Así nunca se guardan email, descripción, monto, nombre de una meta ni texto buscado.

BOOLEANO = "booleano"  # marca de propiedad que solo acepta True o False

TIPOS = {"gasto", "ingreso"}  # valores permitidos para tipo
CATEGORIAS = {"Transporte", "Comida", "Estudios", "Ocio", "Otros"}  # lista fija de categorías
OPERACIONES = {"asignar", "retirar", "transferir"}  # operaciones de fondos en metas (Tarea 8)

EVENTOS_PERMITIDOS: dict[str, dict] = {  # nombre del evento -> {propiedad: valores permitidos}
    # Flujo 1 · Registrar movimiento
    "movimiento_iniciado": {},  # inicio: se abre el formulario de nuevo movimiento
    "movimiento_guardado": {"tipo": TIPOS, "categoria": CATEGORIAS},  # éxito: el movimiento se guardó
    "movimiento_rechazado": {"motivo": {"monto_vacio", "monto_invalido", "supera_limite_mensual", "rechazado_por_servidor"}},  # error que frena el registro
    # Flujo 2 · Aviso antes de superar el límite (Tarea 9 Parte B)
    "aviso_presupuesto_mostrado": {"categoria": CATEGORIAS},  # paso: se mostró el aviso de presupuesto
    "aviso_presupuesto_confirmado": {"categoria": CATEGORIAS},  # éxito: eligió «Guardar y exceder»
    "aviso_presupuesto_cancelado": {"categoria": CATEGORIAS},  # salida: canceló y no se guardó nada
    # Flujo 3 · Pagar un movimiento pendiente
    "pago_iniciado": {"tipo": TIPOS},  # inicio: toca el estado «pendiente» para pagarlo
    "movimiento_pagado": {"tipo": TIPOS},  # éxito: quedó pagado
    "pago_rechazado": {"motivo": {"fondos_reservados_en_metas", "rechazado_por_servidor"}},  # error: permiso denegado por la regla de metas
    # Flujo 4 · Crear meta de ahorro (Tarea 8)
    "meta_creacion_iniciada": {},  # inicio: abre «Nueva Meta»
    "meta_creada": {},  # éxito: la meta se guardó (sin nombre ni montos)
    "meta_rechazada": {"motivo": {"nombre_vacio", "objetivo_invalido", "fecha_vacia", "rechazado_por_servidor"}},  # error de validación
    # Flujo 5 · Mover fondos entre saldo y metas (Tarea 8)
    "fondos_operacion_iniciada": {"operacion": OPERACIONES},  # inicio: abre asignar, retirar o transferir
    "fondos_operacion_realizada": {"operacion": OPERACIONES},  # éxito: la operación se guardó
    "fondos_operacion_rechazada": {"operacion": OPERACIONES, "motivo": {"fondos_insuficientes", "rechazado_por_servidor"}},  # error: sin fondos
    # Flujo 6 · Presupuesto por categoría
    "presupuesto_edicion_iniciada": {"categoria": CATEGORIAS},  # inicio: abre el diálogo de presupuesto
    "presupuesto_categoria_guardado": {"categoria": CATEGORIAS, "supera_limite": BOOLEANO},  # éxito (ejemplo de clase)
    "presupuesto_rechazado": {"motivo": {"vacio", "letras", "menor_o_igual_a_cero", "rechazado_por_servidor"}},  # error de validación
    # Flujo 7 · Buscar y filtrar movimientos
    "busqueda_realizada": {"con_texto": BOOLEANO, "con_filtros": BOOLEANO},  # se buscó (sin guardar el texto buscado)
    "busqueda_sin_resultados": {"con_texto": BOOLEANO, "con_filtros": BOOLEANO},  # la búsqueda no encontró nada
}  # fin de eventos permitidos

FLUJOS = [  # embudos del panel /analitica: pasos en orden, de inicio a éxito
    {"id": "registrar", "nombre": "Registrar movimiento", "pasos": ["movimiento_iniciado", "movimiento_guardado"], "error": "movimiento_rechazado"},  # flujo 1
    {"id": "aviso", "nombre": "Aviso de presupuesto (Tarea 9)", "pasos": ["aviso_presupuesto_mostrado", "aviso_presupuesto_confirmado"], "error": "aviso_presupuesto_cancelado"},  # flujo 2
    {"id": "pagar", "nombre": "Pagar un pendiente", "pasos": ["pago_iniciado", "movimiento_pagado"], "error": "pago_rechazado"},  # flujo 3
    {"id": "meta", "nombre": "Crear meta de ahorro (Tarea 8)", "pasos": ["meta_creacion_iniciada", "meta_creada"], "error": "meta_rechazada"},  # flujo 4
    {"id": "fondos", "nombre": "Mover fondos en metas (Tarea 8)", "pasos": ["fondos_operacion_iniciada", "fondos_operacion_realizada"], "error": "fondos_operacion_rechazada"},  # flujo 5
    {"id": "presupuesto", "nombre": "Presupuesto por categoría", "pasos": ["presupuesto_edicion_iniciada", "presupuesto_categoria_guardado"], "error": "presupuesto_rechazado"},  # flujo 6
]  # fin de flujos (la búsqueda se muestra aparte: realizadas vs. sin resultados)


def validar_evento(evento: str, props: dict) -> None:  # verifica nombre, propiedades y valores de un evento antes de guardarlo
    if evento not in EVENTOS_PERMITIDOS:  # si el evento no está definido
        raise ValueError(f"Evento desconocido: {evento}")  # se rechaza
    permitidas = EVENTOS_PERMITIDOS[evento]  # propiedades que acepta este evento
    sobrantes = set(props) - set(permitidas)  # propiedades que no fueron definidas para este evento
    if sobrantes:  # si llegó algún dato que la pregunta no necesita
        raise ValueError(f"Propiedades no permitidas: {', '.join(sorted(sobrantes))}")  # se rechaza (privacidad)
    for clave, valor in props.items():  # revisa el valor de cada propiedad
        valores = permitidas[clave]  # valores aceptados para esta propiedad
        if valores == BOOLEANO:  # si es una propiedad de sí/no
            if not isinstance(valor, bool):  # y no llegó True o False
                raise ValueError(f"{clave} debe ser verdadero o falso")  # se rechaza
        elif valor not in valores:  # si el valor no está en la lista fija
            raise ValueError(f"{clave} no está en la lista permitida")  # se rechaza (evita texto libre del usuario)


def porcentaje_terminan(iniciados: int, guardados: int) -> int:  # calcula qué % de los que empiezan terminan
    if iniciados <= 0:  # si nadie empezó todavía
        return 0  # evita dividir entre cero
    return int(guardados * 100 / iniciados + 0.5)  # porcentaje redondeado a entero (.5 sube, como Math.round)


def caida_entre_pasos(anterior: int, siguiente: int) -> int:  # % de personas que se pierden entre un paso y el siguiente
    if anterior <= 0:  # si nadie llegó al paso anterior
        return 0  # no hay caída que medir
    return int(max(anterior - siguiente, 0) * 100 / anterior + 0.5)  # porcentaje perdido, redondeado


def armar_embudos(conteos: dict[str, int], errores: dict[tuple[str, str], int]) -> list[dict]:  # arma un embudo por flujo
    embudos = []  # lista de embudos
    for flujo in FLUJOS:  # recorre cada flujo principal
        pasos = []  # pasos de este embudo
        anterior = None  # total del paso anterior
        for evento in flujo["pasos"]:  # recorre los pasos en orden
            total = conteos.get(evento, 0)  # cuántos llegaron a este paso
            caida = caida_entre_pasos(anterior, total) if anterior is not None else 0  # caída desde el paso anterior
            pasos.append({"evento": evento, "total": total, "caida": caida})  # agrega el paso
            anterior = total  # este paso pasa a ser el anterior
        inicio = pasos[0]["total"]  # cuántos empezaron
        exito = pasos[-1]["total"]  # cuántos terminaron
        motivos = [  # errores del flujo agrupados por motivo
            {"motivo": motivo, "total": total}  # un motivo y cuántas veces pasó
            for (evento, motivo), total in sorted(errores.items())  # recorre todos los errores
            if evento == flujo["error"]  # solo los de este flujo
        ]  # fin de motivos
        embudos.append({  # agrega el embudo completo
            "id": flujo["id"],  # identificador del flujo
            "nombre": flujo["nombre"],  # nombre legible
            "pasos": pasos,  # pasos con total y caída
            "porcentaje_terminan": porcentaje_terminan(inicio, exito),  # % que llega al éxito
            "evento_error": flujo["error"],  # evento de error o salida del flujo
            "total_errores": conteos.get(flujo["error"], 0),  # cuántas veces se frenó
            "motivos": motivos,  # errores por motivo
        })  # fin del embudo
    return embudos  # devuelve todos los embudos


def mayor_caida(embudos: list[dict]) -> dict | None:  # busca el paso donde más gente se pierde en toda la app
    mejor = None  # todavía no hay caída
    for embudo in embudos:  # recorre cada embudo
        for i in range(1, len(embudo["pasos"])):  # recorre cada paso desde el segundo
            paso = embudo["pasos"][i]  # paso actual
            previo = embudo["pasos"][i - 1]  # paso anterior
            if previo["total"] == 0:  # si nadie llegó al paso anterior
                continue  # no se puede medir la caída
            if mejor is None or paso["caida"] > mejor["caida"]:  # si esta caída es la mayor hasta ahora
                mejor = {"flujo": embudo["nombre"], "desde": previo["evento"], "hasta": paso["evento"], "caida": paso["caida"]}  # la guarda
    return mejor  # None si no hay datos
