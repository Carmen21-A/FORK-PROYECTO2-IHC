import logging  # importa el módulo logging para emitir mensajes en consola
from email.message import EmailMessage  # importa EmailMessage para construir mensajes de correo estructurados
from smtplib import SMTP, SMTP_SSL  # importa clientes SMTP estándar y cifrados SSL para enviar emails

from app.config import get_settings  # importa get_settings para leer los parámetros del servidor de correo

logger = logging.getLogger("presupuesto.correo")  # crea un logger con el nombre del módulo de correo


def enviar_enlace_recuperacion(email: str, enlace: str) -> None:  # función para enviar el enlace de restablecimiento de contraseña al usuario
    settings = get_settings()  # obtiene la configuración actual del sistema

    # Sin SMTP configurado (desarrollo) el enlace se muestra en la consola del backend
    if not settings.smtp_host or not settings.smtp_from:  # comprueba si no se configuró servidor SMTP o remitente
        logger.warning("Enlace de recuperación para %s: %s", email, enlace)  # imprime el enlace en la consola como advertencia
        return  # termina la función sin intentar conexión de red

    mensaje = EmailMessage()  # crea una nueva instancia de mensaje de correo electrónico
    mensaje["Subject"] = f"{settings.app_name}: restablece tu contraseña"  # define el asunto del correo
    mensaje["From"] = settings.smtp_from  # define el correo del remitente
    mensaje["To"] = email  # define el correo destinatario
    mensaje.set_content(  # redacta el cuerpo en texto plano del correo
        "Recibimos una solicitud para cambiar tu contraseña.\n\n"  # primera línea del mensaje informando la solicitud
        f"Abre este enlace para crear una nueva (válido por {settings.recovery_token_minutes} minutos):\n"  # especifica el tiempo de vigencia
        f"{enlace}\n\n"  # incluye la URL del enlace de recuperación
        "Si no lo pediste, ignora este correo."  # aviso de seguridad si no fue solicitado por el usuario
    )  # fin de set_content

    cliente = SMTP_SSL if settings.smtp_port == 465 else SMTP  # selecciona conexión SSL directa para puerto 465 o SMTP estándar para otros
    with cliente(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:  # establece la conexión con el servidor SMTP con 15s de timeout
        if settings.smtp_use_tls and settings.smtp_port != 465:  # si se configuró TLS y no es puerto 465
            smtp.starttls()  # inicia la capa de cifrado STARTTLS segura
        if settings.smtp_user:  # si se proveyó un usuario para autenticación
            smtp.login(settings.smtp_user, settings.smtp_password or "")  # inicia sesión en el servidor de correo con usuario y contraseña
        smtp.send_message(mensaje)  # envía el correo electrónico a través de la conexión SMTP activa
