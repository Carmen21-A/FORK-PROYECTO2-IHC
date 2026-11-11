# Pruebas de la analítica de interacción (Clase 21)
import pytest  # importa pytest para verificar errores

from app.logica.analitica import porcentaje_terminan, validar_evento  # importa la lógica pura a probar


def test_validar_evento_acepta_solo_lo_definido():  # cada evento acepta solo sus propiedades definidas
    validar_evento("movimiento_iniciado", {})  # inicio sin propiedades: válido
    validar_evento("movimiento_guardado", {"tipo": "gasto", "categoria": "Transporte"})  # éxito con tipo y categoría: válido
    with pytest.raises(ValueError, match="desconocido"):  # un evento no definido se rechaza
        validar_evento("boton_clic", {})  # evento débil del ejemplo de clase
    with pytest.raises(ValueError, match="no permitidas"):  # datos personales o innecesarios se rechazan
        validar_evento("movimiento_guardado", {"tipo": "gasto", "categoria": "Comida", "monto": 50})  # monto no se recopila
    with pytest.raises(ValueError, match="no permitidas"):  # el email nunca se recopila
        validar_evento("movimiento_iniciado", {"email": "ana@gmail.com"})  # intento de mandar el email
    with pytest.raises(ValueError, match="categoria"):  # la categoría debe ser de la lista fija
        validar_evento("movimiento_guardado", {"tipo": "gasto", "categoria": "taxi a casa de Juan"})  # texto libre


def test_porcentaje_terminan():  # prueba el % que termina
    assert porcentaje_terminan(8, 5) == 63  # ejemplo de la clase: 5 de 8 es 63 %
    assert porcentaje_terminan(0, 0) == 0  # sin datos no divide entre cero


def test_api_guarda_eventos_y_arma_el_panel(client, auth):  # recorrido completo por la API
    client.post("/api/eventos", json={"evento": "movimiento_iniciado", "props": {}}, headers=auth)  # primer inicio
    client.post("/api/eventos", json={"evento": "movimiento_iniciado", "props": {}}, headers=auth)  # segundo inicio
    r = client.post(  # un guardado exitoso
        "/api/eventos",  # endpoint de eventos
        json={"evento": "movimiento_guardado", "props": {"tipo": "gasto", "categoria": "Comida"}},  # evento de éxito
        headers=auth,  # token del usuario
    )  # fin del post
    assert r.status_code == 201  # se guardó

    panel = client.get("/api/analitica", headers=auth).json()  # consulta el panel
    assert panel["iniciados"] == 2  # dos empezaron
    assert panel["guardados"] == 1  # uno terminó
    assert panel["porcentaje_terminan"] == 50  # 1 de 2 es 50 %
    assert panel["ultimos"][0]["evento"] == "movimiento_guardado"  # el más reciente va primero
    assert panel["ultimos"][0]["props"] == {"tipo": "gasto", "categoria": "Comida"}  # solo las propiedades definidas


def test_api_rechaza_datos_personales(client, auth):  # el backend no deja guardar datos de la persona
    r = client.post(  # intenta mandar descripción y monto
        "/api/eventos",  # endpoint de eventos
        json={"evento": "movimiento_guardado", "props": {"tipo": "gasto", "categoria": "Comida", "descripcion": "cena"}},  # dato de más
        headers=auth,  # token del usuario
    )  # fin del post
    assert r.status_code == 422  # se rechaza
    assert client.get("/api/analitica", headers=auth).json()["guardados"] == 0  # no se guardó nada


def test_api_exige_sesion(client):  # sin sesión no se pueden enviar ni ver eventos
    assert client.post("/api/eventos", json={"evento": "movimiento_iniciado"}).status_code == 401  # enviar sin token
    assert client.get("/api/analitica").status_code == 401  # ver el panel sin token
