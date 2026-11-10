# Endpoints REST de Metas de Ahorro y Fondos Disponibles (Tarea 8)
from decimal import Decimal  # importa Decimal para manejar montos de dinero con precisión
from uuid import UUID  # importa UUID para tipar los identificadores

from fastapi import APIRouter, Depends, HTTPException, status  # importa utilidades de FastAPI para rutas, dependencias, errores y códigos HTTP
from sqlalchemy import func, select  # importa select para consultas y func para funciones SQL como SUM y COALESCE
from sqlalchemy.orm import Session  # importa Session para trabajar con la base de datos

from app.database import get_db  # importa la dependencia que entrega la sesión de base de datos
from app.dependencias import usuario_actual  # importa la dependencia que obtiene el usuario autenticado
from app.logica.metas import (  # importa las reglas de negocio puras de metas
    calcular_porcentaje,  # calcula el porcentaje de avance de una meta
    calcular_saldo_disponible,  # calcula saldo total y saldo disponible
    validar_asignacion,  # valida que haya fondos para asignar a una meta
    validar_retiro,  # valida que la meta tenga fondos para retirar
    validar_transferencia,  # valida una transferencia entre metas
)  # fin de importaciones de lógica
from app.models import Historial, MetaAhorro, Movimiento, Usuario  # importa los modelos de tablas que se usan aquí
from app.schemas import (  # importa los esquemas Pydantic de entrada y salida
    MetaRead,  # esquema de respuesta de una meta
    MetaUpdate,  # esquema para editar una meta
    MetaWrite,  # esquema para crear una meta
    MontoOperacion,  # esquema con el monto de asignar o retirar
    ResumenFondos,  # esquema con el resumen de saldos
    TransferenciaMetas,  # esquema con la meta destino y el monto a transferir
)  # fin de importaciones de esquemas

router = APIRouter(prefix="/metas", tags=["metas"])  # crea el router con el prefijo /metas


def obtener_saldo_calculado(db: Session, user_id: UUID) -> tuple[Decimal, Decimal, Decimal, Decimal, Decimal]:  # calcula todos los saldos del usuario
    # Devuelve (total_ingresos, total_gastos, saldo_total, fondos_reservados, saldo_disponible).
    # Solo cuenta ingresos y gastos en estado 'pagado' para reflejar el dinero real.
    total_ingresos = db.scalar(  # ejecuta la consulta y obtiene un solo valor
        select(func.coalesce(func.sum(Movimiento.monto), 0)).where(  # suma los montos (0 si no hay ninguno)
            Movimiento.user_id == user_id,  # solo movimientos del usuario
            Movimiento.tipo == "ingreso",  # solo ingresos
            Movimiento.estado == "pagado",  # solo los que ya están pagados
        )  # fin del where
    ) or Decimal("0")  # si la consulta devuelve None usa 0

    total_gastos = db.scalar(  # ejecuta la consulta de gastos
        select(func.coalesce(func.sum(Movimiento.monto), 0)).where(  # suma los montos de gastos
            Movimiento.user_id == user_id,  # solo del usuario
            Movimiento.tipo == "gasto",  # solo gastos
            Movimiento.estado == "pagado",  # solo los pagados
        )  # fin del where
    ) or Decimal("0")  # si no hay gastos usa 0

    fondos_reservados = db.scalar(  # ejecuta la consulta de fondos reservados
        select(func.coalesce(func.sum(MetaAhorro.monto_ahorrado), 0)).where(  # suma lo ahorrado en todas las metas
            MetaAhorro.user_id == user_id  # solo las metas del usuario
        )  # fin del where
    ) or Decimal("0")  # si no tiene metas usa 0

    saldo_total, saldo_disponible = calcular_saldo_disponible(  # aplica la fórmula de la lógica pura
        total_ingresos, total_gastos, fondos_reservados  # pasa los tres totales calculados
    )  # fin de calcular_saldo_disponible

    return total_ingresos, total_gastos, saldo_total, fondos_reservados, saldo_disponible  # devuelve los cinco valores


def _serializar_meta(meta: MetaAhorro) -> MetaRead:  # convierte una meta de la base de datos en la respuesta de la API
    porcentaje = calcular_porcentaje(meta.monto_ahorrado, meta.monto_objetivo)  # calcula el % de avance
    cumplida = meta.monto_ahorrado >= meta.monto_objetivo  # la meta está cumplida si ya se ahorró el objetivo
    return MetaRead(  # arma el esquema de respuesta
        id=meta.id,  # id de la meta
        user_id=meta.user_id,  # dueño de la meta
        nombre=meta.nombre,  # nombre de la meta
        monto_objetivo=float(meta.monto_objetivo),  # monto objetivo como número
        monto_ahorrado=float(meta.monto_ahorrado),  # monto ahorrado como número
        fecha_limite=meta.fecha_limite,  # fecha límite
        porcentaje=porcentaje,  # porcentaje de avance
        cumplida=cumplida,  # si ya se completó
        created_at=meta.created_at,  # fecha de creación
    )  # fin de MetaRead


@router.get("/resumen-fondos", response_model=ResumenFondos)  # endpoint GET /api/metas/resumen-fondos
def get_resumen_fondos(  # devuelve el resumen de saldos para la cabecera de la pantalla
    db: Session = Depends(get_db),  # inyecta la sesión de base de datos
    usuario: Usuario = Depends(usuario_actual),  # inyecta el usuario autenticado
) -> ResumenFondos:  # retorna el resumen de fondos
    ingresos, gastos, total, reservados, disponible = obtener_saldo_calculado(db, usuario.id)  # calcula todos los saldos
    return ResumenFondos(  # arma la respuesta
        total_ingresos=float(ingresos),  # total de ingresos pagados
        total_gastos=float(gastos),  # total de gastos pagados
        saldo_total=float(total),  # ingresos menos gastos
        fondos_reservados=float(reservados),  # dinero apartado en metas
        saldo_disponible=float(disponible),  # dinero libre para usar
    )  # fin de ResumenFondos


@router.get("", response_model=list[MetaRead])  # endpoint GET /api/metas
def get_metas(  # lista las metas del usuario
    db: Session = Depends(get_db),  # inyecta la sesión de base de datos
    usuario: Usuario = Depends(usuario_actual),  # inyecta el usuario autenticado
) -> list[MetaRead]:  # retorna una lista de metas
    consulta = (  # arma la consulta
        select(MetaAhorro)  # selecciona de la tabla metas_ahorro
        .where(MetaAhorro.user_id == usuario.id)  # solo las metas del usuario (nadie ve metas ajenas)
        .order_by(MetaAhorro.created_at.asc())  # ordenadas de la más antigua a la más nueva
    )  # fin de la consulta
    metas = db.scalars(consulta).all()  # ejecuta la consulta y obtiene todas las metas
    return [_serializar_meta(m) for m in metas]  # convierte cada meta al formato de respuesta


@router.post("", response_model=MetaRead, status_code=status.HTTP_201_CREATED)  # endpoint POST /api/metas (responde 201)
def crear_meta(  # crea una nueva meta de ahorro
    payload: MetaWrite,  # datos enviados: nombre, monto objetivo y fecha límite
    db: Session = Depends(get_db),  # inyecta la sesión de base de datos
    usuario: Usuario = Depends(usuario_actual),  # inyecta el usuario autenticado
) -> MetaRead:  # retorna la meta creada
    meta = MetaAhorro(  # crea el objeto de la nueva meta
        user_id=usuario.id,  # la meta pertenece al usuario autenticado
        nombre=payload.nombre.strip(),  # nombre sin espacios sobrantes
        monto_objetivo=payload.monto_objetivo,  # monto que se quiere ahorrar
        monto_ahorrado=Decimal("0.00"),  # toda meta empieza con 0 Bs ahorrados
        fecha_limite=payload.fecha_limite,  # fecha límite para cumplirla
    )  # fin de MetaAhorro
    db.add(meta)  # agrega la meta a la sesión
    db.flush()  # la envía a la base para obtener su id

    db.add(  # agrega un evento al historial
        Historial(  # crea el registro de historial
            user_id=usuario.id,  # usuario que hizo la acción
            movimiento_id=None,  # no está ligado a un movimiento (las metas no crean movimientos)
            accion="meta_creada",  # tipo de acción
            detalle=f"Meta creada: {meta.nombre} · Objetivo: {float(meta.monto_objetivo):.1f} Bs",  # texto descriptivo
        )  # fin de Historial
    )  # fin de db.add
    db.commit()  # guarda todo en la base de datos
    db.refresh(meta)  # recarga la meta con los valores guardados
    return _serializar_meta(meta)  # devuelve la meta creada


@router.put("/{meta_id}", response_model=MetaRead)  # endpoint PUT /api/metas/{id}
def actualizar_meta(  # edita nombre, objetivo o fecha de una meta
    meta_id: UUID,  # id de la meta a editar
    payload: MetaUpdate,  # campos a cambiar (todos opcionales)
    db: Session = Depends(get_db),  # inyecta la sesión de base de datos
    usuario: Usuario = Depends(usuario_actual),  # inyecta el usuario autenticado
) -> MetaRead:  # retorna la meta actualizada
    meta = db.scalar(  # busca la meta
        select(MetaAhorro).where(MetaAhorro.id == meta_id, MetaAhorro.user_id == usuario.id)  # por id y que sea del usuario
    )  # fin de la búsqueda
    if not meta:  # si no existe o es de otro usuario
        raise HTTPException(status_code=404, detail="Meta de ahorro no encontrada")  # responde 404

    if payload.nombre is not None:  # si se envió un nombre nuevo
        meta.nombre = payload.nombre.strip()  # lo actualiza sin espacios sobrantes
    if payload.monto_objetivo is not None:  # si se envió un objetivo nuevo
        meta.monto_objetivo = payload.monto_objetivo  # lo actualiza
    if payload.fecha_limite is not None:  # si se envió una fecha nueva
        meta.fecha_limite = payload.fecha_limite  # la actualiza

    db.commit()  # guarda los cambios
    db.refresh(meta)  # recarga la meta
    return _serializar_meta(meta)  # devuelve la meta actualizada


@router.delete("/{meta_id}", status_code=status.HTTP_204_NO_CONTENT)  # endpoint DELETE /api/metas/{id} (responde 204)
def eliminar_meta(  # elimina una meta; su dinero vuelve al saldo disponible
    meta_id: UUID,  # id de la meta a eliminar
    db: Session = Depends(get_db),  # inyecta la sesión de base de datos
    usuario: Usuario = Depends(usuario_actual),  # inyecta el usuario autenticado
) -> None:  # no devuelve contenido
    meta = db.scalar(  # busca la meta
        select(MetaAhorro).where(MetaAhorro.id == meta_id, MetaAhorro.user_id == usuario.id)  # por id y que sea del usuario
    )  # fin de la búsqueda
    if not meta:  # si no existe o es de otro usuario
        raise HTTPException(status_code=404, detail="Meta de ahorro no encontrada")  # responde 404

    monto_liberado = meta.monto_ahorrado  # guarda cuánto dinero se libera antes de borrar
    nombre_meta = meta.nombre  # guarda el nombre para el historial

    db.delete(meta)  # borra la meta (al dejar de estar reservado, el dinero vuelve al disponible)
    db.add(  # agrega un evento al historial
        Historial(  # crea el registro de historial
            user_id=usuario.id,  # usuario que hizo la acción
            movimiento_id=None,  # no está ligado a un movimiento
            accion="meta_eliminada",  # tipo de acción
            detalle=f"Meta eliminada: {nombre_meta} · Fondos liberados al disponible: {float(monto_liberado):.1f} Bs",  # texto descriptivo
        )  # fin de Historial
    )  # fin de db.add
    db.commit()  # guarda los cambios


@router.post("/{meta_id}/asignar", response_model=MetaRead)  # endpoint POST /api/metas/{id}/asignar
def asignar_fondos_meta(  # pasa dinero del saldo disponible a una meta
    meta_id: UUID,  # id de la meta que recibe el dinero
    payload: MontoOperacion,  # monto a asignar
    db: Session = Depends(get_db),  # inyecta la sesión de base de datos
    usuario: Usuario = Depends(usuario_actual),  # inyecta el usuario autenticado
) -> MetaRead:  # retorna la meta actualizada
    meta = db.scalar(  # busca la meta
        select(MetaAhorro).where(MetaAhorro.id == meta_id, MetaAhorro.user_id == usuario.id)  # por id y que sea del usuario
    )  # fin de la búsqueda
    if not meta:  # si no existe o es de otro usuario
        raise HTTPException(status_code=404, detail="Meta de ahorro no encontrada")  # responde 404

    _, _, _, _, saldo_disponible = obtener_saldo_calculado(db, usuario.id)  # obtiene solo el saldo disponible actual

    try:  # intenta validar la asignación
        validar_asignacion(saldo_disponible, payload.monto)  # verifica que haya fondos suficientes
    except ValueError as e:  # si no hay fondos o el monto es inválido
        raise HTTPException(status_code=400, detail=str(e))  # responde 400 con el motivo

    meta.monto_ahorrado += payload.monto  # suma el monto a lo ahorrado (no se crea ningún movimiento)
    db.add(  # agrega un evento al historial
        Historial(  # crea el registro de historial
            user_id=usuario.id,  # usuario que hizo la acción
            movimiento_id=None,  # no está ligado a un movimiento
            accion="fondos_asignados",  # tipo de acción
            detalle=f"Asignó {float(payload.monto):.1f} Bs a la meta: {meta.nombre}",  # texto descriptivo
        )  # fin de Historial
    )  # fin de db.add
    db.commit()  # guarda los cambios
    db.refresh(meta)  # recarga la meta
    return _serializar_meta(meta)  # devuelve la meta actualizada


@router.post("/{meta_id}/retirar", response_model=MetaRead)  # endpoint POST /api/metas/{id}/retirar
def retirar_fondos_meta(  # devuelve dinero de una meta al saldo disponible
    meta_id: UUID,  # id de la meta de la que se retira
    payload: MontoOperacion,  # monto a retirar
    db: Session = Depends(get_db),  # inyecta la sesión de base de datos
    usuario: Usuario = Depends(usuario_actual),  # inyecta el usuario autenticado
) -> MetaRead:  # retorna la meta actualizada
    meta = db.scalar(  # busca la meta
        select(MetaAhorro).where(MetaAhorro.id == meta_id, MetaAhorro.user_id == usuario.id)  # por id y que sea del usuario
    )  # fin de la búsqueda
    if not meta:  # si no existe o es de otro usuario
        raise HTTPException(status_code=404, detail="Meta de ahorro no encontrada")  # responde 404

    try:  # intenta validar el retiro
        validar_retiro(meta.monto_ahorrado, payload.monto)  # verifica que la meta tenga ese dinero
    except ValueError as e:  # si no alcanza o el monto es inválido
        raise HTTPException(status_code=400, detail=str(e))  # responde 400 con el motivo

    meta.monto_ahorrado -= payload.monto  # resta el monto de lo ahorrado (vuelve al disponible)
    db.add(  # agrega un evento al historial
        Historial(  # crea el registro de historial
            user_id=usuario.id,  # usuario que hizo la acción
            movimiento_id=None,  # no está ligado a un movimiento
            accion="fondos_retirados",  # tipo de acción
            detalle=f"Retiró {float(payload.monto):.1f} Bs de la meta: {meta.nombre} hacia el saldo disponible",  # texto descriptivo
        )  # fin de Historial
    )  # fin de db.add
    db.commit()  # guarda los cambios
    db.refresh(meta)  # recarga la meta
    return _serializar_meta(meta)  # devuelve la meta actualizada


@router.post("/{meta_id}/transferir", response_model=MetaRead)  # endpoint POST /api/metas/{id}/transferir
def transferir_fondos_meta(  # mueve dinero de una meta a otra
    meta_id: UUID,  # id de la meta de origen
    payload: TransferenciaMetas,  # meta destino y monto a transferir
    db: Session = Depends(get_db),  # inyecta la sesión de base de datos
    usuario: Usuario = Depends(usuario_actual),  # inyecta el usuario autenticado
) -> MetaRead:  # retorna la meta de origen actualizada
    meta_origen = db.scalar(  # busca la meta de origen
        select(MetaAhorro).where(MetaAhorro.id == meta_id, MetaAhorro.user_id == usuario.id)  # por id y que sea del usuario
    )  # fin de la búsqueda
    if not meta_origen:  # si no existe o es de otro usuario
        raise HTTPException(status_code=404, detail="Meta de origen no encontrada")  # responde 404

    meta_destino = db.scalar(  # busca la meta de destino
        select(MetaAhorro).where(  # en la tabla de metas
            MetaAhorro.id == payload.meta_destino_id, MetaAhorro.user_id == usuario.id  # por id y que también sea del usuario
        )  # fin del where
    )  # fin de la búsqueda
    if not meta_destino:  # si no existe o es de otro usuario
        raise HTTPException(status_code=404, detail="Meta de destino no encontrada")  # responde 404

    try:  # intenta validar la transferencia
        validar_transferencia(  # verifica las reglas de la transferencia
            meta_origen.id, meta_destino.id, meta_origen.monto_ahorrado, payload.monto  # origen, destino, ahorrado y monto
        )  # fin de validar_transferencia
    except ValueError as e:  # si es la misma meta, no alcanza o el monto es inválido
        raise HTTPException(status_code=400, detail=str(e))  # responde 400 con el motivo

    meta_origen.monto_ahorrado -= payload.monto  # resta el monto de la meta de origen
    meta_destino.monto_ahorrado += payload.monto  # suma el monto a la meta de destino (el total reservado no cambia)

    db.add(  # agrega un evento al historial
        Historial(  # crea el registro de historial
            user_id=usuario.id,  # usuario que hizo la acción
            movimiento_id=None,  # no está ligado a un movimiento
            accion="fondos_transferidos",  # tipo de acción
            detalle=f"Transfirió {float(payload.monto):.1f} Bs de '{meta_origen.nombre}' a '{meta_destino.nombre}'",  # texto descriptivo
        )  # fin de Historial
    )  # fin de db.add
    db.commit()  # guarda ambos cambios juntos
    db.refresh(meta_origen)  # recarga la meta de origen
    return _serializar_meta(meta_origen)  # devuelve la meta de origen actualizada
