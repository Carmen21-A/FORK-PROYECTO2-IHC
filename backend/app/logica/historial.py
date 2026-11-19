# Portado de lib/utils/historial.dart (historial de eventos)


def formato_monto(monto: int | float) -> str:  
    if isinstance(monto, int):  
        return str(monto)  
    return repr(float(monto))  # retorna la representación 


# Texto legible de un evento del historial
def armar_detalle_evento(  
    tipo: str,  
    monto: int | float,  
    categoria: str,  
    descripcion: str | None = None,  
) -> str:  
    tipo_texto = "Gasto" if tipo == "gasto" else "Ingreso"  
    texto_descripcion = (  
        "" if descripcion is None or not descripcion.strip() else f" · {descripcion.strip()}"  # sino añade punto y la descripción sin espacios extra
    ) 
    return f"{tipo_texto} {formato_monto(monto)} Bs · {categoria}{texto_descripcion}"  # retorna el formato completo concatenando tipo, monto en Bs, categoría y descripción
