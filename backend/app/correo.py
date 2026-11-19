import json
import logging
from email.message import EmailMessage
from email.utils import parseaddr
from smtplib import SMTP, SMTP_SSL
from urllib.request import Request, urlopen

from app.config import get_settings

logger = logging.getLogger("presupuesto.correo")

BREVO_URL = "https://api.brevo.com/v3/smtp/email"


def _textos(codigo: str) -> tuple[str, str]:
    settings = get_settings()
    asunto = f"{settings.app_name}: tu código es {codigo}"
    cuerpo = (
        "Recibimos una solicitud para cambiar tu contraseña.\n\n"
        f"Tu código es: {codigo}\n\n"
        f"Escríbelo en la pantalla de Presupuesto Estudiantil. Sirve por {settings.recovery_code_minutes} minutos.\n\n"
        "Si no lo pediste, ignora este correo: tu contraseña sigue igual."
    )
    return asunto, cuerpo


def _enviar_por_brevo(email: str, codigo: str) -> None:
    # Render (plan gratis) bloquea los puertos de correo 25, 465 y 587: Gmail por SMTP no sale.
    # Brevo recibe el correo por HTTPS, que sí está permitido.
    settings = get_settings()
    nombre, remitente = parseaddr(settings.smtp_from or "")
    asunto, cuerpo = _textos(codigo)
    datos = {
        "sender": {"name": nombre or settings.app_name, "email": remitente},
        "to": [{"email": email}],
        "subject": asunto,
        "textContent": cuerpo,
    }
    peticion = Request(
        BREVO_URL,
        data=json.dumps(datos).encode("utf-8"),  # cuerpo en JSON
        headers={"api-key": settings.brevo_api_key, "Content-Type": "application/json", "Accept": "application/json"},  # clave de Brevo
        method="POST",  # se crea un envío
    )  
    with urlopen(peticion, timeout=15) as respuesta:  # envía y espera la respuesta (máximo 15 s)
        if respuesta.status >= 300:  # Brevo responde 201 cuando acepta el correo
            raise RuntimeError(f"Brevo respondió {respuesta.status}")  # el router lo convierte en error 502


def enviar_codigo_recuperacion(email: str, codigo: str) -> None:
    settings = get_settings()

    # En la nube (Render): si hay clave de Brevo, se envía por su API web
    if settings.brevo_api_key and settings.smtp_from:
        _enviar_por_brevo(email, codigo)
        return

    # Sin SMTP configurado (desarrollo) el código se muestra en la consola del backend
    if not settings.smtp_host or not settings.smtp_from:
        logger.warning("Código de recuperación para %s: %s", email, codigo)
        return

    asunto, cuerpo = _textos(codigo)
    mensaje = EmailMessage()
    mensaje["Subject"] = asunto
    mensaje["From"] = settings.smtp_from
    mensaje["To"] = email
    mensaje.set_content(cuerpo)

    cliente = SMTP_SSL if settings.smtp_port == 465 else SMTP
    with cliente(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
        if settings.smtp_use_tls and settings.smtp_port != 465:
            smtp.starttls()
        if settings.smtp_user:
            smtp.login(settings.smtp_user, settings.smtp_password or "")
        smtp.send_message(mensaje)
