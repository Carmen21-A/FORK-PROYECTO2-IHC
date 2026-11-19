# Lógica pura de la analítica de interacción (Clase 21 y Tarea 9 Parte A)
# Regla de privacidad: se registra la acción, no a la persona. Cada evento solo acepta
# las propiedades que su pregunta necesita, y cada propiedad solo acepta valores de una lista fija.
# Así nunca se guardan email, descripción, monto, nombre de una meta ni texto buscado.

BOOLEANO = "booleano"  

TIPOS = {"gasto", "ingreso"}  
CATEGORIAS = {"Transporte", "Comida", "Estudios", "Ocio", "Otros"}  
OPERACIONES = {"asignar", "retirar", "transferir"}  # operaciones de fondos en metas (Tarea 8)

EVENTOS_PERMITIDOS: dict[str, dict] = {  
    # Flujo 1 · Registrar movimiento
    "movimiento_iniciado": {},  
    "movimiento_guardado": {"tipo": TIPOS, "categoria": CATEGORIAS}, 
    "movimiento_rechazado": {"motivo": {"monto_vacio", "monto_invalido", "supera_limite_mensual", "rechazado_por_servidor"}},  
    # Flujo 2 · Aviso antes de superar el límite (Tarea 9 Parte B)
    "aviso_presupuesto_mostrado": {"categoria": CATEGORIAS},  
    "aviso_presupuesto_confirmado": {"categoria": CATEGORIAS},  
    "aviso_presupuesto_cancelado": {"categoria": CATEGORIAS},  
    # Flujo 3 · Pagar un movimiento pendiente
    "pago_iniciado": {"tipo": TIPOS},  
    "movimiento_pagado": {"tipo": TIPOS},  
    "pago_rechazado": {"motivo": {"fondos_reservados_en_metas", "rechazado_por_servidor"}},  
    # Flujo 4 · Crear meta de ahorro (Tarea 8)
    "meta_creacion_iniciada": {},  
    "meta_creada": {},  
    "meta_rechazada": {"motivo": {"nombre_vacio", "objetivo_invalido", "fecha_vacia", "rechazado_por_servidor"}},  
    # Flujo 5 · Mover fondos entre saldo y metas (Tarea 8)
    "fondos_operacion_iniciada": {"operacion": OPERACIONES},  
    "fondos_operacion_realizada": {"operacion": OPERACIONES}, 
    "fondos_operacion_rechazada": {"operacion": OPERACIONES, "motivo": {"fondos_insuficientes", "rechazado_por_servidor"}},  
    # Flujo 6 · Presupuesto por categoría
    "presupuesto_edicion_iniciada": {"categoria": CATEGORIAS},  
    "presupuesto_categoria_guardado": {"categoria": CATEGORIAS, "supera_limite": BOOLEANO},  # éxito (ejemplo de clase)
    "presupuesto_rechazado": {"motivo": {"vacio", "letras", "menor_o_igual_a_cero", "rechazado_por_servidor"}},  
    # Flujo 7 · Buscar y filtrar movimientos
    "busqueda_realizada": {"con_texto": BOOLEANO, "con_filtros": BOOLEANO},  # se buscó (sin guardar el texto buscado)
    "busqueda_sin_resultados": {"con_texto": BOOLEANO, "con_filtros": BOOLEANO},  # la búsqueda no encontró nada
    # Flujo 8 · Mis datos y eliminar la cuenta (Tarea 10)
    "datos_descargados": {"formato": {"json", "csv"}},  
    "cuenta_eliminacion_iniciada": {},  
    "cuenta_eliminada": {},  
    "cuenta_eliminacion_frenada": {"motivo": {"conservo_la_cuenta", "rechazado_por_servidor"}},  
}  # fin de eventos permitidos

FLUJOS = [  
    {"id": "registrar", "nombre": "Registrar movimiento", "pasos": ["movimiento_iniciado", "movimiento_guardado"], "error": "movimiento_rechazado"},  # flujo 1
    {"id": "aviso", "nombre": "Aviso de presupuesto (Tarea 9)", "pasos": ["aviso_presupuesto_mostrado", "aviso_presupuesto_confirmado"], "error": "aviso_presupuesto_cancelado"},  # flujo 2
    {"id": "pagar", "nombre": "Pagar un pendiente", "pasos": ["pago_iniciado", "movimiento_pagado"], "error": "pago_rechazado"},  # flujo 3
    {"id": "meta", "nombre": "Crear meta de ahorro (Tarea 8)", "pasos": ["meta_creacion_iniciada", "meta_creada"], "error": "meta_rechazada"},  # flujo 4
    {"id": "fondos", "nombre": "Mover fondos en metas (Tarea 8)", "pasos": ["fondos_operacion_iniciada", "fondos_operacion_realizada"], "error": "fondos_operacion_rechazada"},  # flujo 5
    {"id": "presupuesto", "nombre": "Presupuesto por categoría", "pasos": ["presupuesto_edicion_iniciada", "presupuesto_categoria_guardado"], "error": "presupuesto_rechazado"},  # flujo 6
    {"id": "eliminar_cuenta", "nombre": "Eliminar cuenta (Tarea 10)", "pasos": ["cuenta_eliminacion_iniciada", "cuenta_eliminada"], "error": "cuenta_eliminacion_frenada"},  # flujo 8
]  


def validar_evento(evento: str, props: dict) -> None:  
    if evento not in EVENTOS_PERMITIDOS:  
        raise ValueError(f"Evento desconocido: {evento}")  
    permitidas = EVENTOS_PERMITIDOS[evento] 
    sobrantes = set(props) - set(permitidas)  
    if sobrantes:  
        raise ValueError(f"Propiedades no permitidas: {', '.join(sorted(sobrantes))}") 
    for clave, valor in props.items():  # revisa el valor de cada propiedad
        valores = permitidas[clave]  
        if valores == BOOLEANO:  
            if not isinstance(valor, bool):  
                raise ValueError(f"{clave} debe ser verdadero o falso") 
        elif valor not in valores:  
            raise ValueError(f"{clave} no está en la lista permitida")  


def porcentaje_terminan(iniciados: int, guardados: int) -> int:  
    if iniciados <= 0:  
        return 0  
    return int(guardados * 100 / iniciados + 0.5)  


def caida_entre_pasos(anterior: int, siguiente: int) -> int: 
    if anterior <= 0:  
        return 0  
    return int(max(anterior - siguiente, 0) * 100 / anterior + 0.5)  # porcentaje perdido, redondeado


def armar_embudos(conteos: dict[str, int], errores: dict[tuple[str, str], int]) -> list[dict]:  
    embudos = []  
    for flujo in FLUJOS:  
        pasos = []  
        anterior = None 
        for evento in flujo["pasos"]:  
            total = conteos.get(evento, 0)  
            caida = caida_entre_pasos(anterior, total) if anterior is not None else 0  
            pasos.append({"evento": evento, "total": total, "caida": caida})  
            anterior = total  
        inicio = pasos[0]["total"]  # cuántos empezaron
        exito = pasos[-1]["total"]  # cuántos terminaron
        motivos = [  
            {"motivo": motivo, "total": total}  
            for (evento, motivo), total in sorted(errores.items())  # recorre todos los errores
            if evento == flujo["error"]  
        ]  
        embudos.append({  
            "id": flujo["id"],  
            "nombre": flujo["nombre"],  
            "pasos": pasos,  
            "porcentaje_terminan": porcentaje_terminan(inicio, exito),  
            "evento_error": flujo["error"], 
            "total_errores": conteos.get(flujo["error"], 0), 
            "motivos": motivos,  
        })  
    return embudos  


def mayor_caida(embudos: list[dict]) -> dict | None:  
    mejor = None  
    for embudo in embudos:  # recorre cada embudo
        for i in range(1, len(embudo["pasos"])):  
            paso = embudo["pasos"][i]  
            previo = embudo["pasos"][i - 1]  
            if previo["total"] == 0:  
                continue  
            if mejor is None or paso["caida"] > mejor["caida"]: 
                mejor = {"flujo": embudo["nombre"], "desde": previo["evento"], "hasta": paso["evento"], "caida": paso["caida"]}  
    return mejor  
