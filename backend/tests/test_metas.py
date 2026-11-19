# Pruebas de Metas de Ahorro y Fondos Disponibles (Tarea 8)
from datetime import date, timedelta
from decimal import Decimal
import pytest
from app.logica.metas import (
    calcular_porcentaje,
    calcular_saldo_disponible,
    validar_asignacion,
    validar_retiro,
    validar_transferencia,
)


def test_logica_calculo_saldo_disponible():
    saldo_total, disponible = calcular_saldo_disponible(1000, 300, 200)
    assert saldo_total == Decimal("700")
    assert disponible == Decimal("500")


def test_logica_validaciones_monto():
    # Asignación
    validar_asignacion(Decimal("500"), Decimal("200"))
    with pytest.raises(ValueError, match="Fondos insuficientes"):
        validar_asignacion(Decimal("100"), Decimal("200"))
    with pytest.raises(ValueError, match="mayor a 0"):
        validar_asignacion(Decimal("500"), Decimal("0"))

    # Retiro
    validar_retiro(Decimal("300"), Decimal("150"))
    with pytest.raises(ValueError, match="Fondos insuficientes en la meta"):
        validar_retiro(Decimal("100"), Decimal("150"))

    # Porcentaje
    assert calcular_porcentaje(50, 200) == 25.0
    assert calcular_porcentaje(200, 200) == 100.0


def test_flujo_completo_api_metas(client, auth, hoy):
    # 1. Registrar un ingreso de 1000 Bs (pagado) y un gasto de 200 Bs (pagado)
    r_ingreso = client.post(
        "/api/movimientos",
        json={"tipo": "ingreso", "monto": 1000, "categoria": "Otros", "descripcion": "Sueldo", "fecha": str(hoy)},
        headers=auth,
    )
    ingreso_id = r_ingreso.json()["id"]
    client.patch(f"/api/movimientos/{ingreso_id}/estado", json={"estado": "pagado"}, headers=auth)

    r_gasto = client.post(
        "/api/movimientos",
        json={"tipo": "gasto", "monto": 200, "categoria": "Comida", "descripcion": "Supermercado", "fecha": str(hoy)},
        headers=auth,
    )
    gasto_id = r_gasto.json()["id"]
    client.patch(f"/api/movimientos/{gasto_id}/estado", json={"estado": "pagado"}, headers=auth)

    # Resumen inicial: saldo_total=800, fondos_reservados=0, saldo_disponible=800
    res = client.get("/api/metas/resumen-fondos", headers=auth).json()
    assert res["saldo_total"] == 800.0
    assert res["fondos_reservados"] == 0.0
    assert res["saldo_disponible"] == 800.0

    # 2. Crear dos metas de ahorro
    fecha_futura = str(hoy + timedelta(days=60))  # fecha límite dentro de 60 días
    r_meta1 = client.post(
        "/api/metas",
        json={"nombre": "Laptop", "monto_objetivo": 2000, "fecha_limite": fecha_futura},
        headers=auth,
    )
    assert r_meta1.status_code == 201
    meta1_id = r_meta1.json()["id"]

    r_meta2 = client.post(
        "/api/metas",
        json={"nombre": "Viaje", "monto_objetivo": 1500, "fecha_limite": fecha_futura},
        headers=auth,
    )
    assert r_meta2.status_code == 201
    meta2_id = r_meta2.json()["id"]

    # 3. Asignar 300 Bs a Meta 1
    r_asig = client.post(f"/api/metas/{meta1_id}/asignar", json={"monto": 300}, headers=auth)
    assert r_asig.status_code == 200
    assert r_asig.json()["monto_ahorrado"] == 300.0

    res = client.get("/api/metas/resumen-fondos", headers=auth).json()
    assert res["fondos_reservados"] == 300.0
    assert res["saldo_disponible"] == 500.0
    assert res["saldo_total"] == 800.0

    # 4. Intento de asignar más del saldo disponible (600 Bs con 500 disponibles) -> debe fallar
    r_fallo = client.post(f"/api/metas/{meta1_id}/asignar", json={"monto": 600}, headers=auth)
    assert r_fallo.status_code == 400
    assert "Fondos insuficientes" in r_fallo.json()["detail"]

    # 5. Transferir 100 Bs de Meta 1 a Meta 2
    r_trans = client.post(
        f"/api/metas/{meta1_id}/transferir",
        json={"meta_destino_id": meta2_id, "monto": 100},
        headers=auth,
    )
    assert r_trans.status_code == 200
    assert r_trans.json()["monto_ahorrado"] == 200.0

    metas = client.get("/api/metas", headers=auth).json()
    meta2 = next(m for m in metas if m["id"] == meta2_id)
    assert meta2["monto_ahorrado"] == 100.0

    # 6. Intento de transferir más de lo que tiene Meta 1 (500 Bs con 200) -> debe fallar
    r_trans_fallo = client.post(
        f"/api/metas/{meta1_id}/transferir",
        json={"meta_destino_id": meta2_id, "monto": 500},
        headers=auth,
    )
    assert r_trans_fallo.status_code == 400
    assert "Fondos insuficientes" in r_trans_fallo.json()["detail"]

    # 7. Retirar 50 Bs de Meta 2 hacia el saldo disponible
    r_ret = client.post(f"/api/metas/{meta2_id}/retirar", json={"monto": 50}, headers=auth)
    assert r_ret.status_code == 200
    assert r_ret.json()["monto_ahorrado"] == 50.0

    # Fondos reservados: 200 (Meta 1) + 50 (Meta 2) = 250 Bs. Disponible: 800 - 250 = 550 Bs
    res = client.get("/api/metas/resumen-fondos", headers=auth).json()
    assert res["fondos_reservados"] == 250.0
    assert res["saldo_disponible"] == 550.0
    assert res["saldo_total"] == 800.0

    # 8. Las operaciones con metas NO generan movimientos ficticios
    movimientos = client.get("/api/movimientos", headers=auth).json()
    assert len(movimientos) == 2


def test_logica_reservas_intactas():
    from app.logica.metas import validar_reservas_intactas

    # Sin metas: se conservan las reglas previas (no se bloquea aunque el saldo quede negativo)
    validar_reservas_intactas(Decimal("10"), Decimal("-30"), Decimal("0"))
    # Con metas, si el disponible sigue en positivo, se permite
    validar_reservas_intactas(Decimal("100"), Decimal("60"), Decimal("200"))
    # Con metas, si la operación deja el disponible negativo, se rechaza
    with pytest.raises(ValueError, match="reservados en tus metas"):
        validar_reservas_intactas(Decimal("20"), Decimal("-20"), Decimal("280"))
    # Una operación que mejora el saldo nunca se bloquea
    validar_reservas_intactas(Decimal("-50"), Decimal("-10"), Decimal("100"))


def _preparar_meta_con_reserva(client, auth, hoy):
    # Ingreso pagado de 300 Bs y una meta con 280 Bs reservados: quedan 20 Bs disponibles
    r = client.post(
        "/api/movimientos",
        json={"tipo": "ingreso", "monto": 300, "categoria": "Otros", "descripcion": "Mesada", "fecha": str(hoy)},
        headers=auth,
    )
    ingreso_id = r.json()["id"]
    client.patch(f"/api/movimientos/{ingreso_id}/estado", json={"estado": "pagado"}, headers=auth)
    meta = client.post(
        "/api/metas",
        json={"nombre": "Matrícula", "monto_objetivo": 500, "fecha_limite": str(hoy + timedelta(days=30))},  # datos de la meta
        headers=auth,
    ).json()
    assert client.post(f"/api/metas/{meta['id']}/asignar", json={"monto": 280}, headers=auth).status_code == 200
    return ingreso_id


def test_no_se_puede_pagar_un_gasto_con_dinero_reservado(client, auth, hoy):
    _preparar_meta_con_reserva(client, auth, hoy)

    gasto = client.post(
        "/api/movimientos",
        json={"tipo": "gasto", "monto": 40, "categoria": "Transporte", "descripcion": "Pasaje", "fecha": str(hoy)},
        headers=auth,
    ).json()
    r = client.patch(f"/api/movimientos/{gasto['id']}/estado", json={"estado": "pagado"}, headers=auth)
    assert r.status_code == 409
    assert "reservados en tus metas" in r.json()["detail"]

    # El gasto sigue pendiente y el disponible no cambió
    movs = client.get("/api/movimientos", headers=auth).json()
    assert next(m for m in movs if m["id"] == gasto["id"])["estado"] == "pendiente"
    res = client.get("/api/metas/resumen-fondos", headers=auth).json()
    assert res["saldo_disponible"] == 20.0
    assert res["fondos_reservados"] == 280.0

    # Un gasto que sí cabe en el disponible se paga normalmente
    chico = client.post(
        "/api/movimientos",
        json={"tipo": "gasto", "monto": 15, "categoria": "Comida", "descripcion": "Salteña", "fecha": str(hoy)},
        headers=auth,
    ).json()
    r = client.patch(f"/api/movimientos/{chico['id']}/estado", json={"estado": "pagado"}, headers=auth)
    assert r.status_code == 200


def test_no_se_puede_eliminar_el_ingreso_que_respalda_las_metas(client, auth, hoy):
    ingreso_id = _preparar_meta_con_reserva(client, auth, hoy)

    r = client.delete(f"/api/movimientos/{ingreso_id}", headers=auth)
    assert r.status_code == 409
    assert len(client.get("/api/movimientos", headers=auth).json()) == 1
