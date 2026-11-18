# Recuperar la contraseña con un código de 4 dígitos (reemplaza al enlace por correo)
from datetime import datetime, timedelta, timezone  # fechas para hacer vencer un código

from app.database import get_db  # dependencia de la base para leer y cambiar registros en la prueba
from app.logica.recuperacion import vencido  # regla de vencimiento del código
from app.main import app  # app de FastAPI (tiene el override de la base de pruebas)
from app.models import RecuperacionPassword  # tabla de códigos de recuperación

CORREO = "ana@test.com"  # usuaria que crea el fixture auth


def pedir_codigo(client, caplog, email: str = CORREO) -> str:  # pide un código y lo lee de la consola
    caplog.clear()  # olvida mensajes de pedidos anteriores
    caplog.set_level("WARNING")  # el código sale como advertencia cuando no hay SMTP
    respuesta = client.post("/api/auth/password/recover", json={"email": email})  # paso 1: pedir el código
    assert respuesta.status_code == 202  # aceptado
    assert respuesta.json()["minutos"] == 15  # la pantalla puede decir cuánto sirve
    mensaje = next(r.getMessage() for r in caplog.records if "Código de recuperación" in r.getMessage())  # línea del código
    return mensaje.rsplit(": ", 1)[1]  # lo que va después de los dos puntos


def con_la_base(funcion):  # ejecuta algo con la misma sesión de base que usa la app
    db = next(app.dependency_overrides[get_db]())  # abre una sesión de la base en memoria
    try:  # siempre se cierra
        return funcion(db)  # hace el cambio o la consulta
    finally:  # al terminar
        db.close()  # cierra la sesión


def test_codigo_de_4_digitos_cambia_la_contrasena_y_entra(client, auth, caplog):
    codigo = pedir_codigo(client, caplog)
    assert len(codigo) == 4 and codigo.isdigit()  # exactamente 4 números

    # Paso 2: el código correcto se acepta y todavía no se gasta
    assert client.post("/api/auth/password/verify", json={"email": CORREO, "codigo": codigo}).json() == {"valido": True}

    # Paso 3: contraseña nueva; entra directo con la sesión que devuelve
    sesion = client.post("/api/auth/password/reset", json={"email": CORREO, "codigo": codigo, "password": "nueva789"})
    assert sesion.status_code == 200
    assert sesion.json()["user"]["email"] == CORREO

    # Con la contraseña nueva sí entra, con la vieja no
    assert client.post("/api/auth/login", json={"email": CORREO, "password": "nueva789"}).status_code == 200
    assert client.post("/api/auth/login", json={"email": CORREO, "password": "123456"}).status_code == 401

    # El código sirve una sola vez
    otra_vez = client.post("/api/auth/password/reset", json={"email": CORREO, "codigo": codigo, "password": "otra000"})
    assert otra_vez.status_code == 400


def test_codigo_incorrecto_dice_cuantos_intentos_quedan_y_bloquea_al_quinto(client, auth, caplog):
    codigo = pedir_codigo(client, caplog)
    malo = "0000" if codigo != "0000" else "1111"  # un código que seguro es distinto

    mensajes = [
        client.post("/api/auth/password/verify", json={"email": CORREO, "codigo": malo}).json()["detail"]
        for _ in range(5)
    ]
    assert mensajes[0] == "El código no es correcto. Te quedan 4 intentos."
    assert mensajes[3] == "El código no es correcto. Te queda 1 intento."
    assert mensajes[4] == "Escribiste mal el código 5 veces. Pide uno nuevo."

    # Después de 5 errores ni el código correcto sirve
    bloqueado = client.post("/api/auth/password/verify", json={"email": CORREO, "codigo": codigo})
    assert bloqueado.status_code == 400

    # Un código nuevo vuelve a funcionar
    nuevo = pedir_codigo(client, caplog)
    assert client.post("/api/auth/password/verify", json={"email": CORREO, "codigo": nuevo}).status_code == 200


def test_pedir_otro_codigo_anula_el_anterior(client, auth, caplog):
    primero = pedir_codigo(client, caplog)
    segundo = pedir_codigo(client, caplog)
    if primero != segundo:  # (1 en 10 000 veces salen iguales)
        assert client.post("/api/auth/password/verify", json={"email": CORREO, "codigo": primero}).status_code == 400
    assert client.post("/api/auth/password/verify", json={"email": CORREO, "codigo": segundo}).status_code == 200


def test_codigo_vencido_pide_uno_nuevo(client, auth, caplog):
    codigo = pedir_codigo(client, caplog)

    def vencer(db):  # mueve la fecha límite al pasado
        recuperacion = db.query(RecuperacionPassword).one()
        recuperacion.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        db.commit()

    con_la_base(vencer)
    respuesta = client.post("/api/auth/password/verify", json={"email": CORREO, "codigo": codigo})
    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "El código venció. Pide uno nuevo."


def test_un_codigo_recien_creado_en_hora_de_bolivia_no_esta_vencido():
    # PostgreSQL devuelve la hora con la zona de La Paz (-04:00); el enlace viejo la daba por vencida
    la_paz = timezone(timedelta(hours=-4))
    ahora = datetime(2026, 11, 16, 19, 0, tzinfo=timezone.utc)
    expira = (ahora + timedelta(minutes=15)).astimezone(la_paz)  # 15:15 en La Paz
    assert not vencido(expira, ahora)
    assert vencido(expira, ahora + timedelta(minutes=16))
    # Sin zona (SQLite) se toma como UTC
    assert not vencido(expira.astimezone(timezone.utc).replace(tzinfo=None), ahora)


def test_la_base_guarda_el_codigo_cifrado_nunca_en_claro(client, auth, caplog):
    codigo = pedir_codigo(client, caplog)
    guardado = con_la_base(lambda db: db.query(RecuperacionPassword).one().token_hash)
    assert codigo not in guardado
    assert len(guardado) == 64


def test_correo_desconocido_no_revela_nada(client, caplog):
    caplog.set_level("WARNING")
    respuesta = client.post("/api/auth/password/recover", json={"email": "nadie@test.com"})
    assert respuesta.status_code == 202
    assert respuesta.json()["message"] == "Si el correo está registrado, te enviamos un código de 4 dígitos."
    assert not any("Código de recuperación" in r.getMessage() for r in caplog.records)  # no se mandó nada

    falso = client.post("/api/auth/password/verify", json={"email": "nadie@test.com", "codigo": "1234"})
    assert falso.json()["detail"] == "Este código no sirve. Pide uno nuevo."


def test_el_codigo_debe_tener_4_numeros(client, auth):
    for codigo in ["123", "12345", "12a4"]:
        respuesta = client.post("/api/auth/password/verify", json={"email": CORREO, "codigo": codigo})
        assert respuesta.status_code == 422


def test_contrasena_nueva_corta_no_gasta_el_codigo(client, auth, caplog):
    codigo = pedir_codigo(client, caplog)
    corta = client.post("/api/auth/password/reset", json={"email": CORREO, "codigo": codigo, "password": "123"})
    assert corta.status_code == 422
    assert client.post("/api/auth/password/verify", json={"email": CORREO, "codigo": codigo}).status_code == 200


def test_en_la_nube_el_codigo_sale_por_brevo(monkeypatch):
    # Render (plan gratis) bloquea SMTP: con BREVO_API_KEY el correo va por la API web de Brevo
    import json

    from app import correo
    from app.config import get_settings

    monkeypatch.setenv("BREVO_API_KEY", "clave-de-prueba")
    monkeypatch.setenv("SMTP_FROM", "Presupuesto Estudiantil <app@gmail.com>")
    get_settings.cache_clear()
    enviado = {}

    class Respuesta:
        status = 201

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def urlopen_falso(peticion, timeout):
        enviado["url"] = peticion.full_url
        enviado["clave"] = peticion.get_header("Api-key")
        enviado["datos"] = json.loads(peticion.data)
        return Respuesta()

    monkeypatch.setattr(correo, "urlopen", urlopen_falso)
    correo.enviar_codigo_recuperacion("ana@test.com", "0427")

    assert enviado["url"] == "https://api.brevo.com/v3/smtp/email"
    assert enviado["clave"] == "clave-de-prueba"
    assert enviado["datos"]["sender"] == {"name": "Presupuesto Estudiantil", "email": "app@gmail.com"}
    assert enviado["datos"]["to"] == [{"email": "ana@test.com"}]
    assert "0427" in enviado["datos"]["subject"]
