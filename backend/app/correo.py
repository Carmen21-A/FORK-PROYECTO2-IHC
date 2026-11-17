import logging  # importa el módulo logging para emitir mensajes en consola
from email.message import EmailMessage  # importa EmailMessage para construir mensajes de correo estructurados
from smtplib import SMTP, SMTP_SSL  # importa clientes SMTP estándar y cifrados SSL para enviar emails

from app.config import get_settings  # importa get_settings para leer los parámetros del servidor de correo

logger = logging.getLogger("presupuesto.correo")  # crea un logger con el nombre del módulo de correo


def enviar_codigo_recuperacion(email: str, codigo: str) -> None:  # función para enviar el código de 4 dígitos al usuario
    settings = get_settings()  # obtiene la configuración actual del sistema

    # Sin SMTP configurado (desarrollo) el código se muestra en la consola del backend
    if not settings.smtp_host or not settings.smtp_from:  # comprueba si no se configuró servidor SMTP o remitente
        logger.warning("Código de recuperación para %s: %s", email, codigo)  # imprime el código en la consola como advertencia
        return  # termina la función sin intentar conexión de red

    mensaje = EmailMessage()  # crea una nueva instancia de mensaje de correo electrónico
    mensaje["Subject"] = f"{settings.app_name}: tu código es {codigo}"  # el código va en el asunto: se ve sin abrir el correo
    mensaje["From"] = settings.smtp_from  # define el correo del remitente
    mensaje["To"] = email  # define el correo destinatario
    mensaje.set_content(  # redacta el cuerpo en texto plano del correo
        "Recibimos una solicitud para cambiar tu contraseña.\n\n"  # primera línea del mensaje informando la solicitud
        f"Tu código es: {codigo}\n\n"  # el código de 4 dígitos
        f"Escríbelo en la pantalla de Presupuesto Estudiantil. Sirve por {settings.recovery_code_minutes} minutos.\n\n"  # dónde usarlo y cuánto dura
        "Si no lo pediste, ignora este correo: tu contraseña sigue igual."  # aviso de seguridad si no fue solicitado por el usuario
    )  # fin de set_content

    cliente = SMTP_SSL if settings.smtp_port == 465 else SMTP  # selecciona conexión SSL directa para puerto 465 o SMTP estándar para otros
    with cliente(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:  # establece la conexión con el servidor SMTP con 15s de timeout
        if settings.smtp_use_tls and settings.smtp_port != 465:  # si se configuró TLS y no es puerto 465
            smtp.starttls()  # inicia la capa de cifrado STARTTLS segura
        if settings.smtp_user:  # si se proveyó un usuario para autenticación
            smtp.login(settings.smtp_user, settings.smtp_password or "")  # inicia sesión en el servidor de correo con usuario y contraseña
        smtp.send_message(mensaje)  # envía el correo electrónico a través de la conexión SMTP activa
