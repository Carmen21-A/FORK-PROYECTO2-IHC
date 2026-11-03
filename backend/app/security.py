from datetime import datetime, timedelta, timezone  # importa utilidades para manejar fechas, tiempos de expiración y zonas horarias
from uuid import UUID  # importa el tipo UUID para identificar usuarios de forma única

import jwt  # importa la librería PyJWT para codificar y decodificar tokens
from pwdlib import PasswordHash  # importa PasswordHash de pwdlib para la gestión segura de contraseñas
from pwdlib.hashers.argon2 import Argon2Hasher  # importa el algoritmo de hashing moderno Argon2
from pwdlib.hashers.bcrypt import BcryptHasher  # importa el algoritmo Bcrypt para retrocompatibilidad con Supabase

from app.config import get_settings  # importa get_settings para acceder a la clave secreta y tiempos de sesión

# Argon2 para las contraseñas nuevas; bcrypt para leer las que vienen de Supabase
password_hash = PasswordHash((Argon2Hasher(), BcryptHasher()))  # instancia el gestor de contraseñas admitiendo Argon2 y Bcrypt


def hash_password(password: str) -> str:  # función para generar el hash seguro de una contraseña en texto plano
    return password_hash.hash(password)  # retorna el hash computado con el algoritmo preferido (Argon2)


def verify_password(password: str, hashed_password: str) -> tuple[bool, str | None]:  # verifica si la contraseña coincide con el hash almacenado
    # Devuelve (es_valida, hash_actualizado) para migrar bcrypt -> argon2 al iniciar sesion
    return password_hash.verify_and_update(password, hashed_password)  # verifica y genera un nuevo hash si correspondía actualizar el algoritmo


def create_access_token(user_id: UUID) -> str:  # función que genera un token JWT de acceso para un usuario
    settings = get_settings()  # carga la configuración de la aplicación
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_minutes)  # calcula la fecha y hora de expiración del token
    return jwt.encode(  # codifica el payload en un token JWT firmado
        {"sub": str(user_id), "exp": expires},  # payload con el identificador del usuario y fecha de expiración
        settings.secret_key,  # clave secreta usada para firmar criptográficamente el token
        algorithm="HS256",  # algoritmo de firma HMAC-SHA256
    )  # retorna el token JWT en formato string


def decode_access_token(token: str) -> UUID:  # función que decodifica y valida un token JWT extrayendo el UUID del usuario
    payload = jwt.decode(  # decodifica el token verificando su firma y vigencia
        token,  # token en texto recibido del cliente
        get_settings().secret_key,  # clave secreta con la que debe verificarse la firma
        algorithms=["HS256"],  # lista de algoritmos permitidos para la decodificación
        options={"require": ["sub", "exp"]},  # exige obligatoriamente los campos 'sub' y 'exp' en el token
    )  # fin de decode
    return UUID(payload["sub"])  # convierte el campo 'sub' a un objeto UUID y lo retorna
