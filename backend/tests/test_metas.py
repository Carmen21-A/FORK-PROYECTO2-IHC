# Pruebas de Metas de Ahorro y Fondos Disponibles (Tarea 8)
from datetime import date, timedelta  # importa date y timedelta para armar fechas límite futuras
from decimal import Decimal  # importa Decimal para comparar montos exactos
import pytest  # importa pytest para verificar que se lancen errores
from app.logica.metas import (  # importa las reglas de negocio puras de metas
    calcular_porcentaje,  # porcentaje de avance de una meta
    calcular_saldo_disponible,  # saldo total y saldo disponible
    validar_asignacion,  # validación al asignar fondos
    validar_retiro,  # validación al retirar fondos
    validar_transferencia,  # validación al transferir entre metas
)  # fin de importaciones


def test_logica_calculo_saldo_disponible():  # prueba la fórmula disponible = ingresos - gastos - reservados
    saldo_total, disponible = calcular_saldo_disponible(1000, 300, 200)  # 1000 de ingresos, 300 de gastos, 200 reservados
    assert saldo_total == Decimal("700")  # el saldo total debe ser 1000 - 300
    assert disponible == Decimal("500")  # el disponible debe ser 700 - 200


def test_logica_validaciones_monto():  # prueba las validaciones de asignar, retirar y el porcentaje
    # Asignación
    validar_asignacion(Decimal("500"), Decimal("200"))  # asignar 200 con 500 disponibles es válido
    with pytest.raises(ValueError, match="Fondos insuficientes"):  # espera un error por falta de fondos
        validar_asignacion(Decimal("100"), Decimal("200"))  # asignar 200 con solo 100 disponibles
    with pytest.raises(ValueError, match="mayor a 0"):  # espera un error por monto inválido
        validar_asignacion(Decimal("500"), Decimal("0"))  # asignar 0 Bs

    # Retiro
    validar_retiro(Decimal("300"), Decimal("150"))  # retirar 150 de una meta con 300 es válido
    with pytest.raises(ValueError, match="Fondos insuficientes en la meta"):  # espera un error por falta de fondos en la meta
        validar_retiro(Decimal("100"), Decimal("150"))  # retirar 150 de una meta con solo 100

    # Porcentaje
    assert calcular_porcentaje(50, 200) == 25.0  # 50 de 200 es 25 %
    assert calcular_porcentaje(200, 200) == 100.0  # 200 de 200 es 100 %


def test_flujo_completo_api_metas(client, auth, hoy):  # prueba el recorrido completo a través de la API
    # 1. Registrar un ingreso de 1000 Bs (pagado) y un gasto de 200 Bs (pagado)
    r_ingreso = client.post(  # crea el ingreso
        "/api/movimientos",  # endpoint de movimientos
        json={"tipo": "ingreso", "monto": 1000, "categoria": "Otros", "descripcion": "Sueldo", "fecha": str(hoy)},  # datos del ingreso
        headers=auth,  # token del usuario de prueba
    )  # fin del post
    ingreso_id = r_ingreso.json()["id"]  # guarda el id del ingreso
    client.patch(f"/api/movimientos/{ingreso_id}/estado", json={"estado": "pagado"}, headers=auth)  # marca el ingreso como pagado

    r_gasto = client.post(  # crea el gasto
        "/api/movimientos",  # endpoint de movimientos
        json={"tipo": "gasto", "monto": 200, "categoria": "Comida", "descripcion": "Supermercado", "fecha": str(hoy)},  # datos del gasto
        headers=auth,  # token del usuario
    )  # fin del post
    gasto_id = r_gasto.json()["id"]  # guarda el id del gasto
    client.patch(f"/api/movimientos/{gasto_id}/estado", json={"estado": "pagado"}, headers=auth)  # marca el gasto como pagado

    # Resumen inicial: saldo_total=800, fondos_reservados=0, saldo_disponible=800
    res = client.get("/api/metas/resumen-fondos", headers=auth).json()  # consulta el resumen de fondos
    assert res["saldo_total"] == 800.0  # 1000 - 200
    assert res["fondos_reservados"] == 0.0  # todavía no hay metas
    assert res["saldo_disponible"] == 800.0  # todo el saldo está libre

    # 2. Crear dos metas de ahorro
    fecha_futura = str(hoy + timedelta(days=60))  # fecha límite dentro de 60 días
    r_meta1 = client.post(  # crea la primera meta
        "/api/metas",  # endpoint de metas
        json={"nombre": "Laptop", "monto_objetivo": 2000, "fecha_limite": fecha_futura},  # datos de la meta
        headers=auth,  # token del usuario
    )  # fin del post
    assert r_meta1.status_code == 201  # debe responder 201 (creada)
    meta1_id = r_meta1.json()["id"]  # guarda el id de la meta 1

    r_meta2 = client.post(  # crea la segunda meta
        "/api/metas",  # endpoint de metas
        json={"nombre": "Viaje", "monto_objetivo": 1500, "fecha_limite": fecha_futura},  # datos de la meta
        headers=auth,  # token del usuario
    )  # fin del post
    assert r_meta2.status_code == 201  # debe responder 201 (creada)
    meta2_id = r_meta2.json()["id"]  # guarda el id de la meta 2

    # 3. Asignar 300 Bs a Meta 1
    r_asig = client.post(f"/api/metas/{meta1_id}/asignar", json={"monto": 300}, headers=auth)  # asigna 300 Bs
    assert r_asig.status_code == 200  # la asignación es aceptada
    assert r_asig.json()["monto_ahorrado"] == 300.0  # la meta 1 queda con 300 Bs

    res = client.get("/api/metas/resumen-fondos", headers=auth).json()  # vuelve a consultar el resumen
    assert res["fondos_reservados"] == 300.0  # ahora hay 300 Bs reservados
    assert res["saldo_disponible"] == 500.0  # el disponible bajó a 800 - 300
    assert res["saldo_total"] == 800.0  # el saldo total se conserva

    # 4. Intento de asignar más del saldo disponible (600 Bs con 500 disponibles) -> debe fallar
    r_fallo = client.post(f"/api/metas/{meta1_id}/asignar", json={"monto": 600}, headers=auth)  # intenta asignar 600 Bs
    assert r_fallo.status_code == 400  # debe ser rechazado
    assert "Fondos insuficientes" in r_fallo.json()["detail"]  # con el mensaje de fondos insuficientes

    # 5. Transferir 100 Bs de Meta 1 a Meta 2
    r_trans = client.post(  # hace la transferencia
        f"/api/metas/{meta1_id}/transferir",  # desde la meta 1
        json={"meta_destino_id": meta2_id, "monto": 100},  # hacia la meta 2, 100 Bs
        headers=auth,  # token del usuario
    )  # fin del post
    assert r_trans.status_code == 200  # la transferencia es aceptada
    assert r_trans.json()["monto_ahorrado"] == 200.0  # la meta 1 queda en 200

    metas = client.get("/api/metas", headers=auth).json()  # lista todas las metas
    meta2 = next(m for m in metas if m["id"] == meta2_id)  # busca la meta 2 en la lista
    assert meta2["monto_ahorrado"] == 100.0  # la meta 2 subió a 100

    # 6. Intento de transferir más de lo que tiene Meta 1 (500 Bs con 200) -> debe fallar
    r_trans_fallo = client.post(  # intenta transferir de más
        f"/api/metas/{meta1_id}/transferir",  # desde la meta 1
        json={"meta_destino_id": meta2_id, "monto": 500},  # 500 Bs hacia la meta 2
        headers=auth,  # token del usuario
    )  # fin del post
    assert r_trans_fallo.status_code == 400  # debe ser rechazado
    assert "Fondos insuficientes" in r_trans_fallo.json()["detail"]  # con el mensaje de fondos insuficientes

    # 7. Retirar 50 Bs de Meta 2 hacia el saldo disponible
    r_ret = client.post(f"/api/metas/{meta2_id}/retirar", json={"monto": 50}, headers=auth)  # retira 50 Bs
    assert r_ret.status_code == 200  # el retiro es aceptado
    assert r_ret.json()["monto_ahorrado"] == 50.0  # la meta 2 queda en 50

    # Fondos reservados: 200 (Meta 1) + 50 (Meta 2) = 250 Bs. Disponible: 800 - 250 = 550 Bs
    res = client.get("/api/metas/resumen-fondos", headers=auth).json()  # consulta el resumen final
    assert res["fondos_reservados"] == 250.0  # 200 + 50
    assert res["saldo_disponible"] == 550.0  # 800 - 250
    assert res["saldo_total"] == 800.0  # el saldo total se conserva

    # 8. Las operaciones con metas NO generan movimientos ficticios
    movimientos = client.get("/api/movimientos", headers=auth).json()  # lista los movimientos
    assert len(movimientos) == 2  # solo siguen el ingreso y el gasto originales


def test_logica_reservas_intactas():  # prueba la regla que protege el dinero reservado en metas
    from app.logica.metas import validar_reservas_intactas  # importa la regla a probar

    # Sin metas: se conservan las reglas previas (no se bloquea aunque el saldo quede negativo)
    validar_reservas_intactas(Decimal("10"), Decimal("-30"), Decimal("0"))  # no lanza error
    # Con metas, si el disponible sigue en positivo, se permite
    validar_reservas_intactas(Decimal("100"), Decimal("60"), Decimal("200"))  # no lanza error
    # Con metas, si la operación deja el disponible negativo, se rechaza
    with pytest.raises(ValueError, match="reservados en tus metas"):  # espera el error de dinero reservado
        validar_reservas_intactas(Decimal("20"), Decimal("-20"), Decimal("280"))  # de 20 libres pasaría a -20
    # Una operación que mejora el saldo nunca se bloquea
    validar_reservas_intactas(Decimal("-50"), Decimal("-10"), Decimal("100"))  # no lanza error


def _preparar_meta_con_reserva(client, auth, hoy):  # función auxiliar: deja 280 Bs reservados y 20 Bs disponibles
    # Ingreso pagado de 300 Bs y una meta con 280 Bs reservados: quedan 20 Bs disponibles
    r = client.post(  # crea el ingreso
        "/api/movimientos",  # endpoint de movimientos
        json={"tipo": "ingreso", "monto": 300, "categoria": "Otros", "descripcion": "Mesada", "fecha": str(hoy)},  # ingreso de 300 Bs
        headers=auth,  # token del usuario
    )  # fin del post
    ingreso_id = r.json()["id"]  # guarda el id del ingreso
    client.patch(f"/api/movimientos/{ingreso_id}/estado", json={"estado": "pagado"}, headers=auth)  # lo marca como pagado
    meta = client.post(  # crea la meta
        "/api/metas",  # endpoint de metas
        json={"nombre": "Matrícula", "monto_objetivo": 500, "fecha_limite": str(hoy + timedelta(days=30))},  # datos de la meta
        headers=auth,  # token del usuario
    ).json()  # obtiene la meta creada
    assert client.post(f"/api/metas/{meta['id']}/asignar", json={"monto": 280}, headers=auth).status_code == 200  # reserva 280 Bs
    return ingreso_id  # devuelve el id del ingreso para otras pruebas


def test_no_se_puede_pagar_un_gasto_con_dinero_reservado(client, auth, hoy):  # pagar un gasto no puede usar dinero de metas
    _preparar_meta_con_reserva(client, auth, hoy)  # deja 280 reservados y 20 disponibles

    gasto = client.post(  # crea un gasto pendiente de 40 Bs
        "/api/movimientos",  # endpoint de movimientos
        json={"tipo": "gasto", "monto": 40, "categoria": "Transporte", "descripcion": "Pasaje", "fecha": str(hoy)},  # datos del gasto
        headers=auth,  # token del usuario
    ).json()  # obtiene el gasto creado
    r = client.patch(f"/api/movimientos/{gasto['id']}/estado", json={"estado": "pagado"}, headers=auth)  # intenta pagarlo
    assert r.status_code == 409  # debe ser rechazado
    assert "reservados en tus metas" in r.json()["detail"]  # con el mensaje de dinero reservado

    # El gasto sigue pendiente y el disponible no cambió
    movs = client.get("/api/movimientos", headers=auth).json()  # lista los movimientos
    assert next(m for m in movs if m["id"] == gasto["id"])["estado"] == "pendiente"  # el gasto sigue pendiente
    res = client.get("/api/metas/resumen-fondos", headers=auth).json()  # consulta el resumen
    assert res["saldo_disponible"] == 20.0  # el disponible sigue en 20
    assert res["fondos_reservados"] == 280.0  # la meta conserva sus 280

    # Un gasto que sí cabe en el disponible se paga normalmente
    chico = client.post(  # crea un gasto de 15 Bs
        "/api/movimientos",  # endpoint de movimientos
        json={"tipo": "gasto", "monto": 15, "categoria": "Comida", "descripcion": "Salteña", "fecha": str(hoy)},  # datos del gasto
        headers=auth,  # token del usuario
    ).json()  # obtiene el gasto creado
    r = client.patch(f"/api/movimientos/{chico['id']}/estado", json={"estado": "pagado"}, headers=auth)  # lo paga
    assert r.status_code == 200  # se acepta porque 15 <= 20


def test_no_se_puede_eliminar_el_ingreso_que_respalda_las_metas(client, auth, hoy):  # eliminar el ingreso no puede dejar metas sin respaldo
    ingreso_id = _preparar_meta_con_reserva(client, auth, hoy)  # deja 280 reservados y obtiene el ingreso

    r = client.delete(f"/api/movimientos/{ingreso_id}", headers=auth)  # intenta eliminar el ingreso de 300 Bs
    assert r.status_code == 409  # debe ser rechazado
    assert len(client.get("/api/movimientos", headers=auth).json()) == 1  # el ingreso sigue ahí
