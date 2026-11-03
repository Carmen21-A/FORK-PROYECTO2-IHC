# Reemplaza a lib/services/presupuestos_service.dart (Tarea 5: presupuesto por categoría)
# El resumen (consumo, porcentaje, estado) se arma en el frontend con
# construirResumenMensual, igual que en Flutter.
from fastapi import APIRouter, Depends, Path, status  # importa utilidades de FastAPI para rutas, dependencias y códigos de estado
from sqlalchemy import delete, select  # importa delete y select de SQLAlchemy para crear sentencias SQL
from sqlalchemy.orm import Session  # importa Session para interactuar con la base de datos

from app.database import get_db  # importa la función para inyectar la sesión de base de datos
from app.dependencias import usuario_actual  # importa la dependencia que devuelve el usuario autenticado
from app.models import PresupuestoCategoria, Usuario  # importa los modelos PresupuestoCategoria y Usuario
from app.schemas import PATRON_MES, PresupuestoRead, PresupuestoWrite  # importa esquemas de lectura, escritura y el patrón del mes

router = APIRouter(prefix="/presupuestos", tags=["presupuestos"])  # inicializa el enrutador de presupuestos
MesPath = Path(pattern=PATRON_MES, description="Mes en formato YYYY-MM")  # validador de parámetro de ruta para el mes (YYYY-MM)
CategoriaPath = Path(pattern="^(Transporte|Comida|Estudios|Ocio|Otros)$")  # validador de parámetro de ruta para categorías permitidas


# Obtiene todos los presupuestos asignados por categoría para un mes
@router.get("/{mes}", response_model=list[PresupuestoRead])  # endpoint GET para obtener presupuestos de un mes determinado
def get_presupuestos_mes(  # función controladora para listar presupuestos del mes
    mes: str = MesPath,  # recibe y valida el parámetro de ruta 'mes'
    db: Session = Depends(get_db),  # inyecta la sesión de la base de datos
    usuario: Usuario = Depends(usuario_actual),  # inyecta el usuario actualmente autenticado
) -> list[PresupuestoCategoria]:  # retorna una lista con los presupuestos del usuario
    consulta = select(PresupuestoCategoria).where(  # inicia consulta seleccionando de la tabla presupuestos_categoria
        PresupuestoCategoria.user_id == usuario.id,  # filtra por el id del usuario actual
        PresupuestoCategoria.mes == mes,  # filtra por el mes especificado en la ruta
    )  # fin de select
    return list(db.scalars(consulta))  # ejecuta la consulta y retorna la lista de resultados


# Guarda o actualiza el presupuesto de una categoría para un mes
@router.put("/{mes}/{categoria}", response_model=PresupuestoRead)  # endpoint PUT para crear o actualizar (upsert) un presupuesto
def save_presupuesto_categoria(  # función controladora para guardar o actualizar el presupuesto
    payload: PresupuestoWrite,  # cuerpo de la petición con el monto a presupuestar
    mes: str = MesPath,  # mes recibido en la ruta
    categoria: str = CategoriaPath,  # categoría recibida en la ruta
    db: Session = Depends(get_db),  # inyecta la sesión de base de datos
    usuario: Usuario = Depends(usuario_actual),  # inyecta el usuario autenticado
) -> PresupuestoCategoria:  # retorna el registro del presupuesto creado o actualizado
    existente = db.scalar(  # busca si ya existe un presupuesto previo para ese mes y categoría
        select(PresupuestoCategoria).where(  # inicia sentencia select
            PresupuestoCategoria.user_id == usuario.id,  # coincide con el usuario
            PresupuestoCategoria.mes == mes,  # coincide con el mes
            PresupuestoCategoria.categoria == categoria,  # coincide con la categoría
        )  # fin de where
    )  # ejecuta y obtiene el primer resultado o None
    if existente is not None:  # si el presupuesto ya existía en la base de datos
        existente.monto = payload.monto  # actualiza el monto existente con el nuevo valor
    else:  # si no existía previamente
        existente = PresupuestoCategoria(  # instancia un nuevo registro de presupuesto
            user_id=usuario.id, mes=mes, categoria=categoria, monto=payload.monto  # asigna usuario, mes, categoría y monto
        )  # fin de inicialización
        db.add(existente)  # añade el nuevo registro a la sesión de SQLAlchemy
    db.commit()  # confirma la transacción en la base de datos
    return existente  # retorna el registro actualizado o recién creado


# Elimina el presupuesto de una categoría para un mes específico
@router.delete("/{mes}/{categoria}", status_code=status.HTTP_204_NO_CONTENT)  # endpoint DELETE para borrar presupuesto retornando 204
def delete_presupuesto_categoria(  # función controladora para eliminar el presupuesto de una categoría
    mes: str = MesPath,  # mes recibido en la ruta
    categoria: str = CategoriaPath,  # categoría a eliminar
    db: Session = Depends(get_db),  # inyecta la sesión de base de datos
    usuario: Usuario = Depends(usuario_actual),  # inyecta el usuario autenticado
) -> None:  # no retorna contenido en el cuerpo
    db.execute(  # ejecuta la sentencia de eliminación
        delete(PresupuestoCategoria).where(  # construye la sentencia delete en presupuestos_categoria
            PresupuestoCategoria.user_id == usuario.id,  # solo registros del usuario autenticado
            PresupuestoCategoria.mes == mes,  # que correspondan al mes indicado
            PresupuestoCategoria.categoria == categoria,  # que correspondan a la categoría indicada
        )  # fin de where
    )  # fin de db.execute
    db.commit()  # confirma la eliminación en la base de datos
