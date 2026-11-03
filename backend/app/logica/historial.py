# Portado de lib/utils/historial.dart (historial de eventos)


def formato_monto(monto: int | float) -> str:  # función que formatea un monto numérico a cadena de texto
    # Igual que Dart: un entero se muestra "50" y un decimal "50.0"
    if isinstance(monto, int):  # comprueba si el monto es un número entero
        return str(monto)  # retorna el entero convertido en texto directamente
    return repr(float(monto))  # retorna la representación en texto del número flotante con su decimal


# Texto legible de un evento del historial
def armar_detalle_evento(  # función que construye el texto descriptivo para guardar en el historial
    tipo: str,  # tipo de movimiento: gasto o ingreso
    monto: int | float,  # monto del movimiento
    categoria: str,  # categoría asignada al movimiento
    descripcion: str | None = None,  # descripción opcional del movimiento
) -> str:  # retorna el detalle formateado en una cadena de texto
    tipo_texto = "Gasto" if tipo == "gasto" else "Ingreso"  # asigna la palabra 'Gasto' si es tipo gasto o 'Ingreso' en caso contrario
    texto_descripcion = (  # genera el sufijo con la descripción limpia
        "" if descripcion is None or not descripcion.strip() else f" · {descripcion.strip()}"  # si no hay descripción queda vacío, sino añade punto y la descripción sin espacios extra
    )  # fin de la asignación condicional
    return f"{tipo_texto} {formato_monto(monto)} Bs · {categoria}{texto_descripcion}"  # retorna el formato completo concatenando tipo, monto en Bs, categoría y descripción
