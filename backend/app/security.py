from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher

from app.config import get_settings

# Argon2 para las contraseñas nuevas; bcrypt para leer las que vienen de Supabase
password_hash = PasswordHash((Argon2Hasher(), BcryptHasher()))


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> tuple[bool, str | None]:
    # Devuelve (es_valida, hash_actualizado) para migrar bcrypt -> argon2 al iniciar sesion
    return password_hash.verify_and_update(password, hashed_password)


def create_access_token(user_id: UUID) -> str:
    settings = get_settings()
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_minutes)
    return jwt.encode(
        {"sub": str(user_id), "exp": expires},
        settings.secret_key,
        algorithm="HS256",
    )


def decode_access_token(token: str) -> UUID:
    payload = jwt.decode(
        token,
        get_settings().secret_key,
        algorithms=["HS256"],  # lista de algoritmos permitidos para la decodificación
        options={"require": ["sub", "exp"]},  # exige obligatoriamente los campos 'sub' y 'exp' en el token
    )
    return UUID(payload["sub"])
