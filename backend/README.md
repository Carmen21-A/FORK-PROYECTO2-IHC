# Backend: FastAPI

API REST de Presupuesto Estudiantil. Reemplaza a Supabase: hace el login, guarda los datos en PostgreSQL y aplica las reglas de negocio.

## Estructura

```
backend/
├── app/
│   ├── main.py            # Arma la API (antes lib/main.dart)
│   ├── config.py          # Variables de entorno (antes lib/env.dart)
│   ├── database.py        # Conexión a PostgreSQL
│   ├── models.py          # Tablas
│   ├── schemas.py         # Datos que entran y salen de la API
│   ├── security.py        # Contraseñas y tokens JWT
│   ├── correo.py          # Correo de recuperación de contraseña
│   ├── dependencias.py    # Usuario actual (sesión)
│   ├── logica/            # Reglas de las tareas (antes lib/utils)
│   │   ├── estado_movimiento.py
│   │   ├── historial.py
│   │   └── limite_mensual.py
│   └── routers/           # Endpoints (antes lib/services)
│       ├── auth.py            # auth_service.dart
│       ├── movimientos.py     # movements_service.dart
│       ├── limites.py         # limites_service.dart
│       ├── presupuestos.py    # presupuestos_service.dart
│       └── historial.py       # historial_service.dart
└── tests/
```

## Correr

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Documentación interactiva: http://localhost:8000/docs

## Endpoints

| Método | Ruta | Qué hace |
|---|---|---|
| POST | `/api/auth/register` | Crear cuenta |
| POST | `/api/auth/login` | Iniciar sesión |
| GET | `/api/auth/me` | Usuario actual |
| PATCH | `/api/auth/password` | Cambiar contraseña |
| POST | `/api/auth/password/recover` | Enviar un código de 4 dígitos al correo |
| POST | `/api/auth/password/verify` | Revisar el código (no lo gasta) |
| POST | `/api/auth/password/reset` | Guardar la contraseña nueva con el código y abrir sesión |
| GET | `/api/movimientos` | Listar (con filtros `texto`, `tipo`, `categoria`, `estado`, `desde`, `hasta`) |
| POST | `/api/movimientos` | Crear (valida el límite mensual) |
| PUT | `/api/movimientos/{id}` | Editar (no cambia el monto si está pagado) |
| PATCH | `/api/movimientos/{id}/estado` | pendiente → pagado → cancelado |
| DELETE | `/api/movimientos/{id}` | Eliminar |
| GET / PUT | `/api/limites/{YYYY-MM}` | Leer / guardar el límite mensual |
| GET | `/api/presupuestos/{YYYY-MM}` | Presupuestos por categoría del mes |
| PUT / DELETE | `/api/presupuestos/{YYYY-MM}/{categoria}` | Guardar / quitar un presupuesto |
| GET | `/api/historial` | Eventos, el más reciente primero |

Todas las rutas, excepto las de registro, login y recuperación, piden `Authorization: Bearer <token>`.

## Recuperar contraseña

Se manda un código de 4 dígitos al correo. Sirve por `RECOVERY_CODE_MINUTES` (15 minutos), solo el último código pedido es válido y con 5 errores deja de servir. En la base se guarda cifrado (hmac con `SECRET_KEY`), nunca el código en claro.

Si `SMTP_HOST` está vacío, el código se imprime en la consola del backend (útil para probar). Para enviarlo por correo de verdad, completar las variables `SMTP_*` del `.env` (por ejemplo, con una contraseña de aplicación de Gmail).

## Pruebas

```bash
pytest
```

Usan una base SQLite en memoria; no hace falta tener PostgreSQL encendido.
