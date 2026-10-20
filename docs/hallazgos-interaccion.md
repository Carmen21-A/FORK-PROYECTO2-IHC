# Decisiones de Interacción — Presupuesto Estudiantil
**Clase 16 · Interacción Humano-Computador**

Tarea evaluada: Gestión y registro de movimientos financieros en la pantalla principal (`MovementsScreen`).

---

## Tabla de Hallazgos de Interacción

| Hallazgo            | Capturas (Antes / Después) | Justificación breve | Estado al terminar |
| ------------------- | -------------------------- | ------------------- | ------------------ |
| **Fitts**           | • **Antes:** `docs/evidencias/clase-16/Fitts/antes.png`<br>• **Después:** `docs/evidencias/clase-16/Fitts/despues.png` | El formulario y botón principal de registro se encontraban al fondo de una lista con desplazamiento, obligando a recorrer una distancia innecesaria. Anclamos la acción principal en un botón flotante accesible para el pulgar. | Corregido. |
| **Hick**            | • **Antes:** `docs/evidencias/clase-16/Hick/antes.png`<br>• **Después:** `docs/evidencias/clase-16/Hick/despues.png` | La presencia simultánea de cuatro menús de filtro con 17 opciones compitiendo aumentaba el tiempo de decisión. Organizamos los filtros mediante jerarquía y revelación progresiva. | Corregido. |
| **Carga cognitiva** | • **Antes:** `docs/evidencias/clase-16/Carga cognitiva/antes.png`<br>• **Después:** `docs/evidencias/clase-16/Carga cognitiva/despues.png` | La concatenación de cuatro datos distintos en una sola línea de texto plano sobrecargaba la interpretación del usuario. Estructuramos cada movimiento con iconografía, tipografía jerárquica y montos diferenciados para permitir un escaneo instantáneo. | Corregido. |

---

## Plan de Entrega (2 Commits)

1. **Commit 1:** `docs: registrar hallazgos de interacción`  
   - Registro de este documento con la tabla de los hallazgos documentados.
   - Carpeta `docs/evidencias/clase-16/` con las capturas del **ANTES** en sus respectivas carpetas (`Fitts/`, `Hick/`, `Carga cognitiva/`).

2. **Commit 2:** `fix: aplicar mejoras de interacción (fitts, hick y carga cognitiva)`  
   - Código funcionando con las mejoras de interacción implementadas en Flutter.
   - Capturas del **DESPUÉS** en `docs/evidencias/clase-16/` demostrando las soluciones aplicadas.
   - Actualización del estado en la tabla con todos los hallazgos en `Corregido.`.