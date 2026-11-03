# Portado de lib/utils/limite_mensual.dart (Tarea 4: límite mensual)


def es_limite_menor_a_gasto(nuevo_limite: float, gasto_actual_mes: float) -> bool:  # función que valida si el nuevo límite es menor a lo ya gastado
    return nuevo_limite < gasto_actual_mes  # retorna verdadero si el nuevo límite es menor que el gasto actual del mes


def supera_limite_mensual(  # función que valida si sumar un nuevo gasto superará el límite del mes
    gasto_actual_del_mes: float,  # parámetro con el gasto acumulado actual del mes
    nuevo_gasto: float,  # parámetro con el monto del nuevo gasto que se quiere hacer
    limite: float,  # parámetro con el límite mensual fijado por el usuario
) -> bool:  # indica que la función retorna un valor booleano
    nuevo_total = gasto_actual_del_mes + nuevo_gasto  # calcula el nuevo total sumando lo gastado más el nuevo gasto
    return nuevo_total > limite  # retorna verdadero si el nuevo total supera el límite establecido
