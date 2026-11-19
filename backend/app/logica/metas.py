# Logica de negocio para Metas de Ahorro y Fondos Disponibles (Tarea 8)
from decimal import Decimal
from uuid import UUID


def calcular_saldo_disponible(
    total_ingresos: Decimal | float,
    total_gastos: Decimal | float,
    fondos_reservados: Decimal | float,
) -> tuple[Decimal, Decimal]:
    # saldo_total = total_ingresos - total_gastos
    # saldo_disponible = saldo_total - fondos_reservados
    ingresos = Decimal(str(total_ingresos))
    gastos = Decimal(str(total_gastos))
    reservados = Decimal(str(fondos_reservados))

    saldo_total = ingresos - gastos
    saldo_disponible = saldo_total - reservados
    return saldo_total, saldo_disponible


def validar_asignacion(saldo_disponible: Decimal | float, monto: Decimal | float) -> None:
    # El monto debe ser mayor a cero y no superar el saldo disponible del usuario
    m = Decimal(str(monto))
    disp = Decimal(str(saldo_disponible))

    if m <= Decimal("0"):
        raise ValueError("El monto a asignar debe ser mayor a 0 Bs.")
    if m > disp:
        raise ValueError(
            f"Fondos insuficientes: tu saldo disponible es de {disp:.2f} Bs e intentas asignar {m:.2f} Bs."
        )


def validar_retiro(monto_ahorrado: Decimal | float, monto: Decimal | float) -> None:
    # El monto debe ser mayor a cero y no superar lo ahorrado en esa meta
    m = Decimal(str(monto))
    ahorrado = Decimal(str(monto_ahorrado))

    if m <= Decimal("0"):
        raise ValueError("El monto a retirar debe ser mayor a 0 Bs.")
    if m > ahorrado:
        raise ValueError(
            f"Fondos insuficientes en la meta: solo cuenta con {ahorrado:.2f} Bs e intentas retirar {m:.2f} Bs."
        )


def validar_transferencia(
    origen_id: UUID,
    destino_id: UUID,
    ahorrado_origen: Decimal | float,
    monto: Decimal | float,
) -> None:
    if origen_id == destino_id:
        raise ValueError("No se puede transferir fondos a la misma meta de origen.")

    m = Decimal(str(monto))
    ahorrado = Decimal(str(ahorrado_origen))

    if m <= Decimal("0"):
        raise ValueError("El monto a transferir debe ser mayor a 0 Bs.")
    if m > ahorrado:
        raise ValueError(
            f"Fondos insuficientes en la meta de origen: cuenta con {ahorrado:.2f} Bs e intentas transferir {m:.2f} Bs."
        )


def validar_reservas_intactas(
    disponible_antes: Decimal | float,
    disponible_despues: Decimal | float,
    fondos_reservados: Decimal | float,
) -> None:
    # Rechaza pagar un gasto, cancelar o eliminar un ingreso pagado, etc., si deja el disponible en negativo.
    # Si el usuario no tiene fondos reservados no se aplica (se conservan las reglas de las tareas 6 y 7).
    antes = Decimal(str(disponible_antes))
    despues = Decimal(str(disponible_despues))
    reservados = Decimal(str(fondos_reservados))

    if reservados > 0 and despues < 0 and despues < antes:
        libre = max(antes, Decimal("0"))
        raise ValueError(
            f"Fondos insuficientes: tienes {reservados:.2f} Bs reservados en tus metas de ahorro "
            f"y solo {libre:.2f} Bs disponibles. Retira fondos de una meta antes de continuar."
        )


def calcular_porcentaje(monto_ahorrado: Decimal | float, monto_objetivo: Decimal | float) -> float:
    obj = float(monto_objetivo)
    ahorr = float(monto_ahorrado)
    if obj <= 0:
        return 0.0
    return round((ahorr / obj) * 100.0, 1)
