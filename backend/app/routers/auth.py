# Reemplaza a lib/services/auth_service.dart (Tarea 1: acceso)
from datetime import datetime, timedelta, timezone  # importa utilidades para manejo de fechas, duraciones y zonas horarias

from fastapi import APIRouter, Depends, HTTPException  # importa componentes principales de FastAPI para rutas y excepciones
from sqlalchemy import delete, select  # importa select para consultas y delete para borrar códigos viejos
from sqlalchemy.orm import Session  # importa Session para manipular la base de datos

from app.config import get_settings  # importa get_settings para acceder a la configuración global
from app.correo import enviar_codigo_recuperacion  # importa la función que manda el código de 4 dígitos
from app.database import get_db  # importa la dependencia que provee la sesión de base de datos
from app.dependencias import usuario_actual  # importa la dependencia que obtiene al usuario con sesión activa
from app.logica.recuperacion import MAX_INTENTOS, codigo_correcto, generar_codigo, hash_codigo, vencido  # reglas del código
from app.models import RecuperacionPassword, Usuario  # importa los modelos de recuperación y usuario
from app.schemas import (  # importa los esquemas de datos para entrada y salida
    Credenciales,  # esquema con email y password
    NuevaPassword,  # esquema con la nueva contraseña
    Registro,  # esquema para crear cuenta (con nombre completo)
    RestablecerPassword,  # esquema con correo, código y contraseña nueva
    Sesion,  # esquema de respuesta con token y usuario
    SolicitudRecuperacion,  # esquema con email para recuperación
    UsuarioRead,  # esquema de lectura de datos del usuario
    VerificarCodigo,  # esquema con correo y código de 4 dígitos
)  # fin de imports de schemas
from app.security import create_access_token, hash_password, verify_password  # importa funciones criptográficas y de JWT

router = APIRouter(prefix="/auth", tags=["auth"])  # crea el router de autenticación con prefijo /auth


def _sesion(usuario: Usuario) -> Sesion:  # función auxiliar para empaquetar un token JWT y los datos del usuario en un objeto Sesion
    return Sesion(access_token=create_access_token(usuario.id), user=usuario)  # genera el token firmado y retorna la sesión completa


# registrar usuario
@router.post("/register", response_model=Sesion, status_code=201)  # endpoint POST para registrar una nueva cuenta de usuario
def sign_up(payload: Registro, db: Session = Depends(get_db)) -> Sesion:  # función controladora del registro
    email = payload.email.lower()  # normaliza el correo electrónico a minúsculas
    if db.scalar(select(Usuario).where(Usuario.email == email)):  # comprueba si ya existe algún usuario con ese correo
        raise HTTPException(  # lanza error 409 si el correo ya está en uso
            status_code=409,  # código de estado 409 Conflicto
            detail="Este correo ya esta registrado, inicia sesion o usa otro correo.",  # mensaje de error legible
        )  # fin de raise
    usuario = Usuario(email=email, nombre=payload.nombre, password_hash=hash_password(payload.password))  # instancia el usuario con su nombre y su contraseña hasheada
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


# recuperar contraseña x correo: paso 1, se manda un código de 4 dígitos
@router.post("/password/recover", status_code=202)  # endpoint POST para pedir el código de recuperación
def reset_password_for_email(  # función controladora para procesar solicitud de recuperación
    payload: SolicitudRecuperacion, db: Session = Depends(get_db)  # recibe el correo solicitado y la sesión de base de datos
) -> dict[str, str | int]:  # retorna mensaje de confirmación y minutos de vigencia
    settings = get_settings()  # carga la configuración del sistema
    usuario = db.scalar(select(Usuario).where(Usuario.email == payload.email.lower()))  # busca al usuario por correo
    if usuario is not None:  # si el correo sí pertenece a un usuario registrado
        # Solo sirve el último código: pedir otro anula los anteriores
        db.execute(delete(RecuperacionPassword).where(RecuperacionPassword.user_id == usuario.id))  # borra códigos viejos
        codigo = generar_codigo()  # sortea el código de 4 dígitos
        db.add(  # guarda el registro de solicitud de recuperación
            RecuperacionPassword(  # instancia el modelo RecuperacionPassword
                user_id=usuario.id,  # vincula el código al id del usuario
                token_hash=hash_codigo(usuario.id, codigo),  # guarda solo el hmac del código, nunca el código
                expires_at=datetime.now(timezone.utc)  # fecha actual en UTC
                + timedelta(minutes=settings.recovery_code_minutes),  # suma los minutos de vigencia permitidos
            )  # fin de RecuperacionPassword
        )  # fin de db.add
        db.commit()  # confirma el guardado en la base de datos
        try:  # intenta enviar el correo con el código
            enviar_codigo_recuperacion(usuario.email, codigo)  # llama a la función de envío de correo
        except Exception as exc:  # captura si el servidor de correo falla
            raise HTTPException(  # lanza error 502 de pasarela si no pudo enviar
                status_code=502, detail="No se pudo enviar el correo con el código. Intenta de nuevo."  # detalle del fallo de correo
            ) from exc  # encadena la excepción original
    # No se revela si el correo existe o no
    return {  # respuesta genérica por seguridad
        "message": "Si el correo está registrado, te enviamos un código de 4 dígitos.",  # mismo texto exista o no
        "minutos": settings.recovery_code_minutes,  # la pantalla dice cuánto sirve el código
    }  # fin de la respuesta


def _codigo_valido(payload: VerificarCodigo, db: Session) -> tuple[Usuario, RecuperacionPassword]:  # revisa el código escrito
    usuario = db.scalar(select(Usuario).where(Usuario.email == payload.email.lower()))  # dueño del correo
    recuperacion = (  # último código pedido con ese correo que no se usó
        db.scalar(  # consulta un solo registro
            select(RecuperacionPassword)  # tabla de códigos
            .where(RecuperacionPassword.user_id == usuario.id, RecuperacionPassword.used_at.is_(None))  # del usuario y sin usar
            .order_by(RecuperacionPassword.expires_at.desc())  # el más nuevo primero
        )  # fin de la consulta
        if usuario is not None  # solo si el correo existe
        else None  # correo desconocido: no hay código
    )  # fin de la búsqueda
    if usuario is None or recuperacion is None:  # nunca se pidió un código (o el correo no existe)
        raise HTTPException(status_code=400, detail="Este código no sirve. Pide uno nuevo.")  # mismo mensaje en ambos casos
    if vencido(recuperacion.expires_at):  # pasó el tiempo de vigencia
        raise HTTPException(status_code=400, detail="El código venció. Pide uno nuevo.")  # mensaje claro de qué hacer
    if recuperacion.intentos >= MAX_INTENTOS:  # ya se equivocó demasiadas veces
        raise HTTPException(status_code=400, detail="Escribiste mal el código 5 veces. Pide uno nuevo.")  # bloquea ese código
    if not codigo_correcto(recuperacion.token_hash, usuario.id, payload.codigo):  # el código no coincide
        recuperacion.intentos += 1  # cuenta el error
        db.commit()  # guarda el intento antes de responder
        quedan = MAX_INTENTOS - recuperacion.intentos  # intentos que le quedan
        if quedan == 0:  # se acabaron los intentos
            detalle = "Escribiste mal el código 5 veces. Pide uno nuevo."  # ese código ya no sirve
        elif quedan == 1:  # último intento
            detalle = "El código no es correcto. Te queda 1 intento."  # singular
        else:  # todavía puede probar varias veces
            detalle = f"El código no es correcto. Te quedan {quedan} intentos."  # plural
        raise HTTPException(status_code=400, detail=detalle)  # rechaza con error 400
    return usuario, recuperacion  # código correcto


# paso 2: comprobar el código antes de pedir la contraseña nueva (no lo gasta)
@router.post("/password/verify")  # endpoint POST para validar el código de 4 dígitos
def verify_otp(payload: VerificarCodigo, db: Session = Depends(get_db)) -> dict[str, bool]:  # función controladora de verificación
    _codigo_valido(payload, db)  # lanza error 400 si el código no sirve
    return {"valido": True}  # el código es correcto: la pantalla pasa a la contraseña nueva


# paso 3: con el código correcto se guarda la contraseña nueva y se abre la sesión
@router.post("/password/reset", response_model=Sesion)  # endpoint POST para poner la contraseña nueva
def reset_password(payload: RestablecerPassword, db: Session = Depends(get_db)) -> Sesion:  # función controladora del cambio
    usuario, recuperacion = _codigo_valido(payload, db)  # se vuelve a revisar: nadie se salta el paso 2
    usuario.password_hash = hash_password(payload.password)  # guarda el hash de la contraseña nueva
    recuperacion.used_at = datetime.now(timezone.utc)  # el código ya se usó: no sirve una segunda vez
    db.commit()  # confirma ambos cambios juntos
    return _sesion(usuario)  # entra directo con la contraseña nueva
