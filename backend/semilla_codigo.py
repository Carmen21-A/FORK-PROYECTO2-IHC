# Pruebas E2E: deja un código de recuperación conocido para un usuario.
#   DATABASE_NAME=budget_e2e python semilla_codigo.py martita@presupuesto.com 4821
# En la app real el código se sortea y llega por correo; la prueba no puede leer el correo,
# así que reemplaza el código sorteado por uno que sí conoce. Solo acepta bases "*e2e*".
import sys  # importa sys para leer los argumentos y salir con error
from datetime import datetime, timedelta, timezone  # fechas para la vigencia del código

from sqlalchemy import create_engine, delete, select  # conexión y consultas
from sqlalchemy.orm import Session  # sesión para guardar los cambios

from app.config import get_settings  # configuración (base de datos, clave secreta y minutos)
from app.logica.recuperacion import hash_codigo  # mismo cifrado que usa la app
from app.models import RecuperacionPassword, Usuario  # tablas de códigos y usuarios


def fijar_codigo(email: str, codigo: str) -> None:  # reemplaza el código del usuario por uno conocido
    settings = get_settings()  # lee la configuración
    url = settings.url_base_de_datos  # base a la que se conecta
    if "e2e" not in (url.database or ""):  # seguridad: nunca en la base de desarrollo
        sys.exit(f"Solo se usa en una base de pruebas (*e2e*), no en '{url.database}'.")  # cancela

    with Session(create_engine(url)) as db:  # abre la base de pruebas
        usuario = db.scalar(select(Usuario).where(Usuario.email == email))  # busca al usuario
        if usuario is None:  # el correo no existe en la semilla
            sys.exit(f"No existe el usuario {email}.")  # cancela
        db.execute(delete(RecuperacionPassword).where(RecuperacionPassword.user_id == usuario.id))  # borra el código sorteado
        db.add(  # guarda el código conocido
            RecuperacionPassword(  # nuevo registro
                user_id=usuario.id,  # dueño del código
                token_hash=hash_codigo(usuario.id, codigo),  # mismo hmac que la app
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.recovery_code_minutes),  # vigencia normal
            )  # fin del registro
        )  # fin de db.add
        db.commit()  # confirma el cambio


if __name__ == "__main__":  # se ejecuta desde la consola
    fijar_codigo(sys.argv[1], sys.argv[2])  # correo y código
