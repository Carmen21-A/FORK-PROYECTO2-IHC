# Hallazgos heurísticos (Presupuesto Estudiantil)

**Acción evaluada:** configurar el límite mensual y registrar un gasto (con un caso permitido y uno bloqueado).

## Tabla de hallazgos

| # | Pantalla y evidencia | Problema y consecuencia | Heurística | Severidad |
|---|---|---|---|---|
| 1 | **Movimientos → formulario, gasto que supera el límite.** Captura del SnackBar rojo: "No se puede registrar, porque supera tu limite mensual de X bs (llevas gastando Y bs)". | La app trata el presupuesto como una billetera y bloquea el registro. Un presupuesto es una meta, no un saldo, y la persona puede gastar más de lo planeado. Si el gasto ya ocurrió en la vida real, no puede registrarlo: sus datos quedan incompletos y el "gastado del mes" deja de reflejar la realidad. El mensaje tampoco ofrece una salida concreta. | **H3** Control y libertad (principal), con **H9** y **H2** | 3 |
| 2 | **Movimientos → búsqueda y filtros, total en pantalla.** Captura con un filtro activo (por ejemplo "este mes") mostrando el total junto a la lista. | `calcularMontoTotalMovimientos` suma todos los montos de la lista filtrada. Si esa lista incluye ingresos y movimientos cancelados, el total no coincide con el "gastado del mes" de la tarjeta del límite y no indica qué representa. La persona puede creer que gastó más o menos de lo real. | **H1** Visibilidad del estado del sistema, con **H2** | 2 |
| 3 | _Pendiente de elegir_ | | | |
