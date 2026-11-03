# Tarea 6: gastos recurrentes (semanal o mensual)
from calendar import monthrange  # importa monthrange para calcular la cantidad de días que tiene un mes
from datetime import date, timedelta  # importa date para fechas y timedelta para sumar o restar días

TEXTO_RECURRENCIA = {"semanal": "cada semana", "mensual": "cada mes"}  # diccionario que mapea el tipo de recurrencia a su texto en español


def siguiente_fecha(fecha: date, recurrencia: str) -> date:  # función que calcula la próxima fecha según la recurrencia semanal o mensual
    # Semanal: 7 dias despues
    if recurrencia == "semanal":  # si la recurrencia es semanal
        return fecha + timedelta(days=7)  # retorna la fecha sumándole exactamente 7 días
    # Mensual: el mismo dia del mes siguiente; si no existe (31 de enero), el ultimo dia (28 de febrero)
    anio, mes = (fecha.year + 1, 1) if fecha.month == 12 else (fecha.year, fecha.month + 1)  # pasa al siguiente mes y si era diciembre salta a enero del año próximo
    return date(anio, mes, min(fecha.day, monthrange(anio, mes)[1]))  # retorna la nueva fecha ajustando al último día del mes si no tiene tantos días
