# Pruebas de la Tarea 9 (Parte B): Aviso antes de superar el presupuesto de la categoría
from app.logica.aviso_presupuesto import calcular_aviso_presupuesto  # importa la regla pura a probar


def test_regla_pura_del_aviso():  # prueba cuándo hay aviso y cuánto se pasaría
    assert calcular_aviso_presupuesto(None, 90, 0, 50) is None  # sin presupuesto no hay aviso
    assert calcular_aviso_presupuesto(100, 40, 0, 60) is None  # 40 + 60 = 100: llega justo, no se pasa
    aviso = calcular_aviso_presupuesto(100, 40, 0, 80)  # 40 + 80 = 120: se pasa por 20
    assert aviso == {"presupuesto": 100, "gastado": 40, "monto": 80, "nuevo_total": 120, "exceso": 20}  # datos del aviso
    assert calcular_aviso_presupuesto(100, 90, 50, 50) is None  # editar sin aumentar el monto no avisa aunque ya esté excedido
    assert calcular_aviso_presupuesto(100, 40, 30, 70)["exceso"] == 10  # editar de 30 a 70 lo hace pasar por 10


def _mes(hoy):  # mes actual en formato YYYY-MM
    return hoy.strftime("%Y-%m")  # p. ej. 2026-11


def _gasto(monto, hoy, **extra):  # arma el cuerpo de un gasto de Transporte
    return {"tipo": "gasto", "monto": monto, "categoria": "Transporte", "descripcion": "", "fecha": str(hoy), **extra}  # datos del gasto


def _preparar(client, auth, hoy):  # presupuesto de Transporte de 100 Bs y un gasto de 40 Bs
    client.put(f"/api/presupuestos/{_mes(hoy)}/Transporte", json={"monto": 100}, headers=auth)  # fija el presupuesto
    client.post("/api/movimientos", json=_gasto(40, hoy), headers=auth)  # ya gastó 40


def test_gasto_sin_aviso(client, auth, hoy):  # un gasto que no pasa el presupuesto se guarda directo
    _preparar(client, auth, hoy)  # presupuesto 100, gastado 40
    r = client.post("/api/movimientos", json=_gasto(30, hoy), headers=auth)  # 40 + 30 = 70
    assert r.status_code == 201  # se guarda sin pedir confirmación


def test_gasto_con_aviso_cancelado_no_cambia_nada(client, auth, hoy):  # si no confirma, no se guarda nada
    _preparar(client, auth, hoy)  # presupuesto 100, gastado 40
    r = client.post("/api/movimientos", json=_gasto(80, hoy), headers=auth)  # 40 + 80 = 120
    assert r.status_code == 409  # se detiene para pedir confirmación
    detalle = r.json()["detail"]  # datos del aviso
    assert detalle["codigo"] == "supera_presupuesto_categoria"  # código del aviso
    assert detalle["exceso"] == 20  # se pasaría por 20 Bs
    assert detalle["nuevo_total"] == 120  # quedaría en 120 Bs
    assert len(client.get("/api/movimientos", headers=auth).json()) == 1  # todo igual: solo sigue el gasto de 40


def test_gasto_con_aviso_confirmado_queda_excedido(client, auth, hoy):  # si confirma, se guarda y queda excedido
    _preparar(client, auth, hoy)  # presupuesto 100, gastado 40
    r = client.post("/api/movimientos", json=_gasto(80, hoy, confirmar_exceso=True), headers=auth)  # confirma el exceso
    assert r.status_code == 201  # se guarda
    total = sum(m["monto"] for m in client.get("/api/movimientos", headers=auth).json())  # suma de Transporte
    assert total == 120  # quedó excedido: 120 de 100


def test_los_ingresos_no_generan_aviso(client, auth, hoy):  # un ingreso nunca pide confirmación
    _preparar(client, auth, hoy)  # presupuesto 100, gastado 40
    r = client.post(  # ingreso grande en la misma categoría
        "/api/movimientos",  # endpoint de movimientos
        json={"tipo": "ingreso", "monto": 500, "categoria": "Transporte", "descripcion": "", "fecha": str(hoy)},  # ingreso
        headers=auth,  # token del usuario
    )  # fin del post
    assert r.status_code == 201  # se guarda directo


def test_editar_un_gasto_tambien_avisa(client, auth, hoy):  # un gasto editado que pasaría el límite pide confirmación
    _preparar(client, auth, hoy)  # presupuesto 100, gastado 40
    gasto = client.post("/api/movimientos", json=_gasto(30, hoy), headers=auth).json()  # gasto de 30 (total 70)
    r = client.put(f"/api/movimientos/{gasto['id']}", json=_gasto(90, hoy), headers=auth)  # lo sube a 90 (total 130)
    assert r.status_code == 409  # pide confirmación
    assert r.json()["detail"]["exceso"] == 30  # se pasaría por 30
    r = client.put(f"/api/movimientos/{gasto['id']}", json=_gasto(90, hoy, confirmar_exceso=True), headers=auth)  # confirma
    assert r.status_code == 200  # se guarda
