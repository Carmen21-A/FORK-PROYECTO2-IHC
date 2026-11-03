-- ====================================================================
-- Esquema de la base de datos - Presupuesto Estudiantil (IHC)
-- PostgreSQL. Son las mismas tablas que habia en Supabase; la tabla
-- "usuarios" reemplaza a auth.users y la seguridad por usuario (RLS)
-- ahora la hace el backend FastAPI filtrando siempre por user_id.
-- ====================================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Cuentas (antes auth.users de Supabase)
CREATE TABLE IF NOT EXISTS usuarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(320) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Ingresos y gastos (Tareas 2, 3 y 4)
CREATE TABLE IF NOT EXISTS movimientos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    tipo VARCHAR(10) NOT NULL,
    monto NUMERIC(12, 2) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    descripcion VARCHAR(500) NOT NULL DEFAULT '',
    estado VARCHAR(12) NOT NULL DEFAULT 'pendiente',
    fecha DATE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_movimientos_tipo CHECK (tipo IN ('gasto', 'ingreso')),
    CONSTRAINT ck_movimientos_estado CHECK (estado IN ('pendiente', 'pagado', 'cancelado')),
    CONSTRAINT ck_movimientos_monto CHECK (monto > 0)
);
-- Gastos recurrentes (Tarea 6). Con ALTER para que tambien se agregue en bases que ya existen
ALTER TABLE movimientos ADD COLUMN IF NOT EXISTS recurrencia VARCHAR(10)
    CONSTRAINT ck_movimientos_recurrencia CHECK (recurrencia IN ('semanal', 'mensual'));
CREATE INDEX IF NOT EXISTS ix_movimientos_user_id ON movimientos (user_id);
CREATE INDEX IF NOT EXISTS idx_movimientos_user_fecha
    ON movimientos (user_id, fecha, created_at);

-- Limite mensual de gastos (Tarea 4). mes = 'YYYY-MM'
CREATE TABLE IF NOT EXISTS limites_mensuales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    mes VARCHAR(7) NOT NULL,
    limite NUMERIC(12, 2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_limites_user_mes UNIQUE (user_id, mes),
    CONSTRAINT ck_limites_limite CHECK (limite > 0)
);
CREATE INDEX IF NOT EXISTS ix_limites_mensuales_user_id ON limites_mensuales (user_id);

-- Presupuesto mensual por categoria (Tarea 5)
-- categoria: 'Transporte', 'Comida', 'Estudios', 'Ocio', 'Otros'
CREATE TABLE IF NOT EXISTS presupuestos_categoria (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    mes VARCHAR(7) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    monto NUMERIC(12, 2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_presupuesto_categoria UNIQUE (user_id, mes, categoria),
    CONSTRAINT ck_presupuesto_categoria_monto CHECK (monto > 0)
);
CREATE INDEX IF NOT EXISTS ix_presupuestos_categoria_user_id ON presupuestos_categoria (user_id);
CREATE INDEX IF NOT EXISTS idx_presupuestos_cat_user_mes
    ON presupuestos_categoria (user_id, mes);

-- Historial de eventos (append-only). movimiento_id no tiene llave foranea
-- para que el evento "eliminado" conserve el id del movimiento borrado.
CREATE TABLE IF NOT EXISTS historial (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    movimiento_id UUID,
    accion VARCHAR(30) NOT NULL,
    detalle VARCHAR(700) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_historial_user_id ON historial (user_id);
CREATE INDEX IF NOT EXISTS idx_historial_user_created
    ON historial (user_id, created_at DESC);

-- Enlaces de "¿Olvidaste tu contraseña?" (antes los manejaba Supabase)
CREATE TABLE IF NOT EXISTS recuperaciones_password (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    token_hash VARCHAR(64) NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS ix_recuperaciones_password_user_id ON recuperaciones_password (user_id);
