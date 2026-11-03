# Reemplaza a lib/services/historial_service.dart
from uuid import UUID  # importa UUID para tipar los identificadores únicos

from fastapi import APIRouter, Depends  # importa APIRouter para crear el enrutador y Depends para inyección de dependencias
from sqlalchemy import select  # importa select para construir consultas SQL con SQLAlchemy
from sqlalchemy.orm import Session  # importa Session para interactuar con la base de datos

from app.database import get_db  # importa get_db para obtener una sesión activa de base de datos
from app.dependencias import usuario_actual  # importa usuario_actual para proteger la ruta requiriendo autenticación
from app.models import Historial, Usuario  # importa los modelos Historial y Usuario
from app.schemas import HistorialRead  # importa el esquema de lectura de eventos de historial

router = APIRouter(prefix="/historial", tags=["historial"])  # define el enrutador con prefijo /historial y etiqueta 'historial'


# Guarda un evento (append-only)
def registrar_evento(  # función auxiliar para registrar un nuevo evento en la tabla historial
    db: Session,  # sesión de base de datos activa
    user_id: UUID,  # identificador del usuario que realizó la acción
    accion: str,  # nombre de la acción (creado, editado, etc.)
    detalle: str,  # descripción detallada del cambio
    movimiento_id: UUID | None = None,  # identificador opcional del movimiento asociado
) -> None:  # la función no retorna ningún valor
    db.add(  # añade una nueva fila al historial
        Historial(  # crea la instancia del modelo Historial
            user_id=user_id,  # asigna el id del usuario
            accion=accion,  # asigna la acción realizada
            movimiento_id=movimiento_id,  # asigna el id del movimiento
            detalle=detalle,  # asigna el texto descriptivo
        )  # fin de inicialización de Historial
    )  # fin de db.add


# Trae los eventos del usuario, reciente primero
@router.get("", response_model=list[HistorialRead])  # endpoint GET en /api/historial que retorna la lista de eventos del historial
def get_historial(  # función controladora para consultar el historial del usuario autenticado
    db: Session = Depends(get_db),  # inyecta la sesión de la base de datos
    usuario: Usuario = Depends(usuario_actual),  # inyecta el usuario autenticado actual
) -> list[Historial]:  # retorna una lista de instancias del modelo Historial
    consulta = (  # construye la sentencia select para consultar la base de datos
        select(Historial)  # selecciona los registros de la tabla historial
        .where(Historial.user_id == usuario.id)  # filtra para mostrar únicamente los eventos pertenecientes al usuario actual
        .order_by(Historial.created_at.desc())  # ordena de forma descendente para mostrar los más recientes primero
    )  # fin de construcción de consulta
    return list(db.scalars(consulta))  # ejecuta la consulta y retorna los resultados como una lista
