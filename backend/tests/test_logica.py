# Portado de test/movimiento_test.dart, test/historial_test.dart y test/limite_mensual_test.dart
from datetime import date

from app.logica.estado_movimiento import (
    es_transicion_valida,
    puede_editar_monto,
    siguiente_estado,
)
from app.logica.historial import armar_detalle_evento
from app.logica.limite_mensual import es_limite_menor_a_gasto, supera_limite_mensual
from app.logica.recurrencia import siguiente_fecha


# ---------- Estados del movimiento ----------
def test_la_accion_hace_la_transicion_esperada():
    assert siguiente_estado("pendiente") == "pagado"
    assert siguiente_estado("pagado") == "cancelado"


def test_transicion_invalida_es_rechazada():
    assert siguiente_estado("cancelado") is None
    assert es_transicion_valida("cancelado", "pagado") is False
    assert es_transicion_valida("pendiente", "cancelado") is False


def test_no_se_puede_editar_el_monto_si_el_estado_es_pagado():
    assert puede_editar_monto("pendiente") is True
    assert puede_editar_monto("cancelado") is True
    assert puede_editar_monto("pagado") is False


# ---------- Detalle del evento del historial ----------
def test_arma_el_detalle_de_un_gasto_con_descripcion():
    detalle = armar_detalle_evento(
        tipo="gasto", monto=50, categoria="Comida", descripcion="Almuerzo"
    )
    assert detalle == "Gasto 50 Bs · Comida · Almuerzo"


def test_arma_el_detalle_de_un_ingreso_sin_descripcion():
    detalle = armar_detalle_evento(tipo="ingreso", monto=200, categoria="Otros", descripcion="")
    assert detalle == "Ingreso 200 Bs · Otros"


def test_ignora_descripcion_vacia_o_con_espacios():
    detalle = armar_detalle_evento(
        tipo="gasto", monto=10, categoria="Transporte", descripcion="   "
    )
    assert detalle == "Gasto 10 Bs · Transporte"


def test_monto_decimal_se_muestra_como_en_flutter():
    assert armar_detalle_evento(tipo="gasto", monto=25.5, categoria="Ocio") == (
        "Gasto 25.5 Bs · Ocio"
    )
    assert armar_detalle_evento(tipo="gasto", monto=50.0, categoria="Ocio") == (
        "Gasto 50.0 Bs · Ocio"
    )


# ---------- Limite mensual ----------
def test_limite_menor_a_lo_ya_gastado():
    assert es_limite_menor_a_gasto(200.0, 300.0) is True
    assert es_limite_menor_a_gasto(500.0, 300.0) is False


def test_para_no_superar_el_limite_mensual():
    assert supera_limite_mensual(gasto_actual_del_mes=400.0, nuevo_gasto=150.0, limite=500.0)
    assert not supera_limite_mensual(gasto_actual_del_mes=400.0, nuevo_gasto=50.0, limite=500.0)


# ---------- Tarea 6: gastos recurrentes ----------
def test_semanal_es_siete_dias_despues_aunque_cambie_de_mes():
    assert siguiente_fecha(date(2026, 11, 3), "semanal") == date(2026, 11, 10)
    assert siguiente_fecha(date(2026, 11, 28), "semanal") == date(2026, 12, 5)


def test_mensual_es_el_mismo_dia_del_mes_siguiente():
    assert siguiente_fecha(date(2026, 11, 3), "mensual") == date(2026, 12, 3)
    assert siguiente_fecha(date(2026, 12, 15), "mensual") == date(2027, 1, 15)


def test_mensual_usa_el_ultimo_dia_si_el_dia_no_existe():
    assert siguiente_fecha(date(2026, 1, 31), "mensual") == date(2026, 2, 28)
    assert siguiente_fecha(date(2028, 1, 31), "mensual") == date(2028, 2, 29)  # bisiesto
