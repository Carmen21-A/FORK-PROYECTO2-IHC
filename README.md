# Presupuesto Estudiantil

Aplicación web de presupuesto personal para estudiantes universitarios, desarrollada como proyecto de la materia Interacción Humano-Computador (IHC).

Permite registrarse, iniciar sesión y gestionar ingresos y gastos, con límite mensual, presupuesto por categoría, metas de ahorro, historial y la opción de descargar los datos o eliminar la cuenta.

> La primera versión se hizo con Flutter y Supabase. Se migró a web con la misma funcionalidad. El código de Flutter sigue en el historial de git (rama `main`, antes de la migración).

---

## Enlaces

| Qué | Enlace |
|---|---|
| **App en la nube** | https://fork-proyecto-2-ihc.vercel.app |
| API (backend) | https://presupuesto-api-80t4.onrender.com/api/health |
| Documentación interactiva de la API | https://presupuesto-api-80t4.onrender.com/docs |
| Repositorio (fork) | https://github.com/Carmen21-A/FORK-PROYECTO2-IHC |
| Reportes de pruebas y cobertura | [reportes/README.md](reportes/README.md) |
| Diseño en Figma | [https://www.figma.com/design/jsgAZTQJxWdZGsgzzknWwB/PRESUPUESTO-ESTUDIANTIL](https://www.figma.com/design/jsgAZTQJxWdZGsgzzknWwB/PRESUPUESTO-ESTUDIANTIL) |

> El backend usa el plan gratis de Render: si nadie lo usó en los últimos 15 minutos, **la primera petición tarda unos 50 segundos** en responder. Después va normal.

### Usuarios de prueba en la app en la nube

El enlace abre sin pedir permisos. Para entrar: **Iniciar Sesión** y uno de estos usuarios.

| Usuario | Correo | Contraseña | Qué tiene |
|---|---|---|---|
| Martita | `martita@presupuesto.com` | `martita123` | Cuenta con datos: 12 movimientos, límite mensual, 3 presupuestos por categoría, 3 metas de ahorro e historial |
| José | `yaknatolmo@necub.com` | `jose1234` | Cuenta nueva, sin movimientos. El correo es temporal: sirve para probar «¿Olvidaste tu contraseña?» y recibir el código de 4 dígitos |

### Evidencias de las clases y tareas

| Entrega | Documento |
|---|---|
| Clase 17 · Código ajeno y refactoring | [evidencias/clase-17.md](evidencias/clase-17.md) |
| Clase 18 · Pruebas E2E y experiencia del usuario | [evidencias/clase-18.md](evidencias/clase-18.md) |
| Clase 20 · Arquitectura de información | [evidencias/Clase-20.md](evidencias/Clase-20.md) |
| Clase 21 · Analítica de interacción | [evidencias/Clase-21.md](evidencias/Clase-21.md) |
| Clase 22 · Patrones oscuros | [evidencias/clase-22.md](evidencias/clase-22.md) |
| Clase 23 · Inventario y tokens | [evidencias/clase-23.md](evidencias/clase-23.md) |
| Tarea 6 · Toda la app con E2E y gastos recurrentes | [evidencias/tarea-6.md](evidencias/tarea-6.md) |
| Tarea 7 · Mejora por feedback y nueva funcionalidad | [evidencias/tarea-7.md](evidencias/tarea-7.md) |
| Tarea 8 · Metas con fondos disponibles | [evidencias/tarea-8.md](evidencias/tarea-8.md) |
| Tarea 9 · Analítica en todo el producto y aviso de presupuesto | [evidencias/tarea-9.md](evidencias/tarea-9.md) |
| Tarea 10 · Mis datos y salida honesta | [evidencias/tarea-10.md](evidencias/tarea-10.md) |

### Documentación de diseño e interacción

| Documento | Enlace |
|---|---|
| Ficha del proyecto | [docs/project-card.md](docs/project-card.md) |
| Evaluación heurística H1–H10 | [docs/evaluacion-heuristica.md](docs/evaluacion-heuristica.md) |
| Hallazgos heurísticos | [docs/hallazgos-heuristicos.md](docs/hallazgos-heuristicos.md) |
| Decisiones de interacción | [docs/decisiones-interaccion.md](docs/decisiones-interaccion.md) |
| Tareas 1 a 5 (acceso, estados, límite, filtros, presupuesto por categoría) | [docs/](docs/) |
| Base de datos y migración desde Supabase | [database/README.md](database/README.md) |
| Backend (rutas de la API) | [backend/README.md](backend/README.md) |
| Frontend (estructura de pantallas) | [frontend/README.md](frontend/README.md) |

---

## Integrantes

- Carmen Jenifer Aranibar Fernandez

Proyecto original (antes del fork): Céspede Rodas Sebastian y Mendoza Ribera Adolfo.

---

## Tecnologías usadas

| Parte | Tecnología |
|---|---|
| Frontend | [Vue 3](https://vuejs.org/) + [Vite](https://vite.dev/) + [Vue Router](https://router.vuejs.org/) |
| Backend | [FastAPI](https://fastapi.tiangolo.com/) (Python) + SQLAlchemy |
| Base de datos | [PostgreSQL](https://www.postgresql.org/) |
| Pruebas | pytest (backend), Vitest (frontend), Playwright + axe (E2E y accesibilidad) |
| Nube | Vercel (frontend), Render (backend), Neon (PostgreSQL), Brevo (correo) |

---

## Estructura del proyecto

```
Project2-IHC/
├── backend/      # API REST con FastAPI (incluye Dockerfile)
├── frontend/     # Aplicación web con Vue 3 (incluye vercel.json)
├── database/     # Esquema SQL de PostgreSQL y migración desde Supabase
├── docs/         # Documentación de las tareas 1 a 5 y de diseño
└── evidencias/   # Evidencias de las clases y tareas 6 a 10
```

Cada carpeta principal tiene su propio README con más detalle.

---

## Cómo correr el proyecto en tu computadora

Verificado en Windows con Python 3.13, Node.js 24, pnpm 12 y PostgreSQL 16. Sirve desde Python 3.12, Node.js 20 y PostgreSQL 15.

### 1. Base de datos

```bash
createdb -U postgres budget
psql -U postgres -d budget -f database/init/001_esquema.sql
```

### 2. Backend (puerto 8000)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate             # Windows (PowerShell o CMD)
# source .venv/Scripts/activate    # Windows con Git Bash
# source .venv/bin/activate        # Linux / Mac
pip install -r requirements-dev.txt
copy .env.example .env             # Linux/Mac/Git Bash: cp .env.example .env
uvicorn app.main:app --reload
```

En `backend/.env`, cambia `DATABASE_URL` por tu usuario y contraseña de PostgreSQL. Comprueba que el backend responda en http://localhost:8000/api/health; la documentación de la API está en http://localhost:8000/docs.

### 3. Frontend (puerto 5173), en otra terminal

```bash
cd frontend
pnpm install
pnpm dev
```

Abre http://localhost:5173. En desarrollo, Vite envía `/api` al backend del puerto 8000, así que no hace falta configurar nada más.

### Recuperar la contraseña en tu computadora

Si `SMTP_HOST` y `BREVO_API_KEY` están vacíos en `backend/.env`, el código de 4 dígitos **no se envía por correo**: aparece en la consola del backend (`Código de recuperación para ...: 1234`).

---

## Despliegue en la nube

| Parte | Servicio | Configuración |
|---|---|---|
| Base de datos | **Neon** (PostgreSQL) | Se crea el proyecto y se ejecuta `database/init/001_esquema.sql` en el *SQL Editor* |
| Backend | **Render** (Web Service, Docker) | Root Directory `backend`, puerto 8000, health check `/api/health` |
| Frontend | **Vercel** | Root Directory `frontend`, preset Vite, salida `dist`. `frontend/vercel.json` hace que al recargar `/movements` o `/metas` no salga 404 |
| Correo | **Brevo** (API por HTTPS) | Render, en el plan gratis, bloquea los puertos de correo (SMTP), así que el código de recuperación se envía por la API de Brevo |

**Variables de entorno.** Las claves nunca se suben al repositorio.

| Dónde | Variable | Valor |
|---|---|---|
| Render | `DATABASE_URL` | La dirección de Neon, empezando con `postgresql+psycopg://` |
| Render | `SECRET_KEY` | Clave larga y aleatoria para firmar las sesiones |
| Render | `CORS_ORIGINS`, `FRONTEND_URL` | `https://fork-proyecto-2-ihc.vercel.app` |
| Render | `PORT` | `8000` |
| Render | `RECOVERY_CODE_MINUTES` | `15` |
| Render | `BREVO_API_KEY` | Clave de API de Brevo, con permiso de *Emails transaccionales* |
| Render | `SMTP_FROM` | `Presupuesto Estudiantil <correo>`: remitente verificado en Brevo |
| Vercel | `VITE_API_URL` | `https://presupuesto-api-80t4.onrender.com/api` (después de cambiarla hay que hacer *Redeploy*) |

Cada `git push` a `main` vuelve a desplegar el frontend (Vercel) y el backend (Render) solos.

---

## Funcionalidades implementadas

- ✅ Registro con nombre completo, correo y contraseña confirmada
- ✅ Inicio y cierre de sesión; la sesión sigue al recargar
- ✅ Rutas privadas protegidas (sin sesión se vuelve al login)
- ✅ Cambio de contraseña con sesión iniciada
- ✅ Recuperación de contraseña con un código de 4 dígitos que llega al correo (sirve 15 minutos, 5 intentos)
- ✅ Registrar, editar y eliminar ingresos y gastos
- ✅ Estados del movimiento: pendiente → pagado → cancelado (no se edita el monto de uno pagado)
- ✅ Búsqueda y filtros por tipo, categoría, periodo y estado, con totales
- ✅ Límite mensual de gastos: aviso en naranja desde el 80 % y bloqueo si se supera
- ✅ Presupuesto mensual por categoría con estados óptimo / alerta / excedido
- ✅ Aviso antes de superar el presupuesto de una categoría, con botones iguales y sin culpa
- ✅ Gastos recurrentes (semanal o mensual): al pagarlos se genera el siguiente
- ✅ Metas de ahorro con fondos disponibles (asignar, retirar y transferir entre metas)
- ✅ Historial de acciones con búsqueda
- ✅ Navegación por intención: Todos los movimientos, Por pagar, Presupuestos y Metas
- ✅ Analítica de interacción por flujo (inicio, éxito, error y bloqueo), sin datos personales
- ✅ Mis datos: ver y descargar los datos (JSON o CSV) y eliminar la cuenta con una confirmación honesta
- ✅ Diseño responsivo (computadora, tablet y celular) y revisión de accesibilidad con axe en cada pantalla

---

## Pruebas

```bash
cd backend  && pytest            # lógica + API (86 pruebas, 100 % de cobertura)
cd frontend && pnpm test         # lógica de utils (81 pruebas, 100 % de líneas)
cd frontend && pnpm test:e2e     # E2E con Playwright (88 pruebas, ver abajo)
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

Para usar el Edge de Windows en vez del Chromium de Playwright:
PowerShell `$env:E2E_CHANNEL="msedge"; pnpm test:e2e`, Git Bash `E2E_CHANNEL=msedge pnpm test:e2e`.

Cada flujo tiene un camino feliz (el usuario hace todo bien) y uno o más alternativos (se equivoca).

| Archivo | Flujos |
|---|---|
| `e2e/flujo_principal.spec.ts` | **Reto de clase:** registrar gasto → el total cambia (y sigue al recargar). Alternativos: contraseña incorrecta, correo no registrado o mal escrito, campos vacíos, gasto que supera el límite, monto vacío o con letras |
| `e2e/acceso.spec.ts` | Login, sesión que sigue al recargar, cerrar sesión, rutas privadas sin sesión → login |
| `e2e/cuenta.spec.ts` | Registro con nombre y confirmación, cambiar contraseña, recuperar contraseña con el código de 4 dígitos |
| `e2e/movimientos.spec.ts` | Editar, eliminar, estados (pendiente → pagado → cancelado), buscar y filtrar |
| `e2e/limite_mensual.spec.ts` | Cambiar el límite; límite menor a lo gastado; letras |
| `e2e/presupuesto_categoria.spec.ts` | El gasto cuenta en su categoría; definir presupuesto; monto vacío o con letras |
| `e2e/aviso_presupuesto.spec.ts` | **Tarea 9:** aviso antes de superar el presupuesto: cancelar o confirmar |
| `e2e/historial.spec.ts` | Las acciones quedan en el historial; búsqueda sin resultados; historial vacío |
| `e2e/gastos_recurrentes.spec.ts` | **Tarea 6:** gasto semanal o mensual → al pagarlo aparece la próxima ocurrencia. Alternativos: supera el límite, gasto que no se repite, ingreso sin opción de repetir |
| `e2e/metas.spec.ts` | **Tarea 8:** crear meta, asignar, retirar y transferir fondos; fondos insuficientes |
| `e2e/arquitectura_informacion.spec.ts` | **Clase 20:** navegación por intención: «Por pagar» muestra solo los pendientes y, al pagarlos, los estados quedan iguales en todas las pestañas |
| `e2e/analitica.spec.ts`, `e2e/analitica_flujos.spec.ts` | **Clase 21 y Tarea 9:** eventos de inicio, éxito, error y bloqueo de cada flujo, sin datos personales |
| `e2e/etica.spec.ts` | **Clase 22:** confirmaciones con botones iguales y mensajes sin culpa |
| `e2e/mis_datos.spec.ts` | **Tarea 10:** ver y descargar los datos, eliminar la cuenta y no poder volver a entrar |
| `e2e/diseno.spec.ts` | Capturas de inicio, login, registro y recuperar (H4); axe en cada pantalla; botones de 44 px (Fitts) |

### Datos conocidos (semilla)

`pnpm semilla` (desde `frontend/`) deja la base `budget_e2e` siempre igual. Las pruebas la
ejecutan solas, y se puede correr también a mano para usar estos usuarios en la app de prueba.

| Usuario | Correo | Contraseña | Datos |
|---|---|---|---|
| Martita | `martita@presupuesto.com` | `martita123` | Límite de 500 Bs y presupuesto de Transporte de 100 Bs este mes; gasto "Pasaje de micro" de 40 Bs (pendiente) e ingreso "Mesada" de 300 Bs (pagado) |
| Pablo | `pablo@presupuesto.com` | `pablo123` | Cuenta nueva, sin movimientos |

Estos son los datos de la base de pruebas E2E. Los usuarios de la app en la nube están en la sección [Enlaces](#usuarios-de-prueba-en-la-app-en-la-nube).

---

## Notas

- Los archivos `.env` y `.env.*` nunca se suben al repositorio (están en `.gitignore`). La excepción es `.env.example`, que no tiene claves.
- Para pasar los datos que había en Supabase, ver [database/README.md](database/README.md).
