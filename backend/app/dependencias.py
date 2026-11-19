import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario
from app.security import decode_access_token

bearer = HTTPBearer(auto_error=False)


# Equivale a Supabase.instance.client.auth.currentUser: sin sesion valida -> 401
def usuario_actual(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> Usuario:
    no_autorizado = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="La sesión no es válida o ha expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise no_autorizado
    try:
        user_id = decode_access_token(credentials.credentials)
    except (jwt.InvalidTokenError, ValueError):
        raise no_autorizado from None
    usuario = db.get(Usuario, user_id)
    if usuario is None:
        raise no_autorizado
    return usuario
