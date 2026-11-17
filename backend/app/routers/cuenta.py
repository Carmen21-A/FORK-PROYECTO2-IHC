# Tarea 10 · Mis datos y salida honesta
#   GET    /api/cuenta/datos  -> todo lo que la app guarda de la persona (ver y descargar en JSON)
#   DELETE /api/cuenta        -> elimina la cuenta y TODOS sus datos (regla de Presupuesto Estudiantil)
from datetime import datetime, timezone  # fecha y hora de la exportación

from fastapi import APIRouter, Depends, HTTPException, status  # utilidades de FastAPI
from sqlalchemy import delete, select  # consultas de lectura y borrado
from sqlalchemy.orm import Session  # sesión de base de datos

from app.database import get_db  # dependencia que entrega la sesión
from app.dependencias import usuario_actual  # usuario con sesión válida
from app.logica.cuenta import TABLAS_DEL_USUARIO, fila, resumen_conteos  # reglas puras de la Tarea 10
from app.models import (  # tablas que guardan datos de la persona
    Evento,  # analítica (no tiene user_id: no es un dato de la persona)
    Historial,  # bitácora de cambios
    LimiteMensual,  # límite de cada mes
    MetaAhorro,  # metas de ahorro
    Movimiento,  # gastos e ingresos
    PresupuestoCategoria,  # presupuesto por categoría
    RecuperacionPassword,  # enlaces de recuperar contraseña
    Usuario,  # la cuenta
)  # fin de modelos
from app.schemas import ConfirmarEliminacion, ResultadoEliminacion  # esquemas de la Tarea 10

router = APIRouter(prefix="/cuenta", tags=["cuenta"])  # rutas /api/cuenta/...

# Qué columnas ve la persona de cada tabla (sin ids internos ni user_id)
CAMPOS = {  # tabla -> (modelo, columnas, orden)
    "movimientos": (Movimiento, ["fecha", "tipo", "categoria", "descripcion", "monto", "estado", "recurrencia", "created_at"], Movimiento.fecha),
    "limites_mensuales": (LimiteMensual, ["mes", "limite"], LimiteMensual.mes),
    "presupuestos_categoria": (PresupuestoCategoria, ["mes", "categoria", "monto"], PresupuestoCategoria.mes),
    "metas_ahorro": (MetaAhorro, ["nombre", "monto_objetivo", "monto_ahorrado", "fecha_limite", "created_at"], MetaAhorro.created_at),
    "historial": (Historial, ["accion", "detalle", "created_at"], Historial.created_at),
}  # fin de campos


@router.get("/datos")  # GET /api/cuenta/datos
def mis_datos(  # devuelve todo lo que la app guarda de la persona
    usuario: Usuario = Depends(usuario_actual),  # solo sus propios datos
    db: Session = Depends(get_db),  # sesión de base de datos
) -> dict:  # JSON listo para ver o descargar
    datos = {}  # una lista por tabla
    for clave, _ in TABLAS_DEL_USUARIO:  # recorre las tablas en el orden del resumen
        modelo, columnas, orden = CAMPOS[clave]  # modelo, columnas visibles y orden
        filas = db.scalars(select(modelo).where(modelo.user_id == usuario.id).order_by(orden)).all()  # solo las de esta persona
        datos[clave] = [fila(f, columnas) for f in filas]  # convierte cada fila a diccionario
    return {  # respuesta completa
        "exportado_en": datetime.now(timezone.utc).isoformat(),  # cuándo se generó
        "cuenta": {"nombre": usuario.nombre, "email": usuario.email, "creada_en": usuario.created_at.isoformat()},  # datos de la cuenta (sin contraseña)
        "resumen": resumen_conteos({clave: len(lista) for clave, lista in datos.items()}),  # cuántos hay de cada cosa
        **datos,  # movimientos, límites, presupuestos, metas e historial
    }  # fin de respuesta


@router.delete("", response_model=ResultadoEliminacion)  # DELETE /api/cuenta
def eliminar_cuenta(  # elimina la cuenta y todos sus datos
    payload: ConfirmarEliminacion,  # la persona confirmó en el diálogo
    usuario: Usuario = Depends(usuario_actual),  # cuenta con sesión válida
    db: Session = Depends(get_db),  # sesión de base de datos
) -> ResultadoEliminacion:  # cuántas filas se borraron de cada tabla
    if not payload.confirmar:  # sin confirmación explícita no se borra nada
        raise HTTPException(  # 422: falta confirmar
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,  # datos incompletos
            detail="Para eliminar tu cuenta tienes que confirmarlo en el diálogo.",  # dice qué hacer
        )  # fin de raise

    # Regla de Presupuesto Estudiantil: se elimina TODO. Se borra tabla por tabla (no se confía
    # solo en el ON DELETE CASCADE) para contar lo borrado y que funcione igual en SQLite.
    conteos = {}  # filas borradas por tabla
    for clave, _ in TABLAS_DEL_USUARIO:  # movimientos, límites, presupuestos, metas e historial
        modelo = CAMPOS[clave][0]  # modelo de la tabla
        conteos[clave] = db.execute(delete(modelo).where(modelo.user_id == usuario.id)).rowcount  # borra y cuenta
    db.execute(delete(RecuperacionPassword).where(RecuperacionPassword.user_id == usuario.id))  # enlaces de recuperación pendientes
    db.delete(usuario)  # por último, la cuenta: el correo y la contraseña desaparecen

    # Tarea 9: evento de éxito del flujo «Eliminar cuenta». Lo registra el servidor porque
    # después de borrar la cuenta el navegador ya no tiene sesión. No lleva ningún dato de la persona.
    db.add(Evento(evento="cuenta_eliminada", props={}))  # solo el nombre del evento y la fecha
    db.commit()  # todo o nada: si algo falla, no se borra nada
    return ResultadoEliminacion(eliminado=resumen_conteos(conteos))  # resumen para el mensaje final
