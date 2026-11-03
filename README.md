# Presupuesto Estudiantil

Aplicación web de presupuesto personal para estudiantes universitarios, desarrollada como proyecto de la materia Interacción Humano-Computador (IHC).

Permite registrarse, iniciar sesión y gestionar movimientos financieros personales (ingresos y gastos), con límite mensual, presupuesto por categoría e historial.

> La primera versión se hizo con Flutter y Supabase. Se migró a web con la misma funcionalidad. El código de Flutter sigue en el historial de git (rama `main`, antes de la migración).

---

## Integrantes

- Céspede Rodas Sebastian
- Mendoza Ribera Adolfo

---

## Tecnologías usadas

| Parte | Tecnología |
|---|---|
| Frontend | [Vue 3](https://vuejs.org/) + [Vite](https://vite.dev/) + [Vue Router](https://router.vuejs.org/) |
| Backend | [FastAPI](https://fastapi.tiangolo.com/) (Python) + SQLAlchemy |
| Base de datos | [PostgreSQL](https://www.postgresql.org/) |
| Pruebas | pytest (backend), Vitest (frontend), Playwright (E2E) |

---

## Estructura del proyecto

```
Project2-IHC/
├── backend/            # API REST con FastAPI
├── frontend/           # Aplicación web con Vue 3
├── database/           # Scripts SQL de PostgreSQL y migración desde Supabase
├── docs/               # Documentación de las tareas
├── evidencias/         # Capturas y evidencias
└── docker-compose.yml  # Levanta las 3 partes juntas
```

Cada carpeta tiene su propio README con más detalle.

---

## Cómo correr el proyecto

### Opción A: con Docker (todo junto)

```bash
docker compose up --build
```

Abrir http://localhost. La base de datos se crea sola la primera vez.

### Opción B: cada parte por separado (desarrollo)

Requisitos: Python 3.12+, Node.js 20+ y PostgreSQL 15+.

```bash
# 1. Base de datos: crear la base y las tablas
createdb -U postgres budget
psql -U postgres -d budget -f database/init/001_esquema.sql

# 2. Backend (puerto 8000)
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows  (Linux/Mac: source .venv/bin/activate)
pip install -r requirements-dev.txt
copy .env.example .env          # y editar DATABASE_URL con tu usuario/clave
uvicorn app.main:app --reload

# 3. Frontend (puerto 5173), en otra terminal
cd frontend
pnpm install
pnpm dev
```

Abrir http://localhost:5173. La documentación interactiva de la API está en http://localhost:8000/docs.

---

## Funcionalidades implementadas

- ✅ Registro de usuario con email y contraseña
- ✅ Inicio y cierre de sesión
- ✅ Cambio de contraseña (usuario autenticado)
- ✅ Recuperación de contraseña por email (enlace con token)
- ✅ Persistencia de sesión (la app recuerda al usuario al recargar)
- ✅ Rutas privadas protegidas (sin sesión no se puede acceder a movimientos)
- ✅ Registrar, editar y eliminar ingresos y gastos
- ✅ Estados del movimiento: pendiente → pagado → cancelado (no se edita el monto de uno pagado)
- ✅ Búsqueda y filtros por tipo, categoría, periodo y estado, con totales
- ✅ Límite mensual de gastos con aviso en vivo y bloqueo si se supera
- ✅ Presupuesto mensual por categoría con estados óptimo / alerta / excedido
- ✅ Historial de acciones con búsqueda
- ✅ Gastos recurrentes (semanal o mensual): al pagarlos se genera el siguiente y cuenta en el límite y en el presupuesto

---

## Pruebas

```bash
cd backend  && pytest            # lógica + API
cd frontend && pnpm test         # lógica de utils (portada de los tests de Flutter)
cd frontend && pnpm test:e2e     # E2E con Playwright (ver abajo)
```

### Pruebas E2E (Playwright)

Un solo comando levanta el backend (puerto 8099) y el frontend (puerto 5199) de prueba,
siembra la base `budget_e2e` y corre las pruebas. No hace falta tener la app encendida
y **no toca tu base `budget`**. Solo necesita PostgreSQL encendido y `backend/.env` configurado.

```bash
cd frontend
pnpm test:e2e --headed           # ver el navegador trabajar
pnpm test:e2e --ui               # cada acción, paso a paso
pnpm test:e2e flujo_principal    # solo el flujo principal
pnpm test:e2e --update-snapshots # aceptar un cambio visual intencional
pnpm exec playwright codegen http://localhost:5173   # grabar una prueba usando la app
```

Cada flujo tiene un camino feliz (el usuario hace todo bien) y uno o más alternativos (se equivoca).

| Archivo | Flujos |
|---|---|
| `e2e/flujo_principal.spec.ts` | **Reto de clase:** registrar gasto → el total cambia (y sigue al recargar). Alternativos: contraseña incorrecta, correo no registrado o mal escrito, campos vacíos, gasto que supera el límite, monto vacío o con letras |
| `e2e/acceso.spec.ts` | Login, sesión que sigue al recargar, cerrar sesión, rutas privadas sin sesión → login |
| `e2e/cuenta.spec.ts` | Registro, cambiar contraseña, recuperar contraseña |
| `e2e/movimientos.spec.ts` | Editar, eliminar, estados (pendiente → pagado → cancelado), buscar y filtrar |
| `e2e/limite_mensual.spec.ts` | Cambiar el límite; límite menor a lo gastado; letras |
| `e2e/presupuesto_categoria.spec.ts` | El gasto cuenta en su categoría; definir presupuesto; monto vacío o con letras |
| `e2e/historial.spec.ts` | Las acciones quedan en el historial; búsqueda sin resultados; historial vacío |
| `e2e/gastos_recurrentes.spec.ts` | **Tarea 6:** gasto semanal o mensual → al pagarlo aparece la próxima ocurrencia y el consumo sube. Alternativos: supera el límite (no se genera y avisa), gasto que no se repite, ingreso sin opción de repetir |
| `e2e/diseno.spec.ts` | Capturas de inicio, login, registro y recuperar (H4); axe en cada pantalla; botones de 44 px (Fitts) |

### Datos conocidos (semilla)

`pnpm semilla` (desde `frontend/`) deja la base `budget_e2e` siempre igual. Las pruebas la
ejecutan solas, y se puede correr también a mano para usar estos usuarios en la app de prueba.

| Usuario | Correo | Contraseña | Datos |
|---|---|---|---|
| Martita | `martita@presupuesto.com` | `martita123` | Límite de 500 Bs y presupuesto de Transporte de 100 Bs este mes; gasto "Pasaje de micro" de 40 Bs (pendiente) e ingreso "Mesada" de 300 Bs (pagado) |
| Pablo | `pablo@presupuesto.com` | `pablo123` | Cuenta nueva, sin movimientos |

Para usar el Edge de Windows en vez del Chromium de Playwright: `$env:E2E_CHANNEL="msedge"; pnpm test:e2e`

---

## Notas

- Los archivos `.env` nunca deben subirse al repositorio (ya están en `.gitignore`).
- Para pasar los datos que había en Supabase, ver [database/README.md](database/README.md).
