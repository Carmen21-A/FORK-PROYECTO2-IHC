# Tarea 10 · Mis datos y salida honesta (lógica pura, sin base de datos)
# Regla de Presupuesto Estudiantil al eliminar la cuenta:
#   «Se elimina todo: movimientos, presupuestos y metas. Antes puede descargar sus movimientos.»
# Ningún dato de esta app afecta a otra persona, por eso la regla no bloquea la eliminación.
from datetime import date, datetime  # tipos de fecha para convertirlos a texto
from decimal import Decimal  # montos de dinero


TABLAS_DEL_USUARIO = [  
    ("movimientos", "movimientos"),  
    ("limites_mensuales", "límites mensuales"), 
    ("presupuestos_categoria", "presupuestos por categoría"),  
    ("metas_ahorro", "metas de ahorro"),  
    ("historial", "registros del historial"),  
]  # fin de tablas


def a_texto(valor):  
    if isinstance(valor, Decimal):  
        return float(valor)  
    if isinstance(valor, (date, datetime)):  
        return valor.isoformat()  # texto estándar
    return valor  


def fila(objeto, campos: list[str]) -> dict:  
    return {campo: a_texto(getattr(objeto, campo)) for campo in campos}  # sin ids internos ni user_id


def resumen_conteos(conteos: dict[str, int]) -> dict[str, int]: 
    return {clave: int(conteos.get(clave, 0)) for clave, _ in TABLAS_DEL_USUARIO}  # 0 si no tiene datos de ese tipo
