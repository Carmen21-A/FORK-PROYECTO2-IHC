# Tarea 10 · Mis datos y salida honesta
# Regla de Presupuesto Estudiantil: se elimina todo (movimientos, presupuestos y metas);
# antes puede descargar sus movimientos. Después de eliminarla, la cuenta no puede iniciar sesión.
from tests.conftest import mes_de, registrar


def preparar_datos(client, auth, hoy):
    mes = mes_de(hoy)
    assert client.post("/api/movimientos", json={"tipo": "ingreso", "monto": 300, "categoria": "Otros", "descripcion": "Mesada", "fecha": hoy.isoformat()}, headers=auth).status_code == 201
    assert client.post("/api/movimientos", json={"tipo": "gasto", "monto": 40, "categoria": "Transporte", "descripcion": "Pasaje de micro", "fecha": hoy.isoformat()}, headers=auth).status_code == 201
    assert client.put(f"/api/limites/{mes}", json={"limite": 500}, headers=auth).status_code in (200, 201)
    assert client.put(f"/api/presupuestos/{mes}/Transporte", json={"monto": 100}, headers=auth).status_code in (200, 201)
    assert client.post("/api/metas", json={"nombre": "Laptop", "monto_objetivo": 1000, "fecha_limite": hoy.replace(year=hoy.year + 1).isoformat()}, headers=auth).status_code == 201


def test_mis_datos_muestra_todo_lo_que_se_guarda(client, auth, hoy):
    preparar_datos(client, auth, hoy)
    datos = client.get("/api/cuenta/datos", headers=auth).json()

    assert datos["cuenta"]["email"] == "ana@test.com"
    assert "password" not in str(datos).lower()
    assert datos["resumen"] == {
        "movimientos": 2,
        "limites_mensuales": 1,
        "presupuestos_categoria": 1,
        "metas_ahorro": 1,
        "historial": 3,
    }
    descripciones = {m["descripcion"] for m in datos["movimientos"]}
    assert descripciones == {"Mesada", "Pasaje de micro"}
    assert "user_id" not in datos["movimientos"][0]


def test_mis_datos_solo_trae_lo_propio(client, auth, hoy):
    preparar_datos(client, auth, hoy)
    otra = registrar(client, "beto@test.com")
    datos = client.get("/api/cuenta/datos", headers=otra).json()
    assert datos["cuenta"]["email"] == "beto@test.com"
    assert datos["movimientos"] == []
    assert sum(datos["resumen"].values()) == 0


def test_eliminar_sin_confirmar_no_borra_nada(client, auth, hoy):
    preparar_datos(client, auth, hoy)
    respuesta = client.request("DELETE", "/api/cuenta", json={"confirmar": False}, headers=auth)
    assert respuesta.status_code == 422
    assert "confirmarlo" in respuesta.json()["detail"]
    assert client.get("/api/cuenta/datos", headers=auth).json()["resumen"]["movimientos"] == 2


def test_eliminar_cuenta_borra_todo_y_ya_no_puede_entrar(client, auth, hoy):
    preparar_datos(client, auth, hoy)
    otra = registrar(client, "beto@test.com")
    client.post("/api/movimientos", json={"tipo": "gasto", "monto": 10, "categoria": "Comida", "descripcion": "Salteña", "fecha": hoy.isoformat()}, headers=otra)

    respuesta = client.request("DELETE", "/api/cuenta", json={"confirmar": True}, headers=auth)
    assert respuesta.status_code == 200
    assert respuesta.json()["eliminado"] == {
        "movimientos": 2,
        "limites_mensuales": 1,
        "presupuestos_categoria": 1,
        "metas_ahorro": 1,
        "historial": 3,
    }

    # Ya no puede iniciar sesión, y la sesión que tenía abierta deja de servir
    login = client.post("/api/auth/login", json={"email": "ana@test.com", "password": "123456"})
    assert login.status_code == 401
    assert client.get("/api/movimientos", headers=auth).status_code == 401
    assert client.get("/api/cuenta/datos", headers=auth).status_code == 401

    # Las otras cuentas no se tocan
    assert [m["descripcion"] for m in client.get("/api/movimientos", headers=otra).json()] == ["Salteña"]

    # El correo queda libre: puede volver a registrarse y empieza de cero
    nueva = registrar(client, "ana@test.com")
    assert sum(client.get("/api/cuenta/datos", headers=nueva).json()["resumen"].values()) == 0


def test_eliminar_cuenta_registra_el_evento_sin_datos_personales(client, auth, hoy):
    preparar_datos(client, auth, hoy)
    client.request("DELETE", "/api/cuenta", json={"confirmar": True}, headers=auth)

    otra = registrar(client, "beto@test.com")
    panel = client.get("/api/analitica", headers=otra).json()
    assert {"evento": "cuenta_eliminada", "total": 1} in panel["conteos"]
    ultimo = next(e for e in panel["ultimos"] if e["evento"] == "cuenta_eliminada")
    assert ultimo["props"] == {}
    embudo = next(e for e in panel["embudos"] if e["id"] == "eliminar_cuenta")
    assert [p["evento"] for p in embudo["pasos"]] == ["cuenta_eliminacion_iniciada", "cuenta_eliminada"]


def test_eventos_de_la_tarea_10_solo_aceptan_listas_fijas(client, auth):
    assert client.post("/api/eventos", json={"evento": "datos_descargados", "props": {"formato": "csv"}}, headers=auth).status_code == 201
    assert client.post("/api/eventos", json={"evento": "cuenta_eliminacion_frenada", "props": {"motivo": "conservo_la_cuenta"}}, headers=auth).status_code == 201
    # El correo nunca se acepta como propiedad
    assert client.post("/api/eventos", json={"evento": "cuenta_eliminacion_iniciada", "props": {"email": "ana@test.com"}}, headers=auth).status_code == 422
    assert client.post("/api/eventos", json={"evento": "datos_descargados", "props": {"formato": "pdf"}}, headers=auth).status_code == 422


def test_mis_datos_incluye_el_nombre_de_la_cuenta(client):
    respuesta = client.post("/api/auth/register", json={"email": "lucia@test.com", "password": "secreto1", "nombre": "Lucía Pérez"})
    token = respuesta.json()["access_token"]
    datos = client.get("/api/cuenta/datos", headers={"Authorization": f"Bearer {token}"}).json()
    assert datos["cuenta"]["nombre"] == "Lucía Pérez"
