# Tarea 9 (Parte B): Aviso antes de superar el presupuesto de una categoría en el mes


def calcular_aviso_presupuesto(  # decide si un gasto nuevo o editado necesita aviso y calcula cuánto se pasaría
    presupuesto: float | None,  # presupuesto de la categoría en ese mes (None si no hay)
    gastado_otros: float,  # lo gastado en la categoría y mes sin contar este gasto
    monto_anterior: float,  # lo que este gasto ya sumaba en la categoría (0 si es nuevo o cambia de categoría)
    monto_nuevo: float,  # lo que sumará este gasto después de guardarlo
) -> dict | None:  # devuelve los datos del aviso, o None si no hace falta avisar
    if presupuesto is None:  # si la categoría no tiene presupuesto en ese mes
        return None  # no hay nada que superar
    total_antes = gastado_otros + monto_anterior  # gasto de la categoría antes de la operación
    total_despues = gastado_otros + monto_nuevo  # gasto de la categoría después de la operación
    if total_despues <= presupuesto:  # si después de guardar sigue dentro del presupuesto
        return None  # no hace falta avisar
    if total_despues <= total_antes:  # si la operación no aumenta el gasto (p. ej. solo cambia la descripción o baja el monto)
        return None  # no es esta operación la que hace pasar el límite
    return {  # datos que la pantalla muestra en el aviso
        "presupuesto": round(presupuesto, 2),  # presupuesto de la categoría
        "gastado": round(gastado_otros, 2),  # lo ya gastado sin este gasto
        "monto": round(monto_nuevo, 2),  # monto de este gasto
        "nuevo_total": round(total_despues, 2),  # cómo quedaría el gasto de la categoría
        "exceso": round(total_despues - presupuesto, 2),  # cuánto se pasaría del presupuesto
    }  # fin del aviso
