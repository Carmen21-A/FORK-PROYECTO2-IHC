from datetime import date, datetime, timezone  # importa tipos de fecha, fecha-hora y zona horaria utc
from decimal import Decimal  # importa Decimal para manejar montos de dinero con precisión exacta
from uuid import UUID, uuid4  # importa tipos UUID y función uuid4 para generar identificadores únicos

from sqlalchemy import (  # importa constructores de columnas y restricciones de SQLAlchemy
    CheckConstraint,  # restricción CHECK para validar reglas a nivel de base de datos
    Date,  # tipo de dato Date para fechas sin hora
    DateTime,  # tipo de dato DateTime para marcas temporales
    ForeignKey,  # clave foránea para enlazar con otras tablas
    Numeric,  # tipo numérico decimal de alta precisión
    String,  # tipo de texto con longitud máxima
    UniqueConstraint,  # restricción UNIQUE para evitar combinaciones duplicadas
    Uuid,  # tipo de columna UUID compatible con PostgreSQL
)  # fin de imports de sqlalchemy
from sqlalchemy.orm import Mapped, mapped_column  # importa anotaciones modernas Mapped y mapped_column del ORM

from app.database import Base  # importa la clase Base declarativa compartida

# Las tablas son las mismas que habia en Supabase (ver database/init/001_esquema.sql)


def utc_now() -> datetime:  # función auxiliar para obtener la fecha y hora actual en zona horaria UTC
    return datetime.now(timezone.utc)  # retorna la fecha-hora actual en UTC


# Reemplaza a auth.users de Supabase
class Usuario(Base):  # modelo que representa la tabla de usuarios registrados
    __tablename__ = "usuarios"  # nombre físico de la tabla en PostgreSQL

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)  # llave primaria UUID generada automáticamente
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)  # correo electrónico único e indexado para búsquedas rápidas
    password_hash: Mapped[str] = mapped_column(String(255))  # hash criptográfico de la contraseña del usuario
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)  # fecha y hora de creación de la cuenta en UTC


class Movimiento(Base):  # modelo para registrar los movimientos financieros (gastos o ingresos)
    __tablename__ = "movimientos"  # nombre físico de la tabla en PostgreSQL
    __table_args__ = (  # restricciones adicionales a nivel de tabla
        CheckConstraint("tipo IN ('gasto', 'ingreso')", name="ck_movimientos_tipo"),  # asegura que el tipo solo sea gasto o ingreso
        CheckConstraint(  # restricción de estados válidos
            "estado IN ('pendiente', 'pagado', 'cancelado')",  # solo permite estos tres estados
            name="ck_movimientos_estado",  # nombre de la restricción
        ),  # fin de restricción de estado
        CheckConstraint("monto > 0", name="ck_movimientos_monto"),  # asegura que el monto sea estrictamente positivo
        CheckConstraint(  # restricción de recurrencia válida
            "recurrencia IN ('semanal', 'mensual')", name="ck_movimientos_recurrencia"  # solo acepta semanal o mensual si se define
        ),  # fin de restricción de recurrencia
    )  # fin de table_args

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)  # identificador único del movimiento
    user_id: Mapped[UUID] = mapped_column(  # columna que vincula el movimiento con un usuario
        Uuid(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), index=True  # clave foránea a usuarios con borrado en cascada
    )  # fin de columna user_id
    tipo: Mapped[str] = mapped_column(String(10))  # almacena 'gasto' o 'ingreso'
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 2))  # valor monetario con 12 dígitos y 2 decimales
    categoria: Mapped[str] = mapped_column(String(50))  # categoría del gasto o ingreso (ej. Comida, Transporte)
    descripcion: Mapped[str] = mapped_column(String(500), default="")  # detalle o nota del movimiento por defecto vacía
    estado: Mapped[str] = mapped_column(String(12), default="pendiente")  # estado del movimiento por defecto pendiente
    fecha: Mapped[date] = mapped_column(Date)  # fecha en la que se registra o programa el movimiento
    # Tarea 6: None = no se repite; "semanal" o "mensual" = gasto recurrente
    recurrencia: Mapped[str | None] = mapped_column(String(10), nullable=True, default=None)  # tipo de recurrencia o None si no se repite
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)  # fecha y hora de creación del registro


class LimiteMensual(Base):  # modelo para almacenar el tope máximo de gastos permitido en un mes
    __tablename__ = "limites_mensuales"  # nombre físico de la tabla en PostgreSQL
    __table_args__ = (  # restricciones de tabla
        UniqueConstraint("user_id", "mes", name="uq_limites_user_mes"),  # impide que un usuario tenga dos límites en un mismo mes
        CheckConstraint("limite > 0", name="ck_limites_limite"),  # asegura que el límite fijado sea mayor a cero
    )  # fin de table_args

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)  # identificador único del registro de límite
    user_id: Mapped[UUID] = mapped_column(  # columna que referencia al usuario dueño del límite
        Uuid(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), index=True  # clave foránea con eliminación en cascada
    )  # fin de columna user_id
    mes: Mapped[str] = mapped_column(String(7))  # mes en formato de texto 'YYYY-MM' (ej. '2026-11')
    limite: Mapped[Decimal] = mapped_column(Numeric(12, 2))  # monto monetario fijado como límite
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)  # fecha de registro del límite


class PresupuestoCategoria(Base):  # modelo para los presupuestos asignados a cada categoría en un mes
    __tablename__ = "presupuestos_categoria"  # nombre físico de la tabla en PostgreSQL
    __table_args__ = (  # restricciones de unicidad y chequeo
        UniqueConstraint("user_id", "mes", "categoria", name="uq_presupuesto_categoria"),  # único presupuesto por categoría al mes
        CheckConstraint("monto > 0", name="ck_presupuesto_categoria_monto"),  # el monto presupuestado debe ser mayor a cero
    )  # fin de table_args

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)  # identificador único del presupuesto
    user_id: Mapped[UUID] = mapped_column(  # clave foránea del usuario
        Uuid(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), index=True  # relación con borrado en cascada
    )  # fin de user_id
    mes: Mapped[str] = mapped_column(String(7))  # mes en formato 'YYYY-MM'
    categoria: Mapped[str] = mapped_column(String(50))  # nombre de la categoría (Transporte, Comida, etc.)
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 2))  # monto asignado para gastar en esa categoría
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)  # fecha de registro original
    updated_at: Mapped[datetime] = mapped_column(  # fecha de última actualización
        DateTime(timezone=True), default=utc_now, onupdate=utc_now  # se actualiza automáticamente con cada cambio
    )  # fin de updated_at


# Append-only: guarda movimiento_id aunque el movimiento ya se haya eliminado
class Historial(Base):  # modelo que registra una bitácora inmutable de eventos realizados
    __tablename__ = "historial"  # nombre físico de la tabla en PostgreSQL

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)  # identificador del evento de historial
    user_id: Mapped[UUID] = mapped_column(  # usuario que realizó la acción
        Uuid(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), index=True  # relación con cascada
    )  # fin de user_id
    movimiento_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)  # id del movimiento afectado (puede ser nulo si se eliminó)
    accion: Mapped[str] = mapped_column(String(30))  # acción ejecutada: creado, editado, eliminado o cambiado_estado
    detalle: Mapped[str] = mapped_column(String(700))  # texto descriptivo del cambio para lectura humana
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)  # marca de tiempo en la que ocurrió el evento


# Enlaces de "olvidé mi contraseña" (reemplaza el token_hash de Supabase)
class RecuperacionPassword(Base):  # modelo que almacena tokens para recuperar contraseñas
    __tablename__ = "recuperaciones_password"  # nombre físico de la tabla en PostgreSQL

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)  # identificador único del registro
    user_id: Mapped[UUID] = mapped_column(  # usuario solicitante de la recuperación
        Uuid(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), index=True  # clave foránea en cascada
    )  # fin de user_id
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)  # hash SHA256 del token enviado por correo
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))  # fecha y hora límite de validez del enlace
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)  # fecha y hora en la que se usó el enlace


# Tarea 8: Metas de Ahorro con fondos disponibles
class MetaAhorro(Base):  # modelo que representa una meta de ahorro del usuario
    __tablename__ = "metas_ahorro"  # nombre de la tabla en la base de datos
    __table_args__ = (  # restricciones a nivel de tabla
        CheckConstraint("monto_objetivo > 0", name="ck_metas_objetivo"),  # el objetivo debe ser mayor a cero
        CheckConstraint("monto_ahorrado >= 0", name="ck_metas_ahorrado"),  # lo ahorrado nunca puede ser negativo
    )  # fin de restricciones

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)  # identificador único de la meta
    user_id: Mapped[UUID] = mapped_column(  # dueño de la meta
        Uuid(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), index=True  # referencia al usuario; si se borra el usuario se borran sus metas
    )  # fin de user_id
    nombre: Mapped[str] = mapped_column(String(100))  # nombre de la meta (máximo 100 caracteres)
    monto_objetivo: Mapped[Decimal] = mapped_column(Numeric(12, 2))  # monto que se quiere alcanzar
    monto_ahorrado: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))  # dinero reservado en la meta (empieza en 0)
    fecha_limite: Mapped[date] = mapped_column(Date)  # fecha hasta la que se quiere cumplir la meta
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)  # fecha y hora de creación
    updated_at: Mapped[datetime] = mapped_column(  # fecha y hora de la última modificación
        DateTime(timezone=True), default=utc_now, onupdate=utc_now  # se actualiza sola cada vez que cambia la meta
    )  # fin de updated_at

