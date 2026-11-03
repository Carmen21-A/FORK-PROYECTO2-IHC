# Reemplaza a lib/services/movements_service.dart
from datetime import date  # importa date para manejo de fechas
from uuid import UUID  # importa UUID para tipar identificadores únicos de movimientos

from fastapi import APIRouter, Depends, HTTPException, Query, status  # importa utilidades de FastAPI para rutas, dependencias, errores y parámetros de consulta
from sqlalchemy import select  # importa select para armar consultas de SQLAlchemy
from sqlalchemy.orm import Session  # importa Session para interactuar con la base de datos

from app.database import get_db  # importa dependencia para obtener la sesión de base de datos
from app.dependencias import usuario_actual  # importa dependencia para validar el usuario en sesión
from app.logica.estado_movimiento import es_transicion_valida, puede_editar_monto  # importa validaciones de transiciones de estado y edición
from app.logica.historial import armar_detalle_evento  # importa generador de texto descriptivo para el historial
from app.logica.limite_mensual import supera_limite_mensual  # importa regla de validación de tope mensual de gastos
from app.logica.recurrencia import TEXTO_RECURRENCIA, siguiente_fecha  # importa mapeo de texto y función de próxima fecha recurrente
from app.models import Movimiento, Usuario  # importa modelos de tabla Movimiento y Usuario
from app.routers.historial import registrar_evento  # importa función para guardar eventos en el historial
from app.routers.limites import calcular_gasto_total_mes, get_limit  # importa funciones para calcular gastos acumulados y consultar límites
from app.schemas import CambioEstado, EstadoCambiado, MovimientoRead, MovimientoWrite  # importa esquemas de datos Pydantic

router = APIRouter(prefix="/movimientos", tags=["movimientos"])  # define el router de movimientos con prefijo /movimientos

ESTADO_INICIAL = "pendiente"  # constante que define el estado por defecto al crear un movimiento


def _detalle(payload: MovimientoWrite) -> str:  # función auxiliar que formatea el detalle legible de un movimiento recibido
    return armar_detalle_evento(  # retorna el string generado por armar_detalle_evento
        tipo=payload.tipo,  # pasa el tipo gasto o ingreso
        monto=float(payload.monto),  # pasa el monto convertido a float
        categoria=payload.categoria,  # pasa la categoría asignada
        descripcion=payload.descripcion,  # pasa la descripción del movimiento
    )  # fin de armar_detalle_evento


def _buscar_propio(db: Session, usuario: Usuario, movimiento_id: UUID) -> Movimiento:  # función auxiliar para buscar un movimiento que pertenezca al usuario
    movimiento = db.scalar(  # ejecuta la consulta select devolviendo el primer resultado
        select(Movimiento).where(  # consulta en tabla movimientos
            Movimiento.id == movimiento_id,  # verifica que coincida el id del movimiento
            Movimiento.user_id == usuario.id,  # verifica que sea propiedad del usuario autenticado
        )  # fin de where
    )  # fin de db.scalar
    if movimiento is None:  # si no se encontró o pertenece a otro usuario
        raise HTTPException(status_code=404, detail="No se encontró el movimiento.")  # lanza error HTTP 404 No Encontrado
    return movimiento  # retorna el movimiento encontrado


# Misma regla que _validarSiExcedioLimiteMensual de movements_screen.dart
def _validar_limite_mensual(  # valida si el nuevo gasto excede el límite del mes del usuario
    db: Session, usuario: Usuario, payload: MovimientoWrite, excluir_id: UUID | None = None  # parámetros: db, usuario, datos del movimiento y opcional id a excluir
) -> None:  # no retorna valor si es válido, lanza excepción si se supera el límite
    if payload.tipo != "gasto":  # si el movimiento no es un gasto (es un ingreso)
        return  # sale de la función porque los ingresos no tienen límite de gasto
    mes = payload.fecha.strftime("%Y-%m")  # extrae el mes en formato YYYY-MM a partir de la fecha
    limite = get_limit(db, usuario.id, mes)  # obtiene el límite fijado para ese mes
    if limite is None:  # si el usuario no tiene ningún límite fijado en ese mes
        return  # permite registrar el gasto sin restricciones
    gasto_actual = calcular_gasto_total_mes(db, usuario.id, mes, excluir_id)  # calcula la suma de gastos actuales del mes excluyendo el que se está editando
    if supera_limite_mensual(  # comprueba si el gasto actual más el nuevo gasto supera el límite mensual
        gasto_actual_del_mes=gasto_actual,  # monto ya gastado
        nuevo_gasto=float(payload.monto),  # monto del nuevo gasto
        limite=limite,  # límite máximo establecido
    ):  # si supera el límite
        raise HTTPException(  # lanza error HTTP 409 Conflicto bloqueando el registro
            status_code=409,  # código de estado 409
            detail=(  # mensaje detallado con el límite y el gasto acumulado
                f"No se puede registrar, porque supera tu límite mensual de {limite} Bs "  # aviso de superación de límite
                f"(llevas gastando {gasto_actual} Bs)"  # detalle de cuánto lleva gastado
            ),  # fin de detail
        )  # fin de raise HTTPException


# Solo un gasto puede repetirse
def _recurrencia(payload: MovimientoWrite) -> str | None:  # funcion recurrencia que recibe payload y devuelve la recurrencia o None
    return payload.recurrencia if payload.tipo == "gasto" else None  # retorna payload.recurrencia si payload.tipo es gasto, sino retorna None


# Tarea 6: al pagar un gasto recurrente se crea el siguiente (pendiente).
# Cuenta en el limite: si lo superaria, no se crea y se devuelve el aviso.
def _generar_siguiente(  # función que genera automáticamente la próxima ocurrencia de un gasto recurrente al pagarlo
    db: Session, usuario: Usuario, movimiento: Movimiento  # recibe la sesión, el usuario y el gasto recurrente original
) -> tuple[Movimiento | None, str | None]:  # retorna una tupla con el nuevo movimiento generado (o None) y un aviso de texto (o None)
    fecha = siguiente_fecha(movimiento.fecha, movimiento.recurrencia)  # calcula la fecha futura (+7 días si es semanal o +1 mes si es mensual)
    mes = fecha.strftime("%Y-%m")  # obtiene el mes de esa fecha futura en formato YYYY-MM
    limite = get_limit(db, usuario.id, mes)  # consulta si existe un límite mensual en el mes futuro
    if limite is not None:  # si existe un límite en el mes futuro
        gasto_actual = calcular_gasto_total_mes(db, usuario.id, mes)  # calcula los gastos ya registrados para ese mes futuro
        if supera_limite_mensual(gasto_actual, float(movimiento.monto), limite):  # verifica si la nueva ocurrencia superaría el límite de ese mes
            return None, (  # si supera el límite, no crea el movimiento y retorna mensaje de advertencia
                f"No se generó el gasto del {fecha.strftime('%d/%m/%Y')}: supera tu límite "  # texto del aviso
                f"mensual de {limite} Bs (llevas gastando {gasto_actual} Bs)"  # texto con los montos
            )  # fin de retorno con aviso

    siguiente = Movimiento(  # crea la nueva instancia del movimiento para la próxima ocurrencia
        user_id=usuario.id,  # asigna el id del mismo usuario
        tipo=movimiento.tipo,  # mantiene el tipo gasto
        monto=movimiento.monto,  # mantiene el mismo monto
        categoria=movimiento.categoria,  # mantiene la misma categoría
        descripcion=movimiento.descripcion,  # mantiene la misma descripción
        estado=ESTADO_INICIAL,  # asigna estado inicial pendiente a la nueva ocurrencia
        fecha=fecha,  # asigna la fecha futura calculada
        recurrencia=movimiento.recurrencia,  # mantiene la misma configuración de recurrencia
    )  # fin de creación de siguiente movimiento
    db.add(siguiente)  # añade el nuevo movimiento a la sesión de base de datos
    db.flush()  # envía a la base de datos para obtener su id autogenerado sin hacer commit definitivo
    detalle = armar_detalle_evento(  # construye la descripción textual del evento para el historial
        movimiento.tipo, float(movimiento.monto), movimiento.categoria, movimiento.descripcion  # parámetros del detalle
    )  # fin de armar_detalle_evento
    registrar_evento(  # registra la creación de la siguiente ocurrencia en la bitácora de historial
        db,  # sesión de base de datos
        usuario.id,  # id del usuario
        "creado",  # acción registrado como creado
        f"{detalle} · se repite {TEXTO_RECURRENCIA[movimiento.recurrencia]}",  # detalle indicando que se repite
        siguiente.id,  # id del nuevo movimiento generado
    )  # fin de registrar_evento
    return siguiente, None  # retorna el nuevo movimiento creado y sin mensaje de aviso de error


# getAll + buscarConFiltros: sin parametros devuelve todos los movimientos
@router.get("", response_model=list[MovimientoRead])  # endpoint GET en /api/movimientos para buscar con filtros o listar todos
def buscar_con_filtros(  # función controladora para consultar y filtrar movimientos
    texto: str | None = Query(default=None, max_length=100),  # parámetro opcional de texto para buscar en descripción
    tipo: str | None = Query(default=None, pattern="^(gasto|ingreso)$"),  # filtro opcional por tipo gasto o ingreso
    categoria: str | None = Query(default=None, max_length=50),  # filtro opcional por categoría
    estado: str | None = Query(default=None, pattern="^(pendiente|pagado|cancelado)$"),  # filtro opcional por estado
    desde: date | None = None,  # filtro opcional de fecha de inicio
    hasta: date | None = None,  # filtro opcional de fecha de fin
    db: Session = Depends(get_db),  # inyecta la sesión de base de datos
    usuario: Usuario = Depends(usuario_actual),  # inyecta el usuario autenticado
) -> list[Movimiento]:  # retorna la lista de movimientos que coincidan
    consulta = select(Movimiento).where(Movimiento.user_id == usuario.id)  # inicia consulta base filtrando por el usuario actual

    # Busqueda por descripcion con coincidencia parcial
    if texto and texto.strip():  # si se envió texto de búsqueda no vacío
        consulta = consulta.where(Movimiento.descripcion.ilike(f"%{texto.strip()}%"))  # añade filtro ILIKE insensible a mayúsculas
    if tipo:  # si se seleccionó filtro de tipo
        consulta = consulta.where(Movimiento.tipo == tipo)  # añade filtro por tipo exacto
    if categoria:  # si se seleccionó categoría
        consulta = consulta.where(Movimiento.categoria == categoria)  # añade filtro por categoría
    if estado:  # si se seleccionó estado
        consulta = consulta.where(Movimiento.estado == estado)  # añade filtro por estado
    if desde:  # si se definió fecha desde
        consulta = consulta.where(Movimiento.fecha >= desde)  # filtra fechas mayores o iguales a 'desde'
    if hasta:  # si se definió fecha hasta
        consulta = consulta.where(Movimiento.fecha <= hasta)  # filtra fechas menores o iguales a 'hasta'

    consulta = consulta.order_by(Movimiento.fecha.asc(), Movimiento.created_at.asc())  # ordena cronológicamente por fecha y creación
    return list(db.scalars(consulta))  # ejecuta la consulta y devuelve los movimientos encontrados


@router.post("", response_model=MovimientoRead, status_code=status.HTTP_201_CREATED)  # endpoint POST para crear un movimiento devolviendo código 201
def create(  # función controladora para registrar un nuevo movimiento
    payload: MovimientoWrite,  # cuerpo de la petición con datos del movimiento
    db: Session = Depends(get_db),  # inyecta la sesión de base de datos
    usuario: Usuario = Depends(usuario_actual),  # inyecta el usuario autenticado
) -> Movimiento:  # retorna el movimiento recién creado
    _validar_limite_mensual(db, usuario, payload)  # valida que no supere el límite mensual si es un gasto
    movimiento = Movimiento(  # instancia el nuevo objeto Movimiento con los datos recibidos
        user_id=usuario.id,  # asigna el id del usuario autenticado
        tipo=payload.tipo,  # asigna gasto o ingreso
        monto=payload.monto,  # asigna el monto numérico
        categoria=payload.categoria,  # asigna la categoría
        descripcion=payload.descripcion.strip(),  # asigna la descripción sin espacios extra en los extremos
        estado=ESTADO_INICIAL,  # asigna estado inicial pendiente
        fecha=payload.fecha,  # asigna la fecha del movimiento
        recurrencia=_recurrencia(payload),  # asigna la recurrencia solo si es un gasto
    )  # fin de creación del movimiento
    db.add(movimiento)  # agrega el movimiento a la sesión
    db.flush()  # sincroniza con la base de datos para obtener el id del registro
    registrar_evento(db, usuario.id, "creado", _detalle(payload), movimiento.id)  # registra el evento de creación en el historial
    db.commit()  # confirma la transacción completa en la base de datos
    return movimiento  # retorna el movimiento registrado


@router.put("/{movimiento_id}", response_model=MovimientoRead)  # endpoint PUT para editar un movimiento existente
def update(  # función controladora para actualizar los datos de un movimiento
    movimiento_id: UUID,  # id del movimiento recibido en la ruta
    payload: MovimientoWrite,  # nuevos datos del movimiento enviados en el cuerpo
    db: Session = Depends(get_db),  # inyecta sesión de base de datos
    usuario: Usuario = Depends(usuario_actual),  # inyecta usuario autenticado
) -> Movimiento:  # retorna el movimiento con los datos modificados
    movimiento = _buscar_propio(db, usuario, movimiento_id)  # busca el movimiento asegurando que pertenezca al usuario
    if not puede_editar_monto(movimiento.estado) and payload.monto != movimiento.monto:  # regla: si ya está pagado no permite cambiar el monto
        raise HTTPException(  # lanza error 409 si intenta cambiar el monto de un movimiento pagado
            status_code=409,  # código HTTP 409 Conflicto
            detail="No es posible modificar el monto porque el movimiento ya fue pagado",  # detalle de la regla
        )  # fin de raise
    _validar_limite_mensual(db, usuario, payload, excluir_id=movimiento.id)  # valida el límite del mes excluyendo el monto anterior del mismo movimiento

    movimiento.tipo = payload.tipo  # actualiza el tipo
    movimiento.monto = payload.monto  # actualiza el monto
    movimiento.categoria = payload.categoria  # actualiza la categoría
    movimiento.descripcion = payload.descripcion.strip()  # actualiza la descripción limpia
    movimiento.fecha = payload.fecha  # actualiza la fecha
    movimiento.recurrencia = _recurrencia(payload)  # actualiza la recurrencia permitida
    registrar_evento(db, usuario.id, "editado", _detalle(payload), movimiento.id)  # registra el evento de edición en el historial
    db.commit()  # guarda los cambios en la base de datos
    return movimiento  # retorna el movimiento actualizado


@router.patch("/{movimiento_id}/estado", response_model=EstadoCambiado)  # endpoint PATCH para cambiar el estado de un movimiento
def cambiar_estado(  # función controladora para transicionar el estado (pendiente -> pagado -> cancelado)
    movimiento_id: UUID,  # id del movimiento en la ruta
    payload: CambioEstado,  # cuerpo con el nuevo estado solicitado
    db: Session = Depends(get_db),  # inyecta sesión de base de datos
    usuario: Usuario = Depends(usuario_actual),  # inyecta usuario autenticado
) -> EstadoCambiado:  # retorna el movimiento y opcionalmente la siguiente ocurrencia o aviso
    movimiento = _buscar_propio(db, usuario, movimiento_id)  # busca el movimiento propio del usuario
    if not es_transicion_valida(movimiento.estado, payload.estado):  # verifica si la transición es permitida por la máquina de estados
        raise HTTPException(  # lanza error 409 si la transición es inválida
            status_code=409,  # código 409
            detail=f"No se puede pasar de {movimiento.estado} a {payload.estado}.",  # mensaje explicativo
        )  # fin de raise
    movimiento.estado = payload.estado  # asigna el nuevo estado al movimiento
    registrar_evento(  # guarda en el historial el cambio de estado realizado
        db, usuario.id, "cambio_estado", f"Estado cambiado a {payload.estado}", movimiento.id  # datos del evento
    )  # fin de registrar_evento
    siguiente, aviso = None, None  # inicializa variables para la siguiente ocurrencia y aviso en None
    if payload.estado == "pagado" and movimiento.tipo == "gasto" and movimiento.recurrencia:  # si se pagó un gasto que tiene recurrencia
        siguiente, aviso = _generar_siguiente(db, usuario, movimiento)  # genera automáticamente el próximo gasto recurrente
    db.commit()  # confirma todas las modificaciones en la base de datos
    return EstadoCambiado.model_validate(movimiento).model_copy(  # valida y copia el modelo de respuesta
        update={  # actualiza los campos adicionales en la respuesta
            "siguiente": MovimientoRead.model_validate(siguiente) if siguiente else None,  # incluye la siguiente ocurrencia si se generó
            "aviso": aviso,  # incluye el aviso si no se pudo generar
        }  # fin de update
    )  # fin de model_copy


@router.delete("/{movimiento_id}", status_code=status.HTTP_204_NO_CONTENT)  # endpoint DELETE para borrar un movimiento retornando código 204
def delete(  # función controladora para eliminar un movimiento
    movimiento_id: UUID,  # id del movimiento en la ruta
    db: Session = Depends(get_db),  # inyecta la sesión de base de datos
    usuario: Usuario = Depends(usuario_actual),  # inyecta el usuario autenticado
) -> None:  # no retorna cuerpo
    movimiento = _buscar_propio(db, usuario, movimiento_id)  # busca el movimiento comprobando pertenencia
    # Guardamos el evento antes de borrar el movimiento
    registrar_evento(  # registra la eliminación en el historial antes de borrar el registro
        db,  # sesión de base de datos
        usuario.id,  # id del usuario
        "eliminado",  # acción marcada como eliminado
        armar_detalle_evento(  # arma el texto del movimiento que se está eliminando
            tipo=movimiento.tipo,  # tipo del movimiento
            monto=float(movimiento.monto),  # monto del movimiento
            categoria=movimiento.categoria,  # categoría del movimiento
            descripcion=movimiento.descripcion,  # descripción del movimiento
        ),  # fin de armar_detalle_evento
        movimiento.id,  # conserva el id del movimiento borrado en la bitácora
    )  # fin de registrar_evento
    db.delete(movimiento)  # elimina el registro de la tabla movimientos
    db.commit()  # confirma la eliminación en la base de datos
