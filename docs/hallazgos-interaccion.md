# Decisiones de Interacción — Presupuesto Estudiantil
**Clase 16 · Interacción Humano-Computador**

Tarea evaluada: Gestión y registro de movimientos financieros en la pantalla principal (`MovementsScreen`).

---

## Tabla de Hallazgos de Interacción

| Hallazgo            | Captura obligatoria                                                                                                                                                               | Justificación breve                                                                                                                                                                                                                                       | Estado al terminar |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------ |
| **Fitts**           | `docs/evidencias/clase-16/antes-fitts.png`<br>*(Pantalla con lista de movimientos y scroll requerido hasta el fondo para alcanzar el formulario de registro, sin botón flotante)* | El formulario y botón principal de registro se encontraban al fondo de una lista con desplazamiento, obligando a recorrer una distancia innecesaria. Anclamos la acción principal en un botón flotante accesible para el pulgar.                          | Corregido.         |
| **Hick**            | `docs/evidencias/clase-16/antes-hick.png`<br>*(Cabecera de filtros con 4 menús desplegables compitiendo a la vez: Tipo, Categoría, Periodo y Estado)*                             | La presencia simultánea de cuatro menús de filtro con 17 opciones compitiendo aumentaba el tiempo de decisión. Organizamos los filtros mediante jerarquía y revelación progresiva.                                                                        | Documentado.       |
| **Carga cognitiva** | `docs/evidencias/clase-16/antes-carga-cognitiva.png`<br>*(Filas de movimientos en texto plano concatenado: `Gasto - 50.0 Bs - Comida - 15 oct` sin jerarquía visual)*             | La concatenación de cuatro datos distintos en una sola línea de texto plano sobrecargaba la interpretación del usuario. Estructuramos cada movimiento con iconografía, tipografía jerárquica y montos diferenciados para permitir un escaneo instantáneo. | Corregido.         |

---

## Plan de Entrega (2 Commits)

1. **Commit 1:** `docs: registrar hallazgos de interacción`  
   - Registro de este documento con la tabla de los 3 hallazgos documentados.
   - Carpeta `docs/evidencias/clase-16/` con las capturas del **ANTES** para cada principio.

2. **Commit 2:** `fix: aplicar mejora de interacción`  
   - Código funcionando con la mejora de interacción implementada en Flutter.
   - Captura del **DESPUÉS** en `docs/evidencias/clase-16/` que demuestre la solución aplicada.
   - Actualización del estado en la tabla para el hallazgo corregido (`Corregido.`).

Se eligio la "carga cognitiva" para implementar y corregir