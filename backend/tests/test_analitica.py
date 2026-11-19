# Pruebas de la analítica de interacción (Clase 21)
import pytest

from app.logica.analitica import porcentaje_terminan, validar_evento


def test_validar_evento_acepta_solo_lo_definido():
    validar_evento("movimiento_iniciado", {})
    validar_evento("movimiento_guardado", {"tipo": "gasto", "categoria": "Transporte"})
    with pytest.raises(ValueError, match="desconocido"):
        validar_evento("boton_clic", {})
    with pytest.raises(ValueError, match="no permitidas"):
        validar_evento("movimiento_guardado", {"tipo": "gasto", "categoria": "Comida", "monto": 50})
    with pytest.raises(ValueError, match="no permitidas"):
        validar_evento("movimiento_iniciado", {"email": "ana@gmail.com"})
    with pytest.raises(ValueError, match="categoria"):
        validar_evento("movimiento_guardado", {"tipo": "gasto", "categoria": "taxi a casa de Juan"})


def test_porcentaje_terminan():
    assert porcentaje_terminan(8, 5) == 63
    assert porcentaje_terminan(0, 0) == 0


def test_api_guarda_eventos_y_arma_el_panel(client, auth):
    client.post("/api/eventos", json={"evento": "movimiento_iniciado", "props": {}}, headers=auth)
    client.post("/api/eventos", json={"evento": "movimiento_iniciado", "props": {}}, headers=auth)
    r = client.post(
        "/api/eventos",
        json={"evento": "movimiento_guardado", "props": {"tipo": "gasto", "categoria": "Comida"}},
        headers=auth,
    )
    assert r.status_code == 201

    panel = client.get("/api/analitica", headers=auth).json()
    assert panel["iniciados"] == 2
    assert panel["guardados"] == 1
    assert panel["porcentaje_terminan"] == 50
    assert panel["ultimos"][0]["evento"] == "movimiento_guardado"
    assert panel["ultimos"][0]["props"] == {"tipo": "gasto", "categoria": "Comida"}


def test_api_rechaza_datos_personales(client, auth):
    r = client.post(
        "/api/eventos",
        json={"evento": "movimiento_guardado", "props": {"tipo": "gasto", "categoria": "Comida", "descripcion": "cena"}},
        headers=auth,
    )
    assert r.status_code == 422
    assert client.get("/api/analitica", headers=auth).json()["guardados"] == 0


def test_api_exige_sesion(client):
    assert client.post("/api/eventos", json={"evento": "movimiento_iniciado"}).status_code == 401
    assert client.get("/api/analitica").status_code == 401


# ---------- Tarea 9 · Parte A: analítica en todo el producto ----------
from app.logica.analitica import EVENTOS_PERMITIDOS, FLUJOS, armar_embudos, caida_entre_pasos, mayor_caida


def test_cada_flujo_tiene_sus_eventos_definidos():
    for flujo in FLUJOS:
        for evento in flujo["pasos"] + [flujo["error"]]:
            assert evento in EVENTOS_PERMITIDOS


def test_errores_solo_con_motivo_de_lista_fija():
    validar_evento("movimiento_rechazado", {"motivo": "supera_limite_mensual"})
    validar_evento("fondos_operacion_rechazada", {"operacion": "asignar", "motivo": "fondos_insuficientes"})
    with pytest.raises(ValueError, match="motivo"):
        validar_evento("movimiento_rechazado", {"motivo": "el usuario escribió mal el monto"})
    with pytest.raises(ValueError, match="operacion"):
        validar_evento("fondos_operacion_iniciada", {"operacion": "robar"})


def test_busqueda_no_guarda_el_texto():
    validar_evento("busqueda_sin_resultados", {"con_texto": True, "con_filtros": False})
    with pytest.raises(ValueError, match="no permitidas"):
        validar_evento("busqueda_realizada", {"con_texto": True, "con_filtros": False, "texto": "taxi a casa de Juan"})
    with pytest.raises(ValueError, match="verdadero o falso"):
        validar_evento("busqueda_realizada", {"con_texto": "taxi", "con_filtros": False})


def test_embudos_y_mayor_caida():
    assert caida_entre_pasos(10, 6) == 40
    conteos = {"movimiento_iniciado": 10, "movimiento_guardado": 6, "meta_creacion_iniciada": 4, "meta_creada": 1}
    errores = {("movimiento_rechazado", "monto_vacio"): 3}
    embudos = armar_embudos(conteos, errores)
    registrar = next(e for e in embudos if e["id"] == "registrar")
    assert [p["total"] for p in registrar["pasos"]] == [10, 6]
    assert registrar["pasos"][1]["caida"] == 40
    assert registrar["motivos"] == [{"motivo": "monto_vacio", "total": 3}]
    caida = mayor_caida(embudos)
    assert caida["flujo"] == "Crear meta de ahorro (Tarea 8)"
    assert caida["caida"] == 75


def test_panel_devuelve_embudos(client, auth):
    client.post("/api/eventos", json={"evento": "meta_creacion_iniciada", "props": {}}, headers=auth)
    client.post("/api/eventos", json={"evento": "meta_rechazada", "props": {"motivo": "nombre_vacio"}}, headers=auth)
    client.post("/api/eventos", json={"evento": "busqueda_realizada", "props": {"con_texto": True, "con_filtros": False}}, headers=auth)
    client.post("/api/eventos", json={"evento": "busqueda_sin_resultados", "props": {"con_texto": True, "con_filtros": False}}, headers=auth)
    panel = client.get("/api/analitica", headers=auth).json()
    meta = next(e for e in panel["embudos"] if e["id"] == "meta")
    assert meta["pasos"][0]["total"] == 1
    assert meta["pasos"][1]["caida"] == 100
    assert meta["motivos"] == [{"motivo": "nombre_vacio", "total": 1}]
    assert panel["mayor_caida"]["hasta"] == "meta_creada"
    assert panel["busquedas"] == {"realizadas": 1, "sin_resultados": 1, "porcentaje_sin_resultados": 100}
