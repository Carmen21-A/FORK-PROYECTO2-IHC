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


# ---------- Tarea 9 · Parte A: analítica en todo el producto ----------
from app.logica.analitica import EVENTOS_PERMITIDOS, FLUJOS, armar_embudos, caida_entre_pasos, mayor_caida  # importa lo nuevo


def test_cada_flujo_tiene_sus_eventos_definidos():  # todos los pasos y errores de los embudos existen en la lista
    for flujo in FLUJOS:  # recorre cada flujo
        for evento in flujo["pasos"] + [flujo["error"]]:  # sus pasos y su evento de error
            assert evento in EVENTOS_PERMITIDOS  # está definido


def test_errores_solo_con_motivo_de_lista_fija():  # el motivo de un error debe venir de la lista fija
    validar_evento("movimiento_rechazado", {"motivo": "supera_limite_mensual"})  # motivo válido
    validar_evento("fondos_operacion_rechazada", {"operacion": "asignar", "motivo": "fondos_insuficientes"})  # válido
    with pytest.raises(ValueError, match="motivo"):  # un motivo escrito a mano se rechaza
        validar_evento("movimiento_rechazado", {"motivo": "el usuario escribió mal el monto"})  # texto libre
    with pytest.raises(ValueError, match="operacion"):  # una operación que no existe se rechaza
        validar_evento("fondos_operacion_iniciada", {"operacion": "robar"})  # valor fuera de la lista


def test_busqueda_no_guarda_el_texto():  # la búsqueda solo guarda si hubo texto o filtros (sí/no)
    validar_evento("busqueda_sin_resultados", {"con_texto": True, "con_filtros": False})  # válido
    with pytest.raises(ValueError, match="no permitidas"):  # el texto buscado nunca se guarda
        validar_evento("busqueda_realizada", {"con_texto": True, "con_filtros": False, "texto": "taxi a casa de Juan"})  # texto
    with pytest.raises(ValueError, match="verdadero o falso"):  # con_texto solo acepta True o False
        validar_evento("busqueda_realizada", {"con_texto": "taxi", "con_filtros": False})  # valor de texto


def test_embudos_y_mayor_caida():  # arma los embudos y encuentra el paso con la mayor caída
    assert caida_entre_pasos(10, 6) == 40  # de 10 a 6 se pierde el 40 %
    conteos = {"movimiento_iniciado": 10, "movimiento_guardado": 6, "meta_creacion_iniciada": 4, "meta_creada": 1}  # datos
    errores = {("movimiento_rechazado", "monto_vacio"): 3}  # 3 rechazos por monto vacío
    embudos = armar_embudos(conteos, errores)  # arma los embudos
    registrar = next(e for e in embudos if e["id"] == "registrar")  # embudo de registrar movimiento
    assert [p["total"] for p in registrar["pasos"]] == [10, 6]  # pasos con sus totales
    assert registrar["pasos"][1]["caida"] == 40  # caída del 40 %
    assert registrar["motivos"] == [{"motivo": "monto_vacio", "total": 3}]  # errores por motivo
    caida = mayor_caida(embudos)  # busca la mayor caída de toda la app
    assert caida["flujo"] == "Crear meta de ahorro (Tarea 8)"  # de 4 a 1 se pierde el 75 %
    assert caida["caida"] == 75  # es la mayor


def test_panel_devuelve_embudos(client, auth):  # la API arma los embudos con datos reales
    client.post("/api/eventos", json={"evento": "meta_creacion_iniciada", "props": {}}, headers=auth)  # inicio
    client.post("/api/eventos", json={"evento": "meta_rechazada", "props": {"motivo": "nombre_vacio"}}, headers=auth)  # error
    client.post("/api/eventos", json={"evento": "busqueda_realizada", "props": {"con_texto": True, "con_filtros": False}}, headers=auth)  # búsqueda
    client.post("/api/eventos", json={"evento": "busqueda_sin_resultados", "props": {"con_texto": True, "con_filtros": False}}, headers=auth)  # sin resultados
    panel = client.get("/api/analitica", headers=auth).json()  # consulta el panel
    meta = next(e for e in panel["embudos"] if e["id"] == "meta")  # embudo de metas
    assert meta["pasos"][0]["total"] == 1  # uno empezó
    assert meta["pasos"][1]["caida"] == 100  # nadie terminó: caída del 100 %
    assert meta["motivos"] == [{"motivo": "nombre_vacio", "total": 1}]  # el error se agrupa por motivo
    assert panel["mayor_caida"]["hasta"] == "meta_creada"  # es la mayor caída
    assert panel["busquedas"] == {"realizadas": 1, "sin_resultados": 1, "porcentaje_sin_resultados": 100}  # búsquedas
