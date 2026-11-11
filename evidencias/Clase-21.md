# Evidencia · Clase 21: Analítica de Interacción

- **Materia:** Interacción Humano-Computador (IHC)
- **Proyecto:** Presupuesto Estudiantil (FastAPI + Vue 3 + PostgreSQL)
- **Fecha:** Martes 10/11/2026
- **Integrantes:**
  - Carmen Jenifer Aranibar Fernandez

---

## 1. La pregunta que responde la analítica

> **De las personas que empiezan a registrar un movimiento, ¿cuántas lo terminan de guardar?**

Para responderla se miden **dos eventos** del flujo principal de la app (*registrar un gasto o ingreso*) y se cuentan en un **panel propio** (`/analitica`).

No se registran clics (`boton_clic`): se registran **intentos de lograr algo** (inicio) y **logros confirmados** (éxito).

---

## 2. Los dos eventos (Slide 9: Presupuesto Estudiantil)

| | Evento de inicio | Evento de éxito |
|---|---|---|
| **Nombre** | `movimiento_iniciado` | `movimiento_guardado` |
| **Cuándo se dispara** | Al tocar **«Nuevo Movimiento»** (se abre el formulario). | **Después** de que el backend confirma que el movimiento se guardó en la BD. Si falla (monto vacío, supera el límite mensual, error de red), **no** se registra. |
| **Propiedades** | ninguna `{}` | `{ tipo, categoria }`: `tipo` es `gasto` o `ingreso`, y `categoria` viene de una lista fija (Transporte, Comida, Estudios, Ocio, Otros). |

Ejemplo de registro guardado:

```js
{
  evento: "movimiento_guardado",
  props: { tipo: "gasto", categoria: "Comida" },
  fecha: "2026-11-10T16:05:12Z"
}
```

Recorrido de un evento (Slide 7):

```
Toca «Guardar» → se guarda el movimiento → track() arma el registro → tabla eventos → se cuenta en /analitica
```

---

## 3. Dónde está el `track()` en el código

| Paso | Archivo |
|---|---|
| Función `track(evento, props)`: arma `{evento, props, fecha}`, lo guarda y hace `console.log('[evento]', registro)` | [`frontend/src/services/analitica.js`](../frontend/src/services/analitica.js) |
| `movimiento_iniciado` se dispara en `nuevoMovimiento()` | [`frontend/src/screens/MovementsScreen.vue`](../frontend/src/screens/MovementsScreen.vue) (línea 448) |
| `movimiento_guardado` se dispara solo si `MovementsService.create` tuvo éxito | [`frontend/src/screens/MovementsScreen.vue`](../frontend/src/screens/MovementsScreen.vue) (línea 388) |
| Endpoint `POST /api/eventos` que guarda en la tabla | [`backend/app/routers/analitica.py`](../backend/app/routers/analitica.py) |
| Regla de privacidad: solo acepta las propiedades definidas | [`backend/app/logica/analitica.py`](../backend/app/logica/analitica.py) |

---

## 4. Tabla `eventos` (misma base de datos de la app)

```sql
CREATE TABLE IF NOT EXISTS eventos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evento VARCHAR(50) NOT NULL,
    props JSONB NOT NULL DEFAULT '{}',
    fecha TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

La tabla **no tiene `user_id` ni email** a propósito: se registra la acción, no a la persona.

---

## 5. Panel propio `/analitica` (Slide 10, obligatorio)

Se entra desde el menú lateral, en **«Analítica»**. El backend (`GET /api/analitica`) ejecuta el equivalente a:

```sql
SELECT evento, COUNT(*) FROM eventos GROUP BY evento;
```

El panel muestra:
- Cuántos `movimiento_iniciado` hay.
- Cuántos `movimiento_guardado` hay.
- El **% que termina**: guardados ÷ iniciados × 100.
- Los **últimos 10 eventos**, con sus propiedades y la hora.
- La etiqueta **«solo desarrollo»** y un aviso de privacidad.

---

## 6. Privacidad: qué datos decidimos NO recopilar y por qué (Slide 6)

| Campo | ¿Se guarda? | Motivo |
|---|:---:|---|
| `evento` | ✅ | Dice qué pasó. |
| `fecha` | ✅ | Dice cuándo pasó. |
| `tipo` | ✅ | Valor fijo (gasto / ingreso), no identifica a nadie. |
| `categoria` | ✅ | Viene de una lista fija, no es texto escrito por el usuario. |
| `email` / nombre / `user_id` | ❌ | Identifican a la persona. La pregunta es sobre el flujo, no sobre quién lo usa. |
| `descripcion` | ❌ | Es texto libre: puede contener nombres o lugares (por ejemplo, *«taxi a casa de Juan»*). |
| `monto` | ❌ | La pregunta no lo necesita y es información financiera sensible. |

**Regla aplicada:** *«¿Lo necesito para responder mi pregunta? Si no, no se guarda. Nada "por si acaso".»*

La regla se cumple en **dos capas**:
1. **Frontend:** `track()` solo recibe `tipo` y `categoria`.
2. **Backend:** `validar_evento()` **rechaza con 422** cualquier propiedad no definida (email, descripción, monto) y cualquier categoría fuera de la lista.

---

## 7. Pruebas: una prueba por evento (Slide 8)

### Unitarias (Vitest): [`frontend/tests/unit/analitica.test.js`](../frontend/tests/unit/analitica.test.js)

| Prueba | Qué comprueba |
|---|---|
| `movimiento_iniciado` se registra una vez, sin propiedades | El evento se dispara una vez y sus props son `{}`. |
| `movimiento_guardado` se registra una vez, con tipo y categoría | Las propiedades son las definidas y ninguna más. |
| No aparece ningún dato personal | El registro no contiene monto, descripción, email ni nombre. |
| Si el guardado falla, no se registra | El evento de éxito solo se dispara después de guardar. |
| El registro se envía a la tabla eventos | `track()` envía el registro al backend. |

### Backend (pytest): [`backend/tests/test_analitica.py`](../backend/tests/test_analitica.py)
- Solo acepta eventos y propiedades definidos; rechaza `boton_clic`, `monto`, `email` y texto libre.
- Calcula el porcentaje (5 de 8 = 63 %, igual que el ejemplo de clase).
- La API guarda los eventos y el panel devuelve los conteos, el % y los últimos eventos.
- Rechaza datos personales (422) y exige sesión (401).

### E2E (Playwright): [`frontend/e2e/analitica.spec.ts`](../frontend/e2e/analitica.spec.ts)
1. Martita empieza dos movimientos, abandona uno y guarda el otro. El panel muestra **2 iniciados, 1 guardado y 50 %**. La descripción y el monto no aparecen, y los datos siguen al recargar.
2. Un gasto que supera el límite mensual cuenta como **iniciado pero no como guardado** (0 %).

### Comandos (PowerShell)

```powershell
# Backend
cd backend
.venv\Scripts\python -m pytest -v

# Frontend unitarias
cd ..\frontend
npm run test

# E2E (con PostgreSQL encendido)
$env:E2E_CHANNEL="msedge"; npm run test:e2e
```

### Resultados

- **Backend (pytest):** 41 passed
- **Frontend (vitest):** 57 passed
- **E2E (Playwright):** 65 passed, sin regresiones en las tareas anteriores
- **Fallos pendientes:** ninguno. En una corrida, `diseno.spec.ts › Historial no tiene problemas de accesibilidad` falló una vez de forma intermitente. Al repetirla 3 veces y volver a correr la suite completa pasó siempre, así que no se relaciona con la analítica.

---

## 8. Una decisión: ¿qué cambiaría si supiera esto? (Slide 2)

El panel responde: *¿qué % de los que empiezan a registrar un movimiento lo terminan?*

| Si el panel muestra… | Decisión de diseño |
|---|---|
| **% alto que termina** (la mayoría guarda) | El formulario funciona; no se toca. |
| **% bajo que termina** (muchos abren y no guardan) | Revisar dónde se pierde la gente: simplificar el formulario (por ejemplo, la descripción ya es opcional) y **avisar del límite mensual antes de que escriba el monto**, no recién al tocar «Guardar». |

Con los datos de prueba de la E2E (2 iniciados, 1 guardado = **50 %**), la mitad de los intentos no termina. La siguiente mejora sería mostrar el **límite disponible dentro del formulario**, antes de guardar.

---

## 9. Archivos afectados

### Backend
- `database/init/001_esquema.sql`: tabla `eventos`.
- `backend/app/models.py`: modelo `Evento`.
- `backend/app/schemas.py`: `EventoWrite`, `EventoRead`, `ConteoEvento`, `PanelAnalitica`.
- `backend/app/logica/analitica.py`: eventos permitidos, regla de privacidad y % que termina.
- `backend/app/routers/analitica.py`: `POST /api/eventos` y `GET /api/analitica`.
- `backend/app/main.py`: registro del router.
- `backend/semilla.py`: vacía `eventos` para que las pruebas sean reproducibles.
- `backend/tests/test_analitica.py`: pruebas del backend.

### Frontend
- `frontend/src/services/analitica.js`: `track()` y los dos eventos.
- `frontend/src/screens/MovementsScreen.vue`: `track()` en el inicio y en el éxito.
- `frontend/src/screens/AnaliticaScreen.vue`: panel `/analitica`.
- `frontend/src/router/appRouter.js`: ruta privada `/analitica`.
- `frontend/src/widgets/AppDrawer.vue`: opción «Analítica» en el menú.
- `frontend/tests/unit/analitica.test.js`: una prueba por evento.
- `frontend/e2e/analitica.spec.ts`: recorrido completo y caso de fallo.

---

## 10. Capturas

<!-- Pendiente: agregar las capturas del panel /analitica, de la consola con «[evento]» y del resultado de las pruebas -->
