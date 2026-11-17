# Tarea 10 · Mis datos y salida honesta (lógica pura, sin base de datos)
# Regla de Presupuesto Estudiantil al eliminar la cuenta:
#   «Se elimina todo: movimientos, presupuestos y metas. Antes puede descargar sus movimientos.»
# Ningún dato de esta app afecta a otra persona, por eso la regla no bloquea la eliminación.
from datetime import date, datetime  # tipos de fecha para convertirlos a texto
from decimal import Decimal  # montos de dinero

# Qué se borra al eliminar la cuenta, en el orden en que se borra (lo que depende del usuario primero)
TABLAS_DEL_USUARIO = [  # (clave en el resumen, nombre legible para el mensaje)
    ("movimientos", "movimientos"),  # gastos e ingresos
    ("limites_mensuales", "límites mensuales"),  # límite de gasto de cada mes
    ("presupuestos_categoria", "presupuestos por categoría"),  # presupuesto de cada categoría y mes
    ("metas_ahorro", "metas de ahorro"),  # metas y el dinero reservado en ellas
    ("historial", "registros del historial"),  # bitácora de cambios de sus movimientos
]  # fin de tablas


def a_texto(valor):  # convierte un valor de la base de datos a algo que JSON entiende
    if isinstance(valor, Decimal):  # montos: número con dos decimales
        return float(valor)  # 40.00 -> 40.0
    if isinstance(valor, (date, datetime)):  # fechas: formato ISO (2026-11-15)
        return valor.isoformat()  # texto estándar
    return valor  # textos y None quedan igual


def fila(objeto, campos: list[str]) -> dict:  # arma un diccionario solo con los campos que la persona necesita ver
    return {campo: a_texto(getattr(objeto, campo)) for campo in campos}  # sin ids internos ni user_id


def resumen_conteos(conteos: dict[str, int]) -> dict[str, int]:  # deja los conteos en el orden de TABLAS_DEL_USUARIO
    return {clave: int(conteos.get(clave, 0)) for clave, _ in TABLAS_DEL_USUARIO}  # 0 si no tiene datos de ese tipo
