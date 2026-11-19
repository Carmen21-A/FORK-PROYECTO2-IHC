# Código de 4 dígitos para "¿Olvidaste tu contraseña?"
# Reemplaza al enlace por correo: el enlace apuntaba al frontend (localhost) y desde otro
# dispositivo no abría nada. Un código se escribe a mano en la misma pantalla donde se pidió.
import hmac  
from datetime import datetime, timezone  
from hashlib import sha256  
from secrets import randbelow 
from uuid import UUID  
from app.config import get_settings  

DIGITOS = 4  
MAX_INTENTOS = 5  


def generar_codigo() -> str:  
    return f"{randbelow(10**DIGITOS):0{DIGITOS}d}"  


def hash_codigo(user_id: UUID, codigo: str) -> str:  
    clave = get_settings().secret_key.encode()  
    # Se mezcla con el id del usuario: el mismo código de dos personas da resúmenes distintos
    return hmac.new(clave, f"{user_id}:{codigo}".encode(), sha256).hexdigest()  


def codigo_correcto(guardado: str, user_id: UUID, codigo: str) -> bool:  
    return hmac.compare_digest(guardado, hash_codigo(user_id, codigo))  


def vencido(expira: datetime, ahora: datetime | None = None) -> bool:  
    ahora = ahora or datetime.now(timezone.utc)  
    if expira.tzinfo is None: 
        expira = expira.replace(tzinfo=timezone.utc)  
    
    return expira <= ahora  
