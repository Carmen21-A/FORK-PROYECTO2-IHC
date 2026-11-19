from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

TipoMovimiento = Literal["gasto", "ingreso"]
EstadoMovimiento = Literal["pendiente", "pagado", "cancelado"]
Categoria = Literal["Transporte", "Comida", "Estudios", "Ocio", "Otros"]
Recurrencia = Literal["semanal", "mensual"]
PATRON_MES = r"^\d{4}-(0[1-9]|1[0-2])$"  # expresión regular para validar el formato de mes 'YYYY-MM'


# ---------- Autenticacion ----------
class Credenciales(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class Registro(Credenciales):
    nombre: str | None = Field(default=None, max_length=100)

    @field_validator("nombre")
    @classmethod
    def limpiar_nombre(cls, valor: str | None) -> str | None:
        if valor is None:
            return None
        limpio = " ".join(valor.split())
        return limpio or None


class UsuarioRead(BaseModel):  # esquema para responder datos públicos de un usuario
    id: UUID  # identificador único del usuario
    email: EmailStr
    nombre: str | None = None
    model_config = ConfigDict(from_attributes=True)


class Sesion(BaseModel):
    access_token: str
    token_type: str = "bearer"  # tipo de token fijado en 'bearer'
    user: UsuarioRead  # información básica del usuario autenticado


class NuevaPassword(BaseModel):
    password: str = Field(min_length=6, max_length=128)


class SolicitudRecuperacion(BaseModel):
    email: EmailStr


class VerificarCodigo(BaseModel):
    email: EmailStr
    codigo: str = Field(pattern=r"^\d{4}$")


class RestablecerPassword(VerificarCodigo):
    password: str = Field(min_length=6, max_length=128)


# ---------- Movimientos ----------
class MovimientoWrite(BaseModel):
    tipo: TipoMovimiento
    monto: Decimal = Field(gt=0, max_digits=12)
    categoria: Categoria
    descripcion: str = Field(default="", max_length=500)
    fecha: date
    # Tarea 6: solo los gastos se repiten; None = no se repite
    recurrencia: Recurrencia | None = None
    # Tarea 9: True cuando el usuario ya vio el aviso de presupuesto y confirmó que quiere guardar
    confirmar_exceso: bool = False


class MovimientoRead(BaseModel):
    id: UUID
    user_id: UUID
    tipo: TipoMovimiento
    monto: float
    categoria: str
    descripcion: str
    estado: EstadoMovimiento
    fecha: date
    recurrencia: Recurrencia | None = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CambioEstado(BaseModel):
    estado: EstadoMovimiento


# Respuesta al cambiar de estado: si un gasto recurrente se paga, trae el siguiente
# que se genero, o el aviso de por que no se pudo generar
class EstadoCambiado(MovimientoRead):
    siguiente: MovimientoRead | None = None
    aviso: str | None = None


# ---------- Limite mensual ----------
class LimiteRead(BaseModel):
    mes: str
    limite: float | None


class LimiteWrite(BaseModel):
    limite: Decimal = Field(gt=0, max_digits=12)


# ---------- Presupuesto por categoria ----------
class PresupuestoRead(BaseModel):
    categoria: str
    monto: float
    model_config = ConfigDict(from_attributes=True)


class PresupuestoWrite(BaseModel):
    monto: Decimal = Field(gt=0, max_digits=12)


# ---------- Historial ----------
class HistorialRead(BaseModel):
    id: UUID
    movimiento_id: UUID | None
    accion: str
    detalle: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------- Tarea 8: Metas de Ahorro y Fondos Disponibles ----------
class MetaWrite(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    monto_objetivo: Decimal = Field(gt=0, max_digits=12)
    fecha_limite: date


class MetaUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    monto_objetivo: Decimal | None = Field(default=None, gt=0, max_digits=12)
    fecha_limite: date | None = None


class MetaRead(BaseModel):
    id: UUID
    user_id: UUID
    nombre: str
    monto_objetivo: float
    monto_ahorrado: float
    fecha_limite: date
    porcentaje: float = 0.0
    cumplida: bool = False
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class MontoOperacion(BaseModel):
    monto: Decimal = Field(gt=0, max_digits=12)


class TransferenciaMetas(BaseModel):
    meta_destino_id: UUID
    monto: Decimal = Field(gt=0, max_digits=12)


class ResumenFondos(BaseModel):
    total_ingresos: float
    total_gastos: float
    saldo_total: float
    fondos_reservados: float
    saldo_disponible: float


# ---------- Clase 21: Analítica de interacción ----------
class EventoWrite(BaseModel):
    evento: str = Field(min_length=1, max_length=50)
    props: dict = Field(default_factory=dict)
    fecha: datetime | None = None


class EventoRead(BaseModel):
    evento: str
    props: dict
    fecha: datetime
    model_config = ConfigDict(from_attributes=True)


class ConteoEvento(BaseModel):
    evento: str
    total: int


class PasoEmbudo(BaseModel):
    evento: str
    total: int
    caida: int


class MotivoError(BaseModel):
    motivo: str
    total: int


class Embudo(BaseModel):
    id: str
    nombre: str
    pasos: list[PasoEmbudo]
    porcentaje_terminan: int
    evento_error: str
    total_errores: int
    motivos: list[MotivoError]


class MayorCaida(BaseModel):
    flujo: str
    desde: str
    hasta: str
    caida: int


class ResumenBusquedas(BaseModel):
    realizadas: int
    sin_resultados: int
    porcentaje_sin_resultados: int


class PanelAnalitica(BaseModel):
    conteos: list[ConteoEvento]
    iniciados: int
    guardados: int
    porcentaje_terminan: int
    ultimos: list[EventoRead]
    embudos: list[Embudo] = []
    mayor_caida: MayorCaida | None = None
    busquedas: ResumenBusquedas | None = None



# ---------- Tarea 10 · Mis datos y salida honesta ----------
class ConfirmarEliminacion(BaseModel):
    confirmar: bool = False


class ResultadoEliminacion(BaseModel):
    eliminado: dict[str, int]
