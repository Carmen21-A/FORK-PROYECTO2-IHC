-- ====================================================================
-- Migración: Tabla de presupuestos mensuales por categoría
-- Proyecto: Presupuesto Estudiantil (IHC)
-- ====================================================================

-- 1. Crear tabla si no existe
CREATE TABLE IF NOT EXISTS public.presupuestos_categoria (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    mes VARCHAR(7) NOT NULL, -- Formato 'YYYY-MM' (ej: '2026-10')
    categoria VARCHAR(50) NOT NULL, -- 'Transporte', 'Comida', 'Estudios', 'Ocio', 'Otros'
    monto NUMERIC(12, 2) NOT NULL CHECK (monto > 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE (user_id, mes, categoria)
);

-- 2. Habilitar Row Level Security (RLS)
ALTER TABLE public.presupuestos_categoria ENABLE ROW LEVEL SECURITY;

-- 3. Políticas de acceso (CRUD por usuario autenticado)
DROP POLICY IF EXISTS "Usuarios pueden ver sus propios presupuestos de categoría" ON public.presupuestos_categoria;
CREATE POLICY "Usuarios pueden ver sus propios presupuestos de categoría"
    ON public.presupuestos_categoria FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Usuarios pueden insertar sus propios presupuestos de categoría" ON public.presupuestos_categoria;
CREATE POLICY "Usuarios pueden insertar sus propios presupuestos de categoría"
    ON public.presupuestos_categoria FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Usuarios pueden actualizar sus propios presupuestos de categoría" ON public.presupuestos_categoria;
CREATE POLICY "Usuarios pueden actualizar sus propios presupuestos de categoría"
    ON public.presupuestos_categoria FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Usuarios pueden eliminar sus propios presupuestos de categoría" ON public.presupuestos_categoria;
CREATE POLICY "Usuarios pueden eliminar sus propios presupuestos de categoría"
    ON public.presupuestos_categoria FOR DELETE
    USING (auth.uid() = user_id);

-- 4. Índices para optimizar consultas por mes y usuario
CREATE INDEX IF NOT EXISTS idx_presupuestos_cat_user_mes
    ON public.presupuestos_categoria (user_id, mes);
