# Evaluación heurística — Presupuesto Estudiantil

Tarea evaluada: configurar el límite mensual y registrar un gasto (flujo: definir límite → registrar gasto → ver la lista y el total).

| # | Pantalla y evidencia | Problema y consecuencia | Heurística | Severidad |
|---|----------------------|-------------------------|------------|-----------|
| 1 | Pantalla Movimientos: al tocar "Guardar" en el formulario (`_save`) y al guardar el límite en el diálogo (`_dialogoCambiarLimite`). | Mientras la app escribe en Supabase no aparece ningún indicador de carga ni el botón se deshabilita. La persona no sabe si el sistema está guardando y puede tocar varias veces → movimientos duplicados. | H1 Visibilidad del estado del sistema: mantener informado al usuario sobre lo que ocurre con una respuesta en tiempo razonable. | 3 |
| 2 | Pantallas Login (`_handleLogin`) y Registro (`_handleRegister`): al enviar credenciales incorrectas. | El error se captura en silencio (`catch (_)`) y solo se limpian los campos; no se muestra ningún mensaje. El usuario no sabe por qué no pudo entrar (contraseña, correo o conexión). | H9 Reconocer, diagnosticar y recuperarse de errores: los mensajes deben ir en lenguaje claro e indicar el problema. | 3 |
| 3 | Pantalla Movimientos: botón de estado de cada movimiento (`_cambiarEstado`), que recorre pendiente → pagado → cancelado. | Un solo toque cambia el estado y `cancelado` es irreversible (`siguienteEstado('cancelado')` devuelve `null`), sin confirmación ni opción de deshacer. Un toque accidental deja el movimiento cancelado sin forma de volver. | H3 Control y libertad: el usuario debe poder deshacer o salir de una acción iniciada por error. | 2 |
