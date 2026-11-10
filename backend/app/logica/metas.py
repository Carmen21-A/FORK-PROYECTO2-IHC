# Logica de negocio para Metas de Ahorro y Fondos Disponibles (Tarea 8)
from decimal import Decimal  # importa Decimal para hacer cálculos de dinero sin errores de redondeo
from uuid import UUID  # importa UUID para tipar los identificadores de las metas


def calcular_saldo_disponible(  # función que calcula el saldo total y el saldo disponible del usuario
    total_ingresos: Decimal | float,  # suma de los ingresos pagados
    total_gastos: Decimal | float,  # suma de los gastos pagados
    fondos_reservados: Decimal | float,  # suma del dinero apartado en todas las metas
) -> tuple[Decimal, Decimal]:  # devuelve una tupla (saldo_total, saldo_disponible)
    # saldo_total = total_ingresos - total_gastos
    # saldo_disponible = saldo_total - fondos_reservados
    ingresos = Decimal(str(total_ingresos))  # convierte los ingresos a Decimal pasando por texto para no perder precisión
    gastos = Decimal(str(total_gastos))  # convierte los gastos a Decimal
    reservados = Decimal(str(fondos_reservados))  # convierte los fondos reservados a Decimal

    saldo_total = ingresos - gastos  # el saldo total es lo que entró menos lo que salió
    saldo_disponible = saldo_total - reservados  # el disponible es el saldo total menos lo apartado en metas
    return saldo_total, saldo_disponible  # devuelve ambos valores


def validar_asignacion(saldo_disponible: Decimal | float, monto: Decimal | float) -> None:  # valida que se pueda asignar dinero a una meta
    # El monto debe ser mayor a cero y no superar el saldo disponible del usuario
    m = Decimal(str(monto))  # convierte el monto a asignar a Decimal
    disp = Decimal(str(saldo_disponible))  # convierte el saldo disponible a Decimal

    if m <= Decimal("0"):  # si el monto es cero o negativo
        raise ValueError("El monto a asignar debe ser mayor a 0 Bs.")  # rechaza la operación con un mensaje claro
    if m > disp:  # si el monto supera lo que el usuario tiene libre
        raise ValueError(  # rechaza la operación por falta de fondos
            f"Fondos insuficientes: tu saldo disponible es de {disp:.2f} Bs e intentas asignar {m:.2f} Bs."  # mensaje con ambos montos
        )  # fin del raise


def validar_retiro(monto_ahorrado: Decimal | float, monto: Decimal | float) -> None:  # valida que se pueda retirar dinero de una meta
    # El monto debe ser mayor a cero y no superar lo ahorrado en esa meta
    m = Decimal(str(monto))  # convierte el monto a retirar a Decimal
    ahorrado = Decimal(str(monto_ahorrado))  # convierte lo ahorrado en la meta a Decimal

    if m <= Decimal("0"):  # si el monto es cero o negativo
        raise ValueError("El monto a retirar debe ser mayor a 0 Bs.")  # rechaza la operación
    if m > ahorrado:  # si quiere retirar más de lo que tiene la meta
        raise ValueError(  # rechaza la operación por falta de fondos en la meta
            f"Fondos insuficientes en la meta: solo cuenta con {ahorrado:.2f} Bs e intentas retirar {m:.2f} Bs."  # mensaje con ambos montos
        )  # fin del raise


def validar_transferencia(  # valida una transferencia de dinero entre dos metas
    origen_id: UUID,  # id de la meta de donde sale el dinero
    destino_id: UUID,  # id de la meta a donde llega el dinero
    ahorrado_origen: Decimal | float,  # dinero ahorrado en la meta de origen
    monto: Decimal | float,  # monto que se quiere transferir
) -> None:  # no devuelve nada; si algo está mal lanza ValueError
    if origen_id == destino_id:  # si el origen y el destino son la misma meta
        raise ValueError("No se puede transferir fondos a la misma meta de origen.")  # rechaza la operación

    m = Decimal(str(monto))  # convierte el monto a transferir a Decimal
    ahorrado = Decimal(str(ahorrado_origen))  # convierte lo ahorrado en la meta de origen a Decimal

    if m <= Decimal("0"):  # si el monto es cero o negativo
        raise ValueError("El monto a transferir debe ser mayor a 0 Bs.")  # rechaza la operación
    if m > ahorrado:  # si quiere transferir más de lo que tiene la meta de origen
        raise ValueError(  # rechaza la operación por falta de fondos
            f"Fondos insuficientes en la meta de origen: cuenta con {ahorrado:.2f} Bs e intentas transferir {m:.2f} Bs."  # mensaje con ambos montos
        )  # fin del raise


def validar_reservas_intactas(  # protege el dinero apartado en metas para que no se gaste por otro camino
    disponible_antes: Decimal | float,  # saldo disponible antes de la operación sobre un movimiento
    disponible_despues: Decimal | float,  # saldo disponible después de la operación
    fondos_reservados: Decimal | float,  # dinero total apartado en metas
) -> None:  # no devuelve nada; si la operación toca dinero reservado lanza ValueError
    # Rechaza pagar un gasto, cancelar o eliminar un ingreso pagado, etc., si deja el disponible en negativo.
    # Si el usuario no tiene fondos reservados no se aplica (se conservan las reglas de las tareas 6 y 7).
    antes = Decimal(str(disponible_antes))  # convierte el disponible anterior a Decimal
    despues = Decimal(str(disponible_despues))  # convierte el disponible posterior a Decimal
    reservados = Decimal(str(fondos_reservados))  # convierte los fondos reservados a Decimal

    if reservados > 0 and despues < 0 and despues < antes:  # hay metas con dinero, el disponible queda negativo y la operación lo empeora
        libre = max(antes, Decimal("0"))  # dinero libre que tenía antes (nunca menor a cero)
        raise ValueError(  # rechaza la operación explicando el motivo
            f"Fondos insuficientes: tienes {reservados:.2f} Bs reservados en tus metas de ahorro "  # primera parte del mensaje
            f"y solo {libre:.2f} Bs disponibles. Retira fondos de una meta antes de continuar."  # segunda parte con la sugerencia
        )  # fin del raise


def calcular_porcentaje(monto_ahorrado: Decimal | float, monto_objetivo: Decimal | float) -> float:  # calcula el % de avance de la meta (0 a 100+)
    obj = float(monto_objetivo)  # convierte el monto objetivo a número decimal
    ahorr = float(monto_ahorrado)  # convierte el monto ahorrado a número decimal
    if obj <= 0:  # si el objetivo es cero o negativo (evita dividir entre cero)
        return 0.0  # devuelve 0 % de avance
    return round((ahorr / obj) * 100.0, 1)  # devuelve el porcentaje redondeado a un decimal
