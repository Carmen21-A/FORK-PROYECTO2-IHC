import json  # importa json para armar el cuerpo de la petición a Brevo
import logging  # importa el módulo logging para emitir mensajes en consola
from email.message import EmailMessage  # importa EmailMessage para construir mensajes de correo estructurados
from email.utils import parseaddr  # separa «Nombre <correo>» en nombre y correo
from smtplib import SMTP, SMTP_SSL  # importa clientes SMTP estándar y cifrados SSL para enviar emails
from urllib.request import Request, urlopen  # petición HTTPS a Brevo sin librerías extra

from app.config import get_settings  # importa get_settings para leer los parámetros del servidor de correo

logger = logging.getLogger("presupuesto.correo")  # crea un logger con el nombre del módulo de correo

BREVO_URL = "https://api.brevo.com/v3/smtp/email"  # API de Brevo para mandar un correo


def _textos(codigo: str) -> tuple[str, str]:  # asunto y cuerpo del correo, iguales por Brevo o por SMTP
    settings = get_settings()  # lee el nombre de la app y los minutos de vigencia
    asunto = f"{settings.app_name}: tu código es {codigo}"  # el código va en el asunto: se ve sin abrir el correo
    cuerpo = (  # cuerpo en texto plano
        "Recibimos una solicitud para cambiar tu contraseña.\n\n"  # primera línea del mensaje informando la solicitud
        f"Tu código es: {codigo}\n\n"  # el código de 4 dígitos
        f"Escríbelo en la pantalla de Presupuesto Estudiantil. Sirve por {settings.recovery_code_minutes} minutos.\n\n"  # dónde usarlo y cuánto dura
        "Si no lo pediste, ignora este correo: tu contraseña sigue igual."  # aviso de seguridad si no fue solicitado por el usuario
    )  # fin del cuerpo
    return asunto, cuerpo  # devuelve ambos textos


def _enviar_por_brevo(email: str, codigo: str) -> None:  # envía por la API web de Brevo (HTTPS, puerto 443)
    # Render (plan gratis) bloquea los puertos de correo 25, 465 y 587: Gmail por SMTP no sale.
    # Brevo recibe el correo por HTTPS, que sí está permitido.
    settings = get_settings()  # lee la clave y el remitente
    nombre, remitente = parseaddr(settings.smtp_from or "")  # «Presupuesto Estudiantil <correo>» -> nombre y correo
    asunto, cuerpo = _textos(codigo)  # mismos textos que por SMTP
    datos = {  # cuerpo que pide la API de Brevo
        "sender": {"name": nombre or settings.app_name, "email": remitente},  # remitente verificado en Brevo
        "to": [{"email": email}],  # destinatario
        "subject": asunto,  # asunto con el código
        "textContent": cuerpo,  # cuerpo en texto plano
    }  # fin de los datos
    peticion = Request(  # arma la petición HTTP
        BREVO_URL,  # dirección de la API
        data=json.dumps(datos).encode("utf-8"),  # cuerpo en JSON
        headers={"api-key": settings.brevo_api_key, "Content-Type": "application/json", "Accept": "application/json"},  # clave de Brevo
        method="POST",  # se crea un envío
    )  # fin de la petición
    with urlopen(peticion, timeout=15) as respuesta:  # envía y espera la respuesta (máximo 15 s)
        if respuesta.status >= 300:  # Brevo responde 201 cuando acepta el correo
            raise RuntimeError(f"Brevo respondió {respuesta.status}")  # el router lo convierte en error 502


def enviar_codigo_recuperacion(email: str, codigo: str) -> None:  # función para enviar el código de 4 dígitos al usuario
    settings = get_settings()  # obtiene la configuración actual del sistema

    # En la nube (Render): si hay clave de Brevo, se envía por su API web
    if settings.brevo_api_key and settings.smtp_from:  # Brevo configurado con un remitente
        _enviar_por_brevo(email, codigo)  # envía por HTTPS
        return  # listo

    # Sin SMTP configurado (desarrollo) el código se muestra en la consola del backend
    if not settings.smtp_host or not settings.smtp_from:  # comprueba si no se configuró servidor SMTP o remitente
        logger.warning("Código de recuperación para %s: %s", email, codigo)  # imprime el código en la consola como advertencia
        return  # termina la función sin intentar conexión de red

    asunto, cuerpo = _textos(codigo)  # mismos textos que por Brevo
    mensaje = EmailMessage()  # crea una nueva instancia de mensaje de correo electrónico
    mensaje["Subject"] = asunto  # el código va en el asunto: se ve sin abrir el correo
    mensaje["From"] = settings.smtp_from  # define el correo del remitente
    mensaje["To"] = email  # define el correo destinatario
    mensaje.set_content(cuerpo)  # redacta el cuerpo en texto plano del correo

    cliente = SMTP_SSL if settings.smtp_port == 465 else SMTP  # selecciona conexión SSL directa para puerto 465 o SMTP estándar para otros
    with cliente(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:  # establece la conexión con el servidor SMTP con 15s de timeout
        if settings.smtp_use_tls and settings.smtp_port != 465:  # si se configuró TLS y no es puerto 465
            smtp.starttls()  # inicia la capa de cifrado STARTTLS segura
        if settings.smtp_user:  # si se proveyó un usuario para autenticación
            smtp.login(settings.smtp_user, settings.smtp_password or "")  # inicia sesión en el servidor de correo con usuario y contraseña
        smtp.send_message(mensaje)  # envía el correo electrónico a través de la conexión SMTP activa
