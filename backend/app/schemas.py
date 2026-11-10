from datetime import date, datetime  # importa tipos de fecha y fecha-hora para esquemas de validación
from decimal import Decimal  # importa Decimal para validación numérica precisa en peticiones
from typing import Literal  # importa Literal para restringir valores a listas fijas de strings
from uuid import UUID  # importa UUID para tipar identificadores únicos

from pydantic import BaseModel, ConfigDict, EmailStr, Field  # importa componentes base de validación de Pydantic

TipoMovimiento = Literal["gasto", "ingreso"]  # define los únicos dos tipos permitidos de movimiento
EstadoMovimiento = Literal["pendiente", "pagado", "cancelado"]  # define los tres estados válidos de un movimiento
Categoria = Literal["Transporte", "Comida", "Estudios", "Ocio", "Otros"]  # define las categorías permitidas
Recurrencia = Literal["semanal", "mensual"]  # define los tipos de frecuencia recurrente permitidos
PATRON_MES = r"^\d{4}-(0[1-9]|1[0-2])$"  # expresión regular para validar el formato de mes 'YYYY-MM'


# ---------- Autenticacion ----------
class Credenciales(BaseModel):  # esquema para recibir datos de inicio de sesión o registro
    email: EmailStr  # campo de correo electrónico validado con formato estándar
    password: str = Field(min_length=6, max_length=128)  # contraseña con mínimo 6 caracteres y máximo 128


class UsuarioRead(BaseModel):  # esquema para responder datos públicos de un usuario
    id: UUID  # identificador único del usuario
    email: EmailStr  # correo electrónico del usuario
    model_config = ConfigDict(from_attributes=True)  # permite leer datos directamente desde objetos SQLAlchemy


class Sesion(BaseModel):  # esquema devuelto al autenticar exitosamente
    access_token: str  # token JWT generado para autenticar siguientes peticiones
    token_type: str = "bearer"  # tipo de token fijado en 'bearer'
    user: UsuarioRead  # información básica del usuario autenticado


class NuevaPassword(BaseModel):  # esquema para peticiones de cambio de contraseña
    password: str = Field(min_length=6, max_length=128)  # nueva contraseña que debe tener al menos 6 caracteres


class SolicitudRecuperacion(BaseModel):  # esquema para pedir recuperación de contraseña
    email: EmailStr  # correo al cual enviar el enlace de recuperación


class VerificarRecuperacion(BaseModel):  # esquema para verificar el enlace de recuperación
    token_hash: str = Field(min_length=20, max_length=256)  # token recibido desde la URL


# ---------- Movimientos ----------
class MovimientoWrite(BaseModel):  # esquema para crear o actualizar un movimiento
    tipo: TipoMovimiento  # tipo de movimiento: gasto o ingreso
    monto: Decimal = Field(gt=0, max_digits=12)  # monto mayor a cero con hasta 12 dígitos
    categoria: Categoria  # categoría seleccionada de la lista permitida
    descripcion: str = Field(default="", max_length=500)  # descripción opcional de hasta 500 caracteres
    fecha: date  # fecha asignada al movimiento
    # Tarea 6: solo los gastos se repiten; None = no se repite
    recurrencia: Recurrencia | None = None  # frecuencia de repetición o None si es único


class MovimientoRead(BaseModel):  # esquema para serializar un movimiento en las respuestas de la API
    id: UUID  # identificador único del movimiento
    user_id: UUID  # identificador del usuario dueño del movimiento
    tipo: TipoMovimiento  # gasto o ingreso
    monto: float  # monto convertido a float para formato JSON
    categoria: str  # nombre de la categoría
    descripcion: str  # descripción del movimiento
    estado: EstadoMovimiento  # estado actual: pendiente, pagado o cancelado
    fecha: date  # fecha del movimiento
    recurrencia: Recurrencia | None = None  # frecuencia de repetición semanal, mensual o nula
    created_at: datetime  # fecha y hora de creación
    model_config = ConfigDict(from_attributes=True)  # mapeo directo desde el modelo ORM


class CambioEstado(BaseModel):  # esquema para la petición de transición de estado
    estado: EstadoMovimiento  # nuevo estado al que se desea pasar el movimiento


# Respuesta al cambiar de estado: si un gasto recurrente se paga, trae el siguiente
# que se genero, o el aviso de por que no se pudo generar
class EstadoCambiado(MovimientoRead):  # esquema de respuesta extendido al cambiar de estado
    siguiente: MovimientoRead | None = None  # siguiente ocurrencia generada si el gasto era recurrente
    aviso: str | None = None  # mensaje de advertencia si no se pudo generar la siguiente ocurrencia


# ---------- Limite mensual ----------
class LimiteRead(BaseModel):  # esquema de respuesta con la información del límite mensual
    mes: str  # mes en formato YYYY-MM
    limite: float | None  # monto del límite fijado o None si no se definió


class LimiteWrite(BaseModel):  # esquema para fijar o modificar el límite mensual
    limite: Decimal = Field(gt=0, max_digits=12)  # monto del límite mayor a cero


# ---------- Presupuesto por categoria ----------
class PresupuestoRead(BaseModel):  # esquema de respuesta para el presupuesto de una categoría
    categoria: str  # categoría correspondiente
    monto: float  # monto presupuestado asignado
    model_config = ConfigDict(from_attributes=True)  # lectura directa desde SQLAlchemy


class PresupuestoWrite(BaseModel):  # esquema para asignar monto a una categoría
    monto: Decimal = Field(gt=0, max_digits=12)  # monto asignado mayor a cero


# ---------- Historial ----------
class HistorialRead(BaseModel):  # esquema de lectura para eventos del historial
    id: UUID  # identificador del evento de historial
    movimiento_id: UUID | None  # id del movimiento referenciado
    accion: str  # tipo de acción realizada (creado, editado, etc.)
    detalle: str  # texto descriptivo del evento
    created_at: datetime  # fecha y hora en la que ocurrió el evento
    model_config = ConfigDict(from_attributes=True)  # lectura directa desde atributos del ORM


# ---------- Tarea 8: Metas de Ahorro y Fondos Disponibles ----------
class MetaWrite(BaseModel):  # esquema de entrada para crear una meta
    nombre: str = Field(min_length=1, max_length=100)  # nombre obligatorio de 1 a 100 caracteres
    monto_objetivo: Decimal = Field(gt=0, max_digits=12)  # objetivo mayor a cero
    fecha_limite: date  # fecha límite obligatoria


class MetaUpdate(BaseModel):  # esquema de entrada para editar una meta (todos los campos opcionales)
    nombre: str | None = Field(default=None, min_length=1, max_length=100)  # nuevo nombre, si se envía
    monto_objetivo: Decimal | None = Field(default=None, gt=0, max_digits=12)  # nuevo objetivo, si se envía
    fecha_limite: date | None = None  # nueva fecha límite, si se envía


class MetaRead(BaseModel):  # esquema de salida con los datos de una meta
    id: UUID  # identificador de la meta
    user_id: UUID  # dueño de la meta
    nombre: str  # nombre de la meta
    monto_objetivo: float  # monto que se quiere alcanzar
    monto_ahorrado: float  # dinero reservado en la meta
    fecha_limite: date  # fecha límite
    porcentaje: float = 0.0  # porcentaje de avance calculado
    cumplida: bool = False  # indica si ya se alcanzó el objetivo
    created_at: datetime  # fecha y hora de creación
    model_config = ConfigDict(from_attributes=True)  # permite leer directamente desde objetos del ORM


class MontoOperacion(BaseModel):  # esquema de entrada para asignar o retirar fondos
    monto: Decimal = Field(gt=0, max_digits=12)  # monto mayor a cero


class TransferenciaMetas(BaseModel):  # esquema de entrada para transferir entre metas
    meta_destino_id: UUID  # meta que recibe el dinero
    monto: Decimal = Field(gt=0, max_digits=12)  # monto mayor a cero


class ResumenFondos(BaseModel):  # esquema de salida con el resumen de saldos del usuario
    total_ingresos: float  # suma de ingresos pagados
    total_gastos: float  # suma de gastos pagados
    saldo_total: float  # ingresos menos gastos
    fondos_reservados: float  # dinero apartado en metas
    saldo_disponible: float  # saldo total menos fondos reservados

