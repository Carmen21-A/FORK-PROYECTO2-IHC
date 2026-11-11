# Endpoints de analítica de interacción (Clase 21)
from datetime import datetime, timezone  # importa datetime y timezone para la fecha por defecto en UTC

from fastapi import APIRouter, Depends, HTTPException, status  # importa utilidades de FastAPI
from sqlalchemy import func, select  # importa select y func para armar SELECT evento, COUNT(*) ... GROUP BY
from sqlalchemy.orm import Session  # importa Session para trabajar con la base de datos

from app.database import get_db  # importa la dependencia que entrega la sesión de base de datos
from app.dependencias import usuario_actual  # importa la dependencia de usuario autenticado
from app.logica.analitica import porcentaje_terminan, validar_evento  # importa las reglas puras de analítica
from app.models import Evento, Usuario  # importa los modelos Evento y Usuario
from app.schemas import ConteoEvento, EventoRead, EventoWrite, PanelAnalitica  # importa los esquemas de analítica

router = APIRouter(tags=["analitica"])  # crea el router (las rutas son /eventos y /analitica)

INICIO = "movimiento_iniciado"  # evento de inicio del flujo principal
EXITO = "movimiento_guardado"  # evento de éxito del flujo principal
CANTIDAD_ULTIMOS = 10  # cuántos eventos recientes muestra el panel


@router.post("/eventos", status_code=status.HTTP_201_CREATED)  # endpoint POST /api/eventos (lo llama track())
def registrar_evento(  # guarda un evento en la tabla eventos
    payload: EventoWrite,  # nombre, propiedades y fecha del evento
    db: Session = Depends(get_db),  # inyecta la sesión de base de datos
    _usuario: Usuario = Depends(usuario_actual),  # exige sesión válida, pero NO se guarda quién fue
) -> dict:  # responde un objeto simple de confirmación
    try:  # intenta validar el evento
        validar_evento(payload.evento, payload.props)  # rechaza eventos desconocidos o con datos de más
    except ValueError as e:  # si no cumple la regla
        raise HTTPException(status_code=422, detail=str(e))  # responde 422 con el motivo

    db.add(  # agrega el registro a la sesión
        Evento(  # crea el evento
            evento=payload.evento,  # nombre del evento
            props=payload.props,  # propiedades mínimas
            fecha=payload.fecha or datetime.now(timezone.utc),  # fecha enviada o la hora actual del servidor
        )  # fin de Evento
    )  # fin de db.add
    db.commit()  # guarda en la base de datos
    return {"ok": True}  # confirma que se guardó


@router.get("/analitica", response_model=PanelAnalitica)  # endpoint GET /api/analitica (panel, solo desarrollo)
def panel_analitica(  # cuenta los eventos y arma el panel
    db: Session = Depends(get_db),  # inyecta la sesión de base de datos
    _usuario: Usuario = Depends(usuario_actual),  # exige sesión válida para ver el panel
) -> PanelAnalitica:  # retorna el panel con conteos, porcentaje y últimos eventos
    filas = db.execute(  # ejecuta SELECT evento, COUNT(*) FROM eventos GROUP BY evento
        select(Evento.evento, func.count()).group_by(Evento.evento).order_by(Evento.evento)  # agrupa y cuenta por nombre
    ).all()  # obtiene todas las filas
    conteos = {evento: total for evento, total in filas}  # convierte las filas en diccionario evento -> total

    iniciados = conteos.get(INICIO, 0)  # cuántos empezaron (0 si ninguno)
    guardados = conteos.get(EXITO, 0)  # cuántos terminaron (0 si ninguno)

    ultimos = db.scalars(  # trae los eventos más recientes
        select(Evento).order_by(Evento.fecha.desc()).limit(CANTIDAD_ULTIMOS)  # ordenados del más nuevo al más viejo
    ).all()  # obtiene la lista

    return PanelAnalitica(  # arma la respuesta
        conteos=[ConteoEvento(evento=e, total=t) for e, t in conteos.items()],  # lista de conteos
        iniciados=iniciados,  # total de inicios
        guardados=guardados,  # total de éxitos
        porcentaje_terminan=porcentaje_terminan(iniciados, guardados),  # % que termina
        ultimos=[EventoRead.model_validate(e) for e in ultimos],  # últimos eventos
    )  # fin de PanelAnalitica
