# Portado de lib/utils/limite_mensual.dart (Tarea 4: límite mensual)


def es_limite_menor_a_gasto(nuevo_limite: float, gasto_actual_mes: float) -> bool:  
    return nuevo_limite < gasto_actual_mes  


def supera_limite_mensual(  
    gasto_actual_del_mes: float,  
    nuevo_gasto: float,  
    limite: float,  
) -> bool:  
    nuevo_total = gasto_actual_del_mes + nuevo_gasto  
    return nuevo_total > limite  
