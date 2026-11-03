# Pruebas de la API: mismos flujos que tenia la app Flutter con Supabase
from datetime import date, timedelta

from tests.conftest import mes_de, registrar


def crear(client, auth, **datos):
    cuerpo = {
        "tipo": "gasto",
        "monto": 25.5,
        "categoria": "Comida",
        "descripcion": "Almuerzo",
        "fecha": datos.pop("fecha").isoformat(),
        **datos,
    }
    return client.post("/api/movimientos", json=cuerpo, headers=auth)


# ---------- Tarea 1: acceso ----------
def test_registro_login_y_rutas_privadas(client):
    registrar(client, "luis@test.com", "secreto1")

    repetido = client.post(
        "/api/auth/register", json={"email": "luis@test.com", "password": "secreto1"}
    )
    assert repetido.status_code == 409
    assert "ya esta registrado" in repetido.json()["detail"]

    malo = client.post("/api/auth/login", json={"email": "luis@test.com", "password": "otra123"})
    assert malo.status_code == 401
    assert "credenciales son incorrectas" in malo.json()["detail"]

    bueno = client.post(
        "/api/auth/login", json={"email": "LUIS@test.com", "password": "secreto1"}
    )
    assert bueno.status_code == 200

    # Sin sesion no se puede acceder a los movimientos
    assert client.get("/api/movimientos").status_code == 401


def test_cambiar_password(client, auth):
    assert client.patch("/api/auth/password", json={"password": "nueva123"}, headers=auth).status_code == 204
    login = client.post("/api/auth/login", json={"email": "ana@test.com", "password": "nueva123"})
    assert login.status_code == 200


def test_recuperar_password_con_enlace(client, auth, caplog):
    caplog.set_level("WARNING")
    respuesta = client.post("/api/auth/password/recover", json={"email": "ana@test.com"})
    assert respuesta.status_code == 202

    # Sin SMTP el enlace sale en la consola, con el mismo formato que Supabase
    enlace = next(r.getMessage() for r in caplog.records if "token_hash=" in r.getMessage())
    token = enlace.split("token_hash=")[1].split("&")[0]
    assert "type=recovery" in enlace

    sesion = client.post("/api/auth/password/verify", json={"token_hash": token})
    assert sesion.status_code == 200
    nueva_auth = {"Authorization": f"Bearer {sesion.json()['access_token']}"}
    assert client.patch("/api/auth/password", json={"password": "otra456"}, headers=nueva_auth).status_code == 204

    # El enlace solo sirve una vez
    assert client.post("/api/auth/password/verify", json={"token_hash": token}).status_code == 400


def test_recuperar_password_no_revela_si_el_correo_existe(client):
    assert client.post("/api/auth/password/recover", json={"email": "nadie@test.com"}).status_code == 202


# ---------- Tareas 2 y 3: estados ----------
def test_estado_inicial_y_transiciones(client, auth, hoy):
    movimiento = crear(client, auth, fecha=hoy).json()
    assert movimiento["estado"] == "pendiente"

    url = f"/api/movimientos/{movimiento['id']}/estado"
    assert client.patch(url, json={"estado": "cancelado"}, headers=auth).status_code == 409

    pagado = client.patch(url, json={"estado": "pagado"}, headers=auth).json()
    assert pagado["estado"] == "pagado"
    # Los demas datos se conservan
    assert pagado["monto"] == 25.5
    assert pagado["descripcion"] == "Almuerzo"

    assert client.patch(url, json={"estado": "cancelado"}, headers=auth).status_code == 200
    assert client.patch(url, json={"estado": "pagado"}, headers=auth).status_code == 409


def test_no_se_edita_el_monto_de_un_movimiento_pagado(client, auth, hoy):
    movimiento = crear(client, auth, fecha=hoy).json()
    client.patch(f"/api/movimientos/{movimiento['id']}/estado", json={"estado": "pagado"}, headers=auth)

    cuerpo = {
        "tipo": "gasto",
        "monto": 99,
        "categoria": "Comida",
        "descripcion": "Almuerzo",
        "fecha": hoy.isoformat(),
    }
    url = f"/api/movimientos/{movimiento['id']}"
    assert client.put(url, json=cuerpo, headers=auth).status_code == 409

    # Otros campos si se pueden editar
    cuerpo["monto"] = 25.5
    cuerpo["descripcion"] = "Cena"
    assert client.put(url, json=cuerpo, headers=auth).json()["descripcion"] == "Cena"


def test_otro_usuario_no_ve_ni_toca_mis_movimientos(client, auth, hoy):
    movimiento = crear(client, auth, fecha=hoy).json()
    otro = registrar(client, "otro@test.com")
    assert client.get("/api/movimientos", headers=otro).json() == []
    assert client.delete(f"/api/movimientos/{movimiento['id']}", headers=otro).status_code == 404


# ---------- Tarea 4: busqueda, filtros y limite mensual ----------
def test_busqueda_y_filtros_combinados(client, auth, hoy):
    crear(client, auth, fecha=hoy, descripcion="Almuerzo universidad")
    crear(client, auth, fecha=hoy, categoria="Transporte", descripcion="Pasaje bus", monto=50)
    crear(client, auth, fecha=hoy, tipo="ingreso", categoria="Otros", descripcion="Beca", monto=1000)
    crear(client, auth, fecha=hoy - timedelta(days=40), descripcion="Cena", monto=30)

    def buscar(**params):
        return client.get("/api/movimientos", params=params, headers=auth).json()

    assert [m["descripcion"] for m in buscar(texto="ALMU")] == ["Almuerzo universidad"]
    assert [m["descripcion"] for m in buscar(tipo="ingreso")] == ["Beca"]
    assert buscar(texto="zzzz") == []
    assert len(buscar(tipo="gasto", categoria="Comida")) == 2
    resultado = buscar(texto="pasaje", tipo="gasto", desde=hoy.isoformat(), hasta=hoy.isoformat())
    assert [m["descripcion"] for m in resultado] == ["Pasaje bus"]
    assert client.get("/api/movimientos", params={"tipo": "otro"}, headers=auth).status_code == 422


def test_limite_mensual_bloquea_gastos_que_lo_superan(client, auth, hoy):
    mes = mes_de(hoy)
    assert client.get(f"/api/limites/{mes}", headers=auth).json()["limite"] is None
    assert client.put(f"/api/limites/{mes}", json={"limite": 20}, headers=auth).json()["limite"] == 20

    bloqueado = crear(client, auth, fecha=hoy, monto=25.5)
    assert bloqueado.status_code == 409
    assert "No se puede registrar, porque supera tu límite mensual de 20.0 Bs" in bloqueado.json()["detail"]
    assert client.get("/api/movimientos", headers=auth).json() == []

    # Los ingresos no consumen el limite
    assert crear(client, auth, fecha=hoy, tipo="ingreso", monto=500).status_code == 201
    assert crear(client, auth, fecha=hoy, monto=15).status_code == 201

    # No se puede poner un limite menor a lo ya gastado
    menor = client.put(f"/api/limites/{mes}", json={"limite": 10}, headers=auth)
    assert menor.status_code == 409
    assert "15.0 Bs" in menor.json()["detail"]


def test_editar_no_cuenta_dos_veces_el_monto_anterior(client, auth, hoy):
    client.put(f"/api/limites/{mes_de(hoy)}", json={"limite": 100}, headers=auth)
    movimiento = crear(client, auth, fecha=hoy, monto=80).json()
    cuerpo = {"tipo": "gasto", "monto": 95, "categoria": "Comida", "descripcion": "", "fecha": hoy.isoformat()}
    assert client.put(f"/api/movimientos/{movimiento['id']}", json=cuerpo, headers=auth).status_code == 200


def test_cancelados_no_cuentan_para_el_limite(client, auth, hoy):
    client.put(f"/api/limites/{mes_de(hoy)}", json={"limite": 100}, headers=auth)
    movimiento = crear(client, auth, fecha=hoy, monto=90).json()
    url = f"/api/movimientos/{movimiento['id']}/estado"
    client.patch(url, json={"estado": "pagado"}, headers=auth)
    client.patch(url, json={"estado": "cancelado"}, headers=auth)
    assert crear(client, auth, fecha=hoy, monto=90).status_code == 201


# ---------- Historial ----------
def test_historial_registra_cada_accion_reciente_primero(client, auth, hoy):
    movimiento = crear(client, auth, fecha=hoy, monto=50, descripcion="Almuerzo").json()
    client.patch(f"/api/movimientos/{movimiento['id']}/estado", json={"estado": "pagado"}, headers=auth)
    client.delete(f"/api/movimientos/{movimiento['id']}", headers=auth)

    eventos = client.get("/api/historial", headers=auth).json()
    assert [e["accion"] for e in eventos] == ["eliminado", "cambio_estado", "creado"]
    assert eventos[2]["detalle"] == "Gasto 50.0 Bs · Comida · Almuerzo"
    assert eventos[1]["detalle"] == "Estado cambiado a pagado"
    # El evento conserva el id aunque el movimiento ya no exista
    assert eventos[0]["movimiento_id"] == movimiento["id"]


# ---------- Tarea 5: presupuesto por categoria ----------
def test_presupuesto_por_categoria_crud(client, auth):
    url = "/api/presupuestos/2026-10"
    assert client.get(url, headers=auth).json() == []

    assert client.put(f"{url}/Comida", json={"monto": 400}, headers=auth).status_code == 200
    assert client.put(f"{url}/Comida", json={"monto": 450.5}, headers=auth).json()["monto"] == 450.5
    client.put(f"{url}/Transporte", json={"monto": 150}, headers=auth)

    presupuestos = {p["categoria"]: p["monto"] for p in client.get(url, headers=auth).json()}
    assert presupuestos == {"Comida": 450.5, "Transporte": 150}

    assert client.delete(f"{url}/Comida", headers=auth).status_code == 204
    assert [p["categoria"] for p in client.get(url, headers=auth).json()] == ["Transporte"]

    # Otro mes no se mezcla
    assert client.get("/api/presupuestos/2026-11", headers=auth).json() == []


def test_presupuesto_valida_monto_categoria_y_mes(client, auth):
    assert client.put("/api/presupuestos/2026-10/Comida", json={"monto": 0}, headers=auth).status_code == 422
    assert client.put("/api/presupuestos/2026-10/Ropa", json={"monto": 10}, headers=auth).status_code == 422
    assert client.put("/api/presupuestos/2026-13/Comida", json={"monto": 10}, headers=auth).status_code == 422


# ---------- Tarea 6: gastos recurrentes ----------
def test_pagar_un_gasto_recurrente_genera_el_siguiente(client, auth):
    fecha = date(2026, 11, 3)
    gasto = crear(client, auth, fecha=fecha, monto=30, recurrencia="semanal").json()
    assert gasto["recurrencia"] == "semanal"

    respuesta = client.patch(
        f"/api/movimientos/{gasto['id']}/estado", json={"estado": "pagado"}, headers=auth
    ).json()

    assert respuesta["estado"] == "pagado"
    siguiente = respuesta["siguiente"]
    assert siguiente["fecha"] == "2026-11-10"
    assert siguiente["estado"] == "pendiente"
    assert siguiente["recurrencia"] == "semanal"
    assert siguiente["monto"] == 30
    assert len(client.get("/api/movimientos", headers=auth).json()) == 2


def test_un_gasto_que_no_se_repite_no_genera_nada(client, auth):
    gasto = crear(client, auth, fecha=date(2026, 11, 3)).json()
    respuesta = client.patch(
        f"/api/movimientos/{gasto['id']}/estado", json={"estado": "pagado"}, headers=auth
    ).json()

    assert respuesta["siguiente"] is None
    assert len(client.get("/api/movimientos", headers=auth).json()) == 1


def test_un_ingreso_no_se_guarda_como_recurrente(client, auth):
    ingreso = crear(client, auth, fecha=date(2026, 11, 3), tipo="ingreso", recurrencia="mensual")
    assert ingreso.json()["recurrencia"] is None


def test_si_el_siguiente_supera_el_limite_no_se_genera_y_avisa(client, auth):
    client.put("/api/limites/2026-11", json={"limite": 100}, headers=auth)
    gasto = crear(client, auth, fecha=date(2026, 11, 3), monto=60, recurrencia="semanal").json()

    respuesta = client.patch(
        f"/api/movimientos/{gasto['id']}/estado", json={"estado": "pagado"}, headers=auth
    ).json()

    assert respuesta["siguiente"] is None
    assert "supera tu límite" in respuesta["aviso"]
    assert len(client.get("/api/movimientos", headers=auth).json()) == 1
