from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

# Las tablas son las mismas que habia en Supabase (ver database/init/001_esquema.sql)


def utc_now() -> datetime:  # función auxiliar para obtener la fecha y hora actual en zona horaria UTC
    return datetime.now(timezone.utc)  # retorna la fecha-hora actual en UTC


# Reemplaza a auth.users de Supabase
class Usuario(Base):  
    __tablename__ = "usuarios"  # nombre físico de la tabla en PostgreSQL

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)  # llave primaria UUID generada automáticamente
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)  # correo electrónico único e indexado para búsquedas rápidas
    nombre: Mapped[str | None] = mapped_column(String(100), nullable=True)  # nombre completo que la persona escribe al registrarse
    password_hash: Mapped[str] = mapped_column(String(255))  # hash criptográfico de la contraseña del usuario
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)  # fecha y hora de creación de la cuenta en UTC


class Movimiento(Base):
    __tablename__ = "movimientos"
    __table_args__ = (
        CheckConstraint("tipo IN ('gasto', 'ingreso')", name="ck_movimientos_tipo"),
        CheckConstraint(
            "estado IN ('pendiente', 'pagado', 'cancelado')",
            name="ck_movimientos_estado",
        ),
        CheckConstraint("monto > 0", name="ck_movimientos_monto"),
        CheckConstraint(
            "recurrencia IN ('semanal', 'mensual')", name="ck_movimientos_recurrencia"
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)  # identificador único del movimiento
    user_id: Mapped[UUID] = mapped_column(  # columna que vincula el movimiento con un usuario
        Uuid(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), index=True  # clave foránea a usuarios con borrado en cascada
    )  
    tipo: Mapped[str] = mapped_column(String(10))  # almacena 'gasto' o 'ingreso'
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 2))  # valor monetario con 12 dígitos y 2 decimales
    categoria: Mapped[str] = mapped_column(String(50))  # categoría del gasto o ingreso (ej. Comida, Transporte)
    descripcion: Mapped[str] = mapped_column(String(500), default="")  # detalle o nota del movimiento por defecto vacía
    estado: Mapped[str] = mapped_column(String(12), default="pendiente")  # estado del movimiento por defecto pendiente
    fecha: Mapped[date] = mapped_column(Date)  # fecha en la que se registra o programa el movimiento
    # Tarea 6: None = no se repite; "semanal" o "mensual" = gasto recurrente
    recurrencia: Mapped[str | None] = mapped_column(String(10), nullable=True, default=None)  # tipo de recurrencia o None si no se repite
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)  # fecha y hora de creación del registro


class LimiteMensual(Base):
    __tablename__ = "limites_mensuales"
    __table_args__ = (
        UniqueConstraint("user_id", "mes", name="uq_limites_user_mes"),
        CheckConstraint("limite > 0", name="ck_limites_limite"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), index=True
    )
    mes: Mapped[str] = mapped_column(String(7))
    limite: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class PresupuestoCategoria(Base):
    __tablename__ = "presupuestos_categoria"
    __table_args__ = (
        UniqueConstraint("user_id", "mes", "categoria", name="uq_presupuesto_categoria"),
        CheckConstraint("monto > 0", name="ck_presupuesto_categoria_monto"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), index=True
    )
    mes: Mapped[str] = mapped_column(String(7))
    categoria: Mapped[str] = mapped_column(String(50))
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )


# Append-only: guarda movimiento_id aunque el movimiento ya se haya eliminado
class Historial(Base):  # modelo que registra una bitácora inmutable de eventos realizados
    __tablename__ = "historial"  # nombre físico de la tabla en PostgreSQL

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), index=True
    )
    movimiento_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    accion: Mapped[str] = mapped_column(String(30))
    detalle: Mapped[str] = mapped_column(String(700))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


# Códigos de 4 dígitos de "olvidé mi contraseña" (antes eran enlaces)
class RecuperacionPassword(Base):
    __tablename__ = "recuperaciones_password"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), index=True
    )  
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    intentos: Mapped[int] = mapped_column(Integer, default=0)


# Tarea 8: Metas de Ahorro con fondos disponibles
class MetaAhorro(Base):
    __tablename__ = "metas_ahorro"
    __table_args__ = (
        CheckConstraint("monto_objetivo > 0", name="ck_metas_objetivo"),
        CheckConstraint("monto_ahorrado >= 0", name="ck_metas_ahorrado"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), index=True
    )
    nombre: Mapped[str] = mapped_column(String(100))
    monto_objetivo: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    monto_ahorrado: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    fecha_limite: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )


# Clase 21: Analítica de interacción. Registra la acción, no a la persona (no hay user_id ni email)
class Evento(Base):  # modelo que representa un evento de analítica
    __tablename__ = "eventos"  # nombre de la tabla en la base de datos

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)  # identificador único del registro
    evento: Mapped[str] = mapped_column(String(50), index=True)  # nombre del evento (p. ej. movimiento_guardado)
    props: Mapped[dict] = mapped_column(JSON().with_variant(JSONB(), "postgresql"), default=dict)  # propiedades mínimas (JSONB en PostgreSQL)
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)  # fecha y hora en que ocurrió

