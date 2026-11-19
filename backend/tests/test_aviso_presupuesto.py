# Pruebas de la Tarea 9 (Parte B): Aviso antes de superar el presupuesto de la categoría
from app.logica.aviso_presupuesto import calcular_aviso_presupuesto


def test_regla_pura_del_aviso():
    assert calcular_aviso_presupuesto(None, 90, 0, 50) is None
    assert calcular_aviso_presupuesto(100, 40, 0, 60) is None
    aviso = calcular_aviso_presupuesto(100, 40, 0, 80)
    assert aviso == {"presupuesto": 100, "gastado": 40, "monto": 80, "nuevo_total": 120, "exceso": 20}
    assert calcular_aviso_presupuesto(100, 90, 50, 50) is None
    assert calcular_aviso_presupuesto(100, 40, 30, 70)["exceso"] == 10


def _mes(hoy):
    return hoy.strftime("%Y-%m")


def _gasto(monto, hoy, **extra):
    return {"tipo": "gasto", "monto": monto, "categoria": "Transporte", "descripcion": "", "fecha": str(hoy), **extra}


def _preparar(client, auth, hoy):
    client.put(f"/api/presupuestos/{_mes(hoy)}/Transporte", json={"monto": 100}, headers=auth)
    client.post("/api/movimientos", json=_gasto(40, hoy), headers=auth)


def test_gasto_sin_aviso(client, auth, hoy):
    _preparar(client, auth, hoy)
    r = client.post("/api/movimientos", json=_gasto(30, hoy), headers=auth)
    assert r.status_code == 201


def test_gasto_con_aviso_cancelado_no_cambia_nada(client, auth, hoy):
    _preparar(client, auth, hoy)
    r = client.post("/api/movimientos", json=_gasto(80, hoy), headers=auth)
    assert r.status_code == 409
    detalle = r.json()["detail"]
    assert detalle["codigo"] == "supera_presupuesto_categoria"
    assert detalle["exceso"] == 20
    assert detalle["nuevo_total"] == 120
    assert len(client.get("/api/movimientos", headers=auth).json()) == 1


def test_gasto_con_aviso_confirmado_queda_excedido(client, auth, hoy):
    _preparar(client, auth, hoy)
    r = client.post("/api/movimientos", json=_gasto(80, hoy, confirmar_exceso=True), headers=auth)
    assert r.status_code == 201
    total = sum(m["monto"] for m in client.get("/api/movimientos", headers=auth).json())
    assert total == 120


def test_los_ingresos_no_generan_aviso(client, auth, hoy):
    _preparar(client, auth, hoy)
    r = client.post(
        "/api/movimientos",
        json={"tipo": "ingreso", "monto": 500, "categoria": "Transporte", "descripcion": "", "fecha": str(hoy)},
        headers=auth,
    )
    assert r.status_code == 201


def test_editar_un_gasto_tambien_avisa(client, auth, hoy):
    _preparar(client, auth, hoy)
    gasto = client.post("/api/movimientos", json=_gasto(30, hoy), headers=auth).json()
    r = client.put(f"/api/movimientos/{gasto['id']}", json=_gasto(90, hoy), headers=auth)
    assert r.status_code == 409
    assert r.json()["detail"]["exceso"] == 30
    r = client.put(f"/api/movimientos/{gasto['id']}", json=_gasto(90, hoy, confirmar_exceso=True), headers=auth)
    assert r.status_code == 200
