# Reemplaza a lib/services/auth_service.dart (Tarea 1: acceso)
from datetime import datetime, timedelta, timezone  # importa utilidades para manejo de fechas, duraciones y zonas horarias
from hashlib import sha256  # importa sha256 para computar hashes seguros de tokens de recuperación
from secrets import token_urlsafe  # importa token_urlsafe para generar cadenas de texto aleatorias e impredecibles
from urllib.parse import urlencode  # importa urlencode para estructurar parámetros de consulta en URLs

from fastapi import APIRouter, Depends, HTTPException  # importa componentes principales de FastAPI para rutas y excepciones
from sqlalchemy import select  # importa select para construir consultas SQL orientadas a objetos
from sqlalchemy.orm import Session  # importa Session para manipular la base de datos

from app.config import get_settings  # importa get_settings para acceder a la configuración global
from app.correo import enviar_enlace_recuperacion  # importa la función para enviar el email de restablecimiento
from app.database import get_db  # importa la dependencia que provee la sesión de base de datos
from app.dependencias import usuario_actual  # importa la dependencia que obtiene al usuario con sesión activa
from app.models import RecuperacionPassword, Usuario  # importa los modelos de recuperación y usuario
from app.schemas import (  # importa los esquemas de datos para entrada y salida
    Credenciales,  # esquema con email y password
    NuevaPassword,  # esquema con la nueva contraseña
    Sesion,  # esquema de respuesta con token y usuario
    SolicitudRecuperacion,  # esquema con email para recuperación
    UsuarioRead,  # esquema de lectura de datos del usuario
    VerificarRecuperacion,  # esquema para verificar token de recuperación
)  # fin de imports de schemas
from app.security import create_access_token, hash_password, verify_password  # importa funciones criptográficas y de JWT

router = APIRouter(prefix="/auth", tags=["auth"])  # crea el router de autenticación con prefijo /auth


def _sesion(usuario: Usuario) -> Sesion:  # función auxiliar para empaquetar un token JWT y los datos del usuario en un objeto Sesion
    return Sesion(access_token=create_access_token(usuario.id), user=usuario)  # genera el token firmado y retorna la sesión completa


# registrar usuario
@router.post("/register", response_model=Sesion, status_code=201)  # endpoint POST para registrar una nueva cuenta de usuario
def sign_up(payload: Credenciales, db: Session = Depends(get_db)) -> Sesion:  # función controladora del registro
    email = payload.email.lower()  # normaliza el correo electrónico a minúsculas
    if db.scalar(select(Usuario).where(Usuario.email == email)):  # comprueba si ya existe algún usuario con ese correo
        raise HTTPException(  # lanza error 409 si el correo ya está en uso
            status_code=409,  # código de estado 409 Conflicto
            detail="Este correo ya esta registrado, inicia sesion o usa otro correo.",  # mensaje de error legible
        )  # fin de raise
    usuario = Usuario(email=email, password_hash=hash_password(payload.password))  # instancia el usuario con su contraseña hasheada
    db.add(usuario)  # agrega el nuevo usuario a la sesión
    db.commit()  # guarda el registro permanentemente en la base de datos
    return _sesion(usuario)  # retorna la sesión iniciada automáticamente con el token JWT


# iniciar sesion
@router.post("/login", response_model=Sesion)  # endpoint POST para autenticación con credenciales existentes
def sign_in_with_password(payload: Credenciales, db: Session = Depends(get_db)) -> Sesion:  # función controladora del login
    usuario = db.scalar(select(Usuario).where(Usuario.email == payload.email.lower()))  # busca al usuario por su correo en minúsculas
    valida, hash_nuevo = (  # desestructura la tupla devuelta por verify_password
        verify_password(payload.password, usuario.password_hash) if usuario else (False, None)  # verifica contraseña o retorna falso si no existe
    )  # fin de verificación
    if usuario is None or not valida:  # si el usuario no existe o la contraseña no coincide
        raise HTTPException(  # lanza error 401 de credenciales incorrectas
            status_code=401,  # código 401 No Autorizado
            detail="Las credenciales son incorrectas, tienes que revisar tu correo o contraseña.",  # mensaje de error
        )  # fin de raise
    if hash_nuevo:  # si el hasher determinó que el hash debía actualizarse de formato
        usuario.password_hash = hash_nuevo  # actualiza el hash guardado en el usuario
        db.commit()  # confirma la actualización en la base de datos
    return _sesion(usuario)  # retorna la sesión con el token JWT recién generado


# usuario actual
@router.get("/me", response_model=UsuarioRead)  # endpoint GET para consultar los datos del usuario autenticado
def current_user(usuario: Usuario = Depends(usuario_actual)) -> Usuario:  # recibe el usuario validado por el token
    return usuario  # retorna los datos del usuario actual


# actualizar contraseña (usuario con sesion, tambien despues de recuperar)
@router.patch("/password", status_code=204)  # endpoint PATCH para cambiar la contraseña del usuario logueado
def update_password(  # función controladora para actualizar contraseña
    payload: NuevaPassword,  # cuerpo de la petición con la nueva contraseña
    usuario: Usuario = Depends(usuario_actual),  # usuario autenticado actual
    db: Session = Depends(get_db),  # sesión de base de datos
) -> None:  # responde con 204 sin contenido
    usuario.password_hash = hash_password(payload.password)  # computa el nuevo hash con la nueva contraseña recibida
    db.commit()  # guarda el cambio en la base de datos


# recuperar contraseña x correo
@router.post("/password/recover", status_code=202)  # endpoint POST para solicitar enlace de recuperación de clave
def reset_password_for_email(  # función controladora para procesar solicitud de recuperación
    payload: SolicitudRecuperacion, db: Session = Depends(get_db)  # recibe el correo solicitado y la sesión de base de datos
) -> dict[str, str]:  # retorna mensaje de confirmación
    settings = get_settings()  # carga la configuración del sistema
    usuario = db.scalar(select(Usuario).where(Usuario.email == payload.email.lower()))  # busca al usuario por correo
    if usuario is not None:  # si el correo sí pertenece a un usuario registrado
        token = token_urlsafe(32)  # genera un token criptográfico seguro de 32 bytes
        db.add(  # guarda el registro de solicitud de recuperación
            RecuperacionPassword(  # instancia el modelo RecuperacionPassword
                user_id=usuario.id,  # vincula el token al id del usuario
                token_hash=sha256(token.encode()).hexdigest(),  # guarda el hash sha256 del token para seguridad
                expires_at=datetime.now(timezone.utc)  # fecha actual en UTC
                + timedelta(minutes=settings.recovery_token_minutes),  # suma los minutos de vigencia permitidos
            )  # fin de RecuperacionPassword
        )  # fin de db.add
        db.commit()  # confirma el guardado en la base de datos
        # Mismo formato de enlace que usaba Supabase: ?token_hash=...&type=recovery
        enlace = f"{settings.frontend_url}/?{urlencode({'token_hash': token, 'type': 'recovery'})}"  # arma el enlace completo hacia el frontend
        try:  # intenta enviar el correo con el enlace
            enviar_enlace_recuperacion(usuario.email, enlace)  # llama a la función de envío de correo
        except Exception as exc:  # captura si el servidor de correo falla
            raise HTTPException(  # lanza error 502 de pasarela si no pudo enviar
                status_code=502, detail="No se pudo enviar el correo de recuperación."  # detalle del fallo de correo
            ) from exc  # encadena la excepción original
    # No se revela si el correo existe o no
    return {"message": "Si el correo está registrado, recibirás un enlace para cambiar tu contraseña."}  # respuesta genérica por seguridad


# Equivale a verifyOTP(type: recovery) de lib/main.dart: abre una sesion con el enlace
@router.post("/password/verify", response_model=Sesion)  # endpoint POST para validar el token del enlace y abrir sesión
def verify_otp(payload: VerificarRecuperacion, db: Session = Depends(get_db)) -> Sesion:  # función controladora de verificación
    token_hash = sha256(payload.token_hash.encode()).hexdigest()  # computa el hash sha256 del token enviado
    recuperacion = db.scalar(  # busca el registro de recuperación que coincida con el hash
        select(RecuperacionPassword).where(RecuperacionPassword.token_hash == token_hash)  # filtra por el hash
    )  # ejecuta la consulta
    ahora = datetime.now(timezone.utc)  # obtiene la fecha y hora actual en UTC
    if (  # verifica si el token es inválido, ya fue usado o ya expiró
        recuperacion is None  # no existe ningún registro con ese hash
        or recuperacion.used_at is not None  # el enlace ya fue utilizado previamente
        or recuperacion.expires_at.replace(tzinfo=timezone.utc) <= ahora  # el enlace ya superó su tiempo límite de validez
    ):  # si alguna de las tres condiciones se cumple
        raise HTTPException(status_code=400, detail="El enlace no es válido o expiró.")  # rechaza con error 400
    usuario = db.get(Usuario, recuperacion.user_id)  # busca al usuario dueño de la recuperación
    if usuario is None:  # si el usuario ya no existe
        raise HTTPException(status_code=400, detail="La cuenta ya no existe.")  # rechaza con error 400
    recuperacion.used_at = ahora  # marca el enlace como utilizado en este momento
    db.commit()  # confirma la marca en la base de datos
    return _sesion(usuario)  # retorna una sesión válida para permitir al usuario cambiar su clave
