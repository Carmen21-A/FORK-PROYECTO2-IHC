# Código de 4 dígitos para "¿Olvidaste tu contraseña?"
# Reemplaza al enlace por correo: el enlace apuntaba al frontend (localhost) y desde otro
# dispositivo no abría nada. Un código se escribe a mano en la misma pantalla donde se pidió.
import hmac  # importa hmac para firmar el código con la clave secreta del servidor
from datetime import datetime, timezone  # fechas con zona horaria para saber si el código venció
from hashlib import sha256  # importa sha256 como función de resumen para el hmac
from secrets import randbelow  # importa randbelow para sortear el código de forma impredecible
from uuid import UUID  # importa el tipo UUID del id del usuario

from app.config import get_settings  # importa la configuración para leer la clave secreta

DIGITOS = 4  # cantidad de números del código
MAX_INTENTOS = 5  # con 5 errores el código deja de servir y hay que pedir otro


def generar_codigo() -> str:  # sortea un código de 4 dígitos, por ejemplo "0427"
    return f"{randbelow(10**DIGITOS):0{DIGITOS}d}"  # número de 0 a 9999 con ceros a la izquierda


def hash_codigo(user_id: UUID, codigo: str) -> str:  # resumen que se guarda en la base (nunca el código en claro)
    clave = get_settings().secret_key.encode()  # clave secreta del servidor
    # Se mezcla con el id del usuario: el mismo código de dos personas da resúmenes distintos
    return hmac.new(clave, f"{user_id}:{codigo}".encode(), sha256).hexdigest()  # 64 caracteres hexadecimales


def codigo_correcto(guardado: str, user_id: UUID, codigo: str) -> bool:  # compara el código escrito con el guardado
    return hmac.compare_digest(guardado, hash_codigo(user_id, codigo))  # comparación en tiempo constante


def vencido(expira: datetime, ahora: datetime | None = None) -> bool:  # True si ya pasó la hora límite
    ahora = ahora or datetime.now(timezone.utc)  # hora actual en UTC
    if expira.tzinfo is None:  # SQLite (pruebas) la devuelve sin zona: está guardada en UTC
        expira = expira.replace(tzinfo=timezone.utc)  # se marca como UTC
    # PostgreSQL la devuelve con la zona del servidor (-04:00 en La Paz). El enlace viejo hacía
    # replace(tzinfo=utc) siempre: le ponía "UTC" a una hora de Bolivia sin convertirla y el
    # enlace de 60 minutos nacía vencido hace 3 horas. Comparar con su zona real lo hace bien.
    return expira <= ahora  # compara instantes, sin importar la zona
