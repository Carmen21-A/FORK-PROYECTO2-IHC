# Base de datos: PostgreSQL

```
database/
├── init/
│   └── 001_esquema.sql              # Crea todas las tablas
└── migracion/
    └── migrar_desde_supabase.py     # Copia los datos que había en Supabase
```

## Tablas

| Tabla | Para qué |
|---|---|
| `usuarios` | Cuentas (antes `auth.users` de Supabase) |
| `movimientos` | Ingresos y gastos |
| `limites_mensuales` | Límite de gasto por mes (`YYYY-MM`) |
| `presupuestos_categoria` | Presupuesto por categoría y mes |
| `historial` | Eventos: creado, editado, cambio_estado, eliminado |
| `recuperaciones_password` | Enlaces de "¿Olvidaste tu contraseña?" |

En Supabase cada usuario solo veía sus datos gracias a RLS. Ahora eso lo hace el backend: todas las consultas filtran por `user_id` del usuario con sesión.

## Crear la base

Con Docker se crea sola (`docker compose up`). Sin Docker:

```bash
createdb -U postgres budget
psql -U postgres -d budget -f database/init/001_esquema.sql
```

## Pasar los datos de Supabase

Supabase por dentro es PostgreSQL, así que el script lee directo de su base. **Supabase no se modifica**, solo se lee.

1. En Supabase: *Project Settings → Database → Connection string → URI*. Copiar la cadena y poner la contraseña de la base.
2. Con la base nueva ya creada (paso anterior), correr:

```bash
pip install "psycopg[binary]"
python database/migracion/migrar_desde_supabase.py ^
  --origen  "postgresql://postgres.xxxx:CLAVE@aws-0-xx.pooler.supabase.com:5432/postgres" ^
  --destino "postgresql://postgres:CLAVE@localhost:5432/budget"
```

Qué hace:

- Copia usuarios, movimientos, límites, presupuestos e historial **con los mismos id**.
- Las contraseñas se copian tal cual (bcrypt de Supabase): **los usuarios entran con su misma contraseña**. Al iniciar sesión, el backend la vuelve a guardar con Argon2.
- Los presupuestos que se guardaron con el formato viejo `2026-10#Comida` en `limites_mensuales` se pasan a `presupuestos_categoria`.
- Se puede correr varias veces: no duplica filas.
