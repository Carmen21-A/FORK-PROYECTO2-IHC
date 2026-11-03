import jwt  # importa la librería PyJWT para decodificar y validar tokens JWT
from fastapi import Depends, HTTPException, status  # importa utilidades de FastAPI para dependencias y manejo de errores HTTP
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer  # importa esquema de seguridad HTTP Bearer para leer el header de autorización
from sqlalchemy.orm import Session  # importa el tipo Session para interactuar con la base de datos

from app.database import get_db  # importa la dependencia que entrega una sesión de base de datos
from app.models import Usuario  # importa el modelo de datos Usuario
from app.security import decode_access_token  # importa la función para decodificar tokens de acceso

bearer = HTTPBearer(auto_error=False)  # inicializa el esquema HTTPBearer sin lanzar error automático si falta la cabecera


# Equivale a Supabase.instance.client.auth.currentUser: sin sesion valida -> 401
def usuario_actual(  # dependencia de FastAPI para obtener el usuario autenticado actual a partir del token Bearer
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),  # extrae las credenciales Bearer enviadas en la petición
    db: Session = Depends(get_db),  # inyecta la sesión de la base de datos
) -> Usuario:  # retorna la instancia del Usuario autenticado
    no_autorizado = HTTPException(  # define el objeto de excepción 401 para reusar cuando la autenticación falle
        status_code=status.HTTP_401_UNAUTHORIZED,  # código de estado HTTP 401 No Autorizado
        detail="La sesión no es válida o ha expirado.",  # mensaje de error legible para el cliente
        headers={"WWW-Authenticate": "Bearer"},  # cabecera estándar indicando esquema Bearer
    )  # fin de la definición de no_autorizado
    if credentials is None:  # verifica si la petición no incluyó ninguna credencial en los headers
        raise no_autorizado  # lanza error 401 si no hay token
    try:  # bloque para intentar decodificar el token JWT
        user_id = decode_access_token(credentials.credentials)  # extrae el id de usuario decodificando el token
    except (jwt.InvalidTokenError, ValueError):  # captura si el token es inválido, adulterado o expiró
        raise no_autorizado from None  # lanza error 401 sin exponer trazas internas
    usuario = db.get(Usuario, user_id)  # busca al usuario en la base de datos por su id primario
    if usuario is None:  # si el usuario ya no existe en la base de datos
        raise no_autorizado  # lanza error 401 impidiendo el acceso
    return usuario  # retorna el usuario autenticado a la ruta protegida
