# Evidencia — Clase 18: Pruebas E2E y Experiencia del Usuario

## 1. Identificación y Reto de Clase

- **Materia:** Interacción Humano-Computador (IHC)
- **Proyecto:** Presupuesto Estudiantil
- **Reto de 30 minutos asignado (Slide 12):**
  > **Presupuesto:** `Registrar gasto -> el total cambia`
- **Flujo estandarizado (Slide 12):**
  $$\text{Semilla} \longrightarrow \text{Login} \longrightarrow \text{Crear} \longrightarrow \text{Lo ve en pantalla}$$

---

## 2. Cumplimiento de Reglas del Reto (Slide 11)

| Regla del docente | Cómo se cumple en el proyecto |
|---|---|
| **Semilla en un comando** | La función `sembrarDatos(request, { limiteMensual })` se ejecuta por API antes de cada test: registra al usuario si no existe, limpia transacciones anteriores y fija el límite mensual requerido para la prueba. |
| **Usuario de prueba en README** | Documentado en `README.md` y `frontend/README.md`: correo `e2e@prueba.com`, clave `123456`. |
| **Pasa desde cero, dos veces** | Se ejecutó dos veces consecutivas de forma idempotente con `2 passed (7.8s)` y `2 passed (7.3s)`. |
| **Escribir como usuario (Slide 7)** | Se emplean exclusivamente selectores semánticos y de accesibilidad: `getByRole`, `getByLabel` y `getByText`, evitando selectores CSS frágiles. |
| **Lo que no expliquen, no cuenta** | A continuación se detalla la justificación técnica, de interacción y de usabilidad de cada flujo. |

---

## 3. Flujos Implementados (`frontend/e2e/registrarGasto.spec.js`)

Se automatizó tanto el **camino feliz** como el **camino alternativo** (Slide 8: *"Por flujo: un camino feliz y uno alternativo"*).

### Flujo Principal: Registrar gasto válido $\rightarrow$ El total cambia

1. **Semilla:** Se configura un límite mensual alto ($10,000\text{ Bs}$) para que el gasto no tenga restricciones de presupuesto.
2. **Login:** El usuario inicia sesión a través de la interfaz usando etiquetas accesibles:
   ```javascript
   await page.getByRole('button', { name: 'Iniciar Sesión' }).click()
   await page.getByLabel('Correo electrónico').fill(email)
   await page.getByLabel('Contraseña', { exact: true }).fill(password)
   await page.getByRole('button', { name: 'Iniciar Sesión' }).click()
   ```
   *Comprobación previa:* Se verifica que el encabezado `Movimientos` esté visible y que el estado inicial indique `Total gastos: 0.0 Bs`.
3. **Crear:** Se abre el formulario y se completan los datos del movimiento:
   ```javascript
   await page.getByRole('button', { name: 'Nuevo Movimiento' }).click()
   await page.getByLabel('Categoría', { exact: true }).selectOption('Comida')
   await page.getByLabel('Monto (Bs)').fill('25.5')
   await page.getByLabel('Descripción (opcional)').fill('Almuerzo E2E')
   await page.getByRole('button', { name: 'Guardar' }).click()
   ```
4. **Lo ve en pantalla (Visibilidad del Estado - Heurística H1):**
   - El total de gastos cambia a `Total gastos: 25.5 Bs`.
   - Se visualiza el movimiento en la lista con `- 25.5 Bs` y su descripción `Almuerzo E2E`.

---

### Flujo Alternativo: Gasto que supera el límite $\rightarrow$ Se bloquea y el total no cambia

1. **Semilla:** Se establece un límite mensual bajo ($20\text{ Bs}$), menor al monto que se intentará ingresar ($25.5\text{ Bs}$).
2. **Login:** Inicia sesión con el usuario de prueba.
3. **Crear:** Se intenta ingresar un gasto de $25.5\text{ Bs}$.
4. **Validación en vivo (Heurística H5 - Prevención de Errores):**
   ```javascript
   await expect(page.getByText(/Supera tu límite mensual/)).toBeVisible()
   ```
5. **Bloqueo al guardar:** Al pulsar "Guardar", la app no efectúa el registro y muestra el mensaje de bloqueo:
   ```javascript
   await expect(page.getByText(/No se puede registrar, porque supera tu límite/)).toBeVisible()
   ```
6. **Lo ve en pantalla:**
   - El total de gastos **permanece inalterado**: `Total gastos: 0.0 Bs`.
   - El movimiento `- 25.5 Bs` **no aparece** en la lista (`toHaveCount(0)`).

---

## 4. Principios de IHC y Usabilidad Aplicados (Slides 6 a 9)

```
Concepto visto en clase (Slide 6)        En la prueba Playwright
─────────────────────────────────        ───────────────────────────
Flujos del app map                  -->  1 prueba para registrar gasto
Criterios de aceptación             -->  expect() por cada condición
Accesibilidad (Slide 7)             -->  getByRole() y getByLabel()
Visibilidad del estado (H1)         -->  toBeVisible() en total y lista
Prevención de errores (H5)          -->  Aviso en vivo de límite mensual
Estados reales (Slide 8)            -->  Validación de éxito y de bloqueo
```

> **Nota sobre diseño (Slide 7 y 9):**  
> *"El clic no prueba nada. Lo que aparece, sí."*  
> No basta con pulsar el botón Guardar; la prueba comprueba la respuesta del sistema en pantalla (cambio del número de total, persistencia en la lista y mensajes de retroalimentación).

---

## 5. Comandos de Ejecución

Con el backend FastAPI (puerto 8000) y el frontend Vite (puerto 5173) en ejecución:

```powershell
# Ejecución estándar (usando Edge instalado en Windows)
cd frontend
$env:E2E_CHANNEL="msedge"; npm run test:e2e

# Modo visual paso a paso (Slide 10: "Miren el navegador trabajar")
$env:E2E_CHANNEL="msedge"; npx playwright test --ui

# Modo headed (con ventana de navegador visible)
$env:E2E_CHANNEL="msedge"; npx playwright test --headed
```

---

## 6. Salida de Ejecución Exitosa

```text
> presupuesto-estudiantil-frontend@2.0.0 test:e2e
> playwright test

Running 2 tests using 1 worker

  ✓  1 [chromium] › e2e\registrarGasto.spec.js:65:3 › Registrar gasto › Flujo principal: registrar gasto -> el total cambia (4.2s)
  ✓  2 [chromium] › e2e\registrarGasto.spec.js:82:3 › Registrar gasto › Flujo alternativo: gasto que supera el límite -> se bloquea y el total no cambia (1.6s)

  2 passed (7.3s)
```
