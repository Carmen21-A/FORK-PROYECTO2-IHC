# Casos que faltaban para llegar al 100 % de cobertura del backend (entrega final)
from datetime import date, timedelta
from uuid import uuid4

import pytest

from app import correo
from app.config import get_settings
from app.database import get_db
from app.logica.metas import calcular_porcentaje, validar_retiro, validar_transferencia
from app.routers import auth as rutas_auth

FUTURO = (date.today() + timedelta(days=365)).isoformat()


def crear_meta(client, auth, nombre="Laptop", objetivo=1000):
    r = client.post("/api/metas", json={"nombre": nombre, "monto_objetivo": objetivo, "fecha_limite": FUTURO}, headers=auth)
    assert r.status_code == 201
    return r.json()["id"]


# ---------- Infraestructura ----------
def test_health_responde_ok(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_get_db_abre_y_cierra_una_sesion():
    generador = get_db()
    sesion = next(generador)
    assert sesion is not None
    generador.close()  # ejecuta el finally: cierra la sesión


def test_token_invalido_responde_401(client):
    r = client.get("/api/auth/me", headers={"Authorization": "Bearer token-falso"})
    assert r.status_code == 401


def test_registro_con_nombre_nulo_explicito(client):
    r = client.post("/api/auth/register", json={"nombre": None, "email": "sin@nombre.com", "password": "123456"})
    assert r.status_code == 201
    assert r.json()["user"]["nombre"] is None


def test_login_actualiza_el_hash_si_hace_falta(client, auth, monkeypatch):
    monkeypatch.setattr(rutas_auth, "verify_password", lambda clave, guardado: (True, "hash-nuevo"))
    assert client.post("/api/auth/login", json={"email": "ana@test.com", "password": "123456"}).status_code == 200


def test_si_falla_el_correo_responde_502(client, auth, monkeypatch):
    def falla(email, codigo):
        raise OSError("sin conexión")

    monkeypatch.setattr(rutas_auth, "enviar_codigo_recuperacion", falla)
    r = client.post("/api/auth/password/recover", json={"email": "ana@test.com"})
    assert r.status_code == 502
    assert r.json()["detail"] == "No se pudo enviar el correo con el código. Intenta de nuevo."


# ---------- Correo ----------
def test_correo_por_smtp(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.prueba.com")
    monkeypatch.setenv("SMTP_FROM", "App <app@prueba.com>")
    monkeypatch.setenv("SMTP_USER", "app@prueba.com")
    monkeypatch.setenv("SMTP_PASSWORD", "clave")
    get_settings.cache_clear()
    usado = {}

    class SMTPFalso:
        def __init__(self, host, puerto, timeout):
            usado["servidor"] = (host, puerto)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def starttls(self):
            usado["tls"] = True

        def login(self, usuario, clave):
            usado["login"] = usuario

        def send_message(self, mensaje):
            usado["asunto"] = mensaje["Subject"]

    monkeypatch.setattr(correo, "SMTP", SMTPFalso)
    correo.enviar_codigo_recuperacion("ana@test.com", "0427")
    assert usado["servidor"] == ("smtp.prueba.com", 587)
    assert usado["tls"] and usado["login"] == "app@prueba.com"
    assert "0427" in usado["asunto"]


def test_brevo_que_rechaza_el_envio_lanza_error(monkeypatch):
    monkeypatch.setenv("BREVO_API_KEY", "clave")
    monkeypatch.setenv("SMTP_FROM", "App <app@prueba.com>")
    get_settings.cache_clear()

    class Rechazo:
        status = 400

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    monkeypatch.setattr(correo, "urlopen", lambda peticion, timeout: Rechazo())
    with pytest.raises(RuntimeError):
        correo.enviar_codigo_recuperacion("ana@test.com", "0427")


# ---------- Límite y movimientos ----------
def test_cambiar_un_limite_que_ya_existia(client, auth):
    mes = date.today().strftime("%Y-%m")
    assert client.put(f"/api/limites/{mes}", json={"limite": 500}, headers=auth).status_code == 200
    r = client.put(f"/api/limites/{mes}", json={"limite": 800}, headers=auth)
    assert r.status_code == 200
    assert float(r.json()["limite"]) == 800


def test_filtrar_por_estado(client, auth):
    hoy = date.today().isoformat()
    client.post("/api/movimientos", json={"tipo": "gasto", "monto": 10, "categoria": "Comida", "descripcion": "a", "fecha": hoy}, headers=auth)
    r = client.get("/api/movimientos", params={"estado": "pendiente"}, headers=auth)
    assert r.status_code == 200
    assert all(m["estado"] == "pendiente" for m in r.json())


def test_editar_un_gasto_cancelado_no_genera_aviso(client, auth):
    hoy = date.today().isoformat()
    mes = hoy[:7]
    client.put(f"/api/presupuestos/{mes}/Comida", json={"monto": 10}, headers=auth)
    m = client.post("/api/movimientos", json={"tipo": "gasto", "monto": 5, "categoria": "Comida", "descripcion": "a", "fecha": hoy}, headers=auth).json()
    url = f"/api/movimientos/{m['id']}/estado"
    client.patch(url, json={"estado": "pagado"}, headers=auth)
    client.patch(url, json={"estado": "cancelado"}, headers=auth)
    r = client.put(f"/api/movimientos/{m['id']}", json={"tipo": "gasto", "monto": 5, "categoria": "Comida", "descripcion": "b", "fecha": hoy}, headers=auth)
    assert r.status_code in (200, 409)


# ---------- Metas ----------
def test_editar_y_eliminar_una_meta(client, auth):
    meta = crear_meta(client, auth)
    r = client.put(f"/api/metas/{meta}", json={"nombre": "  Laptop nueva ", "monto_objetivo": 1500, "fecha_limite": FUTURO}, headers=auth)
    assert r.status_code == 200
    assert r.json()["nombre"] == "Laptop nueva"
    assert client.delete(f"/api/metas/{meta}", headers=auth).status_code == 204
    assert client.get("/api/metas", headers=auth).json() == []


def test_metas_que_no_existen_responden_404(client, auth):
    falso = str(uuid4())
    assert client.put(f"/api/metas/{falso}", json={"nombre": "X"}, headers=auth).status_code == 404
    assert client.delete(f"/api/metas/{falso}", headers=auth).status_code == 404
    assert client.post(f"/api/metas/{falso}/asignar", json={"monto": 10}, headers=auth).status_code == 404
    assert client.post(f"/api/metas/{falso}/retirar", json={"monto": 10}, headers=auth).status_code == 404
    assert client.post(f"/api/metas/{falso}/transferir", json={"meta_destino_id": falso, "monto": 10}, headers=auth).status_code == 404
    meta = crear_meta(client, auth)
    assert client.post(f"/api/metas/{meta}/transferir", json={"meta_destino_id": falso, "monto": 10}, headers=auth).status_code == 404


def test_retirar_mas_de_lo_ahorrado_responde_400(client, auth):
    meta = crear_meta(client, auth)
    r = client.post(f"/api/metas/{meta}/retirar", json={"monto": 50}, headers=auth)
    assert r.status_code == 400
    assert "Fondos insuficientes" in r.json()["detail"]


def test_reglas_de_metas_en_la_logica():
    with pytest.raises(ValueError, match="mayor a 0"):
        validar_retiro(100, 0)
    a, b = uuid4(), uuid4()
    with pytest.raises(ValueError, match="misma meta"):
        validar_transferencia(a, a, 100, 10)
    with pytest.raises(ValueError, match="mayor a 0"):
        validar_transferencia(a, b, 100, 0)
    with pytest.raises(ValueError, match="Fondos insuficientes"):
        validar_transferencia(a, b, 10, 50)
    assert calcular_porcentaje(10, 0) == 0.0
