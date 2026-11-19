# Tarea 9 (Parte B): Aviso antes de superar el presupuesto de una categoría en el mes


def calcular_aviso_presupuesto(  
    presupuesto: float | None,  
    gastado_otros: float,  
    monto_anterior: float,  
    monto_nuevo: float,  
) -> dict | None:  
    if presupuesto is None:  
        return None  
    total_antes = gastado_otros + monto_anterior  
    total_despues = gastado_otros + monto_nuevo  
    if total_despues <= presupuesto:  
        return None  
    if total_despues <= total_antes:  
        return None  
    return {  
        "presupuesto": round(presupuesto, 2), 
        "gastado": round(gastado_otros, 2),  
        "monto": round(monto_nuevo, 2),  
        "nuevo_total": round(total_despues, 2),  
        "exceso": round(total_despues - presupuesto, 2),  
    }  
