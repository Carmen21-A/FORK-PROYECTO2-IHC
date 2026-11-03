# Reemplaza a lib/services/limites_service.dart (Tarea 4: límite mensual)
from calendar import monthrange  # importa monthrange para calcular cuántos días tiene un mes específico
from datetime import date  # importa date para construir fechas
from uuid import UUID  # importa UUID para tipar identificadores de usuario y movimientos

from fastapi import APIRouter, Depends, HTTPException, Path  # importa componentes de FastAPI para crear rutas y manejar excepciones HTTP
from sqlalchemy import func, select  # importa funciones de agregación como sum/coalesce y select de SQLAlchemy
from sqlalchemy.orm import Session  # importa Session para consultas con base de datos

from app.database import get_db  # importa dependencia para inyectar sesión de base de datos
from app.dependencias import usuario_actual  # importa dependencia para verificar sesión activa de usuario
from app.logica.limite_mensual import es_limite_menor_a_gasto  # importa función lógica que compara límite vs gastos
from app.models import LimiteMensual, Movimiento, Usuario  # importa los modelos ORM de la base de datos
from app.schemas import PATRON_MES, LimiteRead, LimiteWrite  # importa esquemas para validar entradas y salidas

router = APIRouter(prefix="/limites", tags=["limites"])  # crea el enrutador con prefijo /limites y tag 'limites'
MesPath = Path(pattern=PATRON_MES, description="Mes en formato YYYY-MM")  # parámetro de ruta validado con patrón 'YYYY-MM'


def get_limit(db: Session, user_id: UUID, mes: str) -> float | None:  # función auxiliar para consultar el límite fijado de un usuario en un mes
    limite = db.scalar(  # ejecuta la consulta select y retorna el valor de la primera columna
        select(LimiteMensual.limite).where(  # selecciona el campo limite de limites_mensuales
            LimiteMensual.user_id == user_id,  # filtra por el id del usuario
            LimiteMensual.mes == mes,  # filtra por el mes especificado
        )  # fin de where
    )  # fin de db.scalar
    return float(limite) if limite is not None else None  # convierte a float si existe el registro o retorna None


# Igual que calcularGastoTotalMes: solo gastos del mes que no esten cancelados
def calcular_gasto_total_mes(  # función para sumar los gastos acumulados que no hayan sido cancelados en un mes
    db: Session, user_id: UUID, mes: str, excluir_id: UUID | None = None  # parámetros: sesión db, id usuario, mes y un id opcional a excluir
) -> float:  # retorna el monto total acumulado como float
    anio, numero_mes = map(int, mes.split("-"))  # descompone el texto 'YYYY-MM' en año y número de mes enteros
    primero = date(anio, numero_mes, 1)  # obtiene la fecha del primer día del mes
    ultimo = date(anio, numero_mes, monthrange(anio, numero_mes)[1])  # obtiene la fecha del último día del mes usando monthrange
    consulta = select(func.coalesce(func.sum(Movimiento.monto), 0)).where(  # inicia consulta sumando montos o devolviendo 0 si no hay
        Movimiento.user_id == user_id,  # solo movimientos del usuario dado
        Movimiento.tipo == "gasto",  # solo movimientos de tipo gasto
        Movimiento.estado != "cancelado",  # excluye los gastos cancelados
        Movimiento.fecha >= primero,  # a partir del primer día del mes
        Movimiento.fecha <= ultimo,  # hasta el último día del mes
    )  # fin de where
    # Al editar, no se cuenta dos veces el monto anterior
    if excluir_id is not None:  # si se especificó un id de movimiento a excluir (por ejemplo al editarlo)
        consulta = consulta.where(Movimiento.id != excluir_id)  # añade filtro para no contar el registro actual dos veces
    return float(db.scalar(consulta) or 0)  # ejecuta la suma y retorna el resultado convertido a float


@router.get("/{mes}", response_model=LimiteRead)  # endpoint GET para leer el límite mensual del usuario
def leer_limite(  # función controladora para consultar el límite de un mes
    mes: str = MesPath,  # mes solicitado validado en la ruta
    db: Session = Depends(get_db),  # inyecta la sesión de base de datos
    usuario: Usuario = Depends(usuario_actual),  # inyecta el usuario autenticado
) -> LimiteRead:  # retorna el esquema LimiteRead con mes y límite
    return LimiteRead(mes=mes, limite=get_limit(db, usuario.id, mes))  # consulta y responde el objeto con el límite


@router.put("/{mes}", response_model=LimiteRead)  # endpoint PUT para establecer o modificar el límite de un mes
def save_month_limit(  # función controladora para guardar el límite mensual
    payload: LimiteWrite,  # cuerpo de la petición con el nuevo límite
    mes: str = MesPath,  # mes a actualizar recibido en la ruta
    db: Session = Depends(get_db),  # inyecta la sesión de base de datos
    usuario: Usuario = Depends(usuario_actual),  # inyecta el usuario autenticado
) -> LimiteRead:  # retorna el límite guardado
    gasto_actual = calcular_gasto_total_mes(db, usuario.id, mes)  # calcula cuánto lleva gastado el usuario en ese mes
    if es_limite_menor_a_gasto(float(payload.limite), gasto_actual):  # valida la regla de negocio: el límite no puede ser inferior a lo ya gastado
        raise HTTPException(  # lanza error HTTP 409 Conflicto si no cumple la regla
            status_code=409,  # código 409
            detail=f'No puede ser menor a lo ya gastado "{gasto_actual} Bs"',  # mensaje explicativo del rechazo
        )  # fin de raise HTTPException

    existente = db.scalar(  # busca si ya había un registro de límite para ese mes
        select(LimiteMensual).where(  # consulta en tabla limites_mensuales
            LimiteMensual.user_id == usuario.id,  # usuario actual
            LimiteMensual.mes == mes,  # mes en cuestión
        )  # fin de where
    )  # ejecuta la consulta
    if existente is not None:  # si ya existía un límite previo
        existente.limite = payload.limite  # actualiza el valor del límite existente
    else:  # si es la primera vez que se define límite en ese mes
        db.add(LimiteMensual(user_id=usuario.id, mes=mes, limite=payload.limite))  # inserta un nuevo registro de límite
    db.commit()  # guarda los cambios permanentemente en la base de datos
    return LimiteRead(mes=mes, limite=float(payload.limite))  # retorna el nuevo límite confirmado
